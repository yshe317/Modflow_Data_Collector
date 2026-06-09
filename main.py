import os

import rasterio

os.environ['KMP_DUPLICATE_LIB_OK']='True'
from test.base import create,run,forward
from src.data.basemap import BaseMap
from src.model.forward_model import ForwardModel
from src.model.bayesian_optimizer import BayesianOptimizer
create([[70,70,0.1,100,0, 10], [130,130,0.1,100,0, 10]])
run()

# forward()
# model = ForwardModel("base", create)
# optimizer = BayesianOptimizer(model, max_iter=100)
# initial_guess = [[80, 80, 0.1, 10, 0, 10]]

# m = BaseMap("scenarios/base/base-time360.tif")
# res = optimizer.optimize(initial_guess, m.get_value())
# print(res)