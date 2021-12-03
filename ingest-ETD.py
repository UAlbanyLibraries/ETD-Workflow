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
        if SIP == "etdadmin_upload_739987.zip":
            
            #print(SIP)
            path = os.path.join(pathSIP, SIP)
            AIP = ArchivalInformationPackage()
            AIP.create(path)
            print (AIP.identifier)
            print (AIP.bag.info['Author'])
            print (AIP.bag.info['Author-Email'])
            print (AIP.bag.info['Title'])
            print (AIP.path)
"""
testAIP = os.path.join(pathSIP, "storage", "etdadmin_upload_739987.zip")
AIP = ArchivalInformationPackage()
AIP.load(testAIP)

print (AIP.identifier)
print (AIP.bag.info['Author'])
print (AIP.bag.info['Author-Email'])
print (AIP.bag.info['Title'])
print (AIP.bag.info['Completion-Date'])
print (AIP.identifier)
#AIP.makeCatalogPackage()

AIP.close()

