import os
from packages import SubmissionInformationPackage

"""
This script looks for ETD packages deposited via ProQuest in the incomingPath.
It then creates a SIP for the package and makes a derivative package for cataloging.
"""

#version of ingest-ETD.py
version = "0.1"
if os.name == "nt":
    incomingPath = "\\\\Lincoln\\Library\\ETDs\\Testing"
else:
    incomingPath = "/media/Library/ETDs/Testing"


for package in os.listdir(incomingPath):
    if package.startswith("etdadmin_upload_") and package.endswith(".zip"):
        #if new?:
        #if package == "etdadmin_upload_739987.zip":
            
        #print(SIP)
        path = os.path.join(incomingPath, package)
        SIP = SubmissionInformationPackage()
        SIP.create(path)
        print (SIP.identifier)
        print ("\t" +  SIP.bag.info['Completion-Date'] + " " + SIP.bag.info['Author-1_lname'])
        #print (SIP.bag.info['Author-Email'])
        #print (SIP.bag.info['Title'])
        #print (SIP.path)
        SIP.load(SIP.path)
        SIP.makeCatalogPackage()