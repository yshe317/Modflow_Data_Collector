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
        self.gwtname = "gwt"
    def build(self):    
        # build simulation
        self.sim = flopy.mf6.MFSimulation(sim_name=self.scenario["sim_name"], sim_ws=self.sim_ws, exe_name="mf6")
        flopy.mf6.ModflowTdis(self.sim, nper=self.scenario["nper"], perioddata=self.scenario["tdis_rc"], time_units=self.scenario["time_units"])

        # build gwf model
        self._build_gwf()
        self._build_gwf_solver()
        
        # build gwt model
        self._build_gwt()
        self._build_gwt_solver()

        # init
        # Instantiating MODFLOW 6 flow-transport exchange mechanism
        flopy.mf6.ModflowGwfgwt(
            self.sim,
            exgtype="GWF6-GWT6",
            exgmnamea=self.gwfname,
            exgmnameb=self.gwtname,
            filename=f"{self.scenario["sim_name"]}.gwfgwt",
        )

        # write simulation
        self.sim.write_simulation(silent=True)
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
        gwt = flopy.mf6.MFModel(
            self.sim,
            model_type="gwt6",
            modelname=self.gwtname,
            model_nam_file=f"{self.gwtname}.nam",
        )
        gwt.name_file.save_flows = True
        top = self.loader.config_to_numpy(self.scenario["top"])
        botm = self.loader.config_to_numpy(self.scenario["botm"])
        # Dis
        flopy.mf6.ModflowGwtdis(
            gwt,
            length_units=self.scenario["length_units"],
            nlay=self.scenario["nlay"],
            nrow=self.scenario["nrow"],
            ncol=self.scenario["ncol"],
            delr=self.scenario["delr"],
            delc=self.scenario["delc"],
            top=top,
            botm=botm,
            idomain=np.ones((self.scenario["nlay"], self.scenario["nrow"], self.scenario["ncol"]), dtype=int),
            filename=f"{self.gwtname}.dis",
        )

        # Instantiating MODFLOW 6 transport initial concentrations
        sconc = self.loader.config_to_numpy(self.scenario["sconc"])
        flopy.mf6.ModflowGwtic(gwt, strt=sconc, filename=f"{self.gwtname}.ic")
        
        # Instantiating MODFLOW 6 transport advection package
        scheme = None
        if self.scenario['mixelm'] == 0:
            scheme = "UPSTREAM"
        elif self.scenario['mixelm']  == -1:
            scheme = "TVD"
        else:
            raise Exception()
        flopy.mf6.ModflowGwtadv(gwt, scheme=scheme, filename=f"{self.gwtname}.adv")
    
        if self.scenario['al'] != 0:
            flopy.mf6.ModflowGwtdsp(
                gwt,
                xt3d_off=True,
                alh=self.scenario['al'],
                ath1=self.scenario['al'] * self.scenario['trpt'],
                filename=f"{self.gwtname}.dsp",
            )

        # Instantiating MODFLOW 6 transport mass storage package (formerly "reaction" package in MT3DMS)
        prsity = self.loader.config_to_numpy(self.scenario["prsity"])
        flopy.mf6.ModflowGwtmst(
            gwt,
            porosity=prsity,
            first_order_decay=False,
            decay=None,
            decay_sorbed=None,
            sorption=None,
            bulk_density=None,
            distcoef=None,
            filename=f"{self.gwtname}.mst",
        )

        # Instantiating MODFLOW 6 transport constant concentration package
        
        
        if self.scenario['cncspd']:
            cncspd = {}
            all_cncspd = self.scenario["chdspd"]
            for key in all_cncspd.keys():
                cncspd[key] = []
                for posi in all_cncspd[key]:
                    _posi = posi[0], posi[1], posi[2] 
                    cncspd[key].append([_posi, sconc[_posi]])
            flopy.mf6.ModflowGwtcnc(
                gwt,
                maxbound=len(cncspd),
                stress_period_data=cncspd,
                save_flows=False,
                pname="CNC-1",
                filename=f"{self.gwtname}.cnc",
            )

        # Instantiating MODFLOW 6 transport source-sink mixing package
        sourcerecarray = [("WEL-1", "AUX", "CONCENTRATION")]
        flopy.mf6.ModflowGwtssm(gwt, sources=sourcerecarray, filename=f"{self.gwtname}.ssm")

        # Instantiating MODFLOW 6 transport output control package
        flopy.mf6.ModflowGwtoc(
            gwt,
            budget_filerecord=f"{self.gwtname}.cbc",
            concentration_filerecord=f"{self.gwtname}.ucn",
            concentrationprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
            saverecord=[("CONCENTRATION", "ALL"), ("BUDGET", "ALL")],
            printrecord=[("CONCENTRATION", "LAST"), ("BUDGET", "LAST")],
        )
    def _build_gwt_solver(self):
        imsgwt = flopy.mf6.ModflowIms(
            self.sim,
            print_option="SUMMARY",
            outer_dvclose=self.scenario["hclose"],
            outer_maximum=self.scenario["nouter"],
            under_relaxation="NONE",
            inner_maximum=self.scenario["ninner"],
            inner_dvclose=self.scenario["hclose"],
            rcloserecord=self.scenario["rclose"],
            linear_acceleration="BICGSTAB",
            scaling_method="NONE",
            reordering_method="NONE",
            relaxation_factor=self.scenario["relax"],
            filename=f"{self.gwtname}.ims",
        )
        self.sim.register_ims_package(imsgwt, [self.gwtname])