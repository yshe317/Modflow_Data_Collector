import flopy
class Modflow6Builder:
    def __init__(self, scenario):
        self.scenario = scenario
        self.model = None
    def build(self):    
        self.sim = flopy.mf6.MFSimulation(sim_name=scenario["sim_name"], sim_ws=sim_ws, exe_name="mf6")
    
    def _build_gwf(self):
        self.model.gwf = self.model.dis

