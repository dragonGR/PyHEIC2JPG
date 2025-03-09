# HEIC to JPG Converter

This Python script efficiently converts HEIC/HEIF (High-Efficiency Image Format) files to JPG format, featuring parallel processing for faster conversions, enhanced user experience, and automatic preservation of EXIF metadata.

## Key Features

- **Parallel Processing**: Utilizes `ThreadPoolExecutor` for concurrent conversion of HEIC files, improving the speed of batch conversions.
- **Command-Line Interface (CLI)**: Interact with the script directly using command-line arguments for easier execution and fine-tuning.
- **Recursive Directory Support**: Search and convert HEIC files in subdirectories with a single command.
- **Custom Output Directory**: Specify a custom location for your converted files.
- **Resize Option**: Automatically resize images during conversion.
- **Delete Originals**: Option to automatically remove original HEIC files after successful conversion.
- **Optimized Image Processing**: Leverages the `pillow-heif` library for efficient HEIC processing.
- **Improved Error Handling**: More robust error management ensures smoother execution.
- **Progress Tracking**: Track the conversion progress for large file sets.
- **Enhanced Folder Management**: Confirms user intent before potentially overwriting existing output directories.
- **Quality Control**: Customize the output JPG quality (1-100) with a simple command-line option.
- **EXIF Metadata Preservation**: Retains important metadata such as camera details, timestamps, and location information in the converted JPG files.

## What This Code Does

This script allows you to seamlessly convert multiple HEIC/HEIF files into JPG format with control over the quality, parallel processing options, and more advanced features.

- **Automated Output Directory**: Creates a dedicated folder (default: "ConvertedFiles") to store the converted JPGs.
- **Parallel Conversion**: Process multiple files simultaneously by specifying the number of workers.
- **Directory Structure Preservation**: Maintains folder hierarchy when using recursive mode.
- **Quality Control**: Specify the desired JPG image quality.
- **EXIF Metadata Preservation**: Automatically extracts and includes metadata from HEIC files into the output JPGs.
- **Error Handling**: Skips individual files that encounter errors without halting the entire process.
- **Performance Statistics**: Provides detailed information about conversion times and success rates.

## Installation

1. Install the required dependencies:
```bash
pip install pillow pillow-heif
```

2. Run the Script:
```bash
python main.py <path/to/your/heic/directory>
```

## Usage Examples

### Basic usage:
```bash
python main.py /path/to/your/heic/directory
```

### Set JPG quality (1-100):
```bash
python main.py -q 90 /path/to/your/heic/directory
```

### Set the number of parallel workers:
```bash
python main.py -w 8 /path/to/your/heic/directory
```

### Process files recursively in subdirectories:
```bash
python main.py -r /path/to/your/heic/directory
```

### Resize images during conversion:
```bash
python main.py --resize 1920x1080 /path/to/your/heic/directory
```

### Specify a custom output directory:
```bash
python main.py -o /custom/output/path /path/to/your/heic/directory
```

### Delete original HEIC files after conversion:
```bash
python main.py -d /path/to/your/heic/directory
```

### Combine multiple options:
```bash
python main.py -q 90 -w 8 -r --resize 1920x1080 -o /custom/output/path /path/to/your/heic/directory
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `-q, --quality` | Output JPG image quality (1-100). Default is 90. |
| `-w, --workers` | Number of parallel workers for conversion. Default is 4. |
| `-o, --output` | Custom output directory. Default is 'ConvertedFiles' in the source directory. |
| `-r, --recursive` | Search for HEIC files in subdirectories. |
| `--resize` | Resize images (format: WIDTHxHEIGHT, e.g., 1920x1080) |
| `-d, --delete-originals` | Delete original HEIC files after successful conversion. |
| `-v, --verbose` | Enable verbose logging. |

This script provides a highly efficient and flexible solution for converting HEIC images to JPG format, making it ideal for both small and large-scale conversions.