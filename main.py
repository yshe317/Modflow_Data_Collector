import os

import rasterio

os.environ['KMP_DUPLICATE_LIB_OK']='True'
from test.base import create,run,forward
from src.data.basemap import BaseMap
from src.model.forward_model import ForwardModel
from src.model.bayesian_optimizer import BayesianOptimizer
# create()
# run()

# forward()
model = ForwardModel("base", create)
optimizer = BayesianOptimizer(model)
initial_guess = [[80,80,0.1, 10, 0, 10]]

m = BaseMap("scenarios/base/base-time360.tif")
res = optimizer.optimize(initial_guess, m.get_value())
print(res)

# create([[80, 80, 0.1, 10, 0, 10]],name="baseb")
# run("baseb")


# create([[66, 82, 5.874447441349426, 13.019722614499488, 1, 15]],name="base1")
# run("base1")