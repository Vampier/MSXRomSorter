# MSXRomSorter
MSX ROM Sorter

This ROM Sorter will be able to sort all known ROMs into their respective folders. The Sorter will also remove all unwanted files (see code) that are not associated with ROMs.

To run on windows make sure to remove the 1st line `#!/usr/bin/env -S python3`

Non Standard Dependencies: 
- SQLite3 https://sqlite.org/ (for SQLite3 database support)
- py7zr `pip install py7zr` or `apt install python3-py7zr`
- Requests `pip install requests`

Upon 1st run this script will create 3 directories:
- unsorted
- notfound
- sorted

A database file is downloaded as well

# Running the script

run the script by typing `python3 romsorter.py` 

If the script runs it will show a menu:

```
------------------------------
RomSorter Menu
------------------------------
[1] Scanning For New Roms
[2] Create Preferred ZIP Files
[3] Exit
------------------------------
Enter your choice:
```
Once you see the menu above place your unsorted ROM Collection in the `unsorted` directory and pick the 1st option

Depending on what files you put in there the directory that can be created looks like this:

- unsorted (Place ROM collections here)
- notfound (Resulting ROMs that aren't in the ROMDB)
- sorted (Sort results)
  - BadDump (known bad dumps)
  - ColecoVision (Limited Colecovision support)
  - Confidential (ROMs that are still for sale or never have been publicly released)
    - BadDump
    - MSX
    - MSX2
  - MSX (All known MSX1 ROMs)
  - MSX2 (All known MSX2 ROMs)
  - SVI (SVI ROMs)
  - Systemroms (Known System ROMs)

The files in not found have a SHA1 file has added to the front of the file - these files are not yet in the database. Files that which are not in the database can be submitted by visiting https://romdb.vampier.net/checkrom.php (bulk upload supported up to 50 files) so that I can process them

# Creating Preferred zip files
Once all files have been sorted a collection of the most relevant files can be generated for the use in sofarun or your favorite emulator.

A new directory will be created:

- perfsorted
  - MSX (MSX ROMs sorted per directory)
  - MSX2 (MSX2 ROMs sorted per directory)
  - ZIP 
    - MSX  (MSX ROM ZIPs sorted per starting letter)
    - MSX2  (MSX2 ROM ZIPs sorted per per starting letter)
   
The ZIP files have been created with `level 0` compression - this means that the MSX can just unpack the file with minimal CPU usage and thus loading procedure times will be reduced.
