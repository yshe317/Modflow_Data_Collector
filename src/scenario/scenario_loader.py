import json
import pathlib
import numpy as np
from numpy.char import isnumeric
import rasterio

class ScenarioLoader:
    def __init__(self, scenario_name, scenarios_dir="scenarios"):
        self.path = pathlib.Path(scenarios_dir) / scenario_name
        with open(self.path / "scenario.json", 'r', encoding='utf-8') as f:
            self.scenario = json.load(f)
        self._numeric_key()
    def _numeric_key(self):
        numeric_key = ['chdspd','wellspd','cncspd']
        for i in numeric_key:
            target = self.scenario[i]
            key_ls = list(target.keys())
            for key in key_ls:
                value = target[key]
                target.pop(key)
                target[int(key)] = value

    def get_scenario(self):
        return self.scenario

    def config_to_numpy(self, config, shape=None):

        if not shape:
            nlay = self.scenario['nlay']
            nrow = self.scenario['nrow']
            ncol = self.scenario['ncol']
            shape = (nlay,nrow,ncol)
        if isinstance(config,(float, int)):
            output = np.full(shape, config, dtype=np.float32)
            return output
        else:
            file = rasterio.open(config)
            return file.read()


        


