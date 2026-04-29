from pandas.core.arrays.timedeltas import truediv_object_array
from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
from src.model.bayesian_optimizer import BayesianOptimizer
from src.data.observed import Observed



def _write_scenario(plt_position, plt_quantity, plt_time):
    sw = ScenarioWriter("lghg")
    sw.set_time(12, 30, 30, 1)

    x = 119
    y = 118
    top = "scenarios/lghg/含水层top范围A.tif"
    bot = "scenarios/lghg/含水层bom范围A.tif"
    sw.set_discretization(1, x, y, 10, 10, 10, top, bot)

    k = "scenarios/lghg/k1范围A.tif" 
    kv = "scenarios/lghg/k1v范围A.tif" 
    sw.set_k(k, kv)
    
    initial_head = "scenarios/lghg/初始水头范围A.tif"
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

    initial_concentration = "scenarios/lghg/初始浓度范围A.tif"
    sw.set_initial_concentration(initial_concentration)


    sw.set_cncspd(None)


    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0
    sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)
    sw.write()


class Model:
    def __init__(self, target, target_col_row):
        self.sl = None
        self.target = target
        self.target_col_row = target_col_row
    def forward(self, theta):
        plt_position = theta[0]
        plt_quantity = theta[1]
        plt_time = theta[2]
        _write_scenario(plt_position, plt_quantity, plt_time)
        self.sl = ScenarioLoader("lghg")
        mb = Modflow6Builder(self.sl)
        sim = mb.build()
        sim.run_simulation(silent=truediv_object_array, report=False)
        # return sim.get_concentration()
    def get_concentration(self):
        row = self.target_col_row[:, 0]
        col = self.target_col_row[:, 1]
        co = Collector(self.sl)
        conc = co.value_of_row_col(row,col)
        return conc
    
    def constraint(self):
        max_col = self.sl.scenario['ncol']
        max_row = self.sl.scenario['nrow']
        nper = self.sl.scenario['nper']
        return max_col, max_row, 1000, 1000, nper, nper 


def main():
    # set scenario
    observed = Observed("scenarios/lghg/observed.csv")
    ob_conc = observed.get_data("1_2_二氯乙烷")
    ob_col_row = observed.get_col_row()
    
    # initial guess
    model = Model(ob_conc,ob_col_row)
    current_plt_position = [5,6]
    current_plt_quantity = [100, 200]
    current_plt_time = [0, 10]

    # for i in range(5):
    #     current_plt_position[0] = i*10
    #     current_plt_position[1] = i*10
    #     current_plt_quantity[0] = i*10
    #     current_plt_quantity[1] = i*10
    #     current_plt_time[0] = i
    #     current_plt_time[1] = 10
    #     model.forward([current_plt_position, current_plt_quantity, current_plt_time])
        
    #     conc = model.get_concentration()
    #     print(conc)
    
    # sim.run_simulation(silent=False, report=True)
    # co = Collector(sl)
    # co.collect()

    optimizer = BayesianOptimizer(model)
    current, best = optimizer.optimize([current_plt_position, current_plt_quantity, current_plt_time], ob_conc)
    print(current)
    print(best)