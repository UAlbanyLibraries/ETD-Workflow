import os
from packages import InformationPackage


#version of readCatalogedSIPs.py
version = "0.1"
if os.name == "nt":
    catalogingPath = "\\\\Lincoln\\Library\\ETDs\\CatalogingPackage"
else:
    catalogingPath = "/media/Library/ETDs/Testing"
incomingPath = os.path.join(catalogingPath, "outgoing")

for package in os.listdir(incomingPath):
    print ("Reading " + package + "...")

    SIP = InformationPackage()
    pathSIP = SIP.lookup(os.path.join(incomingPath, package))
    SIP.loadSIP(pathSIP)
    #print (SIP.bag.is_valid())

    print ("\t" + SIP.identifier)
    print ("\t" + SIP.bag.info['Author'])
    SIP.bag.info['Bib-Record'] = package
    SIP.bag.save()
    #print (SIP.bag.is_valid())

    # remove cataloging package
    print ("Removing cataloging package " + package)
    #os.remove(os.path.join(incomingPath, package))

    # Build IR package
    SIP.makeIRPackage()
