import flopy
import pathlib
import numpy as np
class Modflow6Builder:
    def __init__(self, scenario):
        self.scenario = scenario
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

        flopy.mf6.ModflowGwfdis(
            gwf,
            length_units=self.scenario["length_units"],
            nlay=self.scenario["nlay"],
            nrow=self.scenario["nrow"],
            ncol=self.scenario["ncol"],
            delr=self.scenario["delr"],
            delc=self.scenario["delc"],
            top=self.scenario["top"],
            botm=self.scenario["botm"],
            idomain=np.ones((self.scenario["nlay"], self.scenario["nrow"], self.scenario["ncol"]), dtype=int),
            filename=f"{gwfname}.dis",
        )

        flopy.mf6.ModflowGwfnpf(
            gwf,
            save_flows=False,
            icelltype=self.scenario["icelltype"],
            k=self.scenario["k11"],
            k33=self.scenario["k33"],
            save_specific_discharge=True,
            filename=f"{gwfname}.npf",
        )

        flopy.mf6.ModflowGwfic(
            gwf,
            strt=self.scenario["initial_head"],
            filename=f"{gwfname}.ic"
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

    