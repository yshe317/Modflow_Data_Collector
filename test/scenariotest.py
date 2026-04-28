from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
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
    # sw = ScenarioWriter("real_scenario")
    
    # sw.set_time(12, 30, 30, 1)

    # top = "scenarios/real_scenario/TOP.tif"
    # bot = "scenarios/real_scenario/BOTM.tif"

    # sw.set_discretization(1, 627, 515, 0.5, 0.5, 10, top, bot)
    # sw.set_k(0.3)
    # sw.set_initial_head("scenarios/real_scenario/水位.tif")
    # sw.set_constant_head([(0,5,5), (0,4,6)])
    # sw.set_well([[(0,2,3), 10, 10]])
    # sw.set_initial_concentration(0.1)

    # sw.set_cncspd([(0,5,5), (0,4,6)])
    # nouter, ninner = 100, 300
    # hclose, rclose, relax = 1e-6, 1e-6, 1.0
    # sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    # sw.write()
    sl = ScenarioLoader("real_scenario")
    mb = Modflow6Builder(sl)
    sim = mb.build()

    sim.run_simulation(silent=False, report=True)

    co = Collector(sl)
    co.collect(plot_save_freq=20)