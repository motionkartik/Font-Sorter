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
    Prefers en-US (langID 0x0409) if available, then falls back to other standards.
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

def sanitize_name(name, is_filename=False):
    """
    Removes characters that are invalid for directory or file names.
    """
    # Removes <>:"/\|?* and control characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip()
    
    # Additional check for filenames to avoid leading/trailing spaces/dots on Windows
    if is_filename:
        sanitized = sanitized.strip('. ')

    # Prevent creating names that are empty or just a dot
    return sanitized if sanitized and sanitized != "." else None


def load_keywords(filename="keywords.txt"):
    """
    Loads keywords from a text file located in the same directory as the script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(script_dir, filename)

    if not os.path.exists(keywords_path):
        print(f"Error: Keyword file '{filename}' not found.")
        print(f"Please create it in the same directory as the script: {script_dir}")
        sys.exit(1)
        
    with open(keywords_path, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
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

    rename_choice = input("Do you want to rename fonts based on their metadata? (y/n) ").lower()
    if rename_choice not in ['y', 'n']:
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
                "Timestamp", "Action", "OriginalFile", "NewFile", "Family", "Subfamily",
                "DestinationFolder", "FinalPath", "Details"
            ])
        except IOError as e:
            print(f"Error: Could not create log file. {e}")
            log_choice = 'n'
    
    font_files = []
    for root, _, files in os.walk(source_folder):
        # Prevent walking into the folders the script itself creates
        if os.path.basename(root) in ["00 TrueType Collection Fonts", "00 Skipped", "00 woff", "00 fon"]:
            continue
        for file in files:
            if file.lower().endswith(('.ttf', '.otf', '.ttc', '.woff', '.fon')) and not file.startswith('._'):
                font_files.append(os.path.join(root, file))

    total = len(font_files)
    if total == 0:
        print("No font files (.ttf, .otf, .ttc, .woff, .fon) found in the specified directory.")
        sys.exit(0)

    success_count = 0
    failure_count = 0
    skipped_count = 0
    
    ttc_folder = os.path.join(source_folder, "00 TrueType Collection Fonts")
    woff_folder = os.path.join(source_folder, "00 woff")
    fon_folder = os.path.join(source_folder, "00 fon")
    skipped_folder = os.path.join(source_folder, "00 Skipped")

    for i, font_path in enumerate(font_files, 1):
        original_font_name = os.path.basename(font_path)
        
        # Default values for loop variables
        action_verb = ""
        display_action = ""
        final_font_name = original_font_name
        dest_folder = ""
        final_path = ""
        log_family = ""
        log_subfamily = ""
        log_details = ""

        try:
            if choice == 'c': action_verb = "Copied"
            elif choice == 'm': action_verb = "Moved"
            
            # --- FOLDER AND FILENAME DETERMINATION ---
            if font_path.lower().endswith(".ttc"):
                dest_folder = ttc_folder
                log_family = "TTC Collection"
            elif font_path.lower().endswith(".woff"):
                dest_folder = woff_folder
                log_family = "WOFF Font"
            elif font_path.lower().endswith(".fon"):
                dest_folder = fon_folder
                log_family = "FON Font"
            else:
                with TTFont(font_path, lazy=True) as font:
                    family_name = get_font_name_property(font, 1) or os.path.splitext(original_font_name)[0]
                    subfamily_name = get_font_name_property(font, 2) or "Regular"
                    log_family = family_name
                    log_subfamily = subfamily_name

                    clean_family_for_folder = re.sub(r'[-_.]', ' ', family_name)
                    folder_name_base = re.sub(keyword_pattern, '', clean_family_for_folder, flags=re.IGNORECASE).strip()
                    folder_name_base = re.sub(r'\s{2,}', ' ', folder_name_base)
                    
                    folder_name = (folder_name_base or family_name).title()
                    folder_name = sanitize_name(folder_name) or os.path.splitext(original_font_name)[0]
                    dest_folder = os.path.join(source_folder, folder_name)

                    if rename_choice == 'y':
                        if subfamily_name.lower() in ['regular', 'normal', 'roman', 'plain'] or subfamily_name.lower() in family_name.lower():
                            new_base_name = family_name
                        else:
                            new_base_name = f"{family_name} {subfamily_name}"
                        
                        _, ext = os.path.splitext(original_font_name)
                        new_filename = f"{new_base_name}{ext}"
                        sanitized_filename = sanitize_name(new_filename, is_filename=True)
                        if sanitized_filename:
                            final_font_name = sanitized_filename
            
            # --- DUPLICATE HANDLING LOGIC ---
            ideal_target_path = os.path.join(dest_folder, final_font_name)

            if os.path.exists(ideal_target_path):
                # --- ACTION: SKIP (MOVE AND RENAME IN SKIPPED FOLDER) ---
                if not os.path.exists(skipped_folder):
                    os.makedirs(skipped_folder)
                
                # REVERTED: Determine final path in skipped folder using the ORIGINAL file name
                final_path = os.path.join(skipped_folder, original_font_name)
                counter = 1
                base, ext = os.path.splitext(final_path)
                while os.path.exists(final_path):
                    final_path = f"{base}_{counter}{ext}"
                    counter += 1
                
                shutil.move(font_path, final_path) # Always move duplicates
                skipped_count += 1
                display_action = "Skipped (Duplicate)"
                log_details = f"File already exists at: {ideal_target_path}"
                dest_folder = skipped_folder # Update for logging
                # REVERTED: Simplified print statement for skipped files
                print(f"[{i}/{total}] {display_action}: '{original_font_name}' moved to '{os.path.basename(skipped_folder)}' as target already exists.")

            else:
                # --- ACTION: COPY or MOVE ---
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                final_path = ideal_target_path
                if choice == 'c': shutil.copy2(font_path, final_path)
                elif choice == 'm': shutil.move(font_path, final_path)

                success_count += 1
                display_action = action_verb
                if rename_choice == 'y' and original_font_name != os.path.basename(final_path):
                    display_action += " & Renamed"
                print(f"[{i}/{total}] {display_action}: {original_font_name} → {os.path.basename(final_path)} in '{os.path.basename(dest_folder)}'")

        except Exception as e:
            failure_count += 1
            display_action = "Error"
            final_path = "" # No final path on error
            log_details = str(e)
            print(f"[{i}/{total}] Error processing {original_font_name}: {e}")

        # --- LOG TO CSV ---
        if log_choice == 'y':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_file_name_for_log = os.path.basename(final_path) if final_path else ""
            csv_writer.writerow([
                timestamp, display_action, original_font_name, new_file_name_for_log,
                log_family, log_subfamily, dest_folder, final_path, log_details
            ])
            
    print("\n--------------------")
    print("Processing Complete.")
    print(f"Total files scanned:    {total}")
    print(f"  Succeeded:            {success_count}")
    print(f"  Skipped (Duplicates): {skipped_count}")
    print(f"  Failed:               {failure_count}")

    if log_file:
        log_file.close()
        print(f"\nLog file saved at: {log_file_path}")

if __name__ == "__main__":
    main()

