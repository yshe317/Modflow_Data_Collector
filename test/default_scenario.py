from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector


def createdefaultscenario():
    sw = ScenarioWriter("default")
    sw.set_time(1, 30, 30, 1) # 120 个月
    x = 750
    y = 1000
    sw.set_discretization(1, x, y, 1, 1, 10, 0.0, -10.0)
    
    sw.set_k(0.5, 0.5)
    sw.set_initial_head(5.0)
    
    constant_head = []
    for i in range(x):
        if i == 0:
            for j in range(y):
                constant_head.append((0,i,j, 0))
        elif i == x-1:
            for j in range(y):
                constant_head.append((0,i,j, 10))
    sw.set_constant_head(constant_head)
    sw.set_al(0.5, 0.3)
    sw.set_cncspd([])


    x = 500
    y = 500
    quantity = 1
    concentration = 1000

    begin = 0
    end = 12
    sw.set_well([[(0,x,y), quantity, concentration]], target_period=begin)
    sw.set_well([[(0,x,y), 0, 0]], target_period=end)
    
    sw.set_initial_concentration(0)

    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()


def run():
    sl = ScenarioLoader("default")
    mb = Modflow6Builder(sl)

    sim = mb.build()
    sim.run_simulation(silent=False, report=True)
    collector = Collector(sl)
    collector.collect()

    
    