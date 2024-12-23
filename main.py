import os
import logging
import argparse
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

logging.basicConfig(level=logging.INFO, format='%(message)s')

def convert_single_file(heic_path, jpg_path, output_quality) -> tuple:
    """
    Convert a single HEIC file to JPG format.
    
    #### Args:
        - heic_path (str): Path to the HEIC file.
        - jpg_path (str): Path to save the converted JPG file.
        - output_quality (int): Quality of the output JPG image.

    #### Returns:
        - tuple: Path to the HEIC file and conversion status.
    """
    try:
        with Image.open(heic_path) as image:
            # Automatically handle and preserve EXIF metadata
            exif_data = image.info.get("exif")
            image.save(jpg_path, "JPEG", quality=output_quality, exif=exif_data)
            # Preserve the original access and modification timestamps
            heic_stat = os.stat(heic_path)
            os.utime(jpg_path, (heic_stat.st_atime, heic_stat.st_mtime))
            return heic_path, True  # Successful conversion
    except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
        logging.error("Error converting '%s': %s", heic_path, e)
        return heic_path, False  # Failed conversion

def convert_heic_to_jpg(heic_dir, output_quality=50, max_workers=4) -> None:
    """
    Converts HEIC images in a directory to JPG format using parallel processing.

    #### Args:
        - heic_dir (str): Path to the directory containing HEIC files.
        - output_quality (int, optional): Quality of the output JPG images (1-100). Defaults to 50.
        - max_workers (int, optional): Number of parallel threads. Defaults to 4.
    """
    register_heif_opener()

    if not os.path.isdir(heic_dir):
        logging.error("Directory '%s' does not exist.", heic_dir)
        return

    # Create a directory to store the converted JPG files
    jpg_dir = os.path.join(heic_dir, "ConvertedFiles")
    if os.path.exists(jpg_dir):
        user_input = input("Existing 'ConvertedFiles' folder detected. Delete and proceed? (y/n): ")
        if user_input.lower() != 'y':
            print("Conversion aborted.")
            return
        else:
            shutil.rmtree(jpg_dir)
    os.makedirs(jpg_dir, exist_ok=True)

    # Get all HEIC files in the specified directory
    heic_files = [file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")]
    total_files = len(heic_files)

    if total_files == 0:
        logging.info("No HEIC files found in the directory.")
        return

    # Prepare file paths for conversion
    tasks = []
    for file_name in heic_files:
        heic_path = os.path.join(heic_dir, file_name)
        jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

        # Skip conversion if the JPG already exists
        if os.path.exists(jpg_path):
            logging.info("Skipping '%s' as the JPG already exists.", file_name)
            continue

        tasks.append((heic_path, jpg_path))

    # Convert HEIC files to JPG in parallel using ThreadPoolExecutor
    num_converted = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_single_file, heic_path, jpg_path, output_quality): heic_path
            for heic_path, jpg_path in tasks
        }

        for future in as_completed(future_to_file):
            heic_file = future_to_file[future]
            try:
                _, success = future.result()
                if success:
                    num_converted += 1
                # Display progress
                progress = int((num_converted / total_files) * 100)
                print(f"Conversion progress: {progress}%", end="\r", flush=True)
            except Exception as e:
                logging.error("Error occurred during conversion of '%s': %s", heic_file, e)

    print(f"\nConversion completed successfully. {num_converted} files converted.")

# Parse command line arguments
parser = argparse.ArgumentParser(description="Converts HEIC images to JPG format.",
                                 usage="%(prog)s [options] <heic_directory>",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("heic_dir", type=str, help="Path to the directory containing HEIC images.")
parser.add_argument("-q", "--quality", type=int, default=50, help="Output JPG image quality (1-100). Default is 50.")
parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel workers for conversion.")

parser.epilog = """
Example usage:
  %(prog)s /path/to/your/heic/images -q 90 -w 8
"""

# If no arguments provided, print help message
try:
    args = parser.parse_args()
except SystemExit:
    print(parser.format_help())
    exit()

# Convert HEIC to JPG with parallel processing
convert_heic_to_jpg(args.heic_dir, args.quality, args.workers)
