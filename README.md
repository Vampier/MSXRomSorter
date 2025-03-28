![MSXRomSorter Logo](https://via.placeholder.com/150) <!-- Replace with an actual logo if you have one -->

A Python script to organize MSX and ColecoVision ROM files by SHA1 hash using the `msxromsdb.json` database from [romdb.vampier.net](https://romdb.vampier.net). Sort your ROM collection into categorized directories, handle bad dumps and confidential ROMs, and move unmatched files to a `notfound` directory for further inspection. Designed for MSX fans, this script is cross-platform, user-friendly, and robust, with comprehensive error handling to ensure a smooth experience.

## Features

- **Organize ROMs**: Sorts ROM files from an `unsorted` directory into:
  - `sorted/<platform>/` (normal ROMs)
  - `sorted/bad/<platform>/` (bad dumps)
  - `sorted/confidential/<platform>/` (confidential ROMs)
- **Handle Unmatched Files**: Moves unmatched files to `notfound/<msx|col|misc>/` based on file extension:
  - `.rom` files go to `notfound/msx/`
  - `.col` files go to `notfound/col/`
  - Other extensions go to `notfound/misc/`
- **Dry Run Mode**: Test the sorting process without modifying files using `--dry-run`.
- **Cross-Platform**: Runs on Windows, Linux, and macOS with consistent behavior.
- **Error Handling**: Robust error handling for file operations, network requests, and database parsing, with clear error messages.
- **User-Friendly**: Provides detailed summaries, instructions, and a help message to guide users.
- **Automatic Database Updates**: Downloads or updates the `msxromsdb.json` database from [romdb.vampier.net](https://romdb.vampier.net) as needed.
- **Duplicate Detection**: Identifies and skips duplicate ROMs based on SHA1 hash, removing the duplicate from `unsorted`.

## Directory Structure

After running the script, your directory will look like this:

MSXRomSorter/
├── unsorted/                   # Place your ROM files here
│   ├── game1.rom
│   └── game2.col
├── sorted/                     # Sorted ROMs
│   ├── MSX/                    # Normal MSX ROMs
│   │   └── game1.rom
│   ├── bad/                    # Bad dumps
│   │   └── MSX/
│   └── confidential/           # Confidential ROMs
│       └── MSX/
├── notfound/                   # Unmatched files
│   ├── msx/                    # Unmatched .rom files
│   ├── col/                    # Unmatched .col files
│   └── misc/                   # Other unmatched files
│       └── game2.bin
├── msxromsdb.json              # ROM database (downloaded automatically)
└── rom_sorter.py               # The script



 
