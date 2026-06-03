from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
from src.data.basemap import BaseMap
from src.utils import drop_duplicates
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

def go_throught_test():
    sw = ScenarioWriter("test_scenario")
    sw.set_time(12, 30, 30, 1)
    sw.set_discretization(1, 10, 10, 10, 10, 10, 100, -5)
    sw.set_k(0.3)
    sw.set_initial_head(0.0)
    sw.set_constant_head([(0,5,5), (0,4,6)])
    sw.set_well([[(0,2,3), 10, 10]])
    sw.set_initial_concentration(0.1)

    sw.set_cncspd([(0,5,5), (0,4,6)])
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()
    sl = ScenarioLoader("test_scenario")
    mb = Modflow6Builder(sl)
    sim = mb.build()

    sim.run_simulation(silent=False, report=True)

    co = Collector(sl)
    co.collect()

def working_scenario_test():
    sw = ScenarioWriter("real_scenario")
    
    sw.set_time(12, 30, 30, 1)

    top = "scenarios/real_scenario/TOP.tif"
    bot = "scenarios/real_scenario/BOTM.tif"

    sw.set_discretization(1, 627, 515, 0.5, 0.5, 10, top, bot)
    sw.set_k(0.3)
    sw.set_initial_head("scenarios/real_scenario/水位.tif")
    sw.set_constant_head([(0,5,5), (0,4,6)])
    sw.set_well([[(0,2,3), 1, 10]])
    sw.set_initial_concentration(0.1)

    sw.set_cncspd([(0,5,5), (0,4,6)])
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()
    sl = ScenarioLoader("real_scenario")
    mb = Modflow6Builder(sl)
    sim = mb.build()

    sim.run_simulation(silent=False, report=True)

    co = Collector(sl)
    co.collect(plot_save_freq=20)



def pollution_track_using_1m():
    
    basemap = BaseMap("scenarios/lghg1m/大范围.tif")
    df = pd.read_excel("scenarios/lghg1m/定水头点位.xlsx")


    sw = ScenarioWriter("lghg1m")
    sw.set_time(12, 30, 30, 1)

    
    top_file = "scenarios/lghg1m/大范围Top.tif" 
    bot_file = "scenarios/lghg1m/大范围Bot.tif"
    sw.set_discretization(1, 5224, 5224, 1, 1, 20, top_file, bot_file)

    sw.set_initial_head("scenarios/lghg1m/初始水头.tif")
    sw.set_k(0.3)
    chs = []
    for i in range(len(df)):
        row,col = basemap.get_index_by_xy(df['经度___'].tolist()[i], df['纬度___'].tolist()[i])
        if basemap.in_range(col, row):
            chs.append([0, int(col), int(row)])
    chs = drop_duplicates(chs, lambda x, y: x[1] == y[1] and x[2] == y[2] and x[0] == y[0])
    
    sw.set_constant_head(chs)


    sw.set_initial_concentration(0.0)
    sw.set_cncspd([(0,0,0)])
    sw.set_well([[(0,0,0), 10, 10]])
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()
    print("Scenario written successfully")
    sl = ScenarioLoader("lghg1m")

    print("Scenario loaded successfully")
    mb = Modflow6Builder(sl)
    sim = mb.build()
    print("Running simulation...")
    sim.run_simulation(silent=False, report=True)
    return 0