import os
from packages import SubmissionInformationPackage

#version of createAIP.py
version = "0.1"
if os.name == "nt":
    pathSIP = "\\\\Lincoln\\Library\\ETDs\\AIP_testing\\storage\\SIP"
else:
    pathSIP = "/media/Library/ETDs/AIP_testing/storage/SIP"

sipPath = os.path.join(pathSIP, "etdadmin_upload_739987.zip")

SIP = SubmissionInformationPackage(sipPath)
SIP.load()
print (SIP.bag.info['Completion-Date'])
print (SIP.bag.info['Author'])
print (SIP.bag.info['Bag-Type'])
SIP.close()


# assumes closed package
AIP = SIP.package()
AIP.load()
print (AIP.bag.info['Bag-Type'])
print (AIP.bag.info['Alma-Mms_id'])
AIP.close()