# HEIC to JPG Converter

This Python script efficiently converts HEIC (High-Efficiency Image Format) files to JPG format, offering enhanced features and user experience.

## Key Improvements
- Command-Line Interface (CLI): Interact with the script directly using command-line arguments for easier execution and fine-tuning.
- Optimized Image Processing: Leverages the ``pillow-heif`` library for efficient HEIC processing.
- Improved Error Handling: More robust error management ensures smoother execution.
- Progress Tracking: Track the conversion progress for large file sets.
- Enhanced Folder Management: Confirms user intent before potentially overwriting existing output directories.

## What This Code Does ?

This script allows you to seamlessly convert multiple HEIC files into JPG format with granular control.

- Automated Output Directory: Creates a dedicated folder named "ConvertedFiles" within the HEIC directory to store the converted JPGs.
- Quality Control: Specify the desired JPG image quality using the `-q` or `--quality` argument when running the script.

## Installation

1. Install the required dependency: `pip install pillow-heif`
2. Run the Script:
```bash
python heic_to_jpg.py <path/to/your/heic/directory>  # Replace with actual path
python heic_to_jpg.py -q 90 <path/to/your/heic/directory>  # Set JPG quality (1-100)
```

## Features

- User-friendly CLI for efficient conversion.
- Optimized HEIC processing for faster performance.
- Robust error handling for a smooth user experience.
- Informative progress tracking.
- Flexible output directory management.
- Quality control for JPG output.

This script provides a versatile and efficient solution for converting HEIC images to JPG format.

Feel free to customize the script further based on your specific needs!
