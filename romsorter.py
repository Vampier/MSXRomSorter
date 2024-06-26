#!/usr/bin/env -S python3

import os
import sys
import hashlib
import sqlite3
import unicodedata
import re
import zipfile
import fnmatch
import py7zr
import shutil
import requests

# Dependencies

# Windows: pip install py7zr
# Debian:  apt install python3-py7zr

def importSQLite3(url, databasename):
	# Download the RomDBDump.sql file
	response = requests.get(url)

	# Check if the request was successful
	if response.status_code == 200:
		
		# Delete previous database
		deleteFile(databasename)

		# Connect to SQLite3 database
		conn = sqlite3.connect(databasename)
		cursor = conn.cursor()

		# Execute the SQL dump to create the RomDB.db database
		sql_script = response.text
		cursor.executescript(sql_script)

		# Commit changes and close connection
		conn.commit()
		conn.close()

		print('Database Updated.')
	else:
		print('Failed to create the database.')

def cleanDirectory(root_dir, extentions):
	for root, dirs, files in os.walk(root_dir):
		# Remove files with specified extensions
		for file in files:
			file_path = os.path.join(root, file)
			if file.lower().endswith(tuple(extentions)):
				os.remove(file_path)
				print(f'Removed file: {file_path}')

		# Remove empty directories
		for dir_name in dirs[:]:
			dir_path = os.path.join(root, dir_name)
			try:
				if not os.listdir(dir_path):
					os.rmdir(dir_path)
					print(f'Removed empty directory: {root} - {dir_path}')
					dirs.remove(dir_name)  # Remove directory from list to prevent further iteration
			except Exception as e:
				print(f'Error occurred while removing directory {dir_path}: {e}')

		# Remove empty files
		for file_name in files:
			file_path = os.path.join(root, file_name)
			try:
				if os.path.getsize(file_path) == 0:
					os.remove(file_path)
					print(f'Removed empty file: {file_path}')
			except Exception as e:
				print(f'Error occurred while checking file size for {file_path}: {e}')

def createDir(dirname):
	if not os.path.exists(dirname):
		os.makedirs(dirname)

def deleteFile(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print(f'Warning: File \'{filename}\' does not exist.')

def getRomInfo(sha1value):
	global platform

	sql = "SELECT * FROM RomSorter WHERE sha1 = '%s'" % sha1value
	cur.execute(sql)

	row = cur.fetchone()

	if row is None:
		return 'NotFound'

	GameName = makeFSSafe(row[0]) if row[0] is not None else ''
	row3 = makeFSSafe(row[3]) if row[3] is not None else ''
	row1 = makeFSSafe(row[1]) if row[1] is not None else ''
	row4 = formatname(row[4]) if row[4] is not None else ''
	Remark = formatname(row[5]) if row[5] is not None else ''
	Meta = formatname(row[6]) if row[6] is not None else ''
	platform = row[7] if row[7] is not None else ''
	
	extention = '.rom'	

	if platform == 'ColecoVision':
		extention = '.col'
	
	if row[9] == 'on':		
		platform = '/Confidential/' + platform
	
	GameName = 'Restest-' + GameName if row[10] > 0 else GameName

	fname = f'{GameName} - {row3} ({row1}) {row4} {Remark} {Meta} [{row[8]}]{extention}'
	fname = re.sub(' +', ' ', fname)

	return fname

def getPrefRomInfo(sha1value):
	global platform

	sql = "SELECT GameName, Year, SHA1, IFNULL(shortname, ''), IFNULL(Remark, ''), IFNULL(Meta, ''), " \
		  "CASE WHEN UPPER(Dump) = 'GOODMSX' THEN 'GoodMSX' " \
		  "WHEN UPPER(Dump) = 'BAD' THEN 'BadDump' " \
		  "WHEN UPPER(Dump) = 'AUTHOR' THEN 'original' " \
		  "WHEN UPPER(Dump) = 'TRANSLATED' THEN 'Translated' ELSE '' END AS Dump, " \
		  "CASE WHEN UPPER(Dump) = 'BAD' THEN 'BadDump' " \
		  "WHEN UPPER(Dump) = 'SYSTEM' THEN 'SystemRoms' ELSE Platform END AS Platform, " \
		  "t2.HashID AS GameID, StillForSale, t2.RomType " \
		  "FROM msxdb_rominfo t1 " \
		  "JOIN msxdb_romdetails t2 ON t1.GameID = t2.GameID " \
		  "JOIN msxdb_company t3 ON t1.CompanyID1 = t3.companyid " \
		  f"WHERE 1=1 and stillforsale!='on' and TRIM(UPPER(sha1)) = UPPER('{sha1value}') AND " \
		  "LOWER(active) IN ('1', 'on') AND LOWER(Preferred) IN ('1', 'on') AND platform IN ('MSX', 'MSX2')"
	
	cur.execute(sql)
	row = cur.fetchone()

	if row is None:
		return 'NotFound'

	GameName = makeFSSafe(row[0]) if row[0] else ''
	row3 = makeFSSafe(row[3]) if row[3] else ''
	row1 = makeFSSafe(row[1]) if row[1] else ''
	row4 = formatname(row[4]) if row[4] else ''
	Remark = formatname(row[5]) if row[5] else ''
	Meta = formatname(row[6]) if row[6] else ''
	platform = row[7] if row[7] else ''
	RomMapper = row[10] if row[10] else ''

	extention = '.rom'
	
	fname = f'{GameName} - {row3} [{RomMapper}] {Remark} {Meta}{extention}'
	fname = re.sub(' +', ' ', fname)

	return fname

def handlePrefFiles(dirname, fname):
	global platform
	
	fromfile = os.path.join(dirname, fname)
	if fname[-3:].upper() != '.PY':
		hash_value = sha1value(fromfile).upper()
		newfilename = getPrefRomInfo(hash_value)
		
		if newfilename == 'NotFound':
			return
		
		topath = os.path.abspath(f'perfsorted/{platform}/')
		toDir = os.path.join(topath, newfilename[0].upper())
		tofile = os.path.join(toDir, newfilename)
		
		createDir(toDir)
		found = makeFSSafe(f'{platform} >> {tofile}')
		shutil.copyfile(fromfile, tofile)

def ScanPrefDir(rootDir):
	for dirName, subdirList, fileList in os.walk( rootDir ):
		fileList.sort()
		for extension in ( tuple(ROMTypes) ):
			for filename in fnmatch.filter(fileList, extension):
				handlePrefFiles(dirName,filename)

# Zip the files from given directory that matches the filter
def zipFilesInDir(root_dir, output_dir):
	for root, dirs, _ in os.walk(root_dir):
		for subdir in dirs:
			subdir_path = os.path.join(root, subdir)
			files_to_zip = sorted([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
			if files_to_zip:
				zip_file_path = os.path.join(output_dir, f'{subdir}.zip')
				with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_STORED) as zipf:
					for file in files_to_zip:
						#print (file)
						file_path = os.path.join(subdir_path, file)
						zipf.write(file_path, arcname=file)

def makeFSSafe(strFormat):
	strFormat = strFormat.strip()

	replacements = {
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ý': 'Y', 'Þ': 'TH', 'ß': 'ss',
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'æ': 'ae', 
        'ç': 'c', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ì': 'i', 'í': 'i', 
        'î': 'i', 'ï': 'i', 'ð': 'd', 'ñ': 'n', 'ò': 'o', 'ó': 'o', 'ô': 'o', 
        'õ': 'o', 'ö': 'o', 'ø': 'o', 'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u', 
        'ý': 'y', 'þ': 'th', 'ÿ': 'y','?': '', '/': '-', ':': '', '\r': '', 
		'\n': '', '\t': '', '[[': '[', ']]': ']', '\'': ''
	}

	for old_char, new_char in replacements.items():
		strFormat = strFormat.replace(old_char, new_char)

	return strFormat

def formatname(strField):
	output = strField
	output = output.strip()
	output = makeFSSafe(output)

	if len(output.strip())==0:
		return ''

	output = ' ['+output+']'

	return makeFSSafe(output)

def sha1value(fname):
	BLOCKSIZE = 65536 #64Kb
	hasher = hashlib.sha1()
	with open(fname, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
	afile.close()
	return (hasher.hexdigest())

def dedupeDirectory(directory):
	hash_map = {}
	for root, dirs, files in os.walk(directory):
		for filename in files:
			file_path = os.path.join(root, filename)
			file_hash = sha1value(file_path)
			if file_hash not in hash_map:
				hash_map[file_hash] = [file_path]
			else:
				hash_map[file_hash].append(file_path)

	# Remove duplicates
	for file_list in hash_map.values():
		if len(file_list) > 1:
			for file_path in file_list[1:]:
				os.remove(file_path)
				print(f'Removed duplicate: {file_path}')


def handlefiles(dirname, fname, scantype):
    global platform

    # Check if the file extension is '.py'; if it is, skip processing
    if fname[-3:].upper() == '.PY':
        return

    fromfile = os.path.join(dirname, fname)

    try:
        hash_value = sha1value(fromfile).upper()
        newfilename = getRomInfo(hash_value)

        if newfilename == 'NotFound':
            # Handle case where ROM information is not found
            if scantype == 'sort' and not dirname.startswith('./notfound'):
                tofile = os.path.abspath('./notfound/') + f'/{hash_value}__{fname}'
                print('NotFound: {} to {}'.format(fromfile, tofile))
                shutil.copyfile(fromfile, tofile)
                os.remove(fromfile)
            return

        if scantype == 'scan':
            # Handle scanning operation
            topath = os.path.abspath('./perfsorted/' + platform + '/')
            toDir = os.path.join(topath, newfilename[0].upper())
            tofile = os.path.join(toDir, newfilename)
            print('Sorting for ZIP: {} copy to {}'.format(fromfile, tofile))
        elif scantype == 'sort':
            # Handle sorting operation
            topath = os.path.abspath('sorted/' + platform + '/')
            tofile = os.path.join(topath, newfilename)
            print('found: {} >> {}'.format(fromfile, tofile))

        createDir(topath)
        shutil.copyfile(fromfile, tofile)
        os.remove(fromfile)

    except Exception as e:
        print(e)

def ExtractArchives(rootDir):
	for dirName, subdirList, fileList in os.walk(rootDir):
		for fname in sorted(fileList):
			archiveFile = os.path.join(dirName, fname)
			ext = os.path.splitext(fname)[1].lower()
			
			if ext in ('.zip', '.7z'):
				archive_type = 'ZIP' if ext == '.zip' else '7Z'
				extract_and_print(archiveFile, fname, archive_type)

def extract_and_print(archiveFile, fname, archive_type):
	ext_len = 4 if archive_type == 'ZIP' else 3
	fullPathAndName = archiveFile[:-ext_len]
	print(f'{archive_type} File found: {fname}')
	try:
		extract_function = ExtractArchive if archive_type == 'ZIP' else ExtractArchive
		extract_function(archiveFile, fullPathAndName, archive_type)
	except Exception as e:
		print(f'{archiveFile} error extracting: {e}')

def ExtractArchive(ArchiveName, DestDir, archive_type):
	createDir(DestDir)
	extractor = zipfile.ZipFile if archive_type == 'ZIP' else py7zr.SevenZipFile
	with extractor(ArchiveName, mode='r') as archive:
		archive.extractall(path=DestDir)
	deleteFile(ArchiveName)

def ScanDir(rootDir,scantype):
	for dirName, subdirList, fileList in os.walk( rootDir ):
		for extension in ( tuple(ROMTypes) ):
			for filename in fnmatch.filter(fileList, extension):
				handlefiles(dirName,filename,scantype)

def removeDir(dir_path):
	try:
		# Remove all files and subdirectories in the directory
		for root, dirs, files in os.walk(dir_path, topdown=False):
			for file in files:
				file_path = os.path.join(root, file)
				os.remove(file_path)
			for dir_name in dirs:
				dir_path = os.path.join(root, dir_name)
				os.rmdir(dir_path)
		
		# Finally, remove the top-level directory itself
		os.rmdir(dir_path)
		print(f'Directory \'{dir_path}\' successfully removed.')
	except Exception as e:
		print(f'Already removed: \'{dir_path}\': {e}')

def lowercaseExtentions(directory):
	for filename in os.listdir(directory):
		filepath = os.path.join(directory, filename)
		# Check if the item is a file
		if os.path.isfile(filepath):
			# Split the filename and extension
			name, ext = os.path.splitext(filename)
			# Convert the extension to lowercase
			lowercase_ext = ext.lower()
			# Rename the file with the lowercase extension
			new_filename = name + lowercase_ext
			if filename!=new_filename:
				os.rename(filepath, os.path.join(directory, new_filename))
	
def removeDualHashFileNames(directory):
	for root, dirs, files in os.walk(directory):
		for file in files:
			file_path = os.path.join(root, file)
			if len(file) >= 82:
				prefix = file[:40]
				suffix = file[42:82]
				if prefix == suffix:
					new_name = os.path.join(root, file[42:])
					os.rename(file_path, new_name)
					print(f'Renamed {file_path} to {file[42:]}')

### main ###################################
# Set the directory you want to start from #
############################################

#set Directory with ROMs

unsorterDir = os.path.abspath('./unsorted/')
NotFoundDir = os.path.abspath('./notfound/')
sortedDir= os.path.abspath('./sorted/')
PrefSorted = os.path.abspath('./perfsorted/')
MSXZipIn = os.path.abspath('./perfsorted/MSX2/')
MSXZipOut = os.path.abspath('./perfsorted/ZIP/MSX2/')
MSX2ZipIn = os.path.abspath('./perfsorted/MSX/')
MSX2ZipOut = os.path.abspath('./perfsorted/ZIP/MSX/')

url = 'http://romdb.vampier.net/convertdb.php'
databasename= 'RomDB.db'

# Define extensions to remove
BadFiles = ['mp3','txt','dsk','mia','sys','m3u','vgz','asm','ips','xml',
			'url','ini','ldr','txt','jpg', 'gif', 'png', 'jpeg', 'html', 
			'dsk', 'bas', 'sc5', 'sc8', 'bat', 'obj', 'vrm', 'com', 'cfg', 
			'mp4', 'mov', 'pdf', '32x', 'cas']

# Known ROM Types 
ROMTypes  = ['*.ms1', '*.mx2', '*.mx1', '*.bin', 
			 '*.msx2', '*.dat', '*.gz', '*.col', 
			 '*.eprom', '*.rom']

# Create SQLLite3 database from URL
importSQLite3(url,databasename)

# Open DB connection
conn = sqlite3.connect(databasename)
cur = conn.cursor()

# is this needed?
platform = ''

def ScanDirForNewRoms():
	global platform
	# Scan driectoryies for roms
	ScanDir(unsorterDir,'sort')
	ScanDir(NotFoundDir,'sort')

	cleanDirectory(NotFoundDir, BadFiles)
	cleanDirectory(unsorterDir, BadFiles)

def CreatePrefSortedFiles():

	removeDir(PrefSorted)

	createDir(MSXZipIn)
	createDir(MSX2ZipIn)

	createDir(MSXZipOut)
	createDir(MSX2ZipOut)

	ScanPrefDir(sortedDir)

	zipFilesInDir(MSXZipIn, MSXZipOut)
	zipFilesInDir(MSX2ZipIn, MSX2ZipOut)

def CreateMenu():
	print('-'*30)
	print('RomSorter Menu')
	print('-'*30)
	print('[1] Scanning For New Roms')
	print('[2] Create Preferred ZIP Files')
	print('[3] Exit')
	print('-'*30)


def main():

	# Create directories if they don't exist
	createDir(sortedDir)
	createDir(unsorterDir)
	createDir(NotFoundDir)

	# Dedupe unsorted files
	dedupeDirectory(unsorterDir)
	dedupeDirectory(NotFoundDir)

	# Lower case extentions
	lowercaseExtentions(unsorterDir)
	lowercaseExtentions(NotFoundDir)

	# Extract Archives if found (run twice in case the archives contain archives)
	ExtractArchives(unsorterDir)
	ExtractArchives(unsorterDir)

	# Clean the 'notfound' and 'unsorted' directory
	cleanDirectory(NotFoundDir, BadFiles)
	cleanDirectory(unsorterDir, BadFiles)

	# Remove dual hashes from the filename (accidentally sorted more than once)
	removeDualHashFileNames(NotFoundDir)

	# Menu Loop
	while True:
		CreateMenu()
		choice = input('Enter your choice: ')
		if choice == '1':
			print('-- Scan For New Roms')
			ScanDirForNewRoms()
		elif choice == '2':
			print('-- Creating Preferred ZIP Files')
			CreatePrefSortedFiles()
		elif choice == '3':
			print('Exiting...')
			conn.close()
			break
		else:
			print('Invalid choice. Please try again.')


if __name__ == "__main__":
	main()
