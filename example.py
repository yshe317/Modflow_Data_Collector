# ## MT3DMS Problem 3
#
# The purpose of this script is to (1) recreate the example problems that were first
# described in the 1999 MT3DMS report, and (2) compare MF6-GWT solutions to the
# established MT3DMS solutions.
#
# Ten example problems appear in the 1999 MT3DMS manual, starting on page 130.  This
# notebook demonstrates example 3 from the list below:
#
#   1.  One-Dimensional Transport in a Uniform Flow Field
#   2.  One-Dimensional Transport with Nonlinear or Nonequilibrium Sorption
#   3.  **Two-Dimensional Transport in a Uniform Flow Field**
#   4.  Two-Dimensional Transport in a Diagonal Flow Field
#   5.  Two-Dimensional Transport in a Radial Flow Field
#   6.  Concentration at an Injection/Extraction Well
#   7.  Three-Dimensional Transport in a Uniform Flow Field
#   8.  Two-Dimensional, Vertical Transport in a Heterogeneous Aquifer
#   9.  Two-Dimensional Application Example
#   10. Three-Dimensional Field Case Study

# ### Initial setup
#
# Import dependencies, define the example name and workspace, and read settings from environment variables.

# +
from pathlib import Path
from pprint import pformat
from sqlite3 import TimeFromTicks

import flopy
import git
import matplotlib.pyplot as plt
import numpy as np
from flopy.plot.styles import styles
from modflow_devtools.misc import get_env, timed


from utils.tifloader import TIFLoader
# Example name and workspace paths. If this example is running
# in the git repository, use the folder structure described in
# the README. Otherwise just use the current working directory.
example_name = "gwt-annuo"
try:
    root = Path(git.Repo(".", search_parent_directories=True).working_dir)
except:
    root = None
workspace = root / "examples" if root else Path.cwd()
figs_path = root / "figures" if root else Path.cwd()

# Settings from environment variables
write = get_env("WRITE", True)
run = get_env("RUN", True)
plot = get_env("PLOT", True)
plot_show = get_env("PLOT_SHOW", True)
plot_save = get_env("PLOT_SAVE", True)
# -

# ### Define parameters
#
# Define model units, parameters and other settings.

# +
# Model units
length_units = "meters"
time_units = "days"

# Model parameters
nlay = 1  # Number of layers
nrow = 656  # Number of rows
ncol = 796  # Number of columns
delr = 0.5  # Column width ($m$)
delc = 0.5  # Row width ($m$)
delz = 10.0  # Layer thickness ($m$)
top = 0.0  # Top of the model ($m$)
prsity = 0.3  # Porosity
perlen = 365  # Simulation time ($days$)
k11 = 0.52  # Horizontal hydraulic conductivity ($m/d$)
qwell = 0.4  # Volumetric injection rate ($m^3/d$)
cwell = 4000.0  # Concentration of injected water ($mg/L$)
al = 10.0  # Longitudinal dispersivity ($m$)
trpt = 0.3  # Ratio of transverse to longitudinal dispersivity

# Additional model input
nper = 12  # 12个月
perlen = [30] * nper  # 每个月30天
nstp = [1] * nper
tsmult = [1.0] * nper
sconc = 0.0
dt0 = 0.3
ath1 = al * trpt
dmcoef = 0.0

botm = [top - delz]  # Model geometry

k33 = k11  # Vertical hydraulic conductivity ($m/d$)
icelltype = 0

# Initial conditions
Lx = (ncol - 1) * delr
v = 1.0 / 3.0
prsity = 0.3
q = v * prsity
h1 = q * Lx
# strt = np.zeros((nlay, nrow, ncol), dtype=float)
# strt[0, :, 0] = h1
# height
_gaocheng = TIFLoader("data/s高程.tif")
strt = _gaocheng.get_numpy_array().reshape((1, nrow, ncol))

