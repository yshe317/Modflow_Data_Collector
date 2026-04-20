import rasterio
from test.scenariotest import go_throught_test, working_scenario_test
go_throught_test()

# src = rasterio.open("scenarios/real_scenario/TOP.tif")
# print(src.meta)

working_scenario_test()
