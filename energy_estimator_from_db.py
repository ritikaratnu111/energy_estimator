import sys,os
import logging
import json
import constants
from helper_functions import fabric, tbgen
from helper_functions import VesylaOutput
from measurement import Measurement
import ast

JSON_PATH = "/media/storage1/ritika/energy_estimator/json_files/"

class EnergyEstimator():
    def __init__(self):
        self.testbenches = {}
        self.FABRIC_PATH = ""
        self.logger = None
        self.estimate = {}
        self.debug = {}
        logging.basicConfig(level=logging.DEBUG)

    def get_fabric(self):
        self.FABRIC_PATH = fabric.set_path()
        os.environ['FABRIC_PATH'] = self.FABRIC_PATH

    def get_testbenches(self):
        self.testbenches = tbgen.set_testbenches("db")

    def update_logger(self, path, name, about):
        LOGFILE = f"{path}/activity_gen.log"
        try:
            with open(LOGFILE, 'w'): pass
            self.logger = logging.getLogger()
            handler = logging.FileHandler(LOGFILE)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.info(f"Testbench: {name}")
            self.logger.info(f"About: {about}")
        except Exception as e:
            print(f"Failed to set logfile: {e}")
            self.logger = None

    def get_cells(self, tb, start, end):
        activity = json.load(open(f"{tb}/activity.json"))
        db = f"{JSON_PATH}/primitive_components/"
        for cell, info in activity.items():
            self.estimate[cell] = {}
            total = Measurement()
            nets = 0
            for component, component_info in info.items():
                mode = component_info["mode"]
                logging.info(component)
                T_active = int(component_info["active"]) * constants.CLOCK_PERIOD 
                T_inactive = int(component_info["inactive"]) * constants.CLOCK_PERIOD
                current_active = Measurement()
                current_inactive = Measurement()
                db_active = json.load(open(f"{db}/{component}.json"))["mode"][mode]["active"]
                db_inactive = json.load(open(f"{db}/{component}.json"))["mode"][mode]["inactive"]
                print(T_active, T_inactive)
                print(db_active, db_inactive)
                current_active.update_from_db(db_active, T_active) 
                current_inactive.update_from_db(db_inactive, T_inactive) 
                estimate = current_active + current_inactive
                total = total + estimate
                self.estimate[cell][component] = {
                    "power"    : {
                        "internal"  : estimate.power.internal,
                        "switching"  : estimate.power.switching,
                        "leakage"  : estimate.power.leakage
                    },

                    "energy"    : {
                        "internal"  : estimate.energy.internal,
                        "switching"  : estimate.energy.switching,
                        "leakage"  : estimate.energy.leakage
                    }0.347904990000
                }
            self.estimate[cell]["total"] = {
                "power"    : {
                    "internal"  : total.power.internal,
                    "switching"  : total.power.switching,
                    "leakage"  : total.power.leakage
                },
                "energy"    : {
                    "internal"  : total.energy.internal,
                    "switching"  : total.energy.switching,
                    "leakage"  : total.energy.leakage
                }
        }

    def generate_estimates(self):
        for name, info in self.testbenches.items():
            if info["to_run"] == True:
                tb = info["path"]
                self.update_logger(tb, name, info['about'])
                self.get_cells(tb, 0, 1)
                self.write_energy(tb)
    
    def write_energy(self, tb):
        with open(f"{tb}/estimate_db.json", "w") as file:
            data = json.dumps(self.estimate, indent = 2)
            file.write(data)
