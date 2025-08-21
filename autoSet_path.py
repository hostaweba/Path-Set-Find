import os
import platform
import csv
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

    return drives

def search_for_setpath_file(drive, target_files, max_depth=3):
    """Search up to 3 levels deep for target filenames in the drive."""
    try:
        for root, dirs, files in os.walk(drive):
            # Calculate current depth
            depth = root[len(drive):].count(os.sep)
            
            # Only go up to the third level (depth = 3)
            if depth > max_depth:
                # Skip any directories beyond the max_depth
                dirs[:] = []
                continue

            # Check for the target files
            for file in files:
                for target_file in target_files:
                    if target_file in file:
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
    elif target_file.startswith("_setfromcsv_b"):
        cell = target_file.split("_b")[1].upper()  # Extract the cell reference (e.g., B5)
        return read_path_from_csv(csv_file, cell_reference=cell)

def choose_path(csv_file):
    """Search all drives and set the path based on specific filenames."""
    drives = get_available_drives()
    target_files = ["_setpath_", "_setthispath_", "_setfromcsv_b"]

    for drive in drives:
        print(f"Searching in {drive} up to 3 levels deep...")
        file_path, target_file = search_for_setpath_file(drive, target_files, max_depth=3)

        if file_path:
            print(f"Found {target_file} in {file_path}")
            chosen_path = set_path_based_on_file(drive, file_path, target_file, csv_file)
            if chosen_path:
                return chosen_path
            else:
                print(f"Error determining path from {file_path} with {target_file}")

    return None

# CSV file to be used if _setfromcsv_b5_ is found
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
Key Points:
The script searches for special files (_setpath_, _setthispath_, and _setfromcsv_b).
If _setfromcsv_b5_ is found, it reads the path from the specified cell in the CSV file (e.g., cell B5).
The search only goes one level deep into each drive.
The pandas library is used to read the CSV file.
This solution works for cross-platform environments (Windows, Linux, macOS), and it dynamically sets paths based on files and CSV input.




Search all available drives (depending on the operating system).
Search for specific filenames (like _setpath_, _setthispath_, and _setfromcsv_b5_) at the first level of directories.
Set the path dynamically based on which file is found.
If _setpath_ is found, set the path to that drive.
If _setthispath_ is found, set the path to the folder where the file is located.
If _setfromcsv_b5_ is found, read the path from the CSV file and use the value from cell B5.
Here’s a Python script to handle this:



Explanation:
read_path_from_csv():

This function uses pandas to read the CSV file and extract the value from a specified cell (e.g., B5). The cell_reference argument specifies the cell in Excel-style (e.g., B5 means the 5th row, 2nd column).
get_available_drives():

This function determines the available drives depending on the operating system. On Windows, it checks for drive letters (A: to Z:), while on Linux and macOS, it checks typical mount points (e.g., /media, /mnt, /Volumes).
search_for_setpath_file():

This function searches the first level of each drive for specific filenames (_setpath_, _setthispath_, _setfromcsv_b).
set_path_based_on_file():

Based on the found filename, this function sets the path:
_setpath_: Sets the path to the drive root.
_setthispath_: Sets the path to the folder where the file is located.
_setfromcsv_b: Reads the path from the specified cell (e.g., B5) in the CSV file.
choose_path():

This is the main function that iterates through the drives and searches for the filenames. Once found, it dynamically sets the path based on the file's name and content.

'''