import os
import platform

def get_external_drives():
    """Function to get external drives based on the operating system."""
    drives = []
    
    if platform.system() == "Windows":
        # On Windows, drives are typically assigned letters (C:, D:, etc.)
        for drive in range(65, 91):  # ASCII codes for A-Z
            drive_letter = f"{chr(drive)}:\\"
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
    
    elif platform.system() == "Linux":
        # On Linux, external drives are typically mounted in /media or /mnt
        media_path = "/media"
        mnt_path = "/mnt"
        if os.path.exists(media_path):
            drives.extend([os.path.join(media_path, d) for d in os.listdir(media_path)])
        if os.path.exists(mnt_path):
            drives.extend([os.path.join(mnt_path, d) for d in os.listdir(mnt_path)])
    
    elif platform.system() == "Darwin":
        # On macOS, external drives are usually mounted in /Volumes
        volumes_path = "/Volumes"
        if os.path.exists(volumes_path):
            drives.extend([os.path.join(volumes_path, d) for d in os.listdir(volumes_path)])

    return drives

def get_internal_paths():
    """Predefined internal paths."""
    internal_paths = [
        os.path.expanduser("~"),  # Home directory
        "/path/to/project",        # Custom path
        "/path/to/documents",      # Another custom path
    ]
    return internal_paths

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
    
def choose_path():
    """Display menu to choose a base path and optionally subpaths."""
    external_drives = get_external_drives()
    internal_paths = get_internal_paths()

    # Merge external and internal paths
    options = external_drives + internal_paths

    # Display the base path menu
    print("Choose a base path:")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    
    # User selects a base path
    choice = int(input("Enter the number of your choice: ")) - 1
    if 0 <= choice < len(options):
        chosen_path = options[choice]
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
src = choose_path()

if src:
    print(f"The full path '{src}' has been set to the 'src' variable.")
else:
    print("No valid path selected.")



'''
How it Works:
User selects a base path from external drives or internal paths.
The script lists subfolders in the current directory, and the user can select a subfolder to go deeper into the directory structure.
The user can continue selecting subfolders until they choose to stop by entering "0".
Final path: The fully constructed path is then set to the src variable.


Key Features:
Initial Path Selection: The user selects a base path, either from external drives or predefined internal paths.

Subfolder Selection:

After selecting the base path, the script lists the available subfolders within that directory.
The user can then choose a subfolder, which is appended to the current path.
The process repeats, allowing the user to keep navigating into subfolders until they choose to stop (by selecting "0").
Dynamic Path Construction: The selected subfolders are joined to the base path using os.path.join() to form the final path.



'''
