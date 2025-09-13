import os
import sys
import re
import shutil
import csv
from datetime import datetime

# You must install fonttools for this script to work:
# pip install fonttools
try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("Error: The 'fonttools' library is not installed.")
    print("Please install it by running: pip install fonttools")
    sys.exit(1)

def get_font_name_property(font, name_id):
    """
    Extracts a specific name property (like Family or Subfamily) from a font's 'name' table.
    Prefers en-US (langID 0x0409) if available, then falls back to standard priority.
    Symbol-only names are preserved.
    """
    name_records = font['name'].names
    en_us_name = None
    windows_name = None
    mac_name = None
    other_name = None

    for record in name_records:
        if record.nameID == name_id:
            try:
                text = record.toUnicode()
            except UnicodeDecodeError:
                continue

            # 1. Highest priority → Windows, en-US (langID 0x0409)
            if record.platformID == 3 and record.langID == 0x0409:
                en_us_name = text
            # 2. General Windows fallback
            elif record.platformID == 3 and record.platEncID == 1:
                windows_name = text
            # 3. Mac Roman fallback
            elif record.platformID == 1 and record.platEncID == 0:
                mac_name = text
            # 4. Anything else (last resort)
            elif other_name is None:
                other_name = text

    return en_us_name or windows_name or mac_name or other_name

def sanitize_foldername(name):
    """
    Removes characters that are invalid for directory names on most operating systems.
    """
    # Removes <>:"/\|?* and control characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip()
    # Prevent creating folders with just a dot or empty names
    return sanitized if sanitized and sanitized != "." else None


def load_keywords(filename="keywords.txt"):
    """
    Loads keywords from a text file located in the same directory as the script.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(script_dir, filename)

    if not os.path.exists(keywords_path):
        print(f"Error: Keyword file '{filename}' not found.")
        print(f"Please create it in the same directory as the script: {script_dir}")
        sys.exit(1)
        
    with open(keywords_path, 'r', encoding='utf-8') as f:
        # Read all non-empty lines and strip whitespace
        keywords = [line.strip() for line in f if line.strip()]
    
    # Sort keywords by length descending to match longer phrases first
    keywords.sort(key=len, reverse=True)
    return keywords

def main():
    """
    Main function to run the font sorting script.
    """
    style_keywords = load_keywords()
    keyword_pattern = r'\b(' + '|'.join(re.escape(k) for k in style_keywords) + r')\b'
    
    source_folder = input("Enter the full path to your fonts folder: ")

    if not os.path.isdir(source_folder):
        print("Error: Path does not exist. Exiting.")
        sys.exit(1)

    choice = input("Do you want to (c)opy or (m)ove the fonts? ").lower()
    if choice not in ['c', 'm']:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    log_file_path = None
    csv_writer = None
    log_file = None
    log_choice = input("Do you want to create a CSV log? (y/n) ").lower()
    if log_choice == 'y':
        log_file_path = os.path.join(source_folder, "FontSortLog.csv")
        try:
            log_file = open(log_file_path, 'w', newline='', encoding='utf-8')
            csv_writer = csv.writer(log_file)
            csv_writer.writerow([
                "Timestamp", "Action", "FontFile", "Family", "Subfamily",
                "DestinationFolder", "FinalPath"
            ])
        except IOError as e:
            print(f"Error: Could not create log file. {e}")
            log_choice = 'n'
    
    font_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.ttf', '.otf', '.ttc')) and not file.startswith('._'):
                font_files.append(os.path.join(root, file))

    total = len(font_files)
    if total == 0:
        print("No font files (.ttf, .otf, .ttc) found in the specified directory.")
        sys.exit(0)

    # --- Initialize counters ---
    success_count = 0
    failure_count = 0
    
    ttc_folder = os.path.join(source_folder, "00 TrueType Collection Fonts")
    if not os.path.exists(ttc_folder):
        os.makedirs(ttc_folder)

    for i, font_path in enumerate(font_files, 1):
        font_name = os.path.basename(font_path)
        action = "Skipped"
        try:
            if font_path.lower().endswith(".ttc"):
                dest_folder = ttc_folder
                target_path = os.path.join(dest_folder, font_name)

                counter = 1
                base, ext = os.path.splitext(target_path)
                while os.path.exists(target_path):
                    target_path = f"{base}_{counter}{ext}"
                    counter += 1
                
                if choice == 'c':
                    shutil.copy2(font_path, target_path)
                    action = "Copied"
                elif choice == 'm':
                    shutil.move(font_path, target_path)
                    action = "Moved"
                
                print(f"[{i}/{total}] {action} TTC {font_name} → 00 TrueType Collection Fonts")
                if log_choice == 'y':
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([timestamp, action, font_name, "TTC Collection", "", dest_folder, target_path])
                success_count += 1
                continue

            with TTFont(font_path, lazy=True) as font:
                raw_family = get_font_name_property(font, 1) or os.path.splitext(font_name)[0]
                subfamily = get_font_name_property(font, 2) or "Unknown"

            clean_family = re.sub(r'[-_.]', ' ', raw_family)
            family = re.sub(keyword_pattern, '', clean_family, flags=re.IGNORECASE)
            family = re.sub(r'\s{2,}', ' ', family).strip()

            if not family:
                family = raw_family.strip()
            
            family = family.title()
            
            # --- NEW: Sanitize the final folder name ---
            family = sanitize_foldername(family)
            # If sanitizing results in an empty name, fall back to the font's filename
            if not family:
                family = os.path.splitext(font_name)[0]

            dest_folder = os.path.join(source_folder, family)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            target_path = os.path.join(dest_folder, font_name)

            counter = 1
            base, ext = os.path.splitext(target_path)
            while os.path.exists(target_path):
                target_path = f"{base}_{counter}{ext}"
                counter += 1

            if choice == 'c':
                shutil.copy2(font_path, target_path)
                action = "Copied"
            elif choice == 'm':
                shutil.move(font_path, target_path)
                action = "Moved"
            
            print(f"[{i}/{total}] {action} {font_name} → {family} ({subfamily})")
            if log_choice == 'y':
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([timestamp, action, font_name, family, subfamily, dest_folder, target_path])
            
            success_count += 1

        except Exception as e:
            failure_count += 1
            print(f"[{i}/{total}] Error: Could not process {font_name} - {e}")
            if log_choice == 'y':
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([timestamp, "Error", font_name, "", "", "", str(e)])
    
    # --- NEW: Updated final summary ---
    print("\n--------------------")
    print("Processing Complete.")
    print(f"Total files scanned: {total}")
    print(f"  Succeeded: {success_count}")
    print(f"  Failed:    {failure_count}")

    if log_file:
        log_file.close()
        print(f"\nLog file saved at: {log_file_path}")

if __name__ == "__main__":
    main()