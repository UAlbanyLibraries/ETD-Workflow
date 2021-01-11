import os
from packages import ArchivalInformationPackage

#version of chechAIP.py
version = "0.1"
if os.name == "nt":
    pathAIP = "\\\\Lincoln\\Library\\ETDs\\AIP_testing\\storage\\AIP"
else:
    pathAIP = "/media/Library/ETDs/AIP_testing/storage/AIP"

testAIP = os.path.join(pathAIP, "etdadmin_upload_739987.zip")
AIP = ArchivalInformationPackage()
AIP.load(testAIP)

print (AIP.bag.info['Author'])
print (AIP.bag.info['Author-Email'])
print (AIP.bag.info['Title'])
print (AIP.bag.info['Bag-Type'])
print (AIP.bag.info['Completion-Date'])
print (AIP.excludeList)