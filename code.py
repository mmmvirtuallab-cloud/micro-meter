import os
import argparse
import sys
from typing import List

# --- Pyperclip Setup ---
try:
    import pyperclip
    print("✅ Clipboard library (pyperclip) is available.")
except ImportError:
    print("\n❌ ERROR: pyperclip is not installed.")
    print("Please install it: 'pip install pyperclip'")
    sys.exit(1)
except pyperclip.PyperclipException:
    print("\n❌ ERROR: pyperclip is installed but cannot function on this system.")
    print("If on Linux, you may need to install 'xclip' or 'xsel'.")
    sys.exit(1)
# -----------------------

CODE_FILE_EXTENSIONS = (
    '.py', '.dart', '.js', '.ts', '.jsx', '.tsx', '.java', '.kt', 
    '.c', '.cpp', '.h', '.cs', '.go', '.html', '.css', '.scss', 
    '.json', '.yaml', '.yml', '.md', '.sh', '.txt' # Added common config/text files
)
NON_CODE_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.zip', '.exe', '.bin', '.db', 
    '.lock', '.log', '.dat', '.sqlite', '.webp'
)
OUTPUT_SEPARATOR = '\n\n---\n\n'

def is_code_file(filepath: str) -> bool:
    """Checks if a file has a recognized code/text extension."""
    return filepath.lower().endswith(CODE_FILE_EXTENSIONS) and not filepath.lower().endswith(NON_CODE_EXTENSIONS)

def get_files_from_path(target_path: str, combined_content: List[str]) -> int:
    """Recursively reads code files from a path (file or directory)."""
    files_read = 0
    
    if os.path.isfile(target_path) and is_code_file(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            formatted_entry = f"### File: {target_path}\n\n{content}"
            combined_content.append(formatted_entry)
            files_read += 1
        except UnicodeDecodeError:
            pass
        except Exception:
            pass
            
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                full_path = os.path.join(root, file)
                if is_code_file(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        formatted_entry = f"### File: {full_path}\n\n{content}"
                        combined_content.append(formatted_entry)
                        files_read += 1
                    except UnicodeDecodeError:
                        pass
                    except Exception:
                        pass
                        
    return files_read

def smart_search_and_combine(base_dir: str, targets: List[str]) -> str:
    """
    Searches base_dir for paths matching the targets and combines their content.
    """
    if not os.path.isdir(base_dir):
        return f"Error: Base path '{base_dir}' is not a valid directory."

    target_paths = set()
    found_targets_count = 0
    
    print(f"Scanning project root: {base_dir}")
    
    # 1. First, check if the target is an exact/relative path from the root
    for target in targets:
        # Check if the target is a full or relative path already
        full_target_path = os.path.join(base_dir, target.lstrip(os.sep))
        if os.path.exists(full_target_path):
            target_paths.add(full_target_path)
            found_targets_count += 1
            print(f"  🎯 Found exact path: {full_target_path}")

    # 2. Walk the directory to find partial name matches
    # Use a set to store unique paths to avoid processing the same file multiple times
    
    # Create a list of lowercased target keywords for substring matching
    target_keywords = [t.lower().replace(os.sep, '') for t in targets]
    
    for root, dirs, files in os.walk(base_dir):
        
        # Check folders (dirs) for matches
        for d in dirs:
            for keyword in target_keywords:
                # Matches folder name, e.g., 'lib/screens/auth' matches 'auth'
                if keyword and keyword in d.lower():
                    target_paths.add(os.path.join(root, d))
                    found_targets_count += 1
        
        # Check files for matches
        for f in files:
            full_path = os.path.join(root, f)
            for keyword in target_keywords:
                # Matches file name, e.g., 'login_screen.dart' matches 'login' or 'login_screen'
                if keyword and keyword in f.lower():
                    target_paths.add(full_path)
                    found_targets_count += 1
                    
    print(f"Found {len(target_paths)} unique files/folders matching {found_targets_count} keyword(s).")

    # 3. Read content from all unique found paths
    all_content: List[str] = []
    total_files_read = 0
    
    for path in target_paths:
        files_read = get_files_from_path(path, all_content)
        total_files_read += files_read
        if files_read > 0:
            print(f"  📖 Processed {files_read} file(s) from: {path}")

    print(f"\nTotal code files processed: {total_files_read}")
    
    return OUTPUT_SEPARATOR.join(all_content)

def main():
    """
    Sets up the command-line interface and executes the copy process.
    """
    parser = argparse.ArgumentParser(
        description="Reads code files using smart searching (partial names or full paths).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "base_directory",
        type=str,
        help="The path to the project root directory (e.g., './my_project' or '~/flutter_app')."
    )
    parser.add_argument(
        "targets",
        nargs='+',
        help="One or more file/folder names (full or partial) to search for.\n"
             "Examples:\n"
             "  'login_screen' (searches for files/folders containing 'login_screen')\n"
             "  'lib/auth' (searches for the exact folder/file path)"
    )
    
    args = parser.parse_args()

    # Get the combined content
    all_code_content = smart_search_and_combine(
        base_dir=args.base_directory,
        targets=args.targets
    )

    # Copy to clipboard
    if all_code_content.startswith("Error:"):
        print(f"\n❌ Operation failed: {all_code_content}")
    elif all_code_content:
        try:
            pyperclip.copy(all_code_content)
            # Count the files based on the separator used
            file_count = len(all_code_content.split(OUTPUT_SEPARATOR))
            print(f"\n✨ Success! Content of {file_count} file(s) has been copied to your clipboard.")
        except Exception as e:
            print(f"\n❌ Final Copy FAILED: {e}")
            print("The content was generated, but the clipboard operation failed.")
    else:
        print("\n⚠️ No readable files were found for the specified targets.")

if __name__ == "__main__":
    main()






    