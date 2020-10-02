import os
from packages import ArchivalInformationPackage


#version of ingest-ETD.py
version = "0.1"
if os.name == "nt":
    pathSIP = "\\\\Lincoln\\Library\\ETDs\\AIP_testing"
else:
    pathSIP = "/media/Library/ETDs/AIP_testing"

"""
for SIP in os.listdir(pathSIP):
    if SIP.startswith("etdadmin_upload_") and SIP.endswith(".zip"):
        #if new?:
        if SIP == "etdadmin_upload_738128.zip":
            
            #print(SIP)
            path = os.path.join(pathSIP, SIP)
            AIP = ArchivalInformationPackage()
            AIP.create(path)
            print (AIP.identifier)
            print (AIP.bag.info['Author'])
            print (AIP.bag.info['Author-Email'])
"""
testAIP = os.path.join(pathSIP, "storage", "etdadmin_upload_738128.zip")
AIP = ArchivalInformationPackage()
AIP.load(testAIP)

AIP.metadata()
print (AIP.identifier)
print (AIP.bag.info['Author'])
print (AIP.bag.info['Author-Email'])
print (AIP.bag.info['Title'])
print (AIP.bag.info['Completion-Date'])
AIP.close()
