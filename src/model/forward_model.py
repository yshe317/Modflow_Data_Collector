from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
class ForwardModel:
    def __init__(self, name, write_scenario):
        self.sl = None
        self.name = name
        self._write_scenario = write_scenario
        self.saving_theta = None
    def forward(self, theta):
        self.saving_theta = theta
        self._write_scenario(theta)
        self.sl = ScenarioLoader(self.name)
        mb = Modflow6Builder(self.sl)
        sim = mb.build()
        sim.run_simulation(silent=False, report=False)
        # return sim.get_concentration()
    def get_concentration(self):
        co = Collector(self.sl)
        conc = co.get_conc()
        return conc
    
    def constraint(self):
        max_col = self.sl.scenario['ncol']
        max_row = self.sl.scenario['nrow']
        nper = self.sl.scenario['nper']
        return max_col, max_row, 1000, 1000, nper, nper 
    def collect(self, template, savepath=None):

        co = Collector(self.sl)
        co.set_output_path(savepath)
        # co.collect(output_template=template)
        co.collect_conc(output_template=template)
        co.collect_theta(self.saving_theta)