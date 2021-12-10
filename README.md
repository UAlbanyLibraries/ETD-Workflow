# ETD-Workflow
Workflow for moving ETDs from ProQuest to Alma and Scholar's Archive

### Overview

This repo includes classes for creating and managing preservation packages for UAlbany's Electronic Theses and Dissertations. Also includes are some basic scripts for development and informal testing.

 There are two types of preservation packages. Both packages are Bagit "bags" utilizing [Bagit-python](https://github.com/LibraryOfCongress/bagit-python).

* SubmissionInformationPackage (SIP)
	This is created when the zipped ETD from ProQuest is ingested. It parses the included XML to put the metadata we need in bag-info.txt for later use. Derivative packages are created from the SIP for cataloging and ingest into the Institutional Repository (IR)
* ArchivalInformationPackage (AIP)
	This replaces the corresponding SIP after cataloging and ingest into the IR. It includes all relevant identifiers and URLs created during cataloging and ingest into the IR. The AIP is the package that is pererved long term.


### Basic Use

* `SIP` packages can be created by instantiating an object with a path:

  ````python
  SIP = SubmissionInformationPackage()
  SIP.create(path_to_data)
  ````
  

* Both `SIP` and `AIP` packages are Bagit bags, and AIPs are also are compressed as .zip files. Printing them will only display the path to the canonical bag directory or zip file:

  ```python
  SIP = SubmissionInformationPackage()
  SIP.load(path_to_data)
  print (SIP)
  print (SIP.path)
  
  > <packages.SubmissionInformationPackage object at 0x00000220E3568E50>
  > /path/to/bag
  ```

* Both `SIP` and `AIP` packages must be managed using `.create()` or .load()` which populates all of the package's attibutes. For AIPs this will also automatically uncompressed the package as a temporary directory where they can be parsed and managed as Bags.
* When a package is loaded, many attributes, such as `SIP.bag` and `SIP.data` will helpfully refer to uncompressed package in a temp directory, while `SIP.path` will always remain the full path to the canonical compressed bag as a .zip file.
* Loaded AIPs must be closed after use with `.close()` which removes the temporary directory

 ```python
  SIP = SubmissionInformationPackage()
  SIP.create(path_to_data)
  print (SIP.bag.info['Completion-Date'])
  print (SIP.bag.info['Author'])
  print (SIP.bag.info['Bag-Type'])
  print (SIP.bag.is_valid())
  ```

  ```python
  AIP = ArchivalInformationPackage()
  AIP.load(path_to_zip)
  print (AIP.bag.info['Completion-Date'])
  print (AIP.bag.info['Author'])
  print (AIP.bag.info['Bag-Type'])
  print (AIP.bag.is_valid())
  AIP.close()
  ```

* Additionally, unloaded `SIP` packages can be turned into `AIP` packages, by using `.package()` [NOT WRITTEN YET]

* Remember that an `AIP` package still must be loaded before using it as a bag.

  ```python
  # assumes closed package
  SIP = SubmissionInformationPackage()
  SIP.load(sipPath)
  AIP = SIP.package()
  AIP.load()
  print (AIP.bag.info['Bag-Type'])
  print (AIP.bag.info['Alma-Mms_id'])
  AIP.close()
  ```

### Use as Bags

All SIPs and AIPs are bags and can be used according to the [bagit-python](https://github.com/LibraryOfCongress/bagit-python) docs

  ````python
  SIP = SubmissionInformationPackage()
  SIP.create(path_to_data)

  print (SIP.bag.info['Title'])
  SIP.bag.info['Title'] = "New Updated Title"
  SIP.bag.save()

  if SIP.bag.is_valid():
  	print ("yes, checksums match")
  else:
  	print ("no, content has changed since bagging.")

  ````