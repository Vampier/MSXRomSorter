# MSXRomSorter

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
```
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
└── romsorter.py              # The script
```

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Vampier/MSXRomSorter.git
   cd MSXRomSorter
   ```

2. **Ensure Python 3 is Installed**:
- Download and install Python 3.6 or higher from [python.org](https://www.python.org/downloads/) or your package manager.
- On Windows, you can also install Python via the Microsoft Store.
- Verify installation:
  ```
  python --version
  ```
  On Windows, you might need to use `py` instead of `python`:
  ```
  py --version
  ```
- If Python is not in your PATH, you may need to specify the full path, e.g., on Windows:
  ```
  C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python.exe --version
  ```

3. **No Additional Dependencies**:
- The script uses only Python standard libraries, so no additional packages are required.

## Usage

1. **Prepare Your ROMs**:
- Create an `unsorted` directory in the same directory as the script (or let the script create it for you on the first run).
- Place your MSX or ColecoVision ROM files in the `unsorted` directory. Supported file extensions include `.rom`, `.col`, and others.

2. **Run the Script**:
```
python romsorter.py
```

On Windows, you might need:
```
py romsorter.py
```

If Python is not in your PATH, specify the full path:
```
   C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python.exe romsorter.py
```

3. **Options**:
- `--dry-run`: Simulate the sorting process without modifying files. Useful for testing.
  ```
  python romsorter.py--dry-run
  ```
- `-v, --version`: Show the script version.
  ```
  python romsorter.py--version
  ```
- `-h, --help`: Show the help message with detailed usage instructions.
  ```
  python romsorter.py--help
  ```

4. **What Happens When You Run the Script**:
- **First Run**:
  - If the `unsorted` directory doesn’t exist, the script creates it and displays instructions:
    ```
    ROM Sorter Script (v1.0.0)
    =================
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
    ```
  - Add your ROM files to `unsorted` and run the script again.
- **Database Check**:
  - The script checks for the `msxromsdb.json` database. If it’s missing or outdated, it downloads the latest version from [romdb.vampier.net](https://romdb.vampier.net).
- **Sorting**:
  - ROMs in `unsorted` are sorted based on their SHA1 hash:
    - Matched ROMs go to `sorted/<platform>/`, `sorted/bad/<platform>/`, or `sorted/confidential/<platform>/`.
    - Unmatched ROMs go to `notfound/<msx|col|misc>/`.
  - Duplicates are detected and removed from `unsorted`.
- **Notfound Updates**:
  - Files in `notfound` are rechecked against the database and sorted if a match is found.
- **Cleanup**:
  - Empty directories in `unsorted` and `sorted` are removed.
- **Summary**:
  - A summary of actions is displayed:
    ```
    Sorting Summary:
      Files sorted: 2
      Files moved to notfound: 1
      Files skipped (e.g., long names): 0
      Files removed: 2
      Duplicates skipped: 0

    Thank you for using ROM Sorter! Happy collecting, MSX fans!
    For updates or to report issues, visit: https://github.com/Vampier/MSXRomSorter
    ```

5. **Example Usage**:
- **Scenario**: You have two ROM files, `game1.rom` (a valid MSX ROM) and `unknown.bin` (an unmatched file).
- **Steps**:
  1. Place the files in `unsorted`:
     ```
     unsorted/
     ├── game1.rom
     └── unknown.bin
     ```
  2. Run the script:
     ```
     python romsorter.py
     ```
  3. Output:
     ```
     Checking ROM database updates...
     API last modified: 2025-03-27 12:00:00 UTC
     Database is up-to-date (within 5s).

     Scanning unsorted directory...
     Scanning notfound directory...

     Sorting unsorted files...
     Sorted: game1.rom >> sorted/MSX/game1.rom
     Moved unknown.bin >> notfound/misc/[SHA1] - unknown.bin

     Checking notfound for updates...

     Cleaning up empty directories...

     Sorting Summary:
       Files sorted: 1
       Files moved to notfound: 1
       Files skipped (e.g., long names): 0
       Files removed: 1
       Duplicates skipped: 0

     Thank you for using ROM Sorter! Happy collecting, MSX fans!
     For updates or to report issues, visit: https://github.com/Vampier/MSXRomSorter
     ```
  4. Resulting directory structure:
     ```
     MSXRomSorter/
     ├── unsorted/                   # Now empty
     ├── sorted/
     │   └── MSX/
     │       └── game1.rom
     ├── notfound/
     │   └── misc/
     │       └── [SHA1] - unknown.bin
     ├── msxromsdb.json
     └── romsorter.py
     ```

## Dependencies

- **Python 3.6+**: The script uses only Python standard libraries, including:
  - `json`, `os`, `shutil`, `hashlib`, `sys`, `re`, `urllib.request`, `zipfile`, `datetime`, `pathlib`, `argparse`, `platform`
- **Internet Connection**: Required for the initial download of `msxromsdb.json` from [romdb.vampier.net](https://romdb.vampier.net) and for database updates.

No additional packages are required, making setup straightforward on any platform.

## Windows-Specific Notes

### Long Filenames
Windows has a default maximum path length of 260 characters (MAX_PATH), which can cause issues with long filenames or deep directory structures. The script includes the following mitigations:

- **Error Handling**: Files with names that are too long are skipped with a message:

```
  Skipped <filename>: File name too long
