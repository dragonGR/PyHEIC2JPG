import os
import pyheif
from PIL import Image


def convert_heic_to_jpg(heic_dir):
    # Create a directory to store the converted JPG files
    jpg_dir = os.path.join(heic_dir, "ConvertedFiles")
    os.makedirs(jpg_dir, exist_ok=True)

    # Get all HEIC files in the specified directory
    heic_files = [
        file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")
    ]

    # Convert each HEIC file to JPG
    for file_name in heic_files:
        heic_path = os.path.join(heic_dir, file_name)
        jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

        try:
            # Open the HEIC file using pyheif
            heif_file = pyheif.read(heic_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )

            # Save the image as JPG
            image.save(jpg_path, "JPEG", quality=100)
            print(f"Converted: {file_name}")
        except Exception as e:
            print(f"Error converting {file_name}: {str(e)}")

    print("Conversion completed successfully.")


# Provide the directory path containing the HEIC files
heic_directory = "/path/to/heic"

# Convert HEIC to JPG
convert_heic_to_jpg(heic_directory)
