
# =========================================
# file: nikan_drill_master/modules/__init__.py
# =========================================
from __future__ import annotations
from typing import Callable
from sqlalchemy.orm import Session
from modules.base import ModuleBase
from modules.well_info import WellInfoModule
from modules.code_management import CodeManagementModule
from modules.daily_report import DailyReportModule
from modules.drilling_parameters import DrillingParametersModule
from modules.mud_report import MudReportModule
from modules.bha import BHAModule
from modules.inventory import InventoryModule
from modules.survey_data import SurveyDataModule
from modules.pob import POBModule
from modules.preferences import PreferencesModule
from modules.supervisor_signature import SupervisorSignatureModule
from modules.export_center import ExportCenterModule
from modules.npt_report import NPTReportModule
from modules.service_company_log import ServiceCompanyLogModule
from modules.fuel_water import FuelWaterModule
from modules.downhole_equipment import DownholeEquipmentModule
from modules.time_breakdown import TimeBreakdownModule

MODULES: dict[str, tuple[str, Callable[[Callable[[], Session]], ModuleBase]]] = {}

def register_modules(SessionLocal: Callable[[], Session]) -> None:
    # نظم مطابق ریبون:
    MODULES["well_info"] = ("Well Info", lambda S: WellInfoModule(S))
    MODULES["code_mgmt"] = ("Code Management", lambda S: CodeManagementModule(S))
    MODULES["daily_report"] = ("Daily Report", lambda S: DailyReportModule(S))
    MODULES["drill_params"] = ("Drilling Parameters", lambda S: DrillingParametersModule(S))
    MODULES["mud_report"] = ("Mud Report", lambda S: MudReportModule(S))
    MODULES["bha"] = ("BHA Report", lambda S: BHAModule(S))
    MODULES["inventory"] = ("Inventory", lambda S: InventoryModule(S))
    MODULES["survey"] = ("Survey Data", lambda S: SurveyDataModule(S))
    MODULES["pob"] = ("POB", lambda S: POBModule(S))
    MODULES["preferences"] = ("Preferences", lambda S: PreferencesModule(S))
    MODULES["supervisor_signature"] = ("Supervisor Signature", lambda S: SupervisorSignatureModule(S))
    MODULES["export_center"] = ("Export Center", lambda S: ExportCenterModule(S))
    MODULES["npt"] = ("NPT Report", lambda S: NPTReportModule(S))
    MODULES["service_log"] = ("Service Company Log", lambda S: ServiceCompanyLogModule(S))
    MODULES["fuel_water"] = ("Fuel & Water", lambda S: FuelWaterModule(S))
    MODULES["downhole_equipment"] = ("Downhole Equipment", lambda S: DownholeEquipmentModule(S))
    MODULES["time_breakdown"] = ("Time Breakdown", lambda S: TimeBreakdownModule(S))
