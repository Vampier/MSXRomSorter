#!/usr/bin/env python3

import json
import os
import shutil
import hashlib
import sys
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import argparse
import platform

VERSION = "1.0.1"

# Enable long path support on Windows 10 (version 1607 and later)
if platform.system() == "Windows":
    try:
        import ctypes
        # Enable long path support by setting the registry key (requires admin rights)
        # Alternatively, users can enable it via Group Policy or registry manually
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.SetErrorMode(kernel32.GetErrorMode() | 0x2000)  # SEM_FAILCRITICALERRORS
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not enable long path support on Windows: {e}")
        print("Paths longer than 260 characters may cause issues.")

def calculateSha1(filePath):
    """Calculate SHA1 hash of a file"""
    try:
        sha1Hash = hashlib.sha1()
        with open(filePath, 'rb') as f:
            while chunk := f.read(8192):
                sha1Hash.update(chunk)
        return sha1Hash.hexdigest().upper()
    except (IOError, OSError) as e:
        print(f"Error reading {filePath}: {e}")
        return None

def sanitizeFilename(filename):
    """Remove invalid characters and limit length"""
    try:
        invalidChars = r'[<>:"/\\|?*\x00-\x1F]'
        sanitized = re.sub(invalidChars, '-', filename)
        sanitized = re.sub(r'-+', '-', sanitized).strip('-')
        if not sanitized or sanitized == '.':
            sanitized = 'unnamed'
        return sanitized[:255]
    except (TypeError, re.error) as e:
        print(f"Error sanitizing filename '{filename}': {e}")
        return "unnamed"

def normalizePath(path):
    """Normalize path for display (use forward slashes)"""
    return str(path).replace(os.sep, '/')

def removeEmptyDirs(directory, dryRun=False):
    """Recursively remove empty directories"""
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for dirName in dirs:
                dirPath = os.path.join(root, dirName)
                try:
                    if not os.listdir(dirPath):
                        if dryRun:
                            print(f"[Dry Run] Would remove empty dir: {normalizePath(dirPath)}")
                        else:
                            os.rmdir(dirPath)
                            print(f"Removed empty dir: {normalizePath(dirPath)}")
                except (OSError, PermissionError) as e:
                    print(f"Error removing {normalizePath(dirPath)}: {e}")
    except (OSError, PermissionError) as e:
        print(f"Error walking directory {normalizePath(directory)}: {e}")

def displayScriptInfo():
    """Display script purpose and structure if unsorted dir is missing"""
    print(f"""
ROM Sorter Script (v{VERSION})
==========================
Purpose: Organize ROM files (e.g., MSX, ColecoVision) by SHA1 hash using msxromsdb.json from https://romdb.vampier.net.
         Files from 'unsorted' are sorted into 'sorted' based on platform, bad/confidential status, or moved to 'notfound'.

Data Structure:
- sorted/<platform>/          : Normal ROMs
- sorted/bad/<platform>/      : Bad dumps
- sorted/confidential/<platform>/ : Confidential ROMs
- notfound/msx/               : Unmatched .rom files
- notfound/col/               : Unmatched .col files
- notfound/misc/              : Other unmatched files
- unsorted/                   : Source for ROMs (create this and add files)

Instructions: Add ROM files to 'unsorted' directory and run this script again.
""")
    sys.exit(0)

