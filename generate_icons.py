import os
from PIL import Image

def generate_icons():
    # Paths
    base_dir = r"c:\Users\Monster\Desktop\Akademik Pusula"
    static_dir = os.path.join(base_dir, "static")
    source_img_path = os.path.join(base_dir, "Adsız.png")
    
    # Create static dir if not exists
    os.makedirs(static_dir, exist_ok=True)
    
    if not os.path.exists(source_img_path):
        print(f"Error: Source image not found at {source_img_path}")
        return
        
    try:
        # Open source image
        with Image.open(source_img_path) as img:
            # Ensure it's RGBA format to keep transparency if present
            img = img.convert("RGBA")
            
            # 192x192 icon
            img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
            img_192.save(os.path.join(static_dir, "icon-192.png"), "PNG")
            print("Created icon-192.png")
            
            # 512x512 icon
            img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
            img_512.save(os.path.join(static_dir, "icon-512.png"), "PNG")
            print("Created icon-512.png")
            
            # apple-touch-icon (180x180, often non-transparent background is preferred for iOS but PNG is okay)
            # iOS prefers no transparency (black or white background), but let's just resize first.
            img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
            
            # Create a solid background for Apple touch icon (Black to match Neobrutalist design: #050505)
            background = Image.new('RGB', img_180.size, (5, 5, 5)) 
            background.paste(img_180, mask=img_180.split()[3]) # paste using alpha channel as mask
            background.save(os.path.join(static_dir, "apple-touch-icon.png"), "PNG")
            
            print("Created apple-touch-icon.png")
            
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == '__main__':
    generate_icons()
