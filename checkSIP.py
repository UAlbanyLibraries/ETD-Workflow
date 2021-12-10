import os
from packages import SubmissionInformationPackage

"""
This is a test script for loading SIPs and making cataloging packages.
"""

if os.name == "nt":
    incomingPath = "\\\\Lincoln\\Library\\ETDs"
else:
    incomingPath = "/media/Library/ETDs"

testSIP = os.path.join(incomingPath, "storage", "SIP", "etdadmin_upload_739987")
SIP = SubmissionInformationPackage()
SIP.load(testSIP)

print (SIP.identifier)
print (SIP.bag.info['Author'])
print (SIP.bag.info['Author-Email'])
print (SIP.bag.info['Title'])
print (SIP.bag.info['Completion-Date'])
print (SIP.identifier)
#SIP.makeCatalogPackage()
