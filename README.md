# ETD-Workflow
Workflow for moving ETDs from ProQuest to Alma and Scholar's Archive

### Overview

This repo includes classes for creating and managing preservation packages for UAlbany's Electronic Theses and Dissertations. Also includes are some basic scripts for development and informal testing.

 There are two types of packages:

* SubmissionInformationPackage
* ArchivalInformationPackage

Both packages are compressed Bags utilizing [Bagit-python](https://github.com/LibraryOfCongress/bagit-python). 

### Basic Use

* `SIP` packages can be created by instantiating an object with a path:

  ````python
  SIP = SubmissionInformationPackage(path_to_data)
  ````

  

* Both `SIP` and `AIP` packages are Bagit bags, but are compressed as .zip files. Printing them will only display the path to the canonical zip file:

  ```python
  SIP = SubmissionInformationPackage(path_to_data)
  print (SIP)
  
  > /path/to/bag.zip
  ```

* Both `SIP` and `AIP` packages can be managed using `.load()` which will automatically uncompressed the package as a temporary directory where they can be parsed and managed as Bags.

* Loaded packages must be closed after use with `.close()` which removes the temporary directory

  ```python
  SIP = SubmissionInformationPackage(path_to_zip)
  SIP.load()
  print (SIP.bag.info['Completion-Date'])
  print (SIP.bag.info['Author'])
  print (SIP.bag.info['Bag-Type'])
  print (SIP.bag.is_valid())
  SIP.close()
  ```

* Additionally, unloaded `SIP` packages can be turned into `AIP` packages, by using `.package()`

* Remember that an `AIP` package still must be loaded before using it as a bag.

  ```python
  # assumes closed package
  SIP = SubmissionInformationPackage(sipPath)
  AIP = SIP.package()
  AIP.load()
  print (AIP.bag.info['Bag-Type'])
  print (AIP.bag.info['Alma-Mms_id'])
  AIP.close()
  ```

* When a package is loaded, many attributes, such as `SIP.bag` and `SIP.data` will helpfully refer to uncompressed package in a temp directory, while `SIP.bagDir` will always remain the full path to the canonical compressed bag as a .zip file.