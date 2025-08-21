"""Path Manager (Stable, Fast, Transparent)

Features:
- Choose a base folder from paths.csv (single-column list of absolute folders).
- Add new folder entries to paths.csv.
- Find folders that contain a marker file (set_path.txt) by scanning only desirable locations
  up to a configurable depth (fast and limited).
- Browse into subfolders interactively (breadcrumbs, back, up, quit).
- Optionally list files in the chosen folder by extension (single-folder or recursive with limits).
- Keeps a short recent list for quick access.
- Robust input validation and permission-error handling to avoid crashes.

Usage: run this script with Python 3. Works on Windows, macOS, Linux.
"""

import os
import platform
import csv
import json
import time
from pathlib import Path

# ---------------- CONFIG ----------------
CSV_FILE = "paths.csv"            # CSV file that stores saved folders (one folder per row)
RECENT_FILE = "recent.json"       # JSON file to store recent paths
MARKER_FILENAME = "set_path.txt"  # Marker file to search for
DEFAULT_SCAN_DIRS = ["Desktop", "Documents", "Downloads"]
DEFAULT_MAX_DEPTH = 2              # default scan depth for set_path.txt
MAX_SEARCH_RESULTS = 1000          # safety limit for recursive file searches
SHOW_RESULTS_LIMIT = 100           # how many results to show on screen

# ---------------- UTILITIES ----------------

