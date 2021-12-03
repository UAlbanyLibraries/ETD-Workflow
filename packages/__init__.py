import os
import time
import bagit
import shutil
import zipfile
import tempfile
from datetime import datetime
from lxml import etree as ET

class ArchivalInformationPackage:

    def __init__(self):
        self.excludeList = ["thumbs.db", "desktop.ini", ".ds_store"]
        if os.name == "nt":
            self.pathAIP = "\\\\Lincoln\\Library\\ETDs\\AIP_testing\\storage"
            self.catalogingDir = "\\\\Lincoln\\Library\\ETDs\\CatalogingPackage"
        else:
            self.pathAIP = "/media/Library/ETDs/AIP_testing/storage"
            self.catalogingDir = "/media/Library/ETDs/CatalogingPackage"
        
    def load(self, path):
        """
        Accepts a path of an existing ETD AIP package
        Then extracts it into a temporary directory
        and reads the Bag metadata
        """
        if not os.path.isfile(path) or not path.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid AIP. You may want to create a AIP with .create().")

        #with tempfile.TemporaryDirectory() as self.tempDir:
        self.tempDir = tempfile.mkdtemp()
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(self.tempDir)
            
        self.path = path
        self.bag = bagit.Bag(self.tempDir)
        self.identifier = self.bag.info['Bag-Identifier']
        self.data = os.path.join(self.tempDir, "data") 
        self.status = "AIP"

    def close(self):
        """
        'closes' a bag by deleting the temp directory
        """
        if self.tempDir:
            shutil.rmtree(self.tempDir)
    
    def create(self, path):
        """
        Accepts a path of an incoming .zip ETD package as a SIP
        Creates a new AIP, extracts the data there and turns it into a Bag as an AIP.
        Bag metadata will be held in memory, but you must .load() the AIP again to write to it or run .clean().
        """
        if not os.path.isfile(path):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")
        SIP = os.path.basename(path)
        if not SIP.startswith("etdadmin_upload_") and SIP.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")
        
        self.identifier = os.path.splitext(os.path.basename(path))[0] 
        self.status = "SIP"

        self.bagDir = os.path.join(self.pathAIP, self.identifier)
        if os.path.isdir(self.bagDir):
            raise Exception("ERROR: " + self.identifier + " already exists as a directory.")
        elif os.path.isfile(self.bagDir + ".zip"):
            raise Exception("ERROR: " + self.identifier + " already exists as a file.")
        else:
            os.mkdir(self.bagDir)
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.bagDir)
        
        metadata = {\
        'Bag-Type': 'ETD-AIP', \
        'Bag-Identifier':self.identifier, \
        'Bagging-Date': str(datetime.now().isoformat()), \
        'Posix-Date': str(time.time()), \
        #'BagIt-Profile-Identifier': 'https://archives.albany.edu/static/bagitprofiles/etd-aip-profile-v0.1.json', \
        }
        
        self.bag = bagit.make_bag(self.bagDir, metadata)
        self.data = os.path.join(self.bagDir, "data")
        self.metadata()
        self.status = "AIP"
        
        #Compress package
        print ("compressing...")
        shutil.make_archive(self.bagDir, 'zip', self.bagDir)
        self.path = self.bagDir + ".zip"
        self.data = None
        if os.path.isfile(self.path):
            shutil.rmtree(self.bagDir)
        
    def metadata(self):
        
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
        for author in authorship:
            if author.tag == "DISS_author":
                name = author.find('DISS_name')
                nameList = []
                for namePart in namePartList:
                    if name.find(namePart).text:
                        nameList.append(name.find(namePart).text)
                        if namePart == "DISS_surname":
                            self.bag.info['Author-Surname'] = name.find(namePart).text
                authorList.append(" ".join(nameList))
                if author.find('DISS_contact').find('DISS_email').text:
                    emailList.append(author.find('DISS_contact').find('DISS_email').text)
        self.bag.info['Author'] = "|".join(authorList)
        self.bag.info['Author-Email'] =  "|".join(emailList)
        
        self.bag.info['Title'] = root.xpath('//DISS_submission/DISS_description/DISS_title/text()')[0]
        self.bag.info['Completion-Date'] = root.xpath('//DISS_submission/DISS_description/DISS_dates/DISS_comp_date/text()')[0]
        
        self.bag.save()

    def makeCatalogPackage(self):
        """
        Takes a loaded AIP and creates a derivative package for cataloging
        """
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
        f = open(os.path.join(catalogPackage, "indentifier.txt"), "w")
        f.write(self.identifier)
        f.close()
                
        
    def clean(self):
        """
        Accepts a loaded AIP and cleans out filesystem artifacts
        from the data directory that interfere with Bag validation.
        """
        if self.data is None:
            raise Exception("Error: AIP must be loaded in order to be cleaned.")
        else:
            for root, dirs, files in os.walk(self.data):
                for file in files:
                    if file.lower() in self.excludeList:
                        filePath = os.path.join(root, file)
                        print ("removing " + filePath)
                        #os.remove(filePath)