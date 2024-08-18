import os
import logging
from PIL import Image
from pillow_heif import register_heif_opener
from sys import argv
import argparse
import shutil

logging.basicConfig(level=logging.INFO, format='%(message)s')

def convert_heic_to_jpg(heic_dir, output_quality=50):
  """
  Converts HEIC images in a directory to JPG format.

  Args:
      heic_dir (str): Path to the directory containing HEIC files.
      output_quality (int, optional): Quality of the output JPG images (1-100). Defaults to 50.
  """  
  register_heif_opener()
  if not os.path.isdir(heic_dir):
    logging.error(f"Directory '{heic_dir}' does not exist.")
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
  heic_files = [
      file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")
  ]
  total_files = len(heic_files)

  # Convert each HEIC file to JPG
  num_converted = 0
  for file_index, file_name in enumerate(heic_files, start=1):
    heic_path = os.path.join(heic_dir, file_name.upper())
    jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

    try:
      # Open HEIC file using Pillow with HEIC support
      with Image.open(heic_path) as image:
        # Save the image as JPG with specified quality
        image.save(jpg_path, "JPEG", quality=output_quality)
        num_converted += 1

      # Calculate and display the percentage progress
      progress = int((file_index / total_files) * 100)
      print(f"Conversion progress: {progress}%", end="\r", flush=True)
    except (FileNotFoundError, OSError) as e:
      logging.error(f"Error converting {file_name}: {str(e)}")

  print(f"\nConversion completed successfully. {num_converted} files converted.")

# Parse command line arguments
parser = argparse.ArgumentParser(description="Converts HEIC images to JPG format.",
                                 usage="%(prog)s [options] <heic_directory>",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("heic_dir", type=str, help="Path to the directory containing HEIC images.")
parser.add_argument("-q", "--quality", type=int, default=50, help="Output JPG image quality (1-100). Default is 50.")

parser.epilog = """
Example usage:
  %(prog)s /path/to/your/heic/images -q 90
"""

# If no arguments provided, print help message
try:
  args = parser.parse_args()
except SystemExit:
  print(parser.format_help())
  exit()

# Convert HEIC to JPG
convert_heic_to_jpg(args.heic_dir, args.quality)
