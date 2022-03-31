import os
import zipfile
import tempfile
from tqdm import tqdm
from lxml import etree as ET

if os.name == "nt":
	incomingPath = "\\\\Romeo\\SPE\\ETDs_backup"
else:
	incomingPath = "/media/SPE/ETDs_backup"


for package in tqdm(os.listdir(incomingPath)):
	if package.startswith("etdadmin_upload_") and package.endswith(".zip"):

		packagePath = os.path.join(incomingPath, package)
		tempDir = tempfile.mkdtemp()
		with zipfile.ZipFile(packagePath, "r") as zip_ref:
			zip_ref.extractall(tempDir)


		xmlCount = 0
		for file in os.listdir(tempDir):
			if file.endswith("_DATA.xml"):
				xmlCount += 1
				proquestXML = os.path.join(tempDir, file)
		if xmlCount != 1:
			raise Exception("ERROR: Failed to find ProQuest XML file. " + str(xmlCount) + " relevant files found.")
		root = ET.parse(proquestXML).getroot()
		authorship = root.xpath('//DISS_submission/DISS_authorship')[0]
		namePartList = ['DISS_fname', 'DISS_middle', 'DISS_surname' , 'DISS_suffix']
		authNum = 0
		for author in authorship:
			if author.tag == "DISS_author":
				authNum += 1
				name = author.find('DISS_name')
				authField = "Author-" + str(authNum)
				#if name.find('DISS_surname').text:
				#print (name.find('DISS_surname').text)
				if name.find('DISS_fname').text:
					if name.find('DISS_fname').text.lower().strip == "panpan":
						print ("name: " + package)
				if name.find('DISS_surname').text:
					if name.find('DISS_surname').text.lower().strip == "templeton":
						print ("name: " + package)
					if name.find('DISS_surname').text.lower().strip == "holdsworth":
						print ("name: " + package)
					if name.find('DISS_surname').text.lower().strip == "wilck":
						print ("name: " + package)