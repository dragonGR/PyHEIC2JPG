import os
import logging
import argparse
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def convert_single_file(heic_path: str, jpg_path: str, output_quality: int, resize: Optional[Tuple[int, int]] = None) -> Tuple[str, bool, float]:
    """
    Convert a single HEIC file to JPG format with optional resizing.
    
    #### Args:
        - heic_path (str): Path to the HEIC file.
        - jpg_path (str): Path to save the converted JPG file.
        - output_quality (int): Quality of the output JPG image.
        - resize (tuple, optional): Width and height to resize the image to.

    #### Returns:
        - tuple: Path to the HEIC file, conversion status, and processing time.
    """
    start_time = time.time()
    try:
        with Image.open(heic_path) as image:
            # Resize image if specified
            if resize:
                image = image.resize(resize, Image.LANCZOS)
            
            # Automatically handle and preserve EXIF metadata
            exif_data = image.info.get("exif")
            image.save(jpg_path, "JPEG", quality=output_quality, exif=exif_data, optimize=True)
            
            # Preserve the original access and modification timestamps
            heic_stat = os.stat(heic_path)
            os.utime(jpg_path, (heic_stat.st_atime, heic_stat.st_mtime))
            
            processing_time = time.time() - start_time
            return heic_path, True, processing_time  # Successful conversion
    except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
        logger.error("Error converting '%s': %s", heic_path, e)
        processing_time = time.time() - start_time
        return heic_path, False, processing_time  # Failed conversion

