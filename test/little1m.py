from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
from src.data.basemap import BaseMap
from src.utils import drop_duplicates
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image


def createlittle1m(plt_position, plt_quantity, plt_time):
    sw = ScenarioWriter("little1m")
    sw.set_time(36, 30, 30, 1) # 120 个月
    
    x = 1181
    y = 1181
    top = "scenarios/little1m/top.tif"
    bot = "scenarios/little1m/botm.tif"
    sw.set_discretization(1, x, y, 1, 1, 10, top, bot)

    k = "scenarios/little1m/k11.tif" 
    kv = "scenarios/little1m/k1v1.tif" 
    sw.set_k(k, kv)
    
    initial_head = "scenarios/little1m/ic.tif"
    sw.set_initial_head(initial_head)


    # 定水头是边界
    constant_head = []
    for i in range(x):
        if i == 0 or i == x-1:
            for j in range(y):
                constant_head.append((0,i,j))
        else:
            constant_head.append((0,i,0))
            constant_head.append((0,i,y-1))
    sw.set_constant_head(constant_head)
    
    # set well
    x = plt_position[0]
    y = plt_position[1]
    quantity = plt_quantity[0]
    concentration = plt_quantity[1]

    begin = plt_time[0]
    end = plt_time[1]
    sw.set_well([[(0,x,y), quantity, concentration]], target_period=begin)
    sw.set_well([[(0,x,y), 0, 0]], target_period=end)
    
    # initial_concentration = "scenarios/little1m/icc.tif"
    sw.set_initial_concentration(0)
    sw.set_al(10, 0.1)

    sw.set_cncspd([])

    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()

    return sw

def simu():
    sl = ScenarioLoader("little1m")
    mb = Modflow6Builder(sl)
    sim = mb.build()
    sim.run_simulation(silent=False, report=True)
    collector = Collector(sl)
    collector.collect(output_template="scenarios/little1m/top.tif")