# strt[0, :, 0] = h1
# strt[0, :, -1] = h1
# strt[0, 0, :] = h1
# strt[0, -1, :] = h1
# strt[0, :, 0] = h1
# strt[0, :, -1] = h1
# strt[0, :, :] = strt[0, :, :] - (h1 - top)


ibound_mf2k5 = np.ones((nlay, nrow, ncol), dtype=int)
ibound_mf2k5[0, :, 0] = -1
ibound_mf2k5[0, :, -1] = -1
idomain = np.ones((nlay, nrow, ncol), dtype=int)
icbund = 1
c0 = 0.0
cncspd = [[(0, 0, 0), c0]]
welspd = {0: [[0, 15, 15, qwell]]}  # Well pumping info for MF2K5
spd = {0: [0, 15, 15, cwell, 2]}  # Well pupming info for MT3DMS
#              (k,  i,  j),  flow, conc

qwell = 0.4  # Volumetric injection rate ($m^3/d$)
cwell = 4000.0  # Concentration of injected water ($mg/L$)
spd_mf6 = {0: [[(0, 365, 392), qwell, cwell]]}  # MF6 pumping information

# Set solver parameter values (and related)
nouter, ninner = 100, 300
hclose, rclose, relax = 1e-6, 1e-6, 1.0
ttsmult = 1.0
percel = 1.0  # HMOC parameters in case they are invoked
itrack = 3  # HMOC
wd = 0.5  # HMOC
dceps = 1.0e-5  # HMOC
nplane = 1  # HMOC
npl = 0  # HMOC
nph = 16  # HMOC
npmin = 4  # HMOC
npmax = 32  # HMOC
dchmoc = 1.0e-3  # HMOC
nlsink = nplane  # HMOC
npsink = nph  # HMOC

# Time discretization
tdis_rc = []
tdis_rc.append((perlen, nstp, 1.0))
# -

# ### Model setup
#
# Define functions to build models, write input files, and run the simulation.


