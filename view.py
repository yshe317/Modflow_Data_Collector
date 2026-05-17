import os
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show

def list_tif_files(base_dir="data"):
    tif_files = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(('.tif', '.tiff')):
                tif_files.append(os.path.join(root, f))
    return sorted(tif_files)

def plot_tif(file_path, title=None):
    with rasterio.open(file_path) as src:
        data = src.read(1)
        fig, axes = plt.subplots(1, 1, figsize=(10, 8))
        im = axes.imshow(data, cmap='jet')
        axes.set_title(title or os.path.basename(file_path))
        fig.colorbar(im, ax=axes, label='Value')
        plt.show()

def browse_tif_files(base_dir="data"):
    tif_files = list_tif_files(base_dir)
    
    if not tif_files:
        print(f"No TIFF files found in '{base_dir}' directory.")
        return
    
    print(f"Found {len(tif_files)} TIFF files:")
    for i, f in enumerate(tif_files, 1):
        print(f"{i}. {f}")
    
    while True:
        try:
            choice = input(f"\nEnter file number to view (1-{len(tif_files)}), or 'q' to quit: ")
            if choice.lower() == 'q':
                break
            idx = int(choice) - 1
            if 0 <= idx < len(tif_files):
                plot_tif(tif_files[idx])
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(tif_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = "data"
    
    browse_tif_files(base_dir)