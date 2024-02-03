import os
import logging
import pyheif
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(message)s')

def convert_heic_to_jpg(heic_dir):
    if not os.path.isdir(heic_dir):
        logging.error(f"Directory '{heic_dir}' does not exist.")
        return

    # Create a directory to store the converted JPG files
    jpg_dir = os.path.join(heic_dir, "ConvertedFiles")
    os.makedirs(jpg_dir, exist_ok=True)

    # Get all HEIC files in the specified directory
    heic_files = [
        file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")
    ]
    total_files = len(heic_files)

    # Convert each HEIC file to JPG
    num_converted = 0
    for file_index, file_name in enumerate(heic_files, start=1):
        heic_path = os.path.join(heic_dir, file_name)
        jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

        try:
            # Open the HEIC file using pyheif
            with open(heic_path, "rb") as heic_file:
                heif_file = pyheif.read(heic_file)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )

            # Save the image as JPG
            with open(jpg_path, "wb") as jpg_file:
                image.save(jpg_file, "JPEG", quality=100)
                num_converted += 1

            # Calculate and display the percentage progress
            progress = int((file_index / total_files) * 100)
            print(f"Conversion progress: {progress}%", end="\r", flush=True)
        except Exception as e:
            logging.error(f"Error converting {file_name}: {str(e)}")

    print(f"\nConversion completed successfully. {num_converted} files converted.")

# Provide the directory path containing the HEIC files
heic_directory = "/path/to/heic"

# Convert HEIC to JPG
convert_heic_to_jpg(heic_directory)
