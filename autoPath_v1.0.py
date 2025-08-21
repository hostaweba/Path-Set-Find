'''
Separate the system drive from other drives.
First search non-system drives.
Search the system drive at the end.


Summary:
Non-system drives are searched first, then the system drive is searched last.
System drives are restricted to 2 levels of depth, while non-system drives can be searched to unlimited depth.
The code still works across Windows, Linux, and macOS.
'''

import os
import platform
import re
import pandas as pd

def read_path_from_csv(csv_file, cell_reference="B5"):
    """Read the path from a specified cell in the CSV file."""
    try:
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
    """Search all drives, non-system drives first, then system drive, and set the path based on specific filenames."""
    all_drives = get_available_drives()

    # Separate system drive from non-system drives
    system_drive = None
    non_system_drives = []
    
    for drive in all_drives:
        if is_system_drive(drive):
            system_drive = drive
        else:
            non_system_drives.append(drive)

    # List of target files to search for
    target_files = ["_setpath_", "_setthispath_", "_setfromcsv_"]

    # Search non-system drives first
    for drive in non_system_drives:
        print(f"Searching in {drive}...")
        file_path, target_file = search_for_setpath_file(drive, target_files)

        if file_path:
            print(f"Found {target_file} in {file_path}")
            chosen_path = set_path_based_on_file(drive, file_path, target_file, csv_file)
            if chosen_path:
                return chosen_path
            else:
                print(f"Error determining path from {file_path} with {target_file}")

    # Now search the system drive
    if system_drive:
        print(f"Searching in system drive {system_drive}...")
        file_path, target_file = search_for_setpath_file(system_drive, target_files)

        if file_path:
            print(f"Found {target_file} in {file_path}")
            chosen_path = set_path_based_on_file(system_drive, file_path, target_file, csv_file)
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
    input()
else:
    print("No valid path found or set.")
    input('press')
