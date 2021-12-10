import os
from packages import InformationPackage


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
        SIP = InformationPackage()
        SIP.createSIP(path)
        print (SIP.identifier)
        print ("\t" +  SIP.bag.info['Completion-Date'] + " " + SIP.bag.info['Author'])
        #print (SIP.bag.info['Author-Email'])
        #print (SIP.bag.info['Title'])
        #print (SIP.path)
        SIP.loadSIP(SIP.path)
        SIP.makeCatalogPackage()
"""
testSIP = os.path.join(incomingPath, "storage", "SIP", "etdadmin_upload_739987.zip")
SIP = InformationPackage()
SIP.loadSIP(testSIP)

print (SIP.identifier)
print (SIP.bag.info['Author'])
print (SIP.bag.info['Author-Email'])
print (SIP.bag.info['Title'])
print (SIP.bag.info['Completion-Date'])
print (SIP.identifier)
SIP.makeCatalogPackage()

SIP.close()
"""
