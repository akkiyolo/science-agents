import os
from PIL import Image

def process_sprite(input_path, output_path):
    print(f"Processing {input_path}")
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()

        # Assuming the top-left pixel is the background color (usually white)
        bg_color = datas[0]
        
        # Determine background color tolerance
        tolerance = 20
        def is_bg(pixel):
            return (abs(pixel[0] - bg_color[0]) < tolerance and
                    abs(pixel[1] - bg_color[1]) < tolerance and
                    abs(pixel[2] - bg_color[2]) < tolerance)

        # Find bounds for cropping
        min_x, min_y = img.width, img.height
        max_x, max_y = 0, 0
        
        # Replace background with transparent
        newData = []
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                if is_bg(pixel):
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(pixel)
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y

        img.putdata(newData)
        
        if max_x < min_x or max_y < min_y:
            print(f"Empty image {input_path}")
            return
            
        # Crop to the actual character
        cropped = img.crop((min_x, min_y, max_x, max_y))
        
        # Resize to an appropriate sprite size (e.g. 64x64 or maintaining aspect ratio)
        # Let's target a height of 64 pixels for the characters
        target_height = 96
        aspect_ratio = cropped.width / cropped.height
        target_width = int(target_height * aspect_ratio)
        
        resized = cropped.resize((target_width, target_height), Image.Resampling.NEAREST)
        resized.save(output_path, "PNG")
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    import shutil
    import glob
    
    # Path to artifacts
    artifacts_dir = r"C:\Users\Len\.gemini\antigravity\brain\e48c8375-b96d-491b-8f42-b504aecd122f"
    dest_dir = r"d:\LearnAgents\science-agents-ui\public\assets\sprites"
    
    # Map generated files to their intended names
    sprites = {
        "einstein_sprite": "einstein.png",
        "newton_sprite": "newton.png",
        "curie_sprite": "curie.png",
        "player_sprite": "player.png",
        "galileo_sprite": "galileo.png",
        "darwin_sprite": "darwin.png",
        "lovelace_sprite": "lovelace.png",
        "tesla_sprite": "tesla.png",
        "tree_sprite": "tree.png"
    }
    
    for prefix, dest_name in sprites.items():
        pattern = os.path.join(artifacts_dir, f"{prefix}_*.png")
        matches = glob.glob(pattern)
        if matches:
            # Sort by modification time in case of multiple generations
            matches.sort(key=os.path.getmtime, reverse=True)
            input_file = matches[0]
            output_file = os.path.join(dest_dir, dest_name)
            process_sprite(input_file, output_file)
            
    # Also copy the world map without modifying its background
    map_pattern = os.path.join(artifacts_dir, "academy_world_map_*.png")
    map_matches = glob.glob(map_pattern)
    if map_matches:
        map_matches.sort(key=os.path.getmtime, reverse=True)
        shutil.copy2(map_matches[0], os.path.join(dest_dir, "world_map.png"))
        print(f"Copied world map to {os.path.join(dest_dir, 'world_map.png')}")
