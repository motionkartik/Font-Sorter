# Font Sorter

A Python script that automatically organizes your font collection by parsing font metadata and grouping fonts by their family names. The script intelligently removes style keywords (like "Bold", "Italic", "Regular") from font family names to create clean folder structures.

## Features

- **Automatic Font Organization**: Sorts fonts into folders based on their actual font family names
- **Keyword Filtering**: Removes common style keywords to prevent fragmented folder structures
- **Multiple Font Format Support**: Works with `.ttf`, `.otf`, and `.ttc` files
- **TrueType Collection Handling**: Special handling for `.ttc` files in a dedicated folder
- **Copy or Move Options**: Choose whether to copy or move your fonts during organization
- **CSV Logging**: Optional detailed logging of all operations performed
- **Duplicate Handling**: Automatically handles filename conflicts with smart renaming
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- `fonttools` library

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install required dependencies**:
   ```bash
   pip install fonttools
   ```

3. **Download the script** and save it as `font_sorter.py`

4. **Create a keywords file** (see [Keywords File](#keywords-file) section below)

## Usage

1. **Run the script**:
   ```bash
   python font_sorter.py
   ```

2. **Follow the prompts**:
   - Enter the full path to your fonts folder
   - Choose to copy (c) or move (m) the fonts
   - Optionally enable CSV logging (y/n)

3. **The script will**:
   - Scan all fonts in the specified directory and subdirectories
   - Create organized folders based on font family names
   - Move or copy fonts to their appropriate folders
   - Generate a log file if requested

## Keywords File

The script requires a `keywords.txt` file in the same directory to function properly. This file contains style keywords that should be removed from font family names during organization.

### Creating keywords.txt

Create a text file named `keywords.txt` in the same directory as the script, with one keyword per line:

```
Regular
Bold
Italic
Light
Medium
Heavy
Thin
Black
Condensed
Extended
Oblique
SemiBold
ExtraBold
UltraLight
DemiBold
```

### Why Keywords Matter

Without keyword filtering, a font family like "Helvetica" might be split into multiple folders:
- `Helvetica Bold`
- `Helvetica Italic` 
- `Helvetica Regular`
- `Helvetica Light`

With proper keywords, all variants are organized under a single `Helvetica` folder.

## Example Output Structure

**Before organizing**:
```
Fonts/
├── HelveticaBold.ttf
├── HelveticaItalic.ttf
├── ArialRegular.ttf
├── Arial-Bold.otf
└── TimesNewRoman.ttc
```

**After organizing**:
```
Fonts/
├── 00 TrueType Collection Fonts/
│   └── TimesNewRoman.ttc
├── Helvetica/
│   ├── HelveticaBold.ttf
│   └── HelveticaItalic.ttf
└── Arial/
    ├── ArialRegular.ttf
    └── Arial-Bold.otf
```

## CSV Log Format

When logging is enabled, the script creates `FontSortLog.csv` with the following columns:

| Column | Description |
|--------|-------------|
| Timestamp | Date and time of operation |
| Action | Copied, Moved, or Error |
| FontFile | Original filename |
| Family | Extracted font family name |
| Subfamily | Font style (Bold, Italic, etc.) |
| DestinationFolder | Target folder path |
| FinalPath | Complete path to final location |

## Error Handling

The script handles various error conditions gracefully:

- **Missing fonttools**: Clear installation instructions
- **Invalid paths**: Path validation before processing
- **Corrupted fonts**: Continues processing other fonts
- **File conflicts**: Automatic renaming with numeric suffixes
- **Permission errors**: Detailed error messages
- **Invalid folder names**: Automatic sanitization of folder names

## Advanced Features

### Duplicate File Handling
If a font file already exists in the destination, the script automatically appends a number:
- `Arial.ttf` → `Arial.ttf`
- `Arial.ttf` → `Arial_1.ttf` (if first already exists)

### TrueType Collections
`.ttc` files are automatically placed in a special `00 TrueType Collection Fonts` folder to keep them separate from individual font files.

### Font Metadata Priority
The script prioritizes font name extraction in this order:
1. Windows en-US (English) names
2. General Windows names  
3. Mac Roman names
4. Any other available names

## Troubleshooting

### Common Issues

**"fonttools not installed"**
```bash
pip install fonttools
```

**"Keywords file not found"**  
Create `keywords.txt` in the same directory as the script.

**"Permission denied"**  
Run with administrator/sudo privileges or choose a different destination folder.

**"No fonts found"**  
Ensure your folder contains `.ttf`, `.otf`, or `.ttc` files and the path is correct.

### Safety Tips

- **Always backup your fonts** before running the script
- **Test with a small folder first** to understand the organization pattern
- **Use copy mode initially** to verify results before switching to move mode
- **Keep the CSV log** for record-keeping and troubleshooting

## Contributing

Feel free to submit issues, feature requests, or improvements. Common enhancement areas:

- Additional font format support
- Custom organization patterns
- GUI interface
- Batch processing features
- Integration with font management software

## License

This script is provided as-is for personal and educational use. Please respect font licensing when organizing commercial font collections.