# +
def build_models(sim_name, mixelm=0, silent=False):
    # MODFLOW 6
    name = "p03-mf6"
    gwfname = "gwf-" + name
    sim_ws = workspace / sim_name
    sim = flopy.mf6.MFSimulation(sim_name=sim_name, sim_ws=sim_ws, exe_name="mf6")

    # Instantiating MODFLOW 6 time discretization
    tdis_rc = []
    for i in range(nper):
        tdis_rc.append((perlen[i], nstp[i], tsmult[i]))
    flopy.mf6.ModflowTdis(sim, nper=nper, perioddata=tdis_rc, time_units=time_units)

    # Instantiating MODFLOW 6 groundwater flow model
    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname=gwfname,
        save_flows=True,
        model_nam_file=f"{gwfname}.nam",
    )

    # Instantiating MODFLOW 6 solver for flow model
    imsgwf = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",
        outer_dvclose=hclose,
        outer_maximum=nouter,
        under_relaxation="NONE",
        inner_maximum=ninner,
        inner_dvclose=hclose,
        rcloserecord=rclose,
        linear_acceleration="CG",
        scaling_method="NONE",
        reordering_method="NONE",
        relaxation_factor=relax,
        filename=f"{gwfname}.ims",
    )
    sim.register_ims_package(imsgwf, [gwf.name])

    # Instantiating MODFLOW 6 discretization package
    flopy.mf6.ModflowGwfdis(
        gwf,
        length_units=length_units,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
        idomain=np.ones((nlay, nrow, ncol), dtype=int),
        filename=f"{gwfname}.dis",
    )

    # Instantiating MODFLOW 6 node-property flow package
    flopy.mf6.ModflowGwfnpf(
        gwf,
        save_flows=False,
        icelltype=icelltype,
        k=k11,
        k33=k33,
        save_specific_discharge=True,
        filename=f"{gwfname}.npf",
    )

    # Instantiating MODFLOW 6 initial conditions package for flow model
    flopy.mf6.ModflowGwfic(gwf, strt=strt, filename=f"{gwfname}.ic")

    # Instantiate MODFLOW 6 storage package
    sto = flopy.mf6.ModflowGwfsto(gwf, ss=0, sy=0, filename=f"{gwfname}.sto")

    # Instantiating MODFLOW 6 constant head package
    rowList = np.arange(0, nrow).tolist()
    chdspd = []
    # Loop through the left & right sides.
    # for itm in rowList:
    #     if itm == 0 or itm == nrow-1:
    #         for jtm in np.arange(0, ncol).tolist():
    #             chdspd.append([(0, itm, jtm), strt[0,itm, jtm]])
    #     else:
    #         # first, do left side of model
    #         chdspd.append([(0, itm, 0), strt[0, itm, 0]])
    #         # finally, do right side of model
    #         chdspd.append([(0, itm, ncol - 1), strt[0, itm, ncol-1]])

    # > 2 < 1.9
    # for itm in rowList:
    #     for jtm in np.arange(0, ncol).tolist():
    #         if strt[0, itm, ncol-1] > 1.9 or strt[0, itm, ncol-1] < 1.6:
    #             if not (itm == 0 or itm == nrow-1) and not (jtm == 0 or jtm == ncol-1):
    #                 chdspd.append([(0, itm, jtm), strt[0, itm, jtm]])


    # human set 
    additional = [(0,395, 388), [0,352,300]]
    for i in additional:
        chdspd.append([(0, i[1], i[2]), strt[0, i[1], i[2]]])
    

    chdspd = {0: chdspd}
    print(chdspd)
    flopy.mf6.ModflowGwfchd(
        gwf,
        maxbound=len(chdspd),
        stress_period_data=chdspd,
        save_flows=False,
        pname="CHD-1",
        filename=f"{gwfname}.chd",
    )

    # Instantiate the wel package
    flopy.mf6.ModflowGwfwel(
        gwf,
        print_input=True,
        print_flows=True,
        stress_period_data=spd_mf6,
        save_flows=False,
        auxiliary="CONCENTRATION",
        pname="WEL-1",
        filename=f"{gwfname}.wel",
    )

    # Instantiating MODFLOW 6 output control package for flow model
    flopy.mf6.ModflowGwfoc(
        gwf,
        head_filerecord=f"{gwfname}.hds",
        budget_filerecord=f"{gwfname}.bud",
        headprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
        saverecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
        printrecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
    )

    # Instantiating MODFLOW 6 groundwater transport package
    gwtname = "gwt_" + name
    gwt = flopy.mf6.MFModel(
        sim,
        model_type="gwt6",
        modelname=gwtname,
        model_nam_file=f"{gwtname}.nam",
    )
    gwt.name_file.save_flows = True

    # create iterative model solution and register the gwt model with it
    imsgwt = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",
        outer_dvclose=hclose,
        outer_maximum=nouter,
        under_relaxation="NONE",
        inner_maximum=ninner,
        inner_dvclose=hclose,
        rcloserecord=rclose,
        linear_acceleration="BICGSTAB",
        scaling_method="NONE",
        reordering_method="NONE",
        relaxation_factor=relax,
        filename=f"{gwtname}.ims",
    )
    sim.register_ims_package(imsgwt, [gwt.name])

    # Instantiating MODFLOW 6 transport discretization package
    flopy.mf6.ModflowGwtdis(
        gwt,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
        idomain=1,
        filename=f"{gwtname}.dis",
    )

    # Instantiating MODFLOW 6 transport initial concentrations
    flopy.mf6.ModflowGwtic(gwt, strt=sconc, filename=f"{gwtname}.ic")

    # Instantiating MODFLOW 6 transport advection package
    if mixelm == 0:
        scheme = "UPSTREAM"
    elif mixelm == -1:
        scheme = "TVD"
    else:
        raise Exception()
    flopy.mf6.ModflowGwtadv(gwt, scheme=scheme, filename=f"{gwtname}.adv")

    # Instantiating MODFLOW 6 transport dispersion package
    if al != 0:
        flopy.mf6.ModflowGwtdsp(
            gwt,
            xt3d_off=True,
            alh=al,
            ath1=ath1,
            filename=f"{gwtname}.dsp",
        )

    # Instantiating MODFLOW 6 transport mass storage package (formerly "reaction" package in MT3DMS)
    flopy.mf6.ModflowGwtmst(
        gwt,
        porosity=prsity,
        first_order_decay=False,
        decay=None,
        decay_sorbed=None,
        sorption=None,
        bulk_density=None,
        distcoef=None,
        filename=f"{gwtname}.mst",
    )

    # Instantiating MODFLOW 6 transport constant concentration package
    flopy.mf6.ModflowGwtcnc(
        gwt,
        maxbound=len(cncspd),
        stress_period_data=cncspd,
        save_flows=False,
        pname="CNC-1",
        filename=f"{gwtname}.cnc",
    )

    # Instantiating MODFLOW 6 transport source-sink mixing package
    sourcerecarray = [("WEL-1", "AUX", "CONCENTRATION")]
    flopy.mf6.ModflowGwtssm(gwt, sources=sourcerecarray, filename=f"{gwtname}.ssm")

    # Instantiating MODFLOW 6 transport output control package
    # 修改这里：保存所有时间步的浓度结果
    saverecord = [("CONCENTRATION", "ALL"), ("BUDGET", "LAST")]
    printrecord = [("CONCENTRATION", "LAST"), ("BUDGET", "LAST")]
    flopy.mf6.ModflowGwtoc(
        gwt,
        budget_filerecord=f"{gwtname}.cbc",
        concentration_filerecord=f"{gwtname}.ucn",
        concentrationprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
        saverecord=saverecord,
        printrecord=printrecord,
    )

    # Instantiating MODFLOW 6 flow-transport exchange mechanism
    flopy.mf6.ModflowGwfgwt(
        sim,
        exgtype="GWF6-GWT6",
        exgmnamea=gwfname,
        exgmnameb=gwtname,
        filename=f"{name}.gwfgwt",
    )
    return sim


