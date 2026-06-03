
import os
import pathlib
import json

import numpy as np

class ScenarioWriter:
    def __init__(self, scenario_name, scenarios_dir = "scenarios"):
        self.path = pathlib.Path(scenarios_dir) / scenario_name

        self.scenario = {
            # Model parameters
            "sim_name":scenario_name,
            ## general
            "tif_template" : None,
            "length_units" : "meters", # default is meters 
            "time_units" : None, # default is days
            "icelltype" : 0, # default is 0
            "mixelm" : 0,
            ### model geometry
            "nlay" : None,  # Number of layers
            "nrow" : None,  # Number of rows
            "ncol" : None,  # Number of columns
            "delr" : None,  # Column width ($m$)
            "delc" : None,  # Row width ($m$)
            "delz" : None,  # Layer thickness ($m$)
            "idomain" : None,
            ### model times
            "nper" : None,
            "tdis_rc" : None,    # time step interval
                
            ## for flow model
            "prsity" : 0.3,  # Porosity ($$)
            "k11" : None,  # Horizontal hydraulic conductivity ($m/d$)
            "initial_head" : None,
            'chdspd' : {},
            'wellspd' : {},
            
            ## for pollution model
            "source" : [],
            "al" : 0,  # Longitudinal dispersivity ($m$)
            "trpt" : 0.3,  # Ratio of transverse to longitudinal dispersivity
            "cncspd":None, 
        }
        # make scenario_name as a dir
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    def set_tif_template(self, tif_name):
        self.scenario["tif_template"] = str(tif_name)

    def set_time(self, nper, perlen, nstp, tsmult, unit="days"):
        """ 
        "nper" : None,       # number of periods
        "perlen" : None,     # period length (unit)
        "nstp" : None,       # number of time steps per period
        "tsmult" : None,    # time multiplier
        """
        if type(perlen) != list:
            perlen = [perlen] * nper
        if type(nstp) != list:
            nstp = [nstp] * nper
        if type(tsmult) != list:
            tsmult = [tsmult] * nper
        
        tdis_rc = []
        for i in range(nper):
            tdis_rc.append((perlen[i], nstp[i], tsmult[i]))
        self.scenario["time_units"] = unit
        self.scenario["nper"] = nper
        self.scenario["tdis_rc"] = tdis_rc
        
    def set_discretization(self, nlay, nrow, ncol, delr, delc, delz, top, botm):
        self.scenario["nlay"] = nlay
        self.scenario["nrow"] = nrow
        self.scenario["ncol"] = ncol
        self.scenario["delr"] = delr
        self.scenario["delc"] = delc
        self.scenario["delz"] = delz
        self.scenario["top"] = top
        self.scenario["botm"] = botm
    
    def set_k(self, k11, k33=None):
        if k33 is None:
            k33 = k11
        self.scenario["k11"] = k11
        self.scenario["k33"] = k33

    def set_initial_head(self, initial_head):
        self.scenario["initial_head"] = initial_head

    def set_idomain(self, idomain):
        self.scenario["idomain"] = idomain

    def set_constant_head(self, chdspd_posi, target_period=0):
        """
        chdspd_posi : 位置列表，如[[0,1,2], [0,3,4]]
        """
        self.scenario['chdspd'][target_period] = chdspd_posi
    
    def set_well(self, spd, target_period=0):
        """
        spd: [(z,x,y), qwell, cwell]
        qwell: Volumetric injection rate ($m^3/d$)
        cwell: Concentration of injected water ($mg/L$)
        """
        self.scenario['wellspd'][target_period] = spd

    def set_flowmodel_solver(self, hclose, nouter, ninner, rclose, relax):
        self.scenario["hclose"] = hclose
        self.scenario["nouter"] = nouter
        self.scenario["ninner"] = ninner
        self.scenario["rclose"] = rclose
        self.scenario["relax"] = relax
    
    def set_initial_concentration(self,initial_concentration):
        self.scenario['sconc'] = initial_concentration
    
    def set_al(self, al, trt,diffc= 3e-10):
        self.scenario['al'] = al
        self.scenario['trt'] = trt
        self.scenario['diffc'] = diffc
    def set_cncspd(self,cncspd_posi, target_period=0):
        if not self.scenario['cncspd']:
            self.scenario['cncspd'] = {}
        self.scenario['cncspd'][target_period] = cncspd_posi

    def write(self):
        with open(os.path.join(self.path, "scenario.json"), "w") as f:
            f.write(json.dumps(self.scenario, indent=4))
        