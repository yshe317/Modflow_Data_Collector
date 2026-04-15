import json
import pathlib
class ScenarioLoader:
    def __init__(self, scenario_name, scenarios_dir="scenarios"):
        self.path = pathlib.Path(scenarios_dir) / scenario_name
        with open(self.path / "scenario.json", 'r', encoding='utf-8') as f:
            self.scenario = json.load(f)

    def get_scenario(self):
        return self.scenario

    

