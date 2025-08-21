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

def choose_path():
    """Display menu to choose a path."""
    external_drives = get_external_drives()
    internal_paths = get_internal_paths()

    # Merge external and internal paths
    options = external_drives + internal_paths

    # Display the menu
    print("Choose a path:")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    
    # User selects a path
    choice = int(input("Enter the number of your choice: ")) - 1
    if 0 <= choice < len(options):
        return options[choice]
    else:
        print("Invalid choice")
        return None

# Set the chosen path to the 'src' variable
src = choose_path()

if src:
    print(f"The path '{src}' has been set to the 'src' variable.")
    input('Press any key to continue')
else:
    print("No valid path selected.")
    input("press any key to continue")
    
    
    
'''
Explanation:
get_external_drives():

Windows: It loops through drive letters from A: to Z: and checks if they exist. If they do, it assumes they are available drives.
Linux: It looks in the /media and /mnt directories, where external drives are typically mounted.
macOS: It checks the /Volumes directory for mounted drives (this is where macOS typically mounts external drives).
get_internal_paths(): Similar to the previous example, you can specify your custom internal paths.

Menu: The user is prompted with a menu to select a path, and the selected path is assigned to the src variable.

Customization:
You can modify or expand the internal paths to suit your environment.
If your environment has a different mounting location for external drives, you can adjust the path-checking logic accordingly.
Notes:
This script works cross-platform (Windows, Linux, macOS).
It does not rely on any external libraries, and you can extend it to cover other operating system-specific behaviors if needed.

'''