def write_models( sim, silent=True):
    sim.write_simulation(silent=silent)


@timed
def run_models( sim, silent=True):
    """Run models and assert successful completion."""
    success, buff = sim.run_simulation(silent=silent, report=True)
    assert success, pformat(buff)


# -

# ### Plotting results
#
# Define functions to plot model results.
def plot_results(sim, idx, ax=None):
    """Plot results for a given scenario."""
    with styles.USGSMap():
        gwtname = "gwt_p03-mf6"
        gwfname = "gwf-p03-mf6"
        
        # 获取模型工作目录
        sim_ws = sim.simulation_data.mfpath.get_sim_path()
        
        # 读取浓度结果文件
        ucn_file = Path(sim_ws) / f"{gwtname}.ucn"
        cobj = flopy.utils.HeadFile(ucn_file, text="CONCENTRATION")
        
        # 获取所有时间步
        times = cobj.get_times()
        print(f"Total time steps: {len(times)}")
        print(f"Times: {times}")
        
        # 读取水流模型结果
        hds_file = Path(sim_ws) / f"{gwfname}.hds"
        hobj = flopy.utils.HeadFile(hds_file)
        head = hobj.get_data()
        
        # 读取水流模型用于绘制
        gwf = sim.get_model(gwfname)
        
        # 加载高程TIF文件获取元数据（只需要加载一次）
        import rasterio
        tif_loader = TIFLoader("data/s高程.tif")
        metadata = tif_loader.get_metadata()
        
        # 遍历每个月（每个时间步）保存浓度TIF
        for month, time in enumerate(times, start=1):
            # 获取该时间步的浓度数据
            conc = cobj.get_data(totim=time)
            print(f"Month {month}: time={time}, conc shape={conc.shape}")
            
            # 保存溶质浓度为TIF文件
            if plot_save:
                # 准备浓度数据
                conc_data = conc[0]
                
                # 创建TIF文件，文件名包含月份
                tif_path = figs_path / f"{example_name}-concentration-month{month:02d}.tif"
                with rasterio.open(
                    tif_path,
                    'w',
                    driver='GTiff',
                    height=metadata['height'],
                    width=metadata['width'],
                    count=1,
                    dtype=conc_data.dtype,
                    crs=metadata['crs'],
                    transform=metadata['transform'],
                    nodata=metadata['nodata']
                ) as dst:
                    dst.write(conc_data, 1)
                
                print(f"Month {month} concentration TIF saved to: {tif_path}")
        
        # 只绘制最后一个月的图表
        conc = cobj.get_data(totim=times[-1])
        
        # 创建包含两个子图的图形
        if ax is None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
        
        # 绘制浓度分布图
        pmv1 = flopy.plot.PlotMapView(model=gwf, ax=ax1)
        
        # 绘制浓度等值线
        levels = np.linspace(0, 1000, 11)
        cs1 = pmv1.contour_array(conc[0], levels=levels, cmap="jet")
        ax1.clabel(cs1, inline=True, fontsize=8, fmt="%1.0f")
        
        # 绘制浓度填充图
        fa1 = pmv1.plot_array(conc[0], cmap="jet", vmin=0, vmax=1000, alpha=0.6)
        
        # 添加颜色条
        cbar1 = plt.colorbar(fa1, ax=ax1, shrink=0.8)
        cbar1.set_label("Concentration (mg/L)")
        
        # 标记注入井位置
        # ax1.plot(150, 150, "ko", markersize=8, label="Injection well")
        
        # 设置标题和标签
        ax1.set_xlabel("X (m)")
        ax1.set_ylabel("Y (m)")
        ax1.set_title("Solute Concentration Distribution")
        ax1.legend()
        
        # 设置等比例
        ax1.set_aspect("equal")
        
        # 绘制水流模型高程图
        pmv2 = flopy.plot.PlotMapView(model=gwf, ax=ax2)
        
        # 绘制水头等值线
        hmin = head.min()
        hmax = head.max()
        hlevels = np.linspace(hmin, hmax, 11)
        # cs2 = pmv2.contour_array(head[0], levels=hlevels, cmap="coolwarm")
        # ax2.clabel(cs2, inline=True, fontsize=8, fmt="%1.2f")
        
        # 绘制水头填充图
        fa2 = pmv2.plot_array(head[0], cmap="coolwarm", vmin=hmin, vmax=hmax, alpha=0.6)
        
        # 添加颜色条
        cbar2 = plt.colorbar(fa2, ax=ax2, shrink=0.8)
        cbar2.set_label("Head (m)")
        
        # 标记注入井位置
        # ax2.plot(171, 115, "ko", markersize=8, label="Injection well")
        
        # 设置标题和标签
        ax2.set_xlabel("X (m)")
        ax2.set_ylabel("Y (m)")
        ax2.set_title("Groundwater Head Distribution")
        ax2.legend()
        
        # 设置等比例
        ax2.set_aspect("equal")
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        if plot_save:
            fig_path = figs_path / f"{example_name}-conc-head.png"
            plt.savefig(fig_path, dpi=300, bbox_inches="tight")
            print(f"Figure saved to: {fig_path}")
        
        # 显示图形
        if plot_show:
            plt.show()
        
        return ax1, ax2
# +
# Figure properties
figure_size = (6, 4.5)


# ### Running the example
#
# Define and invoke a function to run the example scenario, then plot results.


# +
def scenario(idx, silent=False):
    sim = build_models(example_name)
    if write:
        write_models(sim, silent=silent)
    # if run:
    #     run_models(sim, silent=silent)
    # if plot:
    #     plot_results(sim, idx)


scenario(0)
# -
