import matplotlib.pyplot as plt
import rasterio

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_tif_with_contour(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)
    
    fig, axes = plt.subplots(1, 1, figsize=(10, 8))
    
    im = axes.imshow(data, cmap='jet')
    
    contour = axes.contour(data, colors='black', linewidths=0.8)
    
    axes.clabel(contour, contour.levels, inline=True, fontsize=8, fmt='%.1f')
    
    axes.set_title('初始水头范围A')
    
    fig.colorbar(im, ax=axes, label='水头值')
    
    plt.show()

if __name__ == "__main__":
    tif_path = r'd:\PollutionSourceTracker\ModflowDataCollector\scenarios\large_scenario\clip_range_dem.tif'
    plot_tif_with_contour(tif_path)