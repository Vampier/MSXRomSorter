# MSXRomSorter
MSX ROM Sorter

This ROM Sorter will be able to sort all known ROMs into their respective folders. The Sorter will also remove all unwanted files (see code) that are not associated with ROMs.

Upon 1st run this script will create 3 directories:
unsorted
notfound
sorted

Unknown files should be placed in unsorted - if files are not found in the ROMDB they will be put into 'notfound', if found they are sorted correctly in the sorted directory.

The files in not found have a SHA1 file has added to the front of the file - these files are not yet in the database. It would be appreceated if you could upload the files at https://romdb.vampier.net/checkrom.php so that I can process them

Use at your own risk etc. 
