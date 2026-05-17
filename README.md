# sticker-cutter

An automated batch-processing utility designed to convert raw cartoon, character, or sticker images into uniform, print-ready cutting sheets. It standardizes the physical size of the actual character (ignoring any original canvas padding) and adds a clean, shape-following dashed cutting line around the perimeter.

This is perfect for parents, teachers, or creators looking to quickly prepare DIY sticker packs or scissor-cutting practice sheets for kids.

---

## 🚀 Key Features

* **True-to-Size Physical Scaling:** Uses DPI-aware calculations to ensure the actual character asset scales to an exact real-world height (e.g., exactly 5.0 cm tall), regardless of the input file's original resolution.
* **Smart Background Trimming:** Automatically detects and strips away empty padding from both transparent alpha channels and solid white/near-white backgrounds to isolate the true bounding box of the figure.
* **Smooth Offset Contours:** Utilizes OpenCV elliptical morphology dilation to trace a perfectly balanced cutting contour that follows complex edges (like hair or fingers) cleanly.
* **Continuous Dashed Pathing:** Employs a custom distance accumulator to draw clean, shape-following vector dashes rather than applying a blocky grid texture overlay.
* **Print-Ready Metadata:** Injects proper DPI headers directly into the output PNG metadata. When dragged and dropped into MS Word, Google Docs, or LibreOffice Writer, the images will automatically display at their true physical size without manual scaling.

---

## 🛠️ Setup & Installation

This project is built and optimized for use with **`uv`**, the ultra-fast Python package manager.

1. **Initialize the Project Directory:**

```bash
   mkdir sticker-cutter
   cd sticker-cutter
   uv init
```

1. **Add Dependencies:**
Add the required high-performance image processing libraries. `uv` will lock and manage these inside an isolated environment automatically:

```bash
uv add pillow opencv-python numpy
```

1. **Save Your Script:**
   Save the processing code as `prepare_snip_sheets.py` in your repository.

---

## 💻 How to Run It

### Using the Defaults

By default, the script looks for a folder named `./raw_cartoons` and exports the finished sheets to `./printable_output`.

1. Create your input folder and add your images (`.png`, `.webp`, `.jpg`, `.jpeg`):

   ```bash
   mkdir raw_cartoons printable_output

```

1. Execute the batch runner via `uv`:

```bash
uv run prepare_snip_sheets.py
```

### Using Custom Folders (Command-Line Arguments)

You can point the program to any arbitrary input or output directories dynamically without modifying the source code:

```bash
# Process a specific batch of images
uv run prepare_snip_sheets.py -i ./bluey_images -o ./bluey_prints

# Process a batch using explicit long flags
uv run prepare_snip_sheets.py --input ./pokemon --output ./pokemon_output
```

To see the built-in documentation and helper flags at any time, run:

```bash
uv run prepare_snip_sheets.py --help
```

---

## ⚙️ Advanced Adjustments

If you need to change the physical output requirements, open `prepare_snip_sheets.py` and modify the core configuration variables right at the top of the file:

```python
# --- CORE DIMENSION CONFIGURATION ---
TARGET_HEIGHT_CM = 5.0            # Exact height of the character in cm
OFFSET_MM = 2.0                   # Distance from character to the cut line
DPI = 300                         # Standard printing resolution (300 is ideal for print)
DASH_LENGTH_PX = 12               # Length of each dash segment
SPACE_LENGTH_PX = 8               # Gap between dashes
# ------------------------------------

```

> This project was generated using `gemini`, it works and it was reviewed and tested by me.
