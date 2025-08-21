'''
Identify the _setfromcsv_ pattern more flexibly:
The pattern _setfromcsv_a1_ may have various alphanumeric values (like a2, b32, d323, etc.). We'll make the pattern matching more flexible by using regular expressions.
Limit the directory depth only for non-system drives:
We’ll exclude system drives from the 3-level depth search. For example, on Windows, the system drive is usually C:, and on Linux/macOS, it’s / (root). We'll restrict the depth accordingly.









'''
import os
import platform
import re
import pandas as pd

def read_path_from_csv(csv_file, cell_reference="B5"):
    """Read the path from a specified cell in the CSV file."""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file, header=None)
        row, col = int(cell_reference[1:]) - 1, ord(cell_reference[0].upper()) - ord('A')
        return df.iat[row, col]
    except (FileNotFoundError, ValueError, IndexError):
        print(f"Error reading from {csv_file} or invalid cell {cell_reference}")
        return None

def get_available_drives():
    """Return a list of available drives based on the OS."""
    drives = []

    if platform.system() == "Windows":
        for drive in range(65, 91):  # ASCII A-Z
            drive_letter = f"{chr(drive)}:\\"
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
    elif platform.system() == "Linux":
        drives = ["/media", "/mnt"]  # Common mount points
    elif platform.system() == "Darwin":  # macOS
        drives = ["/Volumes"]

    # On Linux/macOS, add root "/" as the system drive
    if platform.system() in ["Linux", "Darwin"]:
        drives.append("/")

    return drives

def is_system_drive(drive):
    """Check if the drive is the system drive."""
    if platform.system() == "Windows":
        return drive.lower() == "c:\\"
    elif platform.system() in ["Linux", "Darwin"]:
        return drive == "/"
    return False

def search_for_setpath_file(drive, target_files, max_system_depth=2):
    """Search directories: limit to 2 levels for system drive, unlimited levels for other drives."""
    try:
        for root, dirs, files in os.walk(drive):
            # Calculate current depth
            depth = root[len(drive):].count(os.sep)

            # If it's the system drive, limit the search to max_system_depth (2 levels)
            if is_system_drive(drive) and depth >= max_system_depth:
                dirs[:] = []  # Stop descending further in directories
                continue

            # Check for the target files with flexible regex matching for "_setfromcsv_"
            for file in files:
                for target_file in target_files:
                    if target_file == "_setfromcsv_":
                        # Use regex to match the flexible setfromcsv pattern (e.g., _setfromcsv_a1_, _setfromcsv_b32_)
                        match = re.search(r'_setfromcsv_([a-zA-Z]\d+)_', file)
                        if match:
                            return os.path.join(root, file), f"_setfromcsv_{match.group(1)}_"
                    elif target_file in file:
                        return os.path.join(root, file), target_file

    except PermissionError:
        print(f"Permission denied to access {drive}")
    
    return None, None

def set_path_based_on_file(drive, file_path, target_file, csv_file):
    """Set the path based on the target file found."""
    if target_file == "_setpath_":
        return drive
    elif target_file == "_setthispath_":
        return os.path.dirname(file_path)
    elif target_file.startswith("_setfromcsv_"):
        # Extract the cell reference (e.g., "a1", "b32") from the target file
        cell = target_file.split("_")[2].upper()  # Convert "a1" to "A1", "b32" to "B32"
        return read_path_from_csv(csv_file, cell_reference=cell)

def choose_path(csv_file):
    """Search all drives and set the path based on specific filenames."""
    drives = get_available_drives()
    target_files = ["_setpath_", "_setthispath_", "_setfromcsv_"]

    for drive in drives:
        print(f"Searching in {drive}...")
        file_path, target_file = search_for_setpath_file(drive, target_files)

        if file_path:
            print(f"Found {target_file} in {file_path}")
            chosen_path = set_path_based_on_file(drive, file_path, target_file, csv_file)
            if chosen_path:
                return chosen_path
            else:
                print(f"Error determining path from {file_path} with {target_file}")

    return None

# CSV file to be used if _setfromcsv_a1_ is found
csv_file_path = "paths.csv"

# Call the function to set the path based on the file search
src = choose_path(csv_file_path)

if src:
    print(f"The path '{src}' has been set to the 'src' variable.")
    input('press')
else:
    print("No valid path found or set.")
    input('press')


'''
Key Updates:
System Drive Depth Restriction:

For system drives (C: on Windows, / on Linux/macOS), the search is now restricted to 2 directory levels using the depth value.
python
Copy code
if is_system_drive(drive) and depth >= max_system_depth:
    dirs[:] = []  # Stop descending further in directories
    continue
Unlimited Depth for Non-System Drives:

For other drives (non-system), the script will search all directory levels by not imposing any depth restriction.
Cross-Platform:

The script works across Windows, Linux, and macOS.
It correctly identifies system drives: C: for Windows and / for Linux/macOS.
How It Works:
File Search:

It searches for filenames containing _setpath_, _setthispath_, and _setfromcsv_.
If _setfromcsv_ is found, it looks for a matching pattern like _setfromcsv_a1_, _setfromcsv_b32_, etc., using regular expressions.
System Drive Depth:

On system drives, the script limits the directory traversal to 2 levels. For non-system drives, it searches through all levels.


Limit system drive search to 2 levels:

Use depth to count directory levels during traversal, and restrict the system drive search to 2 levels.
Search through all levels in non-system drives:

For non-system drives, we won't impose any limit on directory depth, allowing the script to explore all levels.
























Regex for Flexible Pattern Matching:

In search_for_setpath_file(), we now use a regular expression to match filenames with the _setfromcsv_ pattern.
The regex '_setfromcsv_([a-zA-Z]\d+)_' captures filenames like _setfromcsv_a1_, _setfromcsv_b32_, etc., where the pattern can have any combination of one letter followed by one or more digits. For example:
_setfromcsv_a1_
_setfromcsv_b32_
_setfromcsv_d323_
System Drive Depth Limitation:

In the function is_system_drive(), we determine if a drive is the system drive:
On Windows, we treat C:\ as the system drive.
On Linux/macOS, we treat / (root) as the system drive.
In search_for_setpath_file(), we limit the depth of the directory traversal to 1 level if the current drive is the system drive, while still allowing up to 3 levels for other drives.
How It Works:
File Pattern Matching:

The script will now look for files that match _setfromcsv_ followed by a letter and a number (e.g., _setfromcsv_a1_, _setfromcsv_b32_).
If it finds such a file, it will extract the cell reference (e.g., a1, b32) and use it to read from the CSV file.
System Drive Depth:

For system drives (C:\ on Windows or / on Linux/macOS), the script will only search up to 1 directory level.
For non-system drives (e.g., D:\, /mnt, /Volumes), the script will search up to 3 directory levels.


Notes:
Regular Expression: The regex pattern ensures that filenames with dynamic values like _setfromcsv_b32_ will be correctly identified.
Cross-Platform: This script works on both Windows and Unix-based systems (Linux/macOS).
CSV File: The CSV file must be structured properly with paths in cells like A1, B32, etc. When the file _setfromcsv_a1_ is found, the script will look up the corresponding path in cell A1 from the CSV file.





'''
