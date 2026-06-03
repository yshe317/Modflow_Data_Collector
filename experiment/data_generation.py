from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
from src.model.bayesian_optimizer import BayesianOptimizer
from src.data.observed import Observed


import matplotlib.pyplot as plt
import numpy as np
# 定义各参数的搜索步长
position_step = 20     # 位置变化步长
amount_step = 20        # 数量变化步长
conc_step = 20          # 浓度变化步长
time_step = 1          # 时间变化步长
def _generate_candidate(current, model):
    """
    生成新的参数候选
    """
    plt_position = current[0].copy() #(2)
    plt_quantity = current[1].copy() #(2)
    plt_time = current[2].copy() #(2)


    # 处理位置参数 [x, y]
    x, y = current[0]
    new_x = x + np.random.randint(-position_step, position_step+1)
    new_y = y + np.random.randint(-position_step, position_step+1)

    # 处理数量和浓度 [amount, concentration]
    amount, conc = current[1]
    new_amount = amount + np.random.randint(-amount_step, amount_step+1)
    new_conc = conc + np.random.randint(-conc_step, conc_step+1)

    # 处理时间参数 [begin_time, end_time]
    begin, end = current[2]
    new_begin = begin + np.random.randint(-time_step, time_step+1)
    new_end = end + np.random.randint(-time_step, time_step+1)
    
    max_col, max_row, max_amount,max_conc, max_begin, max_end = model.constraint()
    print( model.constraint())
    new_x = np.clip(new_x, 0, max_col)        # 假设x范围0-100
    new_y = np.clip(new_y, 0, max_row)        # 假设y范围0-100
    new_amount = np.clip(new_amount, 1, max_amount)   # 数量范围1-1000
    new_conc = np.clip(new_conc, 1, max_conc)  # 浓度范围1-100
    new_begin = np.clip(new_begin, 0, max_begin)  # 开始时间0-23
    new_end = np.clip(new_end, new_begin+1, max_end)  # 结束时间必须在开始时间后
    return [[int(new_x), int(new_y)], [float(new_amount), float(new_conc)], [int(new_begin), int(new_end)]]

def _write_scenario(plt_position, plt_quantity, plt_time, sim_name):
    sw = ScenarioWriter(sim_name)
    sw.set_time(120, 30, 30, 1)

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
        self.theta = None
    def forward(self, theta, sim_name):
        self.theta = theta
        plt_position = theta[0]
        plt_quantity = theta[1]
        plt_time = theta[2]
        _write_scenario(plt_position, plt_quantity, plt_time, sim_name)
        self.sl = ScenarioLoader(sim_name)
        mb = Modflow6Builder(self.sl)
        sim = mb.build()
        sim.run_simulation(silent=True, report=False)
        
        # save head
       
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

    def collect(self):
        co = Collector(self.sl)
        co.collect(plot_save_freq=360)
        co.collect_theta(self.theta)
        

def main():
    # set scenario
    observed = Observed("scenarios/lghg/observed.csv")
    ob_conc = observed.get_data("1_2_二氯乙烷")
    ob_col_row = observed.get_col_row()
    
    # initial guess
    model = Model(ob_conc,ob_col_row)
    current_plt_position = [100,10]
    current_plt_quantity = [1, 10]
    current_plt_time = [0, 10]
    theta = [current_plt_position, current_plt_quantity, current_plt_time]
    for i in range(1):
        model.forward(theta, f"lghg-{i}")
        model.collect()
        theta = _generate_candidate(theta, model)
    # #     conc = model.get_concentration()
    # #     print(conc)