def safe_print(*args, **kwargs):
    """Print that is robust to odd filenames on some consoles."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        enc = kwargs.get("file") or None
        for a in args:
            try:
                print(a, end=" ", file=enc)
            except Exception:
                # fallback minimal print
                print(str(a).encode('utf-8', 'replace'), end=" ")
        print()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def expand(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))

# ---------------- CSV + RECENT ----------------

def read_csv_paths(csv_file=CSV_FILE):
    """Read saved absolute folder paths from CSV. Only return existing directories.
    CSV is expected to be one path per row (first column)."""
    paths = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                p = expand(row[0])
                if os.path.isdir(p):
                    paths.append(p)
    except FileNotFoundError:
        return []
    except Exception as e:
        safe_print("Error reading CSV:", e)
        return []
    return paths


def append_csv_path(new_path, csv_file=CSV_FILE):
    new_path = expand(new_path)
    if not os.path.isdir(new_path):
        safe_print(f"Cannot add: not a directory -> {new_path}")
        return False
    try:
        # ensure folder exists and then append
        with open(csv_file, 'a', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow([new_path])
        return True
    except Exception as e:
        safe_print("Failed to write to CSV:", e)
        return False


def load_recent(recent_file=RECENT_FILE):
    try:
        if not os.path.exists(recent_file):
            return []
        with open(recent_file, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            if isinstance(data, list):
                # validate entries
                return [expand(p) for p in data if os.path.isdir(expand(p))]
    except Exception:
        return []
    return []


def save_recent(path, recent_file=RECENT_FILE, max_items=5):
    path = expand(path)
    items = load_recent(recent_file)
    # move path to front
    new = [path] + [p for p in items if p != path]
    new = new[:max_items]
    try:
        with open(recent_file, 'w', encoding='utf-8') as fh:
            json.dump(new, fh, indent=2)
    except Exception as e:
        safe_print("Warning: could not save recent paths:", e)

# ---------------- DRIVES & DEFAULT LOCATIONS ----------------

def get_external_drives():
    system = platform.system()
    drives = []
    try:
        if system == 'Windows':
            for code in range(67, 91):  # start from C: usually
                letter = f"{chr(code)}:"
                path = letter + os.sep
                if os.path.isdir(path):
                    drives.append(path)
        else:
            # Linux/macOS: check common mount points
            for root in ['/media', '/mnt', '/Volumes']:
                if os.path.exists(root):
                    try:
                        for entry in os.listdir(root):
                            candidate = os.path.join(root, entry)
                            if os.path.isdir(candidate):
                                drives.append(candidate)
                    except PermissionError:
                        continue
    except Exception:
        pass
    return drives


def default_scan_locations():
    """Return absolute paths for default scan dirs under user's home (if they exist).
    e.g. ~/Desktop, ~/Documents, ~/Downloads"""
    home = Path.home()
    locs = []
    for name in DEFAULT_SCAN_DIRS:
        p = home.joinpath(name)
        if p.exists() and p.is_dir():
            locs.append(str(p))
    # always include home as last resort
    locs.append(str(home))
    return locs

# ---------------- LIMITED DEPTH SEARCH FOR MARKER ----------------

def rel_depth(path, base):
    """Return integer depth of path relative to base (base -> 0; base/sub ->1)."""
    try:
        rel = os.path.relpath(path, base)
    except Exception:
        return 999
    if rel == '.' or rel == os.curdir:
        return 0
    # count separators
    return rel.count(os.sep) + 1


def find_marker_paths(base_dirs, marker=MARKER_FILENAME, max_depth=DEFAULT_MAX_DEPTH):
    """Search each base_dir for folders that contain marker file, up to max_depth.
    This is limited and prints progress. Returns sorted list of unique folder paths."""
    found = []
    for base in base_dirs:
        base = expand(base)
        if not os.path.isdir(base):
            continue
        safe_print(f"Scanning: {base} (depth <= {max_depth})...")
        try:
            for root, dirs, files in os.walk(base):
                try:
                    d = rel_depth(root, base)
                except Exception:
                    d = 999
                if d > max_depth:
                    # don't walk deeper
                    dirs[:] = []
                    continue
                if marker in files:
                    found.append(expand(root))
        except PermissionError:
            safe_print(f"Permission denied accessing: {base}")
        except Exception:
            continue
    # unique and sort
    uniq = sorted(list(dict.fromkeys(found)))
    return uniq

# ---------------- FILE SEARCH (OPTIONAL) ----------------

def search_files_in_folder(folder, extension, recursive=False, limit=MAX_SEARCH_RESULTS):
    """Search for files by extension. If recursive True, walk subfolders but stop at 'limit'.
    Returns list of paths (may be truncated)."""
    results = []
    extension = extension if extension.startswith('.') else '.' + extension

    if not recursive:
        try:
            for name in os.listdir(folder):
                if name.lower().endswith(extension.lower()):
                    results.append(os.path.join(folder, name))
                    if len(results) >= limit:
                        break
        except Exception:
            pass
        return results

    # recursive
    for root, dirs, files in os.walk(folder):
        try:
            for f in files:
                try:
                    if f.lower().endswith(extension.lower()):
                        results.append(os.path.join(root, f))
                        if len(results) >= limit:
                            return results
                except Exception:
                    continue
        except PermissionError:
            # skip directories we can't read
            continue
        except Exception:
            continue
    return results

# ---------------- NAVIGATION ----------------

def present_menu(title, options, allow_back=True, allow_quit=True):
    """Show numbered options and return raw user input."""
    safe_print(f"\n=== {title} ===")
    for i, opt in enumerate(options, 1):
        safe_print(f"{i}. {opt}")
    if allow_back:
        safe_print("b. Back")
    if allow_quit:
        safe_print("q. Quit")
    return input("Enter choice: ").strip().lower()


def navigate_folder(start_path):
    """Interactive folder navigation. Returns chosen folder or None."""
    path = expand(start_path)
    history = []
    while True:
        clear_screen()
        safe_print(f"Current: {path}")
        subs = []
        try:
            subs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        except Exception:
            subs = []
        options = ["Use this folder"] + subs
        choice = present_menu("Explore subfolders (enter number)", options, allow_back=len(history) > 0, allow_quit=True)

        if choice == 'q':
            return None
        if choice == 'b' and history:
            path = history.pop()
            continue
        if choice.isdigit():
            idx = int(choice)
            if idx == 1:
                # use this folder
                save_recent(path)
                return path
            else:
                sel_index = idx - 2
                if 0 <= sel_index < len(subs):
                    history.append(path)
                    path = os.path.join(path, subs[sel_index])
                    continue
        safe_print("Invalid choice. Try again.")
        time.sleep(0.6)

# ---------------- MAIN FLOW ----------------

def main_menu():
    while True:
        clear_screen()
        safe_print("SIMPLE PATH MANAGER - Stable & Fast")
        safe_print("")
        safe_print("Choose how to set the path:")
        safe_print("1. Choose from paths.csv (saved folders)")
        safe_print("2. Scan desirable locations for set_path.txt (fast, limited)")
        safe_print("3. Choose from drives & common folders")
        safe_print("4. Add a folder to paths.csv")
        safe_print("5. Recent paths")
        safe_print("q. Quit")

        choice = input("Enter choice: ").strip().lower()

        if choice == 'q':
            return None
        if choice == '1':
            paths = read_csv_paths()
            if not paths:
                safe_print("No saved paths found in paths.csv.")
                input("Press Enter to continue...")
                continue
            ch = present_menu("Saved paths (choose to explore)", paths, allow_back=True)
            if ch == 'b' or ch == 'q':
                continue
            if ch.isdigit() and 1 <= int(ch) <= len(paths):
                chosen = navigate_folder(paths[int(ch)-1])
                return chosen
            safe_print("Invalid selection.")
            time.sleep(0.5)

        elif choice == '2':
            # ask user for depth
            safe_print("Where to scan? (default: Desktop, Documents, Downloads, Home)")
            base_choice = input("Press Enter to use defaults or type a comma-separated list (full paths): ").strip()
            if base_choice:
                bases = [expand(p.strip()) for p in base_choice.split(',') if p.strip()]
            else:
                bases = default_scan_locations()
            # depth
            d_input = input(f"Scan depth (1..5, default {DEFAULT_MAX_DEPTH}): ").strip()
            try:
                depth = int(d_input) if d_input and 1 <= int(d_input) <= 5 else DEFAULT_MAX_DEPTH
            except Exception:
                depth = DEFAULT_MAX_DEPTH
            safe_print("Scanning (fast) — this searches only limited folders and depths...")
            found = find_marker_paths(bases, MARKER_FILENAME, depth)
            if not found:
                safe_print("No marker folders found in chosen locations.")
                input("Press Enter to continue...")
                continue
            ch = present_menu("Marker folders found:", found, allow_back=True)
            if ch == 'b' or ch == 'q':
                continue
            if ch.isdigit() and 1 <= int(ch) <= len(found):
                chosen = navigate_folder(found[int(ch)-1])
                return chosen
            safe_print("Invalid selection.")
            time.sleep(0.5)

        elif choice == '3':
            drives = get_external_drives()
            common = default_scan_locations()
            options = drives + [p for p in common if p not in drives]
            if not options:
                safe_print("No drives or common folders found.")
                input("Press Enter to continue...")
                continue
            ch = present_menu("Drives & common folders:", options, allow_back=True)
            if ch == 'b' or ch == 'q':
                continue
            if ch.isdigit() and 1 <= int(ch) <= len(options):
                chosen = navigate_folder(options[int(ch)-1])
                return chosen
            safe_print("Invalid selection.")
            time.sleep(0.5)

        elif choice == '4':
            newp = input("Enter full folder path to add to paths.csv: ").strip()
            if not newp:
                continue
            newp = expand(newp)
            if os.path.isdir(newp):
                if append_csv_path(newp):
                    safe_print("Path added to CSV.")
                else:
                    safe_print("Failed to add path to CSV.")
            else:
                safe_print("Not a valid directory.")
            input("Press Enter to continue...")

        elif choice == '5':
            recents = load_recent()
            if not recents:
                safe_print("No recent paths saved yet.")
                input("Press Enter to continue...")
                continue
            ch = present_menu("Recent paths:", recents, allow_back=True)
            if ch == 'b' or ch == 'q':
                continue
            if ch.isdigit() and 1 <= int(ch) <= len(recents):
                chosen = navigate_folder(recents[int(ch)-1])
                return chosen
            safe_print("Invalid selection.")
            time.sleep(0.5)
        else:
            safe_print("Invalid choice. Try again.")
            time.sleep(0.5)


if __name__ == '__main__':
    try:
        final = main_menu()
        clear_screen()
        if final:
            safe_print(f"Final chosen path: {final}")

            # Ask to optionally search for files
            ask = input("Do you want to list files by extension in this folder? (y/n): ").strip().lower()
            if ask == 'y':
                ext = input("Enter extension (example: txt, pdf, .jpg): ").strip().lstrip('.')
                rec = input("Recursive? search subfolders as well? (y/n, default n): ").strip().lower()
                recursive = rec == 'y'
                safe_print("Searching (this may take a moment for recursive searches)...")
                results = search_files_in_folder(final, ext, recursive=recursive)
                safe_print(f"Found {len(results)} file(s) matching .{ext}")
                show_more = results[:SHOW_RESULTS_LIMIT]
                for r in show_more:
                    safe_print(r)
                if len(results) > SHOW_RESULTS_LIMIT:
                    safe_print(f"...and {len(results)-SHOW_RESULTS_LIMIT} more (not shown)")
                # offer export
                if results:
                    expo = input("Export results to a text file? (y/n): ").strip().lower()
                    if expo == 'y':
                        outname = input("Enter output filename (default search_results.txt): ").strip() or 'search_results.txt'
                        try:
                            with open(outname, 'w', encoding='utf-8') as of:
                                for r in results:
                                    of.write(r + '\n')
                            safe_print(f"Results exported to {outname}")
                        except Exception as e:
                            safe_print("Failed to export results:", e)
            else:
                safe_print("No file search performed.")
        else:
            safe_print("No path selected. Goodbye.")
    except KeyboardInterrupt:
        safe_print("\nInterrupted by user. Exiting.")
    except Exception as e:
        safe_print("Unexpected error:", e)
        safe_print("Exiting gracefully.")
