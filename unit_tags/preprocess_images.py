import os
import zipfile
import shutil

from PIL import Image
import numpy as np

def crop_and_convert_images(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for filename in os.listdir(src_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            src_path = os.path.join(src_dir, filename)
            dst_path = os.path.join(dst_dir, filename)
            try:
                img = Image.open(src_path).convert('RGB')
                cropped = img.crop((90, 39, 131, 72))  # crop to NATO symbol location
                cropped.save(dst_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

if __name__ == "__main__":
    if not os.path.exists("Red_Strike_V1_2.vmod"):
        raise FileNotFoundError("Red_Strike_V1_2.vmod not found in the current directory.")
    else:
        with zipfile.ZipFile("Red_Strike_V1_2.vmod", "r") as zip_ref:
            zip_ref.extractall("Red_Strike_V1_2")

    crop_and_convert_images("Red_Strike_V1_2/images", "input_images")

    shutil.make_archive("input_images", "zip", "input_images")

    shutil.rmtree("Red_Strike_V1_2")
    shutil.rmtree("input_images")
