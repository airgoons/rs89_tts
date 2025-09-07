"""This script extracts NATO symbology templates from the Red_Strike_V1_2.vmod archive and packages them for future manual processing"""
import os
import hashlib
import shutil
import zipfile
import unit_data_entry

from PIL import Image
import numpy as np

def extract_roi(src_dir, dst_dir, x1, y1, x2, y2):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for filename in os.listdir(src_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            src_path = os.path.join(src_dir, filename)
            dst_path = os.path.join(dst_dir, filename)
            try:
                img = Image.open(src_path).convert('RGB')
                cropped = img.crop((x1, y1, x2, y2))
                cropped.save(dst_path)
            except Exception as e:
                continue

def copy_unique_images(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    
    hashes = set()
    for filename in os.listdir(src_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(src_dir, filename)
            try:
                img = Image.open(path).convert("RGB")
                arr = np.array(img)
                img_bytes = arr.tobytes()
                img_hash = hashlib.sha256(img_bytes).hexdigest()
                if img_hash not in hashes:
                    hashes.add(img_hash)
                    dst_path = os.path.join(dst_dir, filename)
                    img.save(dst_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    zipfiles = [
        "Red_Strike_V1_2.vmod",
    ]

    for zf in zipfiles:
        if not os.path.exists(zf):
            raise FileNotFoundError(f"{zf} not found in the current directory.")
        else:
            with zipfile.ZipFile(zf, "r") as zip_ref:
                zip_ref.extractall(os.path.splitext(zf)[0])

    if os.path.exists("./unsorted_templates"):
        shutil.rmtree("./unsorted_templates")
    if os.path.exists("./unsorted_templates.zip"):
        os.remove("./unsorted_templates.zip")

    os.mkdir("./unsorted_templates")
    os.mkdir("./unsorted_templates/unit_type_templates")
    os.mkdir("./unsorted_templates/unit_type_templates/unsorted")
    os.mkdir("./unsorted_templates/unit_formation_templates")
    os.mkdir("./unsorted_templates/unit_formation_templates/unsorted")
    
    for size in unit_data_entry.UnitType:
        os.mkdir(os.path.join("./unsorted_templates/unit_type_templates", size))

    for formation in unit_data_entry.UnitFormation:
        os.mkdir(os.path.join("./unsorted_templates/unit_formation_templates", formation)) 

    extract_roi("Red_Strike_V1_2/images", "extract_formation_templates", 90, 39, 131, 51)
    copy_unique_images("extract_formation_templates", "./unsorted_templates/unit_formation_templates/unsorted")
    extract_roi("Red_Strike_V1_2/images", "extract_type_templates", 90, 51, 131, 72)
    copy_unique_images("extract_type_templates", "./unsorted_templates/unit_type_templates/unsorted")

    archive_path = shutil.make_archive("unsorted_templates", "zip", "unsorted_templates")

    shutil.rmtree("Red_Strike_V1_2")
    shutil.rmtree("extract_formation_templates")
    shutil.rmtree("extract_type_templates")
    shutil.rmtree("unsorted_templates")