```

- **Long Path Support**: On Windows 10 (version 1607 and later), the script attempts to enable long path support programmatically. However, this may require:
- **Enabling Long Paths Manually**:
  1. Open the Registry Editor (`regedit`).
  2. Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`.
  3. Set `LongPathsEnabled` to `1` (create the DWORD if it doesn’t exist).
  4. Restart your computer.
- Alternatively, use the Group Policy Editor (not available on Windows Home):
  1. Open `gpedit.msc`.
  2. Navigate to `Computer Configuration > Administrative Templates > System > Filesystem`.
  3. Enable `Enable Win32 long paths`.
  4. Restart your computer.
- **Warning**: If long path support cannot be enabled, the script will print a warning:

```  Warning: Could not enable long path support on Windows: <error>
  Paths longer than 260 characters may cause issues.
```

- **Recommendation**: Keep your directory structure shallow and filenames short to avoid issues, or ensure long path support is enabled.

### Path Display
The script normalizes all paths in output messages to use forward slashes (`/`) for consistency across platforms. For example, on Windows, a path like `sorted\MSX\file.rom` will be displayed as `sorted/MSX/file.rom`.

### Running the Script
- Ensure Python is in your PATH, or specify the full path to the Python executable:

```
  C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python.exe romsorter.py
```
- Alternatively, use the `py` launcher, which is often pre-installed on Windows:

```
py romsorter.py
```

- If you encounter permission issues (e.g., `PermissionError`), ensure you have write access to the directory where the script is running, and that files are not marked as read-only.

## Troubleshooting

Here are some common issues and solutions:

- **Error: msxromsdb.json not found!**:
- The script couldn’t download the database. Check your internet connection and try again.
- Ensure the URL `https://romdb.vampier.net/api/get_latest.php` is accessible.
- If the issue persists, you can manually download `msxromsdb.json` from [romdb.vampier.net](https://romdb.vampier.net) and place it in the script’s directory.

- **Error: Permission denied**:
- You lack permission to read/write files in the current directory.
- On Windows, ensure the directory is not read-only (right-click the folder, go to Properties, and uncheck "Read-only").
- Run the script as an administrator:
  - Command Prompt: `Run as administrator`
  - PowerShell: `Start-Process python -ArgumentList "romsorter.py" -Verb RunAs`
- On Linux/macOS, use `sudo` if necessary (not recommended unless required):
  ```
  sudo python romsorter.py
  ```

- **Error: File name too long**:
- See the "Long Filenames" section under "Windows-Specific Notes" for instructions on enabling long path support.
- Alternatively, shorten the filenames or move the script to a directory with a shorter path (e.g., `C:\MSXRomSorter`).

- **No files were sorted**:
- Ensure you’ve placed ROM files in the `unsorted` directory.
- Verify that the `msxromsdb.json` database is present and not corrupted. Run the script with `--dry-run` to see what it would do:
  ```
  python romsorter.py--dry-run
  ```

- **Script crashes or behaves unexpectedly**:
- Check the error message for details. The script is designed to handle most errors gracefully and provide a message.
- If the issue persists, open an issue on GitHub with the error message and steps to reproduce.

## Contributing

We welcome contributions from the MSX community!

## Issues and Feedback

If you encounter any issues or have suggestions, please:

- **Open an Issue**: Go to the [Issues tab](https://github.com/Vampier/MSXRomSorter/issues) and create a new issue. Include:
  - A description of the problem.
  - The error message (if any).
  - Steps to reproduce the issue.
  - Your operating system (Windows, Linux, macOS).
- **Contact**: Reach out via the repository or email (if provided).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---











 
