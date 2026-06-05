import os

import rasterio

from test.scenariotest import go_throught_test, working_scenario_test, pollution_track_using_1m
# from test.vittest import run_all_tests
os.environ['KMP_DUPLICATE_LIB_OK']='True'
# run_all_tests()
# pollution_track_using_1m()
# go_throught_test()
# working_scenario_test()

from experiment.data_generation import main
# main()
from test.little1m import createlittle1m,simu
# current_plt_position = [1000,100]
# current_plt_quantity = [0.01, 10000]
# current_plt_time = [0, 120]
# createlittle1m(current_plt_position, current_plt_quantity, current_plt_time)

# simu()



from test.base import create,run,forward
# create()
# run()

forward()
