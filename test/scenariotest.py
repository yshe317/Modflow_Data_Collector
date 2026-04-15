from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader

def test_scenario_writer_and_loader():
    sw = ScenarioWriter("test_scenario")
    sw.set_time(12, 30, 30, 1)
    sw.write()
    sl = ScenarioLoader("test_scenario")
    scenario = sl.get_scenario()
    print(scenario.keys())