def find_heic_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Find all HEIC files in the specified directory.
    
    #### Args:
        - directory (str): Path to search for HEIC files.
        - recursive (bool): Whether to search subdirectories.
        
    #### Returns:
        - list: List of paths to HEIC files.
    """
    heic_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.heic', '.heif')):
                    heic_files.append(os.path.join(root, file))
    else:
        heic_files = [
            os.path.join(directory, file) 
            for file in os.listdir(directory) 
            if file.lower().endswith(('.heic', '.heif'))
        ]
    
    return heic_files

def convert_heic_to_jpg(
    heic_dir: str, 
    output_quality: int = 90, 
    max_workers: int = 4,
    output_dir: Optional[str] = None,
    recursive: bool = False,
    resize: Optional[Tuple[int, int]] = None,
    delete_originals: bool = False
) -> Dict:
    """
    Converts HEIC images in a directory to JPG format using parallel processing.

    #### Args:
        - heic_dir (str): Path to the directory containing HEIC files.
        - output_quality (int, optional): Quality of the output JPG images (1-100). Defaults to 90.
        - max_workers (int, optional): Number of parallel threads. Defaults to 4.
        - output_dir (str, optional): Custom output directory. If None, uses 'ConvertedFiles' subdirectory.
        - recursive (bool, optional): Search for HEIC files in subdirectories. Defaults to False.
        - resize (tuple, optional): Width and height to resize images to. Defaults to None (no resize).
        - delete_originals (bool, optional): Whether to delete original HEIC files after conversion. Defaults to False.
        
    #### Returns:
        - dict: Statistics about the conversion process.
    """
    start_time = time.time()
    register_heif_opener()

    if not os.path.isdir(heic_dir):
        logger.error("Directory '%s' does not exist.", heic_dir)
        return {"status": "error", "message": f"Directory '{heic_dir}' does not exist."}

    # Define output directory
    if output_dir is None:
        jpg_dir = os.path.join(heic_dir, "ConvertedFiles")
    else:
        jpg_dir = output_dir
        
    # Create output directory if it doesn't exist
    if os.path.exists(jpg_dir):
        user_input = input(f"Existing output folder '{jpg_dir}' detected. Delete and proceed? (y/n): ")
        if user_input.lower() != 'y':
            print("Conversion aborted.")
            return {"status": "aborted", "message": "User aborted conversion."}
        else:
            shutil.rmtree(jpg_dir)
    
    os.makedirs(jpg_dir, exist_ok=True)

    # Get all HEIC files in the specified directory
    heic_files = find_heic_files(heic_dir, recursive=recursive)
    total_files = len(heic_files)

    if total_files == 0:
        logger.info("No HEIC files found in the directory.")
        return {"status": "completed", "files_converted": 0, "message": "No HEIC files found."}

    # Prepare file paths for conversion
    tasks = []
    for heic_path in heic_files:
        # Determine relative path to maintain directory structure in output
        if recursive:
            rel_path = os.path.relpath(heic_path, heic_dir)
            jpg_path = os.path.join(jpg_dir, os.path.splitext(rel_path)[0] + ".jpg")
            # Create intermediate directories if they don't exist
            os.makedirs(os.path.dirname(jpg_path), exist_ok=True)
        else:
            file_name = os.path.basename(heic_path)
            jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

        # Skip conversion if the JPG already exists
        if os.path.exists(jpg_path):
            logger.info("Skipping '%s' as the JPG already exists.", os.path.basename(heic_path))
            continue

        tasks.append((heic_path, jpg_path))

    # Convert HEIC files to JPG in parallel using ThreadPoolExecutor
    num_converted = 0
    failed_files = []
    total_processing_time = 0.0
    
    if not tasks:
        logger.info("No new files to convert.")
        return {"status": "completed", "files_converted": 0, "message": "No new files to convert."}
    
    print(f"Converting {len(tasks)} HEIC files to JPG...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_single_file, heic_path, jpg_path, output_quality, resize): heic_path
            for heic_path, jpg_path in tasks
        }

        for future in as_completed(future_to_file):
            heic_file = future_to_file[future]
            try:
                heic_path, success, proc_time = future.result()
                total_processing_time += proc_time
                
                if success:
                    num_converted += 1
                    # Delete original if requested
                    if delete_originals:
                        os.remove(heic_path)
                else:
                    failed_files.append(os.path.basename(heic_path))
                
                # Display progress
                progress = int((num_converted / len(tasks)) * 100)
                print(f"Conversion progress: {progress}% ({num_converted}/{len(tasks)})", end="\r", flush=True)
            except Exception as e:
                logger.error("Error occurred during conversion of '%s': %s", heic_file, e)
                failed_files.append(os.path.basename(heic_file))

    total_time = time.time() - start_time
    avg_time_per_file = total_processing_time / len(tasks) if tasks else 0
    
    # Print summary
    print(f"\nConversion completed in {total_time:.2f} seconds.")
    print(f"Successfully converted: {num_converted}/{len(tasks)} files.")
    if failed_files:
        print(f"Failed to convert {len(failed_files)} files.")
        
    return {
        "status": "completed",
        "files_converted": num_converted,
        "files_failed": len(failed_files),
        "total_time": total_time,
        "avg_time_per_file": avg_time_per_file,
        "failed_files": failed_files
    }

def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description="Converts HEIC/HEIF images to JPG format.",
        usage="%(prog)s [options] <heic_directory>",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("heic_dir", type=str, help="Path to the directory containing HEIC images.")
    parser.add_argument("-q", "--quality", type=int, default=90, 
                        help="Output JPG image quality (1-100). Default is 90.")
    parser.add_argument("-w", "--workers", type=int, default=4, 
                        help="Number of parallel workers for conversion. Default is 4.")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Custom output directory. Default is 'ConvertedFiles' in the source directory.")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Search for HEIC files in subdirectories.")
    parser.add_argument("--resize", type=str, default=None,
                        help="Resize images (format: WIDTHxHEIGHT, e.g., 1920x1080)")
    parser.add_argument("-d", "--delete-originals", action="store_true",
                        help="Delete original HEIC files after successful conversion.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging.")

    parser.epilog = """
Example usage:
  %(prog)s /path/to/your/heic/images -q 90 -w 8
  %(prog)s /path/to/your/heic/images --resize 1920x1080 -o /custom/output/path
"""

    # If no arguments provided, print help message
    try:
        args = parser.parse_args()
    except SystemExit:
        print(parser.format_help())
        exit()

    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Parse resize option if provided
    resize = None
    if args.resize:
        try:
            width, height = map(int, args.resize.lower().split('x'))
            resize = (width, height)
        except ValueError:
            logger.error("Invalid resize format. Use WIDTHxHEIGHT (e.g., 1920x1080).")
            exit(1)
    
    # Convert HEIC to JPG with parallel processing
    result = convert_heic_to_jpg(
        args.heic_dir, 
        args.quality, 
        args.workers,
        args.output,
        args.recursive,
        resize,
        args.delete_originals
    )
    
    if result["status"] == "error":
        print(f"Error: {result['message']}")
        return 1
    elif result["status"] == "aborted":
        print(f"Aborted: {result['message']}")
        return 0
    
    return 0

if __name__ == "__main__":
    exit(main())