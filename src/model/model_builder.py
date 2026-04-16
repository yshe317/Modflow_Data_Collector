import flopy
import pathlib
import numpy as np
class Modflow6Builder:
    def __init__(self, scenario_loader):
        self.loader = scenario_loader
        self.scenario = scenario_loader.get_scenario()
        self.model = None
        self.sim_ws = pathlib.Path("simulations") / self.scenario["sim_name"]
        self.gwfname = "gwf"
        self.gwtfname = "gwt"
    def build(self):    
        # build simulation
        self.sim = flopy.mf6.MFSimulation(sim_name=self.scenario["sim_name"], sim_ws=self.sim_ws, exe_name="mf6")
        flopy.mf6.ModflowTdis(self.sim, nper=self.scenario["nper"], perioddata=self.scenario["tdis_rc"], time_units=self.scenario["time_units"])

        # build gwf model
        self._build_gwf()
        self._build_gwf_solver()
        
        # build gwt model
        self._build_gwt()
        
        # write simulation
        self.sim.write_simulation()
        return self.sim    
    def _build_gwf(self):
        gwfname = self.gwfname
        gwf = flopy.mf6.ModflowGwf(
            self.sim,
            modelname=gwfname,
            save_flows=True,
            model_nam_file=f"{gwfname}.nam",
        )


        top = self.loader.config_to_numpy(self.scenario["top"])
        botm = self.loader.config_to_numpy(self.scenario["botm"])
        flopy.mf6.ModflowGwfdis(
            gwf,
            length_units=self.scenario["length_units"],
            nlay=self.scenario["nlay"],
            nrow=self.scenario["nrow"],
            ncol=self.scenario["ncol"],
            delr=self.scenario["delr"],
            delc=self.scenario["delc"],
            top=top,
            botm=botm,
            idomain=np.ones((self.scenario["nlay"], self.scenario["nrow"], self.scenario["ncol"]), dtype=int),
            filename=f"{gwfname}.dis",
        )

        k11 = self.loader.config_to_numpy(self.scenario["k11"])
        k33 = self.loader.config_to_numpy(self.scenario["k33"])
        flopy.mf6.ModflowGwfnpf(
            gwf,
            save_flows=False,
            icelltype=self.scenario["icelltype"],
            k=k11,
            k33=k33,
            save_specific_discharge=True,
            filename=f"{gwfname}.npf",
        )

        initial_head = self.loader.config_to_numpy(self.scenario["initial_head"])
        flopy.mf6.ModflowGwfic(
            gwf,
            strt=initial_head,
            filename=f"{gwfname}.ic"
        )

        sto = flopy.mf6.ModflowGwfsto(gwf, ss=0, sy=0, filename=f"{gwfname}.sto")
        
        # 定水头
        chdspd = {}
        all_chdspd = self.scenario["chdspd"]
        for key in all_chdspd.keys():
            chdspd[key] = []
            for posi in all_chdspd[key]:
                _posi = posi[0], posi[1], posi[2] 
                chdspd[key].append([_posi, initial_head[_posi]])
        flopy.mf6.ModflowGwfchd(
            gwf,
            maxbound=len(chdspd),
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
            stress_period_data=self.scenario["wellspd"],
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

    def _build_gwf_solver(self):
        imsgwf = flopy.mf6.ModflowIms(
            self.sim,
            print_option="SUMMARY",
            outer_dvclose=self.scenario["hclose"],
            outer_maximum=self.scenario["nouter"],
            under_relaxation="NONE",
            inner_maximum=self.scenario["ninner"],
            inner_dvclose=self.scenario["hclose"],
            rcloserecord=self.scenario["rclose"],
            linear_acceleration="CG",
            scaling_method="NONE",
            reordering_method="NONE",
            relaxation_factor=self.scenario["relax"],
            filename=f"{self.gwfname}.ims",
        )
        self.sim.register_ims_package(imsgwf, [self.gwfname])
    
    def _build_gwt(self):
        pass

    