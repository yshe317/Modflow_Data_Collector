from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
from src.data.basemap import BaseMap
from src.utils import drop_duplicates

import rasterio
import numpy as np
import pandas as pd
def data_prepare():
    tiffile = rasterio.open("scenarios/base/ksep.tif")
    data = tiffile.read()
    print(np.unique(data))


    k_field = data.copy().astype(float)
    k_field[k_field == 0] = 0
    k_field[k_field == 1] = 60.48
    k_field[k_field == 2] = 25.92
    k_field[k_field == 3] = 8.64
    k_field[k_field == 4] = 17.28
    k_field[k_field == 5] = 34.56
    meta = tiffile.meta.copy()
    # 更新必要的参数（如数据类型要与你的数据一致）
    meta.update(
        dtype=k_field.dtype,
        count=1,
        driver='GTiff'
    )
    with rasterio.open("scenarios/base/knum.tif", 'w', **meta) as dst:
        dst.write(k_field)
    
    idomain = np.where(data == 0, 0, 1)
    print(np.unique(idomain))
    with rasterio.open("scenarios/base/idomain.tif", 'w', **meta) as dst:
        dst.write(idomain)

def create():
    data_prepare()
    sw = ScenarioWriter("base")
    # sw.set_time(120, 30, 30, 1) # 120 个月
    sw.set_time(12, 180, 6, 1) 

    x = 300
    y = 500
    sw.set_discretization(1, x, y, 5, 5, 60, 130 , 70)

    k = "scenarios/base/knum.tif"
    sw.set_k(k)
    sw.set_initial_head(70)


    basemap = BaseMap("scenarios/base/knum.tif")
    df = pd.read_excel("scenarios/base/chd.xls")
    chs = []
    for i in range(len(df)):
        row,col = basemap.get_index_by_xy(df['x'].tolist()[i], df['y'].tolist()[i])
        if basemap.in_range(col, row):
            chs.append([0, int(row), int(col),df['value'].tolist()[i]])
    chs = drop_duplicates(chs, lambda x, y: x[1] == y[1] and x[2] == y[2] and x[0] == y[0])
    sw.set_constant_head(chs)

    # print(chs)
    # pdf = pd.read_excel("scenarios/base/ps.xls")
    # for i in range(len(pdf)):
    #     row,col = basemap.get_index_by_xy(pdf['x'].tolist()[i], pdf['y'].tolist()[i])
    #     print(row, col)
    sw.set_idomain("scenarios/base/idomain.tif")
    sw.set_well([[(0,70,70), 00.1, 100]], target_period=0)
    sw.set_well([[(0,70,70), 0, 0]], target_period=20)

    sw.set_well([[(0,70,130), 0.01, 500]], target_period=2)
    sw.set_well([[(0,70,130), 0, 0]], target_period=20)

    sw.set_al(40, 0.1)
    sw.set_cncspd([])
    
    sw.set_initial_concentration(0)
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)

    sw.write()

def run():
    sl = ScenarioLoader("base")
    mb = Modflow6Builder(sl)
    sim = mb.build()
    sim.run_simulation(silent=False, report=True)
    collector = Collector(sl)
    collector.collect(output_template="scenarios/base/ksep.tif")