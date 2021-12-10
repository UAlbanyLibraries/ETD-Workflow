import os
import time
import bagit
import shutil
import zipfile
import tempfile
from datetime import datetime
from lxml import etree as ET

class InformationPackage:

    def __init__(self):
        self.excludeList = ["thumbs.db", "desktop.ini", ".ds_store"]
        if os.name == "nt":
            self.storagePath = "\\\\Lincoln\\Library\\ETDs\\storage"
            self.catalogingDir = "\\\\Lincoln\\Library\\ETDs\\CatalogingPackage"
            self.IRDir = "\\\\Lincoln\\Library\\ETDs\\IRPackages"
        else:
            self.storagePath = "/media/Library/ETDs/storage"
            self.catalogingDir = "/media/Library/ETDs/CatalogingPackage"
            self.IRDir = "/media/Library/ETDs/IRPackages"

    def loadSIP(self, path):
        """
        Accepts a path of an existing ETD SIP package as a string and loads it as a bag
        """
        print (path)
        if path is None:
            raise Exception("ERROR: not a valid SIP path to load.")
        elif not os.path.isdir(path) or not os.path.basename(path).startswith("etdadmin_upload_"):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP. You may want to create a SIP with .create().")
            
        self.path = path
        self.bag = bagit.Bag(path)
        self.identifier = self.bag.info['Bag-Identifier']
        self.data = os.path.join(self.path, "data") 
        self.status = self.bag.info['Bag-Type']

    def createSIP(self, path):
        """
        Accepts a path of an incoming .zip ETD package
        Copies it to a working directory
        Creates a new SIP, extracts the data there and turns it into a Bag as an SIP.
        Bag metadata will be held in memory, but you must .load() the SIP again to write to it or run .clean().
        """
        if not os.path.isfile(path):
            raise Exception("ERROR: " + str(path) + " is not a valid ProQuest package.")
        filename = os.path.basename(path)
        if not filename.startswith("etdadmin_upload_") and filename.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid ProQuest package.")
        
        self.identifier = os.path.splitext(os.path.basename(path))[0] 
        self.status = "Working"

        # Move the incoming package to the working directory
        self.workingPath = os.path.join(self.storagePath, "ProQuest_packages")
        print ("Moving " + os.path.basename(path) + " to " + self.workingPath)
        shutil.move(path, self.workingPath)
        self.workingPackage = os.path.join(self.workingPath, os.path.basename(path))

        self.pathSIP = os.path.join(self.storagePath, "SIP")

        self.path = os.path.join(self.pathSIP, self.identifier)
        if os.path.isdir(self.path):
            raise Exception("ERROR: " + self.identifier + " already exists as a directory.")
        elif os.path.isfile(self.path + ".zip"):
            raise Exception("ERROR: " + self.identifier + " already exists as a file.")
        else:
            os.mkdir(self.path)
        with zipfile.ZipFile(self.workingPackage, 'r') as zip_ref:
            zip_ref.extractall(self.path)
        
        metadata = {\
        'Bag-Type': 'ETD-SIP', \
        'Bag-Identifier':self.identifier, \
        'Bagging-Date': str(datetime.now().isoformat()), \
        'Posix-Date': str(time.time()), \
        #'BagIt-Profile-Identifier': 'https://archives.albany.edu/static/bagitprofiles/etd-aip-profile-v0.1.json', \
        }
        
        self.bag = bagit.make_bag(self.path, metadata)
        self.data = os.path.join(self.path, "data")
        self.metadata()
        self.status = "ETD-SIP"
        
        
    def metadata(self):
        """
        Reads useful metadata from the XML provided by ProQuest.
        Writes metadata to bag-info.txt where it can be easily ready by bagit-python
        """
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
        namePartList = ['DISS_fname', 'DISS_middle', 'DISS_surname' , 'DISS_suffix']
        authNum = 0
        for author in authorship:
            if author.tag == "DISS_author":
                authNum += 1
                name = author.find('DISS_name')
                authField = "Author-" + str(authNum)
                if name.find('DISS_fname').text:
                    self.bag.info[authField + '_fname'] = name.find('DISS_fname').text
                if name.find('DISS_middle').text:
                    self.bag.info[authField + '_mname'] = name.find('DISS_middle').text
                if name.find('DISS_surname').text:
                    self.bag.info[authField + '_lname'] = name.find('DISS_surname').text
                if name.find('DISS_suffix').text:
                    self.bag.info[authField + '_suffix'] = name.find('DISS_suffix').text
                if author.find("DISS_orcid").text:
                    self.bag.info[authField + '_orcid'] = author.find("DISS_orcid").text
                for contact in author:
                    if contact.tag == "DISS_contact":
                        emailType = contact.attrib['type']
                        if contact.find("DISS_email").text:
                            self.bag.info[authField + '_email_' + emailType] = contact.find("DISS_email").text
        self.bag.info['Title'] = root.xpath('//DISS_submission/DISS_description/DISS_title/text()')[0]
        self.bag.info['Completion-Date'] = root.xpath('//DISS_submission/DISS_description/DISS_dates/DISS_comp_date/text()')[0]
        self.bag.info['Acceptance-Date'] = root.xpath('//DISS_submission/DISS_description/DISS_dates/DISS_accept_date/text()')[0]
        self.bag.info['Degree-Name'] = root.xpath('//DISS_submission/DISS_description/DISS_degree/text()')[0]
        self.bag.info['Institution'] = root.xpath('//DISS_submission/DISS_description/DISS_institution/DISS_inst_name/text()')[0]
        self.bag.info['Department'] = root.xpath('//DISS_submission/DISS_description/DISS_institution/DISS_inst_contact/text()')[0]
        self.bag.info['Keywords'] = root.xpath('//DISS_submission/DISS_description/DISS_categorization/DISS_keyword/text()')[0]
        self.bag.info['Language'] = root.xpath('//DISS_submission/DISS_description/DISS_categorization/DISS_language/text()')[0]
        disciplineList = []


        self.bag.info['disciplines'] =
        self.bag.info['advisor1'] =
        self.bag.info['keywords'] =
        self.bag.info['Abstract'] =

        #document_type
        #embargo_date
        #publication_date
        #season

        self.bag.save()

    def makeCatalogPackage(self):
        """
        Takes a loaded SIP and creates a derivative package for cataloging
        """
        if self.data is None:
            raise Exception("Error: SIP must be loaded first.")
        incoming = os.path.join(self.catalogingDir, "incoming")
        catalogPackage = os.path.join(incoming, self.bag.info['Completion-Date'] + "_" + self.bag.info['Author-Surname'] + "_xxxxxxxx")
        if os.path.isdir(catalogPackage):
            raise Exception("Error, Cataloging Package directory already exists.")
        # Make cataloging package directory
        os.mkdir(catalogPackage)
        # Copy contents of data directory
        for thing in os.listdir(self.data):
            fullPath = os.path.join(self.data, thing)
            if thing.lower() in self.excludeList:
                pass
            elif os.path.isfile(fullPath):
                print ("Copying file " + thing)
                shutil.copy2(fullPath, catalogPackage)
            elif os.path.isdir(fullPath):
                print ("Copying directory " + thing)
                destThing = os.path.join(catalogPackage, thing)
                shutil.copytree(fullPath, destThing)
            else:
                raise Exception("Error, item in data directory unrecognizable: " + fullPath)
        # write ID to identifier.txt
        f = open(os.path.join(catalogPackage, "identifier.txt"), "w")
        f.write(self.identifier)
        f.close()

    def lookup(self, catalogingPackage):
        """
        Accepts the full path of a cataloging package and finds the correct SIP.
        Returns the path of the SIP as a string
        """
        idFile = os.path.join(catalogingPackage, "identifier.txt")
        if not os.path.isfile(idFile):
            raise Exception("Error: ID file is not present for " + catalogingPackage)
        f = open(idFile, "r")
        self.identifier = f.read()
        f.close()
        self.pathSIP = os.path.join(self.storagePath, "SIP")
        SIP = os.path.join(self.pathSIP, self.identifier)
        if not os.path.isdir(SIP):
            raise Exception("Error: Could not find SIP for cataloging package " + catalogingPackage)
        else:
            return SIP

    def makeIRPackage(self):
        """
        Takes a loaded SIP and creates a derivative package for the IR
        """
        if self.data is None:
            raise Exception("Error: SIP must be loaded first.")
        incoming = os.path.join(self.IRDir, "incoming")
        IRPackage = os.path.join(incoming, self.bag.info['Completion-Date'] + "_" + self.bag.info['Author-Surname'] + self.identifier)
        if os.path.isdir(IRPackage):
            raise Exception("Error, IR Package directory already exists.")
        # Make IR package directory
        os.mkdir(IRPackage)
        # Copy contents of data directory
        for thing in os.listdir(self.data):
            pass

                
        
    def clean(self):
        """
        Accepts a loaded AIP and cleans out filesystem artifacts
        from the data directory that interfere with Bag validation.
        """
        if self.data is None:
            raise Exception("Error: SIP must be loaded in order to be cleaned.")
        else:
            for root, dirs, files in os.walk(self.data):
                for file in files:
                    if file.lower() in self.excludeList:
                        filePath = os.path.join(root, file)
                        print ("removing " + filePath)
                        #os.remove(filePath)

    def createAIP(self, path):
        pass

        """
        #Compress package
        print ("compressing...")
        shutil.make_archive(self.bagDir, 'zip', self.bagDir)
        self.path = self.bagDir + ".zip"
        self.data = None
        if os.path.isfile(self.path):
            shutil.rmtree(self.bagDir)

        #remove the original ProQuest package
        #os.remove(self.workingPackage)
        """

    def close(self):
        """
        'closes' a zipped AIP bag by deleting the temp directory
        """
        if self.tempDir:
            shutil.rmtree(self.tempDir)

    def loadAIP(self, path):
        """
        Accepts a path of an existing zipped ETD AIP package as a string
        Then extracts it into a temporary directory
        and reads the Bag metadata
        """
        if path is None:
            raise Exception("ERROR: not a valid SIP path to load.")
        elif not os.path.isfile(path) or not path.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP. You may want to create a SIP with .create().")

        #with tempfile.TemporaryDirectory() as self.tempDir:
        self.tempDir = tempfile.mkdtemp()
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(self.tempDir)
            
        self.path = path
        self.bag = bagit.Bag(self.tempDir)
        self.identifier = self.bag.info['Bag-Identifier']
        self.data = os.path.join(self.tempDir, "data") 
        self.status = self.bag.info['Bag-Type']