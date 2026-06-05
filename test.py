import flopy
import numpy as np
import pathlib
from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder
from src.data.collector import Collector
import matplotlib.pyplot as plt

loader = ScenarioLoader("base")
scenario = loader.scenario

sim_ws = pathlib.Path("simulations") / "test"
sim = flopy.mf6.MFSimulation(sim_name="test", sim_ws=sim_ws, exe_name="mf6")

flopy.mf6.ModflowTdis(sim, nper=scenario["nper"], perioddata=scenario["tdis_rc"], time_units=scenario["time_units"])
print("Tdis built successfully")

# build gwf model
gwfname = "gwf"
gwf = flopy.mf6.ModflowGwf(
    sim,
    modelname=gwfname,
    save_flows=True,
    model_nam_file=f"{gwfname}.nam",
)


idomain =  np.ones((scenario["nlay"], scenario["nrow"], scenario["ncol"]), dtype=int)
idomain_true = loader.config_to_numpy("scenarios/base/idomain.tif").astype(int)
    
top = loader.config_to_numpy(scenario["top"])
botm = loader.config_to_numpy(scenario["botm"])

flopy.mf6.ModflowGwfdis(
    gwf,
    length_units=scenario["length_units"],
    nlay=1,
    nrow=scenario["nrow"],
    ncol=scenario["ncol"],
    delr=scenario["delr"],
    delc=scenario["delc"],
    top=top,
    botm=botm,
    idomain=idomain_true,
    filename=f"{gwfname}.dis",
)

k11 = loader.config_to_numpy(scenario["k11"])
np.clip(k11, 0.00001, None, out=k11)
k33 = loader.config_to_numpy(scenario["k33"])
np.clip(k33, 0.00001, None, out=k33)
print(k11.shape)
flopy.mf6.ModflowGwfnpf(
    gwf,
    save_flows=False,
    icelltype=scenario["icelltype"],
    k=k11,
    k33=k33,
    save_specific_discharge=True,
    filename=f"{gwfname}.npf",
)

initial_head = loader.config_to_numpy(scenario["initial_head"])
flopy.mf6.ModflowGwfic(
    gwf,
    strt=initial_head,
    filename=f"{gwfname}.ic"
)

# sto = flopy.mf6.ModflowGwfsto(gwf, ss=0, sy=0, filename=f"{gwfname}.sto")

# 定水头
chdspd = {}
all_chdspd = scenario["chdspd"]
for key in all_chdspd.keys():
    chdspd[key] = []
    for posi in all_chdspd[key]:
        _posi = posi[0], posi[1], posi[2]
        if len(posi) != 3:
            print(posi)
            chdspd[key].append([_posi, posi[3]])
        else:
            chdspd[key].append([_posi, initial_head[_posi]])
max_cells = max(len(cells) for cells in chdspd.values()) if chdspd else 0
flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=max_cells,
    stress_period_data=chdspd,
    save_flows=False,
    pname="CHD-1",
    filename=f"{gwfname}.chd",
)


#定流量井
flopy.mf6.ModflowGwfwel(
    gwf,
    print_input=True,
    print_flows=True,
    stress_period_data=scenario["wellspd"],
    save_flows=False,
    auxiliary="CONCENTRATION",
    pname="WEL-1",
    filename=f"{gwfname}.wel",
)

# 输出控制
flopy.mf6.ModflowGwfoc(
    gwf,
    head_filerecord=f"{gwfname}.hds",
    budget_filerecord=f"{gwfname}.bud",
    headprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
    saverecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
    printrecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
)
imsgwf = flopy.mf6.ModflowIms(
    sim,
    print_option="SUMMARY",
    outer_dvclose=scenario["hclose"],
    outer_maximum=scenario["nouter"],
    under_relaxation="NONE",
    inner_maximum=scenario["ninner"],
    inner_dvclose=scenario["hclose"],
    rcloserecord=scenario["rclose"],
    linear_acceleration="CG",
    scaling_method="NONE",
    reordering_method="NONE",
    relaxation_factor=scenario["relax"],
    filename=f"{gwfname}.ims",
)
sim.register_ims_package(imsgwf, [gwfname])
print("GWF model built successfully")

sim.write_simulation(silent=False)
sim.run_simulation(silent=False, report=True)

hds_file = sim_ws / f"{gwfname}.hds"
hobj = flopy.utils.HeadFile(hds_file)
head = hobj.get_data()

head = np.where(idomain_true == 0, np.nan, head)
plt.imshow(head[0])
plt.show()
