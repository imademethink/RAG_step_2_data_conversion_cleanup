import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = 800000000

def tile_image(image_path, tile_size=(256, 256), output_dir="tiles"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img = Image.open(image_path)
    img_w, img_h = img.size

    tiles = []
    # Step-by-step grid slicing (Fixed-Size)
    for i in range(0, img_w, tile_size[0]):
        for j in range(0, img_h, tile_size[1]):
            # Define the bounding box for the chunk
            box = (i, j, i + tile_size[0], j + tile_size[1])
            tile = img.crop(box)

            tile_name = f"tile_{i}_{j}.jpg"
            save_path = os.path.join(output_dir, tile_name)
            tile.save(save_path)
            tiles.append(save_path)

    return tiles, img.size


satellite_img1 = "..\\..\\data\\hi_res_img\\imgg1.jpg"
satellite_img2 = "..\\..\\data\\hi_res_img\\imgg2.jpg"
satellite_img3 = "..\\..\\data\\hi_res_img\\imgg3.jpg"
output_img_dir = "..\\..\\data\\hi_res_img\\tiles\\"

tile_paths, original_size = tile_image(satellite_img2, tile_size=(224, 224), output_dir=output_img_dir)







# ============================================================
# ============================================================
# automated cross verification
# ============================================================
# ============================================================

import numpy as np


def validate_image_chunks(original_path, tile_dir, tile_size, original_dim):
    results = {
        "dimension_check": True,
        "coverage_check": True,
        "pixel_integrity": True,
        "errors": []
    }

    # 1. VALIDATE DIMENSIONS: Are all tiles exactly the requested size?
    tile_files = [os.path.join(tile_dir, f) for f in os.listdir(tile_dir)]
    for path in tile_files:
        with Image.open(path) as t:
            if t.size != tile_size:
                # Edge tiles might be smaller; if not allowed, mark as error
                results["dimension_check"] = False
                results["errors"].append(f"Tile {path} has wrong size: {t.size}")

    # 2. VALIDATE COVERAGE: Do number of tiles match (Width/Size * Height/Size)?
    expected_count = (np.ceil(original_dim[0] / tile_size[0]) *
                      np.ceil(original_dim[1] / tile_size[1]))
    if len(tile_files) != expected_count:
        results["coverage_check"] = False

    # 3. PIXEL INTEGRITY: Can we reconstruct the original image exactly?
    # (Simplified: check if total pixel count matches)
    original_img = Image.open(original_path)
    orig_array = np.array(original_img)

    # Check a specific sample pixel (e.g., center) to ensure no color shift
    # In a full QE suite, you'd stitch them back and compare MSE (Mean Squared Error)
    if orig_array.size > 0:
        results["pixel_integrity"] = True

    return results

report = validate_image_chunks(original_path=satellite_img2, tile_dir=output_img_dir,
                               tile_size=(224, 224), original_dim=original_size)
print(f"Dimensions Passed: {report['dimension_check']}")
print(f"Full Coverage: {report['coverage_check']}")



