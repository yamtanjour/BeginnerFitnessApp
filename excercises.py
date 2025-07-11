import os
import json
import shutil

base_dir = 'exercises'
output_json = 'all_exercises.json'
output_img_dir = 'exercise_images'
os.makedirs(output_img_dir, exist_ok=True)

all_exercises = []

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if not os.path.isdir(folder_path):
        continue

    print(f"🔍 Processing exercise: {folder}")

    # Load info.json
    info_path = os.path.join(folder_path, 'exercise.json')
    if not os.path.isfile(info_path):
        print(f"⚠️ Missing info.json in: {folder}")
        continue

    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON in {folder}: {e}")
        continue

    data['name'] = folder
    data['images'] = []

    # Look into images/ subfolder
    images_folder = os.path.join(folder_path, 'images')
    if not os.path.isdir(images_folder):
        print(f"⚠️ No images folder in: {folder}")
        continue

    for filename in os.listdir(images_folder):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            ext = os.path.splitext(filename)[1]
            new_filename = f"{folder}_{len(data['images'])}{ext}"
            src_path = os.path.join(images_folder, filename)
            dst_path = os.path.join(output_img_dir, new_filename)

            try:
                shutil.copy(src_path, dst_path)
                data['images'].append(new_filename)
            except Exception as e:
                print(f"❌ Copy error for {folder}: {e}")

    print(f"✅ {folder}: {len(data['images'])} image(s) processed")
    all_exercises.append(data)

# Save combined JSON
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(all_exercises, f, indent=2)

print(f"\n🎉 Finished. Total exercises: {len(all_exercises)}")
