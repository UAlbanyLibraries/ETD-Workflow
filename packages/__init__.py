import os
import time
import bagit
import shutil
import zipfile
import tempfile
from datetime import datetime
from lxml import etree as ET


class InformationPackage:

    def __init__(self, path):
        self.excludeList = ["thumbs.db", "desktop.ini", ".ds_store"]
        if os.name == "nt":
            rootPath = "\\\\Lincoln\\Library\\ETDs\\AIP_testing\\storage"
        else:
            rootPath = "/media/Library/ETDs/AIP_testing/storage"
        self.pathSIP = os.path.join(rootPath, 'SIP')
        self.pathAIP = os.path.join(rootPath, 'AIP')
        if not os.path.isdir(self.pathSIP):
            os.mkdir(self.pathSIP)
        if not os.path.isdir(self.pathAIP):
            os.mkdir(self.pathAIP)

    def __str__(self):
        return self.bagDir

    def load(self):
        # loads a compressed back by extracting it into a 
        if not os.path.isfile(self.bagDir) or not self.bagDir.endswith(".zip"):
            # needs additional validations
            raise Exception("ERROR: " + str(self.bagDir) + " is not a valid package. You may want to create a SIP with .create(), or generate an AIP with .package().")

        self.tempDir = tempfile.mkdtemp()
        with zipfile.ZipFile(self.bagDir, "r") as zip_ref:
            zip_ref.extractall(self.tempDir)

        self.bag = bagit.Bag(self.tempDir)
        self.identifier = self.bag.info['Bag-Identifier']
        self.data = os.path.join(self.tempDir, "data")

    def close(self):
        # closes a loaded bag by deleting its temp directory
        if self.tempDir:
            shutil.rmtree(self.tempDir)

    def clean(self):
        # this would not work for loaded .zip packages
        for root, dirs, files in os.walk(self.data):
            for file in files:
                if file.lower() in self.excludeList:
                    filePath = os.path.join(root, file)
                    print("removing " + filePath)
                    # os.remove(filePath)


class SubmissionInformationPackage(InformationPackage):
    def __init__(self, path):
        super().__init__(path)

        # check if existing SIP or data that needs to be packaged
        if os.path.dirname(path) == self.pathSIP:
            # already an existing SIP
            self.bagDir = path
        else:
            self.create(path)

    def create(self, path):
        # Creates a SIP from a path to a file or directory of files

        print('Generating SIP for package: ' + path)
        if not os.path.isfile(path):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")
        SIP = os.path.basename(path)
        if not SIP.startswith("etdadmin_upload_") and SIP.endswith(".zip"):
            # needs more validations?
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")

        self.identifier = os.path.splitext(os.path.basename(path))[0]

        self.bagDir = os.path.join(self.pathSIP, self.identifier)
        if os.path.isdir(self.bagDir):
            raise Exception("ERROR: " + self.identifier + " already exists as a directory.")
        elif os.path.isfile(self.bagDir + ".zip"):
            raise Exception("ERROR: " + self.identifier + " already exists as a file.")
        else:
            os.mkdir(self.bagDir)
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.bagDir)

        metadata = {
            'Bag-Type': 'ETD-SIP',
            'Bag-Identifier': self.identifier,
            'Bagging-Date': str(datetime.now().isoformat()),
            'Posix-Date': str(time.time()),
            # 'BagIt-Profile-Identifier': 'https://archives.albany.edu/static/bagitprofiles/etd-aip-profile-v0.1.json', \
        }

        self.bag = bagit.make_bag(self.bagDir, metadata)
        self.data = os.path.join(self.bagDir, "data")
        self.metadata()

        # Compress package
        print("Compressing...")
        shutil.make_archive(self.bagDir, 'zip', self.bagDir)
        if os.path.isfile(self.bagDir + ".zip"):
            shutil.rmtree(self.bagDir)
        self.bagDir = self.bagDir + ".zip"

        # Remove original

    def package(self):
        # Generates an AIP from a SIP

        # load zip file to tempDir
        self.load()

        # update metadata
        print("updating metadata...")
        self.bag.info["Bag-Type"] = "EAD-AIP"
        # The mms_id from the Alma bib record
        self.bag.info["Alma-Mms_id"] = ""
        # The url to the access copy (DIP) in the Scholar's Archive Institutional Repository
        self.bag.info["IR-URL"] = ""
        self.bag.save()

        # Validate SIP
        if not self.bag.is_valid():
            raise Exception("ERROR: SIP " + str(self.bagDir) + " failed to validate checksums!")
        else:
            # Move to AIP
            oldBagDir = self.bagDir
            self.bagDir = os.path.join(self.pathAIP, self.identifier)
            if os.path.isdir(self.bagDir):
                raise Exception("ERROR: " + self.identifier + " already exists as a directory.")
            elif os.path.isfile(self.bagDir + ".zip"):
                raise Exception("ERROR: " + self.identifier + " already exists as a file.")
            else:
                # Move temp bag to AIP
                shutil.copytree(self.tempDir, self.bagDir)

                self.bag = bagit.Bag(self.bagDir)
                self.data = os.path.join(self.bagDir, "data")

                # Compress package
                print("Compressing...")
                shutil.make_archive(self.bagDir, 'zip', self.bagDir)
                if os.path.isfile(self.bagDir + ".zip"):
                    shutil.rmtree(self.bagDir)

        # close tempDir
        self.close()

        # remove compressed SIP
        os.remove(oldBagDir)

        # return and AIP
        AIP = ArchivalInformationPackage(self.bagDir + ".zip")
        return AIP

    def metadata(self):
        # Parses an XML file included in the ETD package and adds useful metadata to the Bag

        xmlCount = 0
        for file in os.listdir(self.data):
            if file.endswith("_DATA.xml"):
                xmlCount += 1
                self.proquestXML = os.path.join(self.data, file)
        if xmlCount != 1:
            raise Exception("ERROR: Failed to find ProQuest XML file. " + str(xmlCount) + " relevant files found.")
        root = ET.parse(self.proquestXML).getroot()
        authorList = []
        emailList = []
        authorship = root.xpath('//DISS_submission/DISS_authorship')[0]
        namePartList = ['DISS_fname', 'DISS_middle', 'DISS_surname', 'DISS_suffix']
        for author in authorship:
            if author.tag == "DISS_author":
                name = author.find('DISS_name')
                nameList = []
                for namePart in namePartList:
                    if name.find(namePart).text:
                        nameList.append(name.find(namePart).text)
                authorList.append(" ".join(nameList))
                if author.find('DISS_contact').find('DISS_email').text:
                    emailList.append(author.find('DISS_contact').find('DISS_email').text)
        self.bag.info['Author'] = "|".join(authorList)
        self.bag.info['Author-Email'] = "|".join(emailList)

        self.bag.info['Title'] = root.xpath('//DISS_submission/DISS_description/DISS_title/text()')[0]
        self.bag.info['Completion-Date'] = root.xpath('//DISS_submission/DISS_description/DISS_dates/DISS_comp_date/text()')[0]

        self.bag.save()


class ArchivalInformationPackage(InformationPackage):
    def __init__(self, path):
        super().__init__(path)

        self.bagDir = path
