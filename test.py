from src.data.basemap import BaseMap
import numpy as np

t = BaseMap("scenarios/base/base-time360.tif").get_value()
a = BaseMap("data/baseb/baseb-time360.tif").get_value()
b = BaseMap("data/base1/base1-time360.tif").get_value()
print(t.shape)

def r(output, target):
    squared_diff = (output - target) ** 2
    mask = ~np.isnan(squared_diff)
    valid_values = squared_diff[mask]
    
    if valid_values.size == 0:
        return np.nan  # 处理全NaN情况
    
    mean_squared_diff = np.mean(valid_values)
    return -0.5 * mean_squared_diff

print(r(t, t))
print(r(t+1, t))
print(r(a, t))
print(r(b, t))