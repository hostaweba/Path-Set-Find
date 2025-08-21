import os
import platform
import csv

def read_paths_from_csv(csv_file):
    """Reads paths from the CSV file and returns paths based on the current OS."""
    paths = []

    # Determine the current operating system
    current_os = platform.system()

    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if current_os == "Windows":
                    paths.append(row[0])  # Use the Windows column
                elif current_os == "Linux":
                    paths.append(row[1])  # Use the Linux column
                elif current_os == "Darwin":  # macOS is "Darwin"
                    paths.append(row[2])  # Use the macOS column
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return []
    
    return paths

def list_subfolders(path):
    """List subfolders of the selected path."""
    try:
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    except PermissionError:
        print(f"Permission denied to access {path}")
        return []
    except FileNotFoundError:
        print(f"Path not found: {path}")
        return []

def choose_path_from_csv(csv_file):
    """Choose a path from the list based on the current OS."""
    paths = read_paths_from_csv(csv_file)

    if not paths:
        print("No paths available or error reading the CSV file.")
        return None

    # Display the menu to choose a base path
    print("Choose a base path:")
    for idx, path in enumerate(paths, 1):
        print(f"{idx}. {path}")
    
    # User selects a base path
    choice = int(input("Enter the number of your choice: ")) - 1
    if 0 <= choice < len(paths):
        chosen_path = paths[choice]
    else:
        print("Invalid choice")
        return None

    # Add subfolder selection loop
    while True:
        subfolders = list_subfolders(chosen_path)
        if not subfolders:
            print(f"No subfolders found in {chosen_path} or permission denied.")
            break

        print(f"\nCurrent path: {chosen_path}")
        print("Subfolders:")
        print("0. Stop choosing subfolders (use current path)")
        for idx, folder in enumerate(subfolders, 1):
            print(f"{idx}. {folder}")

        sub_choice = int(input("Enter the number of your choice: ")) - 1
        if sub_choice == -1:
            # Stop if the user chooses 0
            break
        elif 0 <= sub_choice < len(subfolders):
            # Append chosen subfolder to the current path
            chosen_path = os.path.join(chosen_path, subfolders[sub_choice])
        else:
            print("Invalid choice")
    
    return chosen_path

# Set the chosen path to the 'src' variable
csv_file_path = "paths.csv"
src = choose_path_from_csv(csv_file_path)

if src:
    print(f"The full path '{src}' has been set to the 'src' variable.")
    input('press')
else:
    print("No valid path selected.")
    input('press')

'''
First column: Windows paths
Second column: Linux paths
Third column: macOS paths



Key Steps:
read_paths_from_csv(): This function reads the paths from the CSV file. Depending on the detected OS (Windows, Linux, or macOS), it selects the appropriate paths.

For Windows, it takes the path from the first column.
For Linux, it takes the path from the second column.
For macOS (Darwin), it takes the path from the third column.
list_subfolders(): This function lists the subfolders within the selected path to allow navigation through directories.

choose_path_from_csv(): This is the main function that allows the user to:

Choose a base path from the CSV.
Optionally select subfolders, navigating deeper into directories.
CSV File: The script expects the CSV file (paths.csv) to have three columns, with paths for each OS. Make sure the file exists in the same directory as the script or adjust the csv_file_path to point to the correct location.




Notes:
The script automatically selects the appropriate paths based on the operating system.
It handles both CSV parsing and subfolder navigation.
You can customize the CSV file with more paths as needed.


'''