import os

import rasterio

from test.scenariotest import go_throught_test, working_scenario_test, pollution_track_using_1m
# from test.vittest import run_all_tests
os.environ['KMP_DUPLICATE_LIB_OK']='True'
# run_all_tests()
pollution_track_using_1m()
# go_throught_test()
# working_scenario_test()
