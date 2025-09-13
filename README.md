# Font Sorter

A Python script that organizes font files by family name, stripping style keywords and creating organized folder structures. This is a Python port of the original PowerShell font sorter.

## Features

- **Font Family Detection**: Automatically extracts font family names from TTF, OTF, and TTC files
- **Style Keyword Removal**: Strips common style keywords (Bold, Italic, Light, etc.) from family names
- **Folder Organization**: Creates folders based on cleaned family names
- **TTC Support**: Special handling for TrueType Collection files
- **Copy/Move Operations**: Choose to copy or move font files
- **CSV Logging**: Optional detailed logging of all operations
- **Interactive & Command Line**: Both interactive and command-line interfaces

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode
```bash
python font_sorter.py --interactive
```

### Command Line Mode
```bash
# Copy fonts and create log
python font_sorter.py "C:\Path\To\Fonts" --action copy --log

# Move fonts without logging
python font_sorter.py "C:\Path\To\Fonts" --action move
```

### Command Line Options
- `source`: Path to the fonts folder (required)
- `--action {copy,move}`: Action to perform (default: copy)
- `--log`: Create a CSV log file
- `--interactive`: Run in interactive mode

## How It Works

1. **Font Detection**: Scans the specified directory and subdirectories for TTF, OTF, and TTC files
2. **Family Extraction**: Uses fontTools to read font metadata and extract family names
3. **Name Cleaning**: 
   - Replaces separators (-, _, .) with spaces
   - Removes style keywords (Bold, Italic, Light, etc.)
   - Normalizes spacing and capitalization
4. **Folder Creation**: Creates folders based on cleaned family names
5. **File Organization**: Copies or moves fonts to appropriate folders
6. **TTC Handling**: Places all TrueType Collection files in a special "00 TrueType Collection Fonts" folder

## Style Keywords Removed

The script removes a comprehensive list of style keywords including:
- Weight terms: Hairline, Thin, Light, Regular, Medium, Bold, Black, Heavy, etc.
- Style terms: Italic, Oblique, Slanted, Cursive, Script, etc.
- Width terms: Compressed, Condensed, Extended, Wide, etc.
- And many more specialized terms

## Log File Format

When logging is enabled, a CSV file is created with the following columns:
- Timestamp
- Action (Copied/Moved/Error)
- FontFile
- Family (cleaned name)
- Subfamily
- DestinationFolder
- FinalPath

## Requirements

- Python 3.7+
- fonttools library

## License

This script is provided as-is for font organization purposes.

