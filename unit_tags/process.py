"""This script uses manually processed templates to identify unit types and formations in input images."""

import os
import cv2
from unit_data_entry import UnitDataEntry, UnitType, UnitFormation, SpecialCases
import json
import zipfile
import shutil


def load_templates(template_dir, enum_cls):
    templates = {}
    for entry in enum_cls:
        entry_dir = os.path.join(template_dir, entry.value)
        entry_templates = []
        if os.path.isdir(entry_dir):
            for fname in os.listdir(entry_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    path = os.path.join(entry_dir, fname)
                    img = cv2.imread(path, cv2.IMREAD_COLOR)
                    if img is not None:
                        entry_templates.append(img)
        else:
            # Fallback to single file
            path = os.path.join(template_dir, f"{entry.value}.png")
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_COLOR)
                if img is not None:
                    entry_templates.append(img)
        templates[entry] = entry_templates
    return templates

def match_template(image, templates, threshold=0.7):
    best_match = None
    best_score = 0.0
    for entry, template_list in templates.items():
        for template in template_list:
            if template is None:
                continue
            # Resize template to match image size if needed
            if template.shape != image.shape:
                template_resized = cv2.resize(template, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_AREA)
            else:
                template_resized = template
            res = cv2.matchTemplate(image, template_resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > best_score and max_val > threshold:
                best_score = max_val
                best_match = entry
    return best_match

import asyncio

async def process_single_image(filename, image_dir, type_templates, formation_templates):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return None
    path = os.path.join(image_dir, filename)
    img = await asyncio.to_thread(cv2.imread, path, cv2.IMREAD_COLOR)
    if img is None:
        return None
    roi_formation = img[0:12, 0:41]
    unit_formation = await asyncio.to_thread(match_template, roi_formation, formation_templates)
    roi_type = img[12:33, 0:41]
    unit_type = await asyncio.to_thread(match_template, roi_type, type_templates, 0.7)
    return UnitDataEntry(filename, unit_type, unit_formation)

async def process_images(image_dir, type_templates, formation_templates):
    tasks = []
    for filename in os.listdir(image_dir):
        tasks.append(process_single_image(filename, image_dir, type_templates, formation_templates))
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

if __name__ == "__main__":

    with zipfile.ZipFile("templates.zip", 'r') as zf:
        zf.extractall("")

    with zipfile.ZipFile("input_images.zip", 'r') as zf:
        zf.extractall("input_images")

    formation_templates = load_templates("templates/unit_formation_templates", UnitFormation)
    type_templates = load_templates("templates/unit_type_templates", UnitType)

    async def main():
        entries_raw = await process_images("input_images", type_templates, formation_templates)
        entries_raw += SpecialCases
        entries = {entry.filename: entry.__dict__ for entry in entries_raw}
        json.dump(entries, open("output.json", "w"), indent=4)

    asyncio.run(main())
    shutil.rmtree("templates")
    shutil.rmtree("input_images")

    data_out = []
    with open("output.json", 'r') as f:
        with open("purged.csv", 'w') as csvfile:
            csvfile.write("purged filename\n")
            data_in = json.load(f)

            for entry_filename, entry in data_in.items():
                if entry['unit_type'] is None and entry['unit_formation'] is None:
                    # Filter out entries that are not relevant
                    if ("_F_" in entry_filename) and\
                        ("Mrk" not in entry_filename) and\
                        ("Naval" not in entry_filename) and\
                        ("Air" not in entry_filename) and\
                        ("Helo" not in entry_filename):
                        csvfile.write(f"{entry_filename}\n")
                    else:
                        continue
                else:
                    data_out.append(entry)
        
    with open("unit_tags.json", 'w') as f:
        json.dump(data_out, f, indent=4)
        print(f"Filtered {len(data_in) - len(data_out)} entries with no unit_formation and no unit_type.")
        print(f"Saved {len(data_out)} entries to parsed_output.json.")

    with open("unit_tags.json", 'r') as f:
        data = json.load(f)

        invalid_entries = []
        for entry in data:
            if entry['unit_type'] is None:
                invalid_entries.append(entry)
            elif entry['unit_formation'] is None:
                entry["unit_formation"] = UnitFormation.COMPANY
            elif (entry['unit_type'] is None) and (entry['unit_formation'] is None):
                invalid_entries.append(entry)
            else:
                continue

        if invalid_entries:
            print("Entries with (no unit_type), or (no unit_type and no unit_formation)")
            for entry in invalid_entries:
                print(f" - {entry["filename"]} {entry["unit_type"]} {entry["unit_formation"]}")
        else:
            print("All entries have valid unit_type or unit_formation.")