def checkAndUpdateRomdb(dryRun=False):
    """Check and update ROM database"""
    url = "https://romdb.vampier.net/api/get_latest.php"
    zipFilename = "msxromsdb.zip"
    outputDir = Path(__file__).parent
    extractedJson = outputDir / "msxromsdb.json"
    
    print("Checking ROM database updates...")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Error fetching or parsing ROM database: {e}")
        return False

    romdbEntry = next((item for item in data if item["file"] == "json-msxromsdb.zip"), None)
    if not romdbEntry:
        print("Error: json-msxromsdb.zip not found in API response.")
        return False
    
    apiTimestamp = romdbEntry.get("last_modified", "Not available")
    try:
        apiDt = datetime.fromtimestamp(int(apiTimestamp), tz=timezone.utc)
        print(f"API last modified: {apiDt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    except (ValueError, TypeError):
        print(f"API timestamp unparsed: {apiTimestamp}")
        return False
        
    downloadUrl = romdbEntry["download_location"]
    
    if extractedJson.exists():
        try:
            with open(extractedJson, 'r', encoding='utf-8') as f:
                jsonData = json.load(f)
                contentTimestamp = jsonData.get("timestamp", None)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading local JSON: {e}")
            contentTimestamp = None
        
        if contentTimestamp:
            try:
                contentDt = datetime.strptime(contentTimestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                print(f"Local JSON timestamp: {contentTimestamp} UTC")
                timeDiff = abs((apiDt - contentDt).total_seconds())
                if timeDiff <= 5:
                    print("Database is up-to-date (within 5s).")
                    return True
                else:
                    print(f"Database outdated by {timeDiff:.2f}s. Updating...")
            except ValueError:
                print(f"Local timestamp unparsed: {contentTimestamp}")
    
    if dryRun:
        print(f"[Dry Run] Would download and unzip {zipFilename}")
        return True
    
    try:
        urllib.request.urlretrieve(downloadUrl, zipFilename)
        print(f"Downloaded {zipFilename}")
        with zipfile.ZipFile(zipFilename, 'r') as zipRef:
            zipRef.extractall(outputDir)
        print(f"Extracted to {normalizePath(outputDir)}")
        
        if not extractedJson.exists():
            print("Error: msxromsdb.json not found in zip.")
            return False
        
        os.remove(zipFilename)
        print("Cleaned up zip file.")
        return True
    except (urllib.error.URLError, zipfile.BadZipFile, OSError, PermissionError) as e:
        print(f"Error downloading or extracting ROM database: {e}")
        return False
    finally:
        if os.path.exists(zipFilename):
            try:
                os.remove(zipFilename)
            except (OSError, PermissionError) as e:
                print(f"Error cleaning up {zipFilename}: {e}")

def copyToDestination(sha1, srcPath, romLookup, baseDir, badDir, confidentialDir, dryRun=False, stats=None):
    """Copy file to destination based on SHA1"""
    if sha1 not in romLookup:
        return False
    
    romInfo = romLookup[sha1]
    if romInfo['isConfidential']:
        destDir = os.path.join(confidentialDir, romInfo['platform'])
    elif romInfo['isBad']:
        destDir = os.path.join(badDir, romInfo['platform'])
    else:
        destDir = os.path.join(baseDir, romInfo['platform'])
    
    destPath = os.path.join(destDir, romInfo['filename'])
    filename = os.path.basename(srcPath)
    
    if dryRun:
        print(f"[Dry Run] Would sort {filename} >> {normalizePath(destPath)}")
        if stats:
            stats['copied'] += 1
        return True
    
    try:
        os.makedirs(os.path.dirname(destPath), exist_ok=True)
        shutil.copy2(srcPath, destPath)
        return True
    except (OSError, shutil.Error, PermissionError) as e:
        if isinstance(e, OSError) and e.errno == 36:  # File name too long
            print(f"Skipped {filename}: File name too long")
            if stats:
                stats['skipped'] += 1
        else:
            print(f"Error copying {filename} to {normalizePath(destPath)}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""
ROM Sorter v{VERSION}
=============

Description:
  Organizes ROM files (e.g., MSX, ColecoVision) by SHA1 hash using msxromsdb.json
  from https://romdb.vampier.net. Sorts files from 'unsorted' into:
    - 'sorted/<platform>/' (normal ROMs)
    - 'sorted/bad/<platform>/' (bad dumps)
    - 'sorted/confidential/<platform>/' (confidential ROMs)
  Unmatched files go to 'notfound/<msx|col|misc>/'.
  Creates 'unsorted' if missing and exits with instructions.
"""
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate sorting without modifying files")
    parser.add_argument("-v", "--version", action="store_true", help="Show script version")
    args = parser.parse_args()

    if args.version:
        print(f"ROM Sorter Version: {VERSION}")
        sys.exit(0)

    dryRun = args.dry_run
    if dryRun:
        print("Running in dry-run mode...")

    # Stats for summary
    stats = {'copied': 0, 'moved': 0, 'skipped': 0, 'removed': 0, 'duplicates': 0}

    # Define base directories
    baseDir = 'sorted'
    badDir = os.path.join('sorted', 'bad')
    confidentialDir = os.path.join('sorted', 'confidential')
    notfoundDir = 'notfound'
    unsortedDir = 'unsorted'

    # Check if unsorted exists
    try:
        if not os.path.exists(unsortedDir):
            os.makedirs(unsortedDir, exist_ok=True)
            displayScriptInfo()
    except (OSError, PermissionError) as e:
        print(f"Error creating 'unsorted' directory: {e}")
        sys.exit(1)

    # Update database
    if not checkAndUpdateRomdb(dryRun):
        print("Proceeding with existing database if available.")

    # Load JSON
    jsonFile = 'msxromsdb.json'
    if not os.path.exists(jsonFile):
        print(f"Error: {jsonFile} not found! Please ensure the database is available.")
        sys.exit(1)
    try:
        with open(jsonFile, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {jsonFile}: {e}")
        sys.exit(1)

    # Build ROM lookup
    romLookup = {}
    try:
        for rom in data['roms']:
            platform = rom['platform']
            for hashInfo in rom['hashes']:
                sha1 = hashInfo['sha1']
                filename = sanitizeFilename(hashInfo['FileName'])
                dump = hashInfo['dump']
                stillforsale = hashInfo.get('stillforsale')
                romLookup[sha1] = {
                    'filename': filename,
                    'platform': platform,
                    'isBad': dump == 'BadDump',
                    'isConfidential': stillforsale == 'on',
                    'originalFilename': hashInfo['FileName']
                }
    except (KeyError, TypeError) as e:
        print(f"Error building ROM lookup from {jsonFile}: {e}")
        sys.exit(1)

    # Cache unsorted files
    unsortedFiles = {}
    print("\nScanning unsorted directory...")
    try:
        for root, _, files in os.walk(unsortedDir):
            for file in files:
                srcPath = os.path.join(root, file)
                sha1 = calculateSha1(srcPath)
                if sha1:
                    unsortedFiles[sha1] = srcPath
    except (OSError, PermissionError) as e:
        print(f"Error scanning unsorted directory: {e}")
        sys.exit(1)

    # Cache notfound files
    notfoundFiles = {}
    print("Scanning notfound directory...")
    try:
        for root, _, files in os.walk(notfoundDir):
            for file in files:
                filepath = os.path.join(root, file)
                sha1 = calculateSha1(filepath)
                if sha1:
                    notfoundFiles[sha1] = filepath
    except (OSError, PermissionError) as e:
        print(f"Error scanning notfound directory: {e}")
        sys.exit(1)

    # Process unsorted files
    print("\nSorting unsorted files...")
    for sha1, srcPath in unsortedFiles.items():
        filename = os.path.basename(srcPath)
        if copyToDestination(sha1, srcPath, romLookup, baseDir, badDir, confidentialDir, dryRun, stats):
            if not dryRun:
                try:
                    destPath = os.path.join(
                        confidentialDir if romLookup[sha1]['isConfidential'] else badDir if romLookup[sha1]['isBad'] else baseDir,
                        romLookup[sha1]['platform'],
                        romLookup[sha1]['filename']
                    )
                    os.remove(srcPath)
                    print(f"Sorted: {filename} >> {normalizePath(destPath)}")
                    stats['removed'] += 1
                except (OSError, PermissionError) as e:
                    print(f"Error removing {filename}: {e}")
            else:
                destPath = os.path.join(
                    confidentialDir if romLookup[sha1]['isConfidential'] else badDir if romLookup[sha1]['isBad'] else baseDir,
                    romLookup[sha1]['platform'],
                    romLookup[sha1]['filename']
                )
                print(f"[Dry Run] Would sort {filename} >> {normalizePath(destPath)}")
        else:
            ext = os.path.splitext(srcPath)[1].lower()
            notfoundSubdir = 'msx' if ext == '.rom' else 'col' if ext == '.col' else 'misc'
            destFilename = filename if sha1 in filename else f"[{sha1}] - {filename}"
            destPath = os.path.join(notfoundDir, notfoundSubdir, destFilename)
            
            if sha1 in notfoundFiles:
                print(f"Skipped duplicate {filename} (SHA1: {sha1})")
                stats['duplicates'] += 1
                if not dryRun:
                    try:
                        os.remove(srcPath)
                        stats['removed'] += 1
                    except (OSError, PermissionError) as e:
                        print(f"Error removing duplicate {filename}: {e}")
            else:
                if dryRun:
                    print(f"[Dry Run] Would move {filename} >> {normalizePath(destPath)}")
                    stats['moved'] += 1
                else:
                    try:
                        os.makedirs(os.path.join(notfoundDir, notfoundSubdir), exist_ok=True)
                        shutil.move(srcPath, destPath)
                        print(f"Moved {filename} >> {normalizePath(destPath)}")
                        notfoundFiles[sha1] = destPath
                        stats['moved'] += 1
                    except (OSError, shutil.Error, PermissionError) as e:
                        if isinstance(e, OSError) and e.errno == 36:
                            print(f"Skipped {filename}: File name too long")
                            stats['skipped'] += 1
                        else:
                            print(f"Error moving {filename}: {e}")

    # Check notfound for updates
    print("\nChecking notfound for updates...")
    try:
        for root, _, files in os.walk(notfoundDir):
            for file in files:
                filepath = os.path.join(root, file)
                sha1 = calculateSha1(filepath)
                if sha1 and copyToDestination(sha1, filepath, romLookup, baseDir, badDir, confidentialDir, dryRun, stats):
                    if not dryRun:
                        try:
                            destPath = os.path.join(
                                confidentialDir if romLookup[sha1]['isConfidential'] else badDir if romLookup[sha1]['isBad'] else baseDir,
                                romLookup[sha1]['platform'],
                                romLookup[sha1]['filename']
                            )
                            os.remove(filepath)
                            print(f"Sorted: {file} to {normalizePath(destPath)}")
                            if sha1 in notfoundFiles:
                                del notfoundFiles[sha1]
                            stats['removed'] += 1
                        except (OSError, PermissionError) as e:
                            print(f"Error removing {file}: {e}")
                    else:
                        destPath = os.path.join(
                            confidentialDir if romLookup[sha1]['isConfidential'] else badDir if romLookup[sha1]['isBad'] else baseDir,
                            romLookup[sha1]['platform'],
                            romLookup[sha1]['filename']
                        )
                        print(f"[Dry Run] Would sort {file} to {normalizePath(destPath)}")
    except (OSError, PermissionError) as e:
        print(f"Error checking notfound directory: {e}")

    # Clean up empty directories
    print("\nCleaning up empty directories...")
    removeEmptyDirs(unsortedDir, dryRun)
    removeEmptyDirs(baseDir, dryRun)

    # Summary
    print("\nSorting Summary:")
    print(f"  Files sorted: {stats['copied']}")
    print(f"  Files moved to notfound: {stats['moved']}")
    print(f"  Files skipped (e.g., long names): {stats['skipped']}")
    print(f"  Files sorted: {stats['removed']}")
    print(f"  Duplicates skipped: {stats['duplicates']}")
    print("\nThank you for using ROM Sorter! Happy MSX-ing!")
    print("\nIf you have roms you would like to add please submit them at https://romdb.vampier.net/checkrom.php");
    print("\nFor updates or to report issues, visit: https://github.com/Vampier/MSXRomSorter")
    sys.exit(0)

if __name__ == "__main__":
    main()
