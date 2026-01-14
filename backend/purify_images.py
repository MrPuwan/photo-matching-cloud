from PIL import Image
import os

input_folder = "downloaded_images"
output_folder = "purified_images"

for person in os.listdir(input_folder):
    person_path = os.path.join(input_folder, person)
    if not os.path.isdir(person_path):
        continue
    out_person_path = os.path.join(output_folder, person)
    os.makedirs(out_person_path, exist_ok=True)
    
    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)
        out_img_path = os.path.join(out_person_path, img_name)
        try:
            with Image.open(img_path) as img:
                rgb_img = img.convert("RGB")  # Convert to 8-bit RGB
                rgb_img.save(out_img_path)
                print(f"✅ Converted: {out_img_path}")
        except Exception as e:
            print(f"❌ Failed: {img_path} -> {e}")
