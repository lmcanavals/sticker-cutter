import os
import glob
import argparse
import cv2
import numpy as np
from PIL import Image

# --- CORE DIMENSION CONFIGURATION ---
TARGET_HEIGHT_CM = 5.0  # Exact height of the character in cm
OFFSET_MM = 2.0  # Distance from character to the cut line
DPI = 300  # Standard printing resolution
DASH_LENGTH_PX = 12  # Length of each dash segment
SPACE_LENGTH_PX = 8  # Gap between dashes
# ------------------------------------


def process_character_image(input_path, output_path):
    # 1. Load image and ensure standard RGBA layout
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    # 2. Convert white/near-white backgrounds to transparent
    white_mask = (r > 240) & (g > 240) & (b > 240)
    data[white_mask, 3] = 0
    img = Image.fromarray(data)

    # 3. Strip any existing canvas padding
    bbox = img.getbbox()
    if not bbox:
        print(f"Skipping {input_path}: No content detected.")
        return
    img = img.crop(bbox)

    # 4. Calculate exact dimensions based on physical DPI
    target_height_px = int((TARGET_HEIGHT_CM / 2.54) * DPI)
    aspect_ratio = img.width / img.height
    target_width_px = int(target_height_px * aspect_ratio)

    # Resize character
    img = img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)

    # 5. Add clean padding to avoid edge clipping
    offset_px = int((OFFSET_MM / 10.0 / 2.54) * DPI)
    safety_buffer = offset_px + 20

    extended_w = target_width_px + (safety_buffer * 2)
    extended_h = target_height_px + (safety_buffer * 2)

    padded_character = Image.new("RGBA", (extended_w, extended_h), (0, 0, 0, 0))
    padded_character.paste(img, (safety_buffer, safety_buffer))

    # 6. Extract Alpha mask and expand it (Dilate)
    np_padded = np.array(padded_character)
    alpha_mask = np_padded[:, :, 3]

    kernel_size = (offset_px * 2) + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated_mask = cv2.dilate(alpha_mask, kernel, iterations=1)

    # 7. Trace the perimeter and draw the dashed line
    contours, _ = cv2.findContours(
        dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    dash_layer = np.zeros_like(alpha_mask, dtype=np.uint8)

    for contour in contours:
        points = contour.reshape(-1, 2)
        if len(points) < 2:
            continue
        points = np.vstack([points, points[0]])

        distance_accumulator = 0
        should_draw = True

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            step_dist = np.linalg.norm(p2 - p1)
            distance_accumulator += step_dist

            if should_draw:
                cv2.line(dash_layer, tuple(p1), tuple(p2), 255, thickness=2)
                if distance_accumulator >= DASH_LENGTH_PX:
                    should_draw = False
                    distance_accumulator = 0
            else:
                if distance_accumulator >= SPACE_LENGTH_PX:
                    should_draw = True
                    distance_accumulator = 0

    # 8. Composite onto a clean white background canvas
    final_canvas = Image.new("RGB", (extended_w, extended_h), (255, 255, 255))
    final_canvas.paste(padded_character, (0, 0), padded_character)

    dash_rgba = np.zeros((extended_h, extended_w, 4), dtype=np.uint8)
    dash_rgba[dash_layer > 0] = [100, 100, 100, 255]
    dash_pil = Image.fromarray(dash_rgba)
    final_canvas.paste(dash_pil, (0, 0), dash_pil)

    # Save output preserving DPI headers
    final_canvas.save(output_path, "PNG", dpi=(DPI, DPI))


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Batch process images to make character sizes uniform and add dashed cutting outlines."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="./raw_cartoons",
        help="Path to the directory containing raw cartoon images (default: ./raw_cartoons)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./printable_output",
        help="Path to the directory where processed images will be saved (default: ./printable_output)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    extensions = ("*.png", "*.webp", "*.jpg", "*.jpeg")
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(args.input, ext)))

    if not image_files:
        print(f"No source images found in '{args.input}'.")
        return

    print(f"Processing {len(image_files)} images from '{args.input}'...")
    for file_path in image_files:
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(args.output, f"{name}_print.png")
        try:
            process_character_image(file_path, output_path)
            print(f"  Succeeded: {filename}")
        except Exception as e:
            print(f"  Failed to process {filename}: {str(e)}")


if __name__ == "__main__":
    main()
