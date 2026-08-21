import os
import re
import base64
import zipfile

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(WORKSPACE_DIR, 'index.html')
STANDALONE_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, 'Rizal_Chapter_4_Standalone.html')
ZIP_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, 'Rizal_Chapter_4_Package.zip')

def get_mime_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    elif ext == '.svg':
        return 'image/svg+xml'
    return 'application/octet-stream'

def build_standalone_html():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_image(match):
        img_rel_path = match.group(1)
        full_img_path = os.path.join(WORKSPACE_DIR, img_rel_path.replace('/', os.sep))
        if os.path.exists(full_img_path):
            mime_type = get_mime_type(full_img_path)
            with open(full_img_path, 'rb') as img_file:
                b64_data = base64.b64encode(img_file.read()).decode('utf-8')
            print(f"  Embedded {img_rel_path} ({mime_type})")
            return f'src="data:{mime_type};base64,{b64_data}"'
        else:
            print(f"  WARNING: Image not found: {full_img_path}")
            return match.group(0)

    # Match src="slide_photo/..."
    updated_content = re.sub(r'src="(slide_photo/[^"]+)"', replace_image, content)

    print(f"Writing standalone bundle to {STANDALONE_OUTPUT_PATH}...")
    with open(STANDALONE_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    size_mb = os.path.getsize(STANDALONE_OUTPUT_PATH) / (1024 * 1024)
    print(f"Successfully generated standalone HTML! Size: {size_mb:.2f} MB")

def build_zip_package():
    print(f"Creating ZIP archive at {ZIP_OUTPUT_PATH}...")
    with zipfile.ZipFile(ZIP_OUTPUT_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(INDEX_PATH, 'index.html')
        slide_photo_dir = os.path.join(WORKSPACE_DIR, 'slide_photo')
        if os.path.exists(slide_photo_dir):
            for root, _, files in os.walk(slide_photo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, WORKSPACE_DIR)
                    zipf.write(file_path, arcname)
                    print(f"  Added to ZIP: {arcname}")
    
    size_mb = os.path.getsize(ZIP_OUTPUT_PATH) / (1024 * 1024)
    print(f"Successfully generated ZIP archive! Size: {size_mb:.2f} MB")

if __name__ == '__main__':
    build_standalone_html()
    build_zip_package()
