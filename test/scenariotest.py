from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
def test_scenario_writer_and_loader():
    pass



def go_throught_test():
    sw = ScenarioWriter("test_scenario")
    sw.set_time(12, 30, 30, 1)
    sw.set_discretization(1, 10, 10, 10, 10, 10, 100, 0)
    sw.set_k(0.3)
    sw.set_initial_head(0.0)
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()
    sl = ScenarioLoader("test_scenario")
    scenario = sl.get_scenario()
    mb = Modflow6Builder(scenario)
    sim = mb.build()

    sim.run_simulation(silent=False, report=True)
