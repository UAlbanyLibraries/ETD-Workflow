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
        else:
            self.pathAIP = "/media/Library/ETDs/AIP_testing/storage"
        
    def load(self, path):
        if not os.path.isfile(path) or not path.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid AIP. You may want to create a AIP with .create().")

        #with tempfile.TemporaryDirectory() as self.tempDir:
        self.tempDir = tempfile.mkdtemp()
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(self.tempDir)
            
        self.bagDir = self.tempDir
        self.bag = bagit.Bag(self.bagDir)
        self.identifier = self.bag.info['Bag-Identifier']
        self.data = os.path.join(self.bagDir, "data") 

    def close(self):
        if self.tempDir:
            shutil.rmtree(self.tempDir)
    
    def create(self, path):
        if not os.path.isfile(path):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")
        SIP = os.path.basename(path)
        if not SIP.startswith("etdadmin_upload_") and SIP.endswith(".zip"):
            raise Exception("ERROR: " + str(path) + " is not a valid SIP.")
        
        self.identifier = os.path.splitext(os.path.basename(path))[0] 
        
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
        
        #Compress package
        print ("compressing")
        shutil.make_archive(self.bagDir, 'zip', self.bagDir)
        if os.path.isfile(self.bagDir + ".zip"):
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
                authorList.append(" ".join(nameList))
                if author.find('DISS_contact').find('DISS_email').text:
                    emailList.append(author.find('DISS_contact').find('DISS_email').text)
        self.bag.info['Author'] = "|".join(authorList)
        self.bag.info['Author-Email'] =  "|".join(emailList)
        
        self.bag.info['Title'] = root.xpath('//DISS_submission/DISS_description/DISS_title/text()')[0]
        self.bag.info['Completion-Date'] = root.xpath('//DISS_submission/DISS_description/DISS_dates/DISS_comp_date/text()')[0]
        
        self.bag.save()
        
                
        
    def clean(self):
        for root, dirs, files in os.walk(self.data):
            for file in files:
                if file.lower() in self.excludeList:
                    filePath = os.path.join(root, file)
                    print ("removing " + filePath)
                    #os.remove(filePath)