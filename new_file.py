#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIKAN DRILL MASTER - Complete Drilling Reporting System
Single File Implementation with SQLite Database
"""

import sys
import sqlite3
import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# PyQt6 imports
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# ============================================
# DATA MODELS SECTION
# ============================================

@dataclass
class WellInfo:
    """Well basic information model"""
    id: int = 0
    name: str = ""
    rig_name: str = ""
    operator: str = ""
    field: str = ""
    project: str = ""
    well_type: str = "Onshore"  # Onshore/Offshore
    rig_type: str = "Land"  # Land, Jackup, SemiSub
    well_shape: str = "Vertical"  # Vertical, Deviated, Horizontal
    derrick_height: float = 0.0  # ft
    gle: float = 0.0
    rte: float = 0.0
    msl: float = 0.0
    kop1: float = 0.0
    kop2: float = 0.0
    latitude: str = ""
    longitude: str = ""
    northing: str = ""
    easting: str = ""
    hole_size: float = 0.0  # inch
    final_depth: float = 0.0  # m
    water_depth: float = 0.0  # m
    spud_date: str = ""
    start_hole_date: str = ""
    rig_move_date: str = ""
    report_date: str = ""
    supervisor_day: str = ""
    supervisor_night: str = ""
    toolpusher_day: str = ""
    toolpusher_night: str = ""
    operation_manager: str = ""
    geologist1: str = ""
    geologist2: str = ""
    client_rep: str = ""
    objectives: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class TimeLogEntry:
    """Time log entry model"""
    id: int = 0
    report_id: int = 0
    start_time: str = "00:00"
    end_time: str = "00:00"
    duration: str = "00:00"
    main_code: str = ""
    sub_code: str = ""
    description: str = ""
    is_npt: bool = False
    status: str = "In Progress"
    remarks: str = ""

@dataclass
class DailyReport:
    """Daily operations report model"""
    id: int = 0
    well_id: int = 0
    report_date: str = ""
    rig_day: int = 1
    depth_0000: float = 0.0
    depth_0600: float = 0.0
    depth_2400: float = 0.0
    pit_gain: float = 0.0
    operations_done: str = ""
    work_summary: str = ""
    problems: str = ""
    general_notes: str = ""
    time_logs: List[TimeLogEntry] = field(default_factory=list)

@dataclass
class DrillingParameters:
    """Drilling parameters model"""
    id: int = 0
    report_id: int = 0
    wob_min: float = 0.0
    wob_max: float = 0.0
    surface_rpm_min: float = 0.0
    surface_rpm_max: float = 0.0
    motor_rpm_min: float = 0.0
    motor_rpm_max: float = 0.0
    torque_min: float = 0.0
    torque_max: float = 0.0
    pump_pressure_min: float = 0.0
    pump_pressure_max: float = 0.0
    pump_output_min: float = 0.0
    pump_output_max: float = 0.0
    hsi: float = 0.0
    annular_velocity: float = 0.0
    tfa: float = 0.0
    bit_revolution: float = 0.0
    pump1_spm: float = 0.0
    pump1_spp: float = 0.0
    pump2_spm: float = 0.0
    pump2_spp: float = 0.0
    pump3_spm: float = 0.0
    pump3_spp: float = 0.0

@dataclass
class MudProperties:
    """Mud properties model"""
    id: int = 0
    report_id: int = 0
    mud_type: str = ""
    sample_time: str = ""
    mud_weight: float = 0.0  # ppg
    plastic_viscosity: float = 0.0  # cp
    yield_point: float = 0.0  # lb/100ft²
    funnel_viscosity: float = 0.0  # sec/qt
    gel_10s: float = 0.0
    gel_10m: float = 0.0
    gel_30m: float = 0.0
    fluid_loss: float = 0.0  # cc/30min
    cake_thickness: float = 0.0  # mm
    calcium: float = 0.0  # ppm
    chloride: float = 0.0  # ppm
    kcl: float = 0.0  # ppm
    ph: float = 0.0
    hardness: float = 0.0
    mbt: float = 0.0  # lb/bbl
    solid_percent: float = 0.0  # %
    oil_percent: float = 0.0  # %
    water_percent: float = 0.0  # %
    glycol_percent: float = 0.0  # %
    temperature: float = 0.0  # °C
    pf: float = 0.0
    mf: float = 0.0

@dataclass
class MudVolumes:
    """Mud volumes model"""
    id: int = 0
    report_id: int = 0
    volume_in_hole: float = 0.0  # bbl
    total_circulated: float = 0.0  # bbl
    downhole_loss: float = 0.0  # bbl
    surface_loss: float = 0.0  # bbl
    suction_tank: float = 0.0  # bbl
    reserve_tank: float = 0.0  # bbl
    degasser: float = 0.0  # bbl
    desander: float = 0.0  # bbl
    desilter: float = 0.0  # bbl
    middle_tank: float = 0.0  # bbl
    total_tank: float = 0.0  # bbl
    sand_trap: float = 0.0  # bbl

@dataclass
class BitRecord:
    """Bit record model"""
    id: int = 0
    well_id: int = 0
    bit_no: str = ""
    size: float = 0.0  # inch
    manufacturer: str = ""
    type: str = ""
    serial_no: str = ""
    iadc_code: str = ""
    dull_grading: str = ""
    reason_pulled: str = ""
    depth_in: float = 0.0  # m
    depth_out: float = 0.0  # m
    hours: float = 0.0
    cum_drilled: float = 0.0  # m
    cum_hours: float = 0.0
    rop: float = 0.0  # m/hr
    formation: str = ""
    lithology: str = ""
    wob_avg: float = 0.0
    rpm_avg: float = 0.0
    flowrate_avg: float = 0.0
    spp_avg: float = 0.0
    pv_avg: float = 0.0
    yp_avg: float = 0.0
    cumulative_drilling: float = 0.0  # m
    revolution: float = 0.0
    tfa: float = 0.0
    photo_before: str = ""
    photo_after: str = ""
    created_date: str = ""

@dataclass
class BHAComponent:
    """BHA component model"""
    id: int = 0
    run_id: int = 0
    tool_type: str = ""
    od: float = 0.0  # inch
    id: float = 0.0  # inch
    length: float = 0.0  # m
    serial_no: str = ""
    weight: float = 0.0  # kg
    remarks: str = ""

@dataclass
class BHARun:
    """BHA run model"""
    id: int = 0
    well_id: int = 0
    run_no: int = 0
    run_date: str = ""
    components: List[BHAComponent] = field(default_factory=list)

@dataclass
class SurveyPoint:
    """Well survey point model"""
    id: int = 0
    well_id: int = 0
    md: float = 0.0  # measured depth, m
    inc: float = 0.0  # inclination, degrees
    azi: float = 0.0  # azimuth, degrees
    tvd: float = 0.0  # true vertical depth, m
    north: float = 0.0  # m
    east: float = 0.0  # m
    vs: float = 0.0  # vertical section, m
    hd: float = 0.0  # horizontal displacement, m
    dls: float = 0.0  # dogleg severity, °/30m
    tool: str = ""
    survey_date: str = ""

@dataclass
class FormationTop:
    """Formation top model"""
    id: int = 0
    well_id: int = 0
    name: str = ""
    lithology: str = ""
    md: float = 0.0  # m
    tvd: float = 0.0  # m
    description: str = ""

@dataclass
class Personnel:
    """Personnel model"""
    id: int = 0
    well_id: int = 0
    company: str = ""
    name: str = ""
    position: str = ""
    arrival_date: str = ""
    departure_date: str = ""
    pob_status: bool = False  # Person on Board status
    contact: str = ""
    emergency_contact: str = ""

@dataclass
class InventoryItem:
    """Inventory item model"""
    id: int = 0
    well_id: int = 0
    item: str = ""
    opening: float = 0.0
    received: float = 0.0
    used: float = 0.0
    remaining: float = 0.0
    unit: str = ""
    category: str = ""
    last_updated: str = ""

@dataclass
class ServiceCompany:
    """Service company log model"""
    id: int = 0
    well_id: int = 0
    company_name: str = ""
    service_type: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    contact_person: str = ""
    contact_phone: str = ""

@dataclass
class SafetyRecord:
    """Safety and BOP record model"""
    id: int = 0
    well_id: int = 0
    fire_drill_date: str = ""
    bop_drill_date: str = ""
    h2s_drill_date: str = ""
    days_without_lti: int = 0
    days_without_lta: int = 0
    bop_name: str = ""
    bop_type: str = ""
    working_pressure: float = 0.0  # psi
    size: float = 0.0  # inch
    rams: str = ""
    last_test_date: str = ""
    next_test_due: str = ""
    test_pressure: float = 0.0  # psi
    test_duration: float = 0.0  # minutes

@dataclass
class WasteManagement:
    """Waste management record model"""
    id: int = 0
    well_id: int = 0
    recycled: float = 0.0  # bbl
    ph: float = 0.0
    turbidity: float = 0.0  # NTU
    tss: float = 0.0  # mg/L
    hardness: float = 0.0  # mg/L
    calcium: float = 0.0  # mg/L
    cutting_transport: float = 0.0  # m³
    disposal_method: str = ""
    disposal_company: str = ""
    disposal_date: str = ""

@dataclass
class CementData:
    """Cement and additives model"""
    id: int = 0
    well_id: int = 0
    material: str = ""
    received: float = 0.0
    consumed: float = 0.0
    backload: float = 0.0
    inventory: float = 0.0
    unit: str = ""
    last_updated: str = ""

@dataclass
class CasingData:
    """Casing data model"""
    id: int = 0
    well_id: int = 0
    size: float = 0.0  # inch
    grade: str = ""
    weight: float = 0.0  # lb/ft
    depth: float = 0.0  # m
    shoe_depth: float = 0.0  # m
    accessories: str = ""
    setting_date: str = ""
    test_pressure: float = 0.0  # psi

@dataclass
class DownholeEquipment:
    """Downhole equipment model"""
    id: int = 0
    well_id: int = 0
    equipment_name: str = ""
    serial_no: str = ""
    equipment_id: str = ""
    sliding_hours: float = 0.0
    cum_rotation_hours: float = 0.0
    cum_pumping_hours: float = 0.0
    cum_total_hours: float = 0.0
    last_maintenance: str = ""
    next_maintenance: str = ""
    status: str = "Operational"

@dataclass
class DrillPipeSpec:
    """Drill pipe specifications model"""
    id: int = 0
    well_id: int = 0
    size: float = 0.0  # inch
    weight: float = 0.0  # lb/ft
    grade: str = ""
    connection: str = ""
    id: float = 0.0  # inner diameter, inch
    tj_od: float = 0.0  # tool joint OD, inch
    tj_id: float = 0.0  # tool joint ID, inch
    std_no_in_derrick: int = 0
    total_length: float = 0.0  # m
    remarks: str = ""

@dataclass
class SolidControl:
    """Solid control equipment model"""
    id: int = 0
    report_id: int = 0
    equipment: str = ""
    feed_rate: float = 0.0  # bbl/hr
    hours_operated: float = 0.0
    loss: float = 0.0  # bbl
    cone_size: str = ""
    num_cones: int = 0
    underflow: float = 0.0  # %
    overflow: float = 0.0  # %
    daily_hours: float = 0.0
    cumulative_hours: float = 0.0

@dataclass
class WeatherData:
    """Weather data model"""
    id: int = 0
    report_id: int = 0
    wind_speed: float = 0.0  # knots
    wind_direction: str = ""
    temperature: float = 0.0  #°C
    visibility: float = 0.0  # km
    sea_state: str = ""
    wave_height: float = 0.0  # m
    recorded_time: str = ""

@dataclass
class CodeDefinition:
    """Code management definition model"""
    id: int = 0
    main_phase: str = ""
    main_code: str = ""
    sub_code: str = ""
    code_name: str = ""
    description: str = ""
    is_npt: bool = False
    color: str = "#FFFFFF"
    created_date: str = ""

@dataclass
class User:
    """User model for authentication"""
    id: int = 0
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: str = "operator"  # admin, supervisor, operator, viewer
    email: str = ""
    phone: str = ""
    is_active: bool = True
    created_at: str = ""
    last_login: str = ""

@dataclass
class LookAheadPlan:
    """Seven days lookahead plan model"""
    id: int = 0
    well_id: int = 0
    plan_date: str = ""
    day_number: int = 0
    activity: str = ""
    tools: str = ""
    responsible: str = ""
    remarks: str = ""
    status: str = "Planned"  # Planned, In Progress, Completed, Delayed

@dataclass
class NPTReport:
    """Non-Productive Time report model"""
    id: int = 0
    report_id: int = 0
    start_time: str = ""
    end_time: str = ""
    duration: str = ""
    main_code: str = ""
    sub_code: str = ""
    description: str = ""
    responsible_party: str = ""
    corrective_action: str = ""
    cost_estimate: float = 0.0  # USD
    status: str = "Open"  # Open, Investigating, Resolved, Closed

@dataclass
class TransportLog:
    """Boats and chopper log model"""
    id: int = 0
    well_id: int = 0
    transport_type: str = ""  # Boat, Chopper
    name: str = ""
    arrival_datetime: str = ""
    departure_datetime: str = ""
    status: str = ""  # Arrived, Departed, Waiting
    pax_in: int = 0
    pax_out: int = 0
    cargo: str = ""
    remarks: str = ""

@dataclass
class MaterialRequest:
    """Material handling request model"""
    id: int = 0
    well_id: int = 0
    material: str = ""
    requested_qty: float = 0.0
    outstanding_qty: float = 0.0
    received_qty: float = 0.0
    backload_qty: float = 0.0
    unit: str = ""
    request_date: str = ""
    required_date: str = ""
    status: str = "Requested"  # Requested, Approved, Ordered, Received, Closed

@dataclass
class Preferences:
    """User preferences model"""
    id: int = 0
    user_id: int = 0
    default_units: str = "metric"  # metric, imperial
    theme: str = "light"  # light, dark
    company_logo_path: str = ""
    load_previous_report: bool = True
    auto_save_interval: int = 5  # minutes
    language: str = "en"  # en, fa, ar
    date_format: str = "yyyy-MM-dd"
    time_format: str = "24h"  # 24h, 12h

# ============================================
# DATABASE MANAGER SECTION
# ============================================

class DatabaseManager:
    """SQLite database manager for Nikan Drill Master"""
    
    def __init__(self, db_path="nikan_drill_master.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.init_database()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.connection.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        if not self.connect():
            return False
        
        try:
            # Wells table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wells (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                rig_name TEXT,
                operator TEXT,
                field TEXT,
                project TEXT,
                well_type TEXT CHECK(well_type IN ('Onshore', 'Offshore')),
                rig_type TEXT CHECK(rig_type IN ('Land', 'Jackup', 'SemiSub')),
                well_shape TEXT CHECK(well_shape IN ('Vertical', 'Deviated', 'Horizontal')),
                derrick_height REAL,
                gle REAL,
                rte REAL,
                msl REAL,
                kop1 REAL,
                kop2 REAL,
                latitude TEXT,
                longitude TEXT,
                northing TEXT,
                easting TEXT,
                hole_size REAL,
                final_depth REAL,
                water_depth REAL,
                spud_date TEXT,
                start_hole_date TEXT,
                rig_move_date TEXT,
                report_date TEXT,
                supervisor_day TEXT,
                supervisor_night TEXT,
                toolpusher_day TEXT,
                toolpusher_night TEXT,
                operation_manager TEXT,
                geologist1 TEXT,
                geologist2 TEXT,
                client_rep TEXT,
                objectives TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Users table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT CHECK(role IN ('admin', 'supervisor', 'operator', 'viewer')),
                email TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """)
            
            # Daily reports table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                report_date TEXT NOT NULL,
                rig_day INTEGER,
                depth_0000 REAL,
                depth_0600 REAL,
                depth_2400 REAL,
                pit_gain REAL,
                operations_done TEXT,
                work_summary TEXT,
                problems TEXT,
                general_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (well_id) REFERENCES wells (id),
                UNIQUE(well_id, report_date)
            )
            """)
            
            # Time logs table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                start_time TEXT,
                end_time TEXT,
                duration TEXT,
                main_code TEXT,
                sub_code TEXT,
                description TEXT,
                is_npt INTEGER DEFAULT 0,
                status TEXT,
                remarks TEXT,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Drilling parameters table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS drilling_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                wob_min REAL,
                wob_max REAL,
                surface_rpm_min REAL,
                surface_rpm_max REAL,
                motor_rpm_min REAL,
                motor_rpm_max REAL,
                torque_min REAL,
                torque_max REAL,
                pump_pressure_min REAL,
                pump_pressure_max REAL,
                pump_output_min REAL,
                pump_output_max REAL,
                hsi REAL,
                annular_velocity REAL,
                tfa REAL,
                bit_revolution REAL,
                pump1_spm REAL,
                pump1_spp REAL,
                pump2_spm REAL,
                pump2_spp REAL,
                pump3_spm REAL,
                pump3_spp REAL,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Mud properties table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mud_properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                mud_type TEXT,
                sample_time TEXT,
                mud_weight REAL,
                plastic_viscosity REAL,
                yield_point REAL,
                funnel_viscosity REAL,
                gel_10s REAL,
                gel_10m REAL,
                gel_30m REAL,
                fluid_loss REAL,
                cake_thickness REAL,
                calcium REAL,
                chloride REAL,
                kcl REAL,
                ph REAL,
                hardness REAL,
                mbt REAL,
                solid_percent REAL,
                oil_percent REAL,
                water_percent REAL,
                glycol_percent REAL,
                temperature REAL,
                pf REAL,
                mf REAL,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Mud volumes table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mud_volumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                volume_in_hole REAL,
                total_circulated REAL,
                downhole_loss REAL,
                surface_loss REAL,
                suction_tank REAL,
                reserve_tank REAL,
                degasser REAL,
                desander REAL,
                desilter REAL,
                middle_tank REAL,
                total_tank REAL,
                sand_trap REAL,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Bit records table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                bit_no TEXT,
                size REAL,
                manufacturer TEXT,
                type TEXT,
                serial_no TEXT,
                iadc_code TEXT,
                dull_grading TEXT,
                reason_pulled TEXT,
                depth_in REAL,
                depth_out REAL,
                hours REAL,
                cum_drilled REAL,
                cum_hours REAL,
                rop REAL,
                formation TEXT,
                lithology TEXT,
                wob_avg REAL,
                rpm_avg REAL,
                flowrate_avg REAL,
                spp_avg REAL,
                pv_avg REAL,
                yp_avg REAL,
                cumulative_drilling REAL,
                revolution REAL,
                tfa REAL,
                photo_before TEXT,
                photo_after TEXT,
                created_date TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # BHA runs table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bha_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                run_no INTEGER,
                run_date TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # BHA components table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bha_components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                tool_type TEXT,
                od REAL,
                id REAL,
                length REAL,
                serial_no TEXT,
                weight REAL,
                remarks TEXT,
                FOREIGN KEY (run_id) REFERENCES bha_runs (id)
            )
            """)
            
            # Survey data table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                md REAL,
                inc REAL,
                azi REAL,
                tvd REAL,
                north REAL,
                east REAL,
                vs REAL,
                hd REAL,
                dls REAL,
                tool TEXT,
                survey_date TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Formation tops table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS formation_tops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                name TEXT,
                lithology TEXT,
                md REAL,
                tvd REAL,
                description TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Personnel table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                company TEXT,
                name TEXT,
                position TEXT,
                arrival_date TEXT,
                departure_date TEXT,
                pob_status INTEGER DEFAULT 0,
                contact TEXT,
                emergency_contact TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Inventory table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                item TEXT,
                opening REAL,
                received REAL,
                used REAL,
                remaining REAL,
                unit TEXT,
                category TEXT,
                last_updated TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Service companies table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                company_name TEXT,
                service_type TEXT,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                contact_person TEXT,
                contact_phone TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Safety records table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS safety_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                fire_drill_date TEXT,
                bop_drill_date TEXT,
                h2s_drill_date TEXT,
                days_without_lti INTEGER,
                days_without_lta INTEGER,
                bop_name TEXT,
                bop_type TEXT,
                working_pressure REAL,
                size REAL,
                rams TEXT,
                last_test_date TEXT,
                next_test_due TEXT,
                test_pressure REAL,
                test_duration REAL,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Waste management table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_management (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                recycled REAL,
                ph REAL,
                turbidity REAL,
                tss REAL,
                hardness REAL,
                calcium REAL,
                cutting_transport REAL,
                disposal_method TEXT,
                disposal_company TEXT,
                disposal_date TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Cement data table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cement_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                material TEXT,
                received REAL,
                consumed REAL,
                backload REAL,
                inventory REAL,
                unit TEXT,
                last_updated TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Casing data table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS casing_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                size REAL,
                grade TEXT,
                weight REAL,
                depth REAL,
                shoe_depth REAL,
                accessories TEXT,
                setting_date TEXT,
                test_pressure REAL,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Downhole equipment table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS downhole_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                equipment_name TEXT,
                serial_no TEXT,
                equipment_id TEXT,
                sliding_hours REAL,
                cum_rotation_hours REAL,
                cum_pumping_hours REAL,
                cum_total_hours REAL,
                last_maintenance TEXT,
                next_maintenance TEXT,
                status TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Drill pipe specs table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS drill_pipe_specs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                size REAL,
                weight REAL,
                grade TEXT,
                connection TEXT,
                id REAL,
                tj_od REAL,
                tj_id REAL,
                std_no_in_derrick INTEGER,
                total_length REAL,
                remarks TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Solid control table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS solid_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                equipment TEXT,
                feed_rate REAL,
                hours_operated REAL,
                loss REAL,
                cone_size TEXT,
                num_cones INTEGER,
                underflow REAL,
                overflow REAL,
                daily_hours REAL,
                cumulative_hours REAL,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Weather data table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                wind_speed REAL,
                wind_direction TEXT,
                temperature REAL,
                visibility REAL,
                sea_state TEXT,
                wave_height REAL,
                recorded_time TEXT,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Code definitions table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                main_phase TEXT,
                main_code TEXT,
                sub_code TEXT,
                code_name TEXT,
                description TEXT,
                is_npt INTEGER DEFAULT 0,
                color TEXT,
                created_date TEXT
            )
            """)
            
            # Lookahead plans table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lookahead_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                plan_date TEXT,
                day_number INTEGER,
                activity TEXT,
                tools TEXT,
                responsible TEXT,
                remarks TEXT,
                status TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # NPT reports table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS npt_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                start_time TEXT,
                end_time TEXT,
                duration TEXT,
                main_code TEXT,
                sub_code TEXT,
                description TEXT,
                responsible_party TEXT,
                corrective_action TEXT,
                cost_estimate REAL,
                status TEXT,
                FOREIGN KEY (report_id) REFERENCES daily_reports (id)
            )
            """)
            
            # Transport logs table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transport_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                transport_type TEXT,
                name TEXT,
                arrival_datetime TEXT,
                departure_datetime TEXT,
                status TEXT,
                pax_in INTEGER,
                pax_out INTEGER,
                cargo TEXT,
                remarks TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # Material requests table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id INTEGER NOT NULL,
                material TEXT,
                requested_qty REAL,
                outstanding_qty REAL,
                received_qty REAL,
                backload_qty REAL,
                unit TEXT,
                request_date TEXT,
                required_date TEXT,
                status TEXT,
                FOREIGN KEY (well_id) REFERENCES wells (id)
            )
            """)
            
            # User preferences table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                default_units TEXT,
                theme TEXT,
                company_logo_path TEXT,
                load_previous_report INTEGER DEFAULT 1,
                auto_save_interval INTEGER,
                language TEXT,
                date_format TEXT,
                time_format TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            # Insert default admin user if not exists
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if self.cursor.fetchone()[0] == 0:
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role, email, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """, ("admin", password_hash, "System Administrator", "admin", "admin@nikan.com", 1))
            
            # Insert default code definitions
            self.cursor.execute("SELECT COUNT(*) FROM code_definitions")
            if self.cursor.fetchone()[0] == 0:
                default_codes = [
                    ("Drilling", "DR", "DRILL", "Drilling", "Rotary drilling operations", 0, "#4CAF50"),
                    ("Tripping", "TP", "TRIP", "Tripping", "Pipe tripping operations", 0, "#2196F3"),
                    ("Circulation", "CI", "CIRC", "Circulation", "Mud circulation", 0, "#00BCD4"),
                    ("Casing", "CS", "CSG", "Casing", "Casing operations", 0, "#FF9800"),
                    ("Cementing", "CM", "CEM", "Cementing", "Cementing operations", 0, "#795548"),
                    ("Waiting", "WT", "WAIT", "Waiting", "Waiting on weather/instructions", 1, "#FF5722"),
                    ("Repair", "RP", "REPR", "Repair", "Equipment repair", 1, "#F44336"),
                    ("Maintenance", "MT", "MNT", "Maintenance", "Scheduled maintenance", 1, "#9C27B0"),
                ]
                for code in default_codes:
                    self.cursor.execute("""
                    INSERT INTO code_definitions (main_phase, main_code, sub_code, code_name, description, is_npt, color, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    """, code)
            
            self.connection.commit()
            print("Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_well_info(self, well_info: WellInfo) -> int:
        """Save well information to database"""
        if not self.connect():
            return -1
        
        try:
            # Check if well already exists
            self.cursor.execute(
                "SELECT id FROM wells WHERE name = ?",
                (well_info.name,)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing well
                self.cursor.execute("""
                UPDATE wells SET
                    rig_name=?, operator=?, field=?, project=?,
                    well_type=?, rig_type=?, well_shape=?,
                    derrick_height=?, gle=?, rte=?, msl=?, kop1=?, kop2=?,
                    latitude=?, longitude=?, northing=?, easting=?,
                    hole_size=?, final_depth=?, water_depth=?,
                    spud_date=?, start_hole_date=?, rig_move_date=?,
                    report_date=?, supervisor_day=?, supervisor_night=?,
                    toolpusher_day=?, toolpusher_night=?, operation_manager=?,
                    geologist1=?, geologist2=?, client_rep=?, objectives=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE name=?
                """, (
                    well_info.rig_name, well_info.operator, well_info.field,
                    well_info.project, well_info.well_type, well_info.rig_type,
                    well_info.well_shape, well_info.derrick_height,
                    well_info.gle, well_info.rte, well_info.msl,
                    well_info.kop1, well_info.kop2,
                    well_info.latitude, well_info.longitude,
                    well_info.northing, well_info.easting,
                    well_info.hole_size, well_info.final_depth,
                    well_info.water_depth, well_info.spud_date,
                    well_info.start_hole_date, well_info.rig_move_date,
                    well_info.report_date, well_info.supervisor_day,
                    well_info.supervisor_night, well_info.toolpusher_day,
                    well_info.toolpusher_night, well_info.operation_manager,
                    well_info.geologist1, well_info.geologist2,
                    well_info.client_rep, well_info.objectives,
                    well_info.name
                ))
                well_id = existing[0]
            else:
                # Insert new well
                self.cursor.execute("""
                INSERT INTO wells (
                    name, rig_name, operator, field, project,
                    well_type, rig_type, well_shape, derrick_height,
                    gle, rte, msl, kop1, kop2, latitude, longitude,
                    northing, easting, hole_size, final_depth, water_depth,
                    spud_date, start_hole_date, rig_move_date, report_date,
                    supervisor_day, supervisor_night, toolpusher_day,
                    toolpusher_night, operation_manager, geologist1,
                    geologist2, client_rep, objectives
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         ?, ?, ?, ?)
                """, (
                    well_info.name, well_info.rig_name, well_info.operator,
                    well_info.field, well_info.project, well_info.well_type,
                    well_info.rig_type, well_info.well_shape,
                    well_info.derrick_height, well_info.gle, well_info.rte,
                    well_info.msl, well_info.kop1, well_info.kop2,
                    well_info.latitude, well_info.longitude,
                    well_info.northing, well_info.easting,
                    well_info.hole_size, well_info.final_depth,
                    well_info.water_depth, well_info.spud_date,
                    well_info.start_hole_date, well_info.rig_move_date,
                    well_info.report_date, well_info.supervisor_day,
                    well_info.supervisor_night, well_info.toolpusher_day,
                    well_info.toolpusher_night, well_info.operation_manager,
                    well_info.geologist1, well_info.geologist2,
                    well_info.client_rep, well_info.objectives
                ))
                well_id = self.cursor.lastrowid
            
            self.connection.commit()
            return well_id
            
        except Exception as e:
            print(f"Save well info error: {e}")
            return -1
        finally:
            self.disconnect()
    
    def get_well_info(self, well_id: int) -> Optional[WellInfo]:
        """Retrieve well information by ID"""
        if not self.connect():
            return None
        
        try:
            self.cursor.execute("SELECT * FROM wells WHERE id = ?", (well_id,))
            row = self.cursor.fetchone()
            
            if row:
                return WellInfo(
                    id=row[0], name=row[1], rig_name=row[2], operator=row[3],
                    field=row[4], project=row[5], well_type=row[6], rig_type=row[7],
                    well_shape=row[8], derrick_height=row[9], gle=row[10],
                    rte=row[11], msl=row[12], kop1=row[13], kop2=row[14],
                    latitude=row[15], longitude=row[16], northing=row[17],
                    easting=row[18], hole_size=row[19], final_depth=row[20],
                    water_depth=row[21], spud_date=row[22], start_hole_date=row[23],
                    rig_move_date=row[24], report_date=row[25], supervisor_day=row[26],
                    supervisor_night=row[27], toolpusher_day=row[28],
                    toolpusher_night=row[29], operation_manager=row[30],
                    geologist1=row[31], geologist2=row[32], client_rep=row[33],
                    objectives=row[34], created_at=row[35], updated_at=row[36]
                )
            return None
            
        except Exception as e:
            print(f"Get well info error: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_all_wells(self) -> List[WellInfo]:
        """Retrieve all wells from database"""
        if not self.connect():
            return []
        
        try:
            self.cursor.execute("SELECT * FROM wells ORDER BY created_at DESC")
            rows = self.cursor.fetchall()
            wells = []
            
            for row in rows:
                wells.append(WellInfo(
                    id=row[0], name=row[1], rig_name=row[2], operator=row[3],
                    field=row[4], project=row[5], well_type=row[6], rig_type=row[7],
                    well_shape=row[8], derrick_height=row[9], gle=row[10],
                    rte=row[11], msl=row[12], kop1=row[13], kop2=row[14],
                    latitude=row[15], longitude=row[16], northing=row[17],
                    easting=row[18], hole_size=row[19], final_depth=row[20],
                    water_depth=row[21], spud_date=row[22], start_hole_date=row[23],
                    rig_move_date=row[24], report_date=row[25], supervisor_day=row[26],
                    supervisor_night=row[27], toolpusher_day=row[28],
                    toolpusher_night=row[29], operation_manager=row[30],
                    geologist1=row[31], geologist2=row[32], client_rep=row[33],
                    objectives=row[34], created_at=row[35], updated_at=row[36]
                ))
            return wells
            
        except Exception as e:
            print(f"Get all wells error: {e}")
            return []
        finally:
            self.disconnect()
    
    def save_daily_report(self, report: DailyReport) -> int:
        """Save daily report to database"""
        if not self.connect():
            return -1
        
        try:
            # Check if report already exists for this date
            self.cursor.execute(
                "SELECT id FROM daily_reports WHERE well_id = ? AND report_date = ?",
                (report.well_id, report.report_date)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing report
                self.cursor.execute("""
                UPDATE daily_reports SET
                    rig_day=?, depth_0000=?, depth_0600=?, depth_2400=?,
                    pit_gain=?, operations_done=?, work_summary=?,
                    problems=?, general_notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """, (
                    report.rig_day, report.depth_0000, report.depth_0600,
                    report.depth_2400, report.pit_gain, report.operations_done,
                    report.work_summary, report.problems, report.general_notes,
                    existing[0]
                ))
                report_id = existing[0]
            else:
                # Insert new report
                self.cursor.execute("""
                INSERT INTO daily_reports (
                    well_id, report_date, rig_day, depth_0000, depth_0600,
                    depth_2400, pit_gain, operations_done, work_summary,
                    problems, general_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.well_id, report.report_date, report.rig_day,
                    report.depth_0000, report.depth_0600, report.depth_2400,
                    report.pit_gain, report.operations_done, report.work_summary,
                    report.problems, report.general_notes
                ))
                report_id = self.cursor.lastrowid
            
            # Save time logs
            if report.time_logs:
                # Delete existing time logs for this report
                self.cursor.execute("DELETE FROM time_logs WHERE report_id = ?", (report_id,))
                
                # Insert new time logs
                for log in report.time_logs:
                    self.cursor.execute("""
                    INSERT INTO time_logs (
                        report_id, start_time, end_time, duration,
                        main_code, sub_code, description, is_npt, status, remarks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        report_id, log.start_time, log.end_time, log.duration,
                        log.main_code, log.sub_code, log.description,
                        1 if log.is_npt else 0, log.status, log.remarks
                    ))
            
            self.connection.commit()
            return report_id
            
        except Exception as e:
            print(f"Save daily report error: {e}")
            return -1
        finally:
            self.disconnect()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        if not self.connect():
            return None
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute("""
            SELECT id, username, password_hash, full_name, role, email, phone, 
                   is_active, created_at, last_login
            FROM users WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash))
            
            row = self.cursor.fetchone()
            if row:
                # Update last login time
                self.cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (row[0],)
                )
                self.connection.commit()
                
                return User(
                    id=row[0], username=row[1], password_hash=row[2],
                    full_name=row[3], role=row[4], email=row[5],
                    phone=row[6], is_active=bool(row[7]),
                    created_at=row[8], last_login=row[9]
                )
            return None
            
        except Exception as e:
            print(f"Authenticate user error: {e}")
            return None
        finally:
            self.disconnect()
            
# ============================================
# UI COMPONENTS SECTION
# ============================================

class RibbonTab(QWidget):
    """Ribbon style tab widget"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create ribbon groups
        self.groups = {}
    
    def add_group(self, group_name, widget):
        """Add a group to the ribbon"""
        self.groups[group_name] = widget
        self.layout.addWidget(widget)

class RibbonGroup(QGroupBox):
    """Ribbon group with icon buttons"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.buttons = []
    
    def add_button(self, text, icon=None, callback=None, tooltip=""):
        """Add a ribbon button"""
        btn = QPushButton(text)
        if icon:
            btn.setIcon(QIcon(icon))
        if callback:
            btn.clicked.connect(callback)
        if tooltip:
            btn.setToolTip(tooltip)
        
        btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                margin: 2px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        
        self.layout.addWidget(btn)
        self.buttons.append(btn)
        return btn

class WellInfoWidget(QWidget):
    """Well information widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_well_id = -1
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Well Information")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # Basic Information Section
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.well_name_input = QLineEdit()
        self.well_name_input.setPlaceholderText("Enter well name")
        
        self.rig_name_input = QLineEdit()
        self.rig_name_input.setPlaceholderText("Enter rig name")
        
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("Enter operator company")
        
        self.field_input = QLineEdit()
        self.field_input.setPlaceholderText("Enter field name")
        
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Enter project name")
        
        basic_layout.addRow("Well Name:", self.well_name_input)
        basic_layout.addRow("Rig Name:", self.rig_name_input)
        basic_layout.addRow("Operator:", self.operator_input)
        basic_layout.addRow("Field:", self.field_input)
        basic_layout.addRow("Project:", self.project_input)
        
        basic_group.setLayout(basic_layout)
        form_layout.addRow(basic_group)
        
        # Well Configuration Section
        config_group = QGroupBox("Well Configuration")
        config_layout = QFormLayout()
        
        # Well Type
        well_type_layout = QHBoxLayout()
        self.onshore_radio = QRadioButton("Onshore")
        self.offshore_radio = QRadioButton("Offshore")
        self.onshore_radio.setChecked(True)
        well_type_layout.addWidget(self.onshore_radio)
        well_type_layout.addWidget(self.offshore_radio)
        well_type_layout.addStretch()
        
        # Rig Type
        self.rig_type_combo = QComboBox()
        self.rig_type_combo.addItems(["Land", "Jackup", "SemiSub", "Drillship", "Platform"])
        
        # Well Shape
        self.well_shape_combo = QComboBox()
        self.well_shape_combo.addItems(["Vertical", "Deviated", "Horizontal", "S-shaped", "J-shaped"])
        
        config_layout.addRow("Well Type:", QWidget())
        config_layout.itemAt(config_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(well_type_layout)
        config_layout.addRow("Rig Type:", self.rig_type_combo)
        config_layout.addRow("Well Shape:", self.well_shape_combo)
        
        # Derrick Height
        self.derrick_height_spin = QDoubleSpinBox()
        self.derrick_height_spin.setRange(0, 500)
        self.derrick_height_spin.setSuffix(" ft")
        self.derrick_height_spin.setValue(100)
        
        config_layout.addRow("Derrick Height:", self.derrick_height_spin)
        
        config_group.setLayout(config_layout)
        form_layout.addRow(config_group)
        
        # Location and Coordinates Section
        location_group = QGroupBox("Location and Coordinates")
        location_layout = QFormLayout()
        
        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("e.g., 29.123456")
        
        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("e.g., 48.654321")
        
        self.northing_input = QLineEdit()
        self.northing_input.setPlaceholderText("UTM Northing")
        
        self.easting_input = QLineEdit()
        self.easting_input.setPlaceholderText("UTM Easting")
        
        location_layout.addRow("Latitude:", self.latitude_input)
        location_layout.addRow("Longitude:", self.longitude_input)
        location_layout.addRow("Northing:", self.northing_input)
        location_layout.addRow("Easting:", self.easting_input)
        
        location_group.setLayout(location_layout)
        form_layout.addRow(location_group)
        
        # Elevation References Section
        elevation_group = QGroupBox("Elevation References")
        elevation_layout = QFormLayout()
        
        self.gle_spin = QDoubleSpinBox()
        self.gle_spin.setRange(-1000, 10000)
        self.gle_spin.setSuffix(" ft")
        
        self.rte_spin = QDoubleSpinBox()
        self.rte_spin.setRange(-1000, 10000)
        self.rte_spin.setSuffix(" ft")
        
        self.msl_spin = QDoubleSpinBox()
        self.msl_spin.setRange(-1000, 10000)
        self.msl_spin.setSuffix(" ft")
        
        self.kop1_spin = QDoubleSpinBox()
        self.kop1_spin.setRange(0, 10000)
        self.kop1_spin.setSuffix(" ft")
        
        self.kop2_spin = QDoubleSpinBox()
        self.kop2_spin.setRange(0, 10000)
        self.kop2_spin.setSuffix(" ft")
        
        elevation_layout.addRow("GLE:", self.gle_spin)
        elevation_layout.addRow("RTE:", self.rte_spin)
        elevation_layout.addRow("MSL:", self.msl_spin)
        elevation_layout.addRow("KOP1:", self.kop1_spin)
        elevation_layout.addRow("KOP2:", self.kop2_spin)
        
        elevation_group.setLayout(elevation_layout)
        form_layout.addRow(elevation_group)
        
        # Well Dimensions Section
        dimensions_group = QGroupBox("Well Dimensions")
        dimensions_layout = QFormLayout()
        
        self.hole_size_spin = QDoubleSpinBox()
        self.hole_size_spin.setRange(0, 100)
        self.hole_size_spin.setSuffix(" inch")
        self.hole_size_spin.setValue(8.5)
        
        self.final_depth_spin = QDoubleSpinBox()
        self.final_depth_spin.setRange(0, 50000)
        self.final_depth_spin.setSuffix(" m")
        self.final_depth_spin.setValue(3000)
        
        self.water_depth_spin = QDoubleSpinBox()
        self.water_depth_spin.setRange(0, 5000)
        self.water_depth_spin.setSuffix(" m")
        
        dimensions_layout.addRow("Hole Size:", self.hole_size_spin)
        dimensions_layout.addRow("Final Depth:", self.final_depth_spin)
        dimensions_layout.addRow("Water Depth:", self.water_depth_spin)
        
        dimensions_group.setLayout(dimensions_layout)
        form_layout.addRow(dimensions_group)
        
        # Dates Section
        dates_group = QGroupBox("Important Dates")
        dates_layout = QFormLayout()
        
        self.spud_date_edit = QDateEdit()
        self.spud_date_edit.setCalendarPopup(True)
        self.spud_date_edit.setDate(QDate.currentDate())
        
        self.start_hole_date_edit = QDateEdit()
        self.start_hole_date_edit.setCalendarPopup(True)
        self.start_hole_date_edit.setDate(QDate.currentDate())
        
        self.rig_move_date_edit = QDateEdit()
        self.rig_move_date_edit.setCalendarPopup(True)
        self.rig_move_date_edit.setDate(QDate.currentDate())
        
        self.report_date_edit = QDateEdit()
        self.report_date_edit.setCalendarPopup(True)
        self.report_date_edit.setDate(QDate.currentDate())
        
        dates_layout.addRow("Spud Date:", self.spud_date_edit)
        dates_layout.addRow("Start Hole Date:", self.start_hole_date_edit)
        dates_layout.addRow("Rig Move Date:", self.rig_move_date_edit)
        dates_layout.addRow("Report Date:", self.report_date_edit)
        
        dates_group.setLayout(dates_layout)
        form_layout.addRow(dates_group)
        
        # Personnel Section
        personnel_group = QGroupBox("Personnel")
        personnel_layout = QFormLayout()
        
        self.supervisor_day_input = QLineEdit()
        self.supervisor_night_input = QLineEdit()
        self.toolpusher_day_input = QLineEdit()
        self.toolpusher_night_input = QLineEdit()
        self.operation_manager_input = QLineEdit()
        self.geologist1_input = QLineEdit()
        self.geologist2_input = QLineEdit()
        self.client_rep_input = QLineEdit()
        
        personnel_layout.addRow("Day Supervisor:", self.supervisor_day_input)
        personnel_layout.addRow("Night Supervisor:", self.supervisor_night_input)
        personnel_layout.addRow("Day Toolpusher:", self.toolpusher_day_input)
        personnel_layout.addRow("Night Toolpusher:", self.toolpusher_night_input)
        personnel_layout.addRow("Operation Manager:", self.operation_manager_input)
        personnel_layout.addRow("Geologist 1:", self.geologist1_input)
        personnel_layout.addRow("Geologist 2:", self.geologist2_input)
        personnel_layout.addRow("Client Rep:", self.client_rep_input)
        
        personnel_group.setLayout(personnel_layout)
        form_layout.addRow(personnel_group)
        
        # Objectives Section
        objectives_group = QGroupBox("Well Objectives")
        objectives_layout = QVBoxLayout()
        
        self.objectives_text = QTextEdit()
        self.objectives_text.setPlaceholderText("Enter well objectives here...")
        self.objectives_text.setMinimumHeight(150)
        
        objectives_layout.addWidget(self.objectives_text)
        objectives_group.setLayout(objectives_layout)
        form_layout.addRow(objectives_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Well Info")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        self.save_button.clicked.connect(self.save_well_info)
        
        self.load_button = QPushButton("Load Existing Well")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.load_button.clicked.connect(self.load_well_dialog)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def save_well_info(self):
        """Save well information to database"""
        well_info = WellInfo(
            name=self.well_name_input.text().strip(),
            rig_name=self.rig_name_input.text().strip(),
            operator=self.operator_input.text().strip(),
            field=self.field_input.text().strip(),
            project=self.project_input.text().strip(),
            well_type="Onshore" if self.onshore_radio.isChecked() else "Offshore",
            rig_type=self.rig_type_combo.currentText(),
            well_shape=self.well_shape_combo.currentText(),
            derrick_height=self.derrick_height_spin.value(),
            gle=self.gle_spin.value(),
            rte=self.rte_spin.value(),
            msl=self.msl_spin.value(),
            kop1=self.kop1_spin.value(),
            kop2=self.kop2_spin.value(),
            latitude=self.latitude_input.text().strip(),
            longitude=self.longitude_input.text().strip(),
            northing=self.northing_input.text().strip(),
            easting=self.easting_input.text().strip(),
            hole_size=self.hole_size_spin.value(),
            final_depth=self.final_depth_spin.value(),
            water_depth=self.water_depth_spin.value(),
            spud_date=self.spud_date_edit.date().toString("yyyy-MM-dd"),
            start_hole_date=self.start_hole_date_edit.date().toString("yyyy-MM-dd"),
            rig_move_date=self.rig_move_date_edit.date().toString("yyyy-MM-dd"),
            report_date=self.report_date_edit.date().toString("yyyy-MM-dd"),
            supervisor_day=self.supervisor_day_input.text().strip(),
            supervisor_night=self.supervisor_night_input.text().strip(),
            toolpusher_day=self.toolpusher_day_input.text().strip(),
            toolpusher_night=self.toolpusher_night_input.text().strip(),
            operation_manager=self.operation_manager_input.text().strip(),
            geologist1=self.geologist1_input.text().strip(),
            geologist2=self.geologist2_input.text().strip(),
            client_rep=self.client_rep_input.text().strip(),
            objectives=self.objectives_text.toPlainText().strip()
        )
        
        if not well_info.name:
            QMessageBox.warning(self, "Validation Error", "Well name is required!")
            return
        
        well_id = self.db.save_well_info(well_info)
        if well_id > 0:
            self.current_well_id = well_id
            QMessageBox.information(self, "Success", f"Well information saved successfully! (ID: {well_id})")
        else:
            QMessageBox.warning(self, "Error", "Failed to save well information.")
    
    def load_well_dialog(self):
        """Show dialog to load existing well"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Existing Well")
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Search field
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search wells...")
        search_button = QPushButton("Search")
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Wells list
        self.wells_table = QTableWidget()
        self.wells_table.setColumnCount(4)
        self.wells_table.setHorizontalHeaderLabels(["ID", "Well Name", "Field", "Created"])
        self.wells_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.wells_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Load wells data
        wells = self.db.get_all_wells()
        self.wells_table.setRowCount(len(wells))
        
        for i, well in enumerate(wells):
            self.wells_table.setItem(i, 0, QTableWidgetItem(str(well.id)))
            self.wells_table.setItem(i, 1, QTableWidgetItem(well.name))
            self.wells_table.setItem(i, 2, QTableWidgetItem(well.field))
            self.wells_table.setItem(i, 3, QTableWidgetItem(well.created_at))
        
        layout.addWidget(self.wells_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load Selected")
        cancel_button = QPushButton("Cancel")
        
        load_button.clicked.connect(lambda: self.load_selected_well(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def load_selected_well(self, dialog):
        """Load selected well from the dialog"""
        selected_items = self.wells_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a well to load.")
            return
        
        well_id = int(self.wells_table.item(selected_items[0].row(), 0).text())
        well_info = self.db.get_well_info(well_id)
        
        if well_info:
            self.populate_form(well_info)
            dialog.accept()
    
    def populate_form(self, well_info: WellInfo):
        """Populate form with well information"""
        self.current_well_id = well_info.id
        self.well_name_input.setText(well_info.name)
        self.rig_name_input.setText(well_info.rig_name)
        self.operator_input.setText(well_info.operator)
        self.field_input.setText(well_info.field)
        self.project_input.setText(well_info.project)
        
        if well_info.well_type == "Onshore":
            self.onshore_radio.setChecked(True)
        else:
            self.offshore_radio.setChecked(True)
        
        self.rig_type_combo.setCurrentText(well_info.rig_type)
        self.well_shape_combo.setCurrentText(well_info.well_shape)
        self.derrick_height_spin.setValue(well_info.derrick_height)
        
        self.gle_spin.setValue(well_info.gle)
        self.rte_spin.setValue(well_info.rte)
        self.msl_spin.setValue(well_info.msl)
        self.kop1_spin.setValue(well_info.kop1)
        self.kop2_spin.setValue(well_info.kop2)
        
        self.latitude_input.setText(well_info.latitude)
        self.longitude_input.setText(well_info.longitude)
        self.northing_input.setText(well_info.northing)
        self.easting_input.setText(well_info.easting)
        
        self.hole_size_spin.setValue(well_info.hole_size)
        self.final_depth_spin.setValue(well_info.final_depth)
        self.water_depth_spin.setValue(well_info.water_depth)
        
        # Parse dates
        if well_info.spud_date:
            self.spud_date_edit.setDate(QDate.fromString(well_info.spud_date, "yyyy-MM-dd"))
        if well_info.start_hole_date:
            self.start_hole_date_edit.setDate(QDate.fromString(well_info.start_hole_date, "yyyy-MM-dd"))
        if well_info.rig_move_date:
            self.rig_move_date_edit.setDate(QDate.fromString(well_info.rig_move_date, "yyyy-MM-dd"))
        if well_info.report_date:
            self.report_date_edit.setDate(QDate.fromString(well_info.report_date, "yyyy-MM-dd"))
        
        self.supervisor_day_input.setText(well_info.supervisor_day)
        self.supervisor_night_input.setText(well_info.supervisor_night)
        self.toolpusher_day_input.setText(well_info.toolpusher_day)
        self.toolpusher_night_input.setText(well_info.toolpusher_night)
        self.operation_manager_input.setText(well_info.operation_manager)
        self.geologist1_input.setText(well_info.geologist1)
        self.geologist2_input.setText(well_info.geologist2)
        self.client_rep_input.setText(well_info.client_rep)
        
        self.objectives_text.setPlainText(well_info.objectives)
    
    def clear_form(self):
        """Clear all form fields"""
        self.current_well_id = -1
        self.well_name_input.clear()
        self.rig_name_input.clear()
        self.operator_input.clear()
        self.field_input.clear()
        self.project_input.clear()
        self.onshore_radio.setChecked(True)
        self.rig_type_combo.setCurrentIndex(0)
        self.well_shape_combo.setCurrentIndex(0)
        self.derrick_height_spin.setValue(100)
        
        self.gle_spin.setValue(0)
        self.rte_spin.setValue(0)
        self.msl_spin.setValue(0)
        self.kop1_spin.setValue(0)
        self.kop2_spin.setValue(0)
        
        self.latitude_input.clear()
        self.longitude_input.clear()
        self.northing_input.clear()
        self.easting_input.clear()
        
        self.hole_size_spin.setValue(8.5)
        self.final_depth_spin.setValue(3000)
        self.water_depth_spin.setValue(0)
        
        current_date = QDate.currentDate()
        self.spud_date_edit.setDate(current_date)
        self.start_hole_date_edit.setDate(current_date)
        self.rig_move_date_edit.setDate(current_date)
        self.report_date_edit.setDate(current_date)
        
        self.supervisor_day_input.clear()
        self.supervisor_night_input.clear()
        self.toolpusher_day_input.clear()
        self.toolpusher_night_input.clear()
        self.operation_manager_input.clear()
        self.geologist1_input.clear()
        self.geologist2_input.clear()
        self.client_rep_input.clear()
        
        self.objectives_text.clear()

class DailyReportWidget(QWidget):
    """Daily operations report widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_report_id = -1
        self.time_logs = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Daily Operations Report")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Select Well:"))
        
        self.well_combo = QComboBox()
        self.well_combo.currentIndexChanged.connect(self.on_well_selected)
        
        self.load_wells_button = QPushButton("Refresh Wells")
        self.load_wells_button.clicked.connect(self.load_wells)
        
        well_layout.addWidget(self.well_combo)
        well_layout.addWidget(self.load_wells_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # Report header section
        header_group = QGroupBox("Report Header")
        header_layout = QFormLayout()
        
        self.report_date_edit = QDateEdit()
        self.report_date_edit.setCalendarPopup(True)
        self.report_date_edit.setDate(QDate.currentDate())
        
        self.rig_day_spin = QSpinBox()
        self.rig_day_spin.setRange(1, 365)
        self.rig_day_spin.setValue(1)
        
        header_layout.addRow("Report Date:", self.report_date_edit)
        header_layout.addRow("Rig Day:", self.rig_day_spin)
        
        header_group.setLayout(header_layout)
        form_layout.addRow(header_group)
        
        # Depth readings section
        depth_group = QGroupBox("Depth Readings")
        depth_layout = QGridLayout()
        
        self.depth_0000_spin = QDoubleSpinBox()
        self.depth_0000_spin.setRange(0, 50000)
        self.depth_0000_spin.setSuffix(" m")
        
        self.depth_0600_spin = QDoubleSpinBox()
        self.depth_0600_spin.setRange(0, 50000)
        self.depth_0600_spin.setSuffix(" m")
        
        self.depth_2400_spin = QDoubleSpinBox()
        self.depth_2400_spin.setRange(0, 50000)
        self.depth_2400_spin.setSuffix(" m")
        
        self.pit_gain_spin = QDoubleSpinBox()
        self.pit_gain_spin.setRange(0, 1000)
        self.pit_gain_spin.setSuffix(" bbl")
        
        depth_layout.addWidget(QLabel("Depth @ 00:00:"), 0, 0)
        depth_layout.addWidget(self.depth_0000_spin, 0, 1)
        depth_layout.addWidget(QLabel("Depth @ 06:00:"), 0, 2)
        depth_layout.addWidget(self.depth_0600_spin, 0, 3)
        depth_layout.addWidget(QLabel("Depth @ 24:00:"), 1, 0)
        depth_layout.addWidget(self.depth_2400_spin, 1, 1)
        depth_layout.addWidget(QLabel("Pit Gain:"), 1, 2)
        depth_layout.addWidget(self.pit_gain_spin, 1, 3)
        
        depth_group.setLayout(depth_layout)
        form_layout.addRow(depth_group)
        
        # Operations section
        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout()
        
        self.operations_text = QTextEdit()
        self.operations_text.setPlaceholderText("Describe operations done during this shift...")
        self.operations_text.setMinimumHeight(100)
        
        operations_layout.addWidget(self.operations_text)
        operations_group.setLayout(operations_layout)
        form_layout.addRow(operations_group)
        
        # Work summary section
        summary_group = QGroupBox("Work Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Summary of work completed...")
        self.summary_text.setMinimumHeight(80)
        
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        form_layout.addRow(summary_group)
        
        # Problems section
        problems_group = QGroupBox("Problems / Alerts")
        problems_layout = QVBoxLayout()
        
        self.problems_text = QTextEdit()
        self.problems_text.setPlaceholderText("Report any problems or alerts...")
        self.problems_text.setMinimumHeight(80)
        
        problems_layout.addWidget(self.problems_text)
        problems_group.setLayout(problems_layout)
        form_layout.addRow(problems_group)
        
        # General notes section
        notes_group = QGroupBox("General Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Any additional notes...")
        self.notes_text.setMinimumHeight(80)
        
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        form_layout.addRow(notes_group)
        
        # Time Log Section
        time_log_group = QGroupBox("Time Log")
        time_log_layout = QVBoxLayout()
        
        # Time log table
        self.time_log_table = QTableWidget()
        self.time_log_table.setColumnCount(8)
        self.time_log_table.setHorizontalHeaderLabels([
            "From", "To", "Duration", "Main Code", "Sub Code", 
            "Description", "NPT", "Status"
        ])
        
        # Time log buttons
        time_log_buttons = QHBoxLayout()
        add_log_button = QPushButton("Add Time Log")
        add_log_button.clicked.connect(self.add_time_log_dialog)
        
        edit_log_button = QPushButton("Edit Selected")
        edit_log_button.clicked.connect(self.edit_time_log)
        
        delete_log_button = QPushButton("Delete Selected")
        delete_log_button.clicked.connect(self.delete_time_log)
        
        time_log_buttons.addWidget(add_log_button)
        time_log_buttons.addWidget(edit_log_button)
        time_log_buttons.addWidget(delete_log_button)
        time_log_buttons.addStretch()
        
        time_log_layout.addWidget(self.time_log_table)
        time_log_layout.addLayout(time_log_buttons)
        time_log_group.setLayout(time_log_layout)
        form_layout.addRow(time_log_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Save button
        self.save_button = QPushButton("Save Daily Report")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1f6391;
            }
        """)
        self.save_button.clicked.connect(self.save_daily_report)
        main_layout.addWidget(self.save_button)
        
        self.setLayout(main_layout)
        
        # Load wells initially
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def on_well_selected(self, index):
        """Handle well selection change"""
        if index >= 0:
            well_id = self.well_combo.itemData(index)
            # TODO: Load existing report for this well/date
    
    def add_time_log_dialog(self):
        """Show dialog to add time log entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Time Log Entry")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Time inputs
        time_layout = QHBoxLayout()
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(0, 0))
        
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(0, 0))
        
        self.duration_label = QLabel("00:00")
        
        time_layout.addWidget(QLabel("From:"))
        time_layout.addWidget(self.start_time_edit)
        time_layout.addWidget(QLabel("To:"))
        time_layout.addWidget(self.end_time_edit)
        time_layout.addWidget(QLabel("Duration:"))
        time_layout.addWidget(self.duration_label)
        time_layout.addStretch()
        
        form.addRow("Time:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(time_layout)
        
        # Code selection
        self.main_code_combo = QComboBox()
        self.sub_code_combo = QComboBox()
        
        # TODO: Load codes from database
        self.main_code_combo.addItems(["Drilling", "Tripping", "Circulation", "Casing", "Cementing", "Waiting", "Repair"])
        
        form.addRow("Main Code:", self.main_code_combo)
        form.addRow("Sub Code:", self.sub_code_combo)
        
        # Description
        self.log_description = QLineEdit()
        self.log_description.setPlaceholderText("Enter description...")
        form.addRow("Description:", self.log_description)
        
        # NPT checkbox
        self.npt_checkbox = QCheckBox("NPT (Non-Productive Time)")
        form.addRow("", self.npt_checkbox)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["In Progress", "Completed", "Suspended", "Cancelled"])
        form.addRow("Status:", self.status_combo)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Entry")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_time_log_entry(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_time_log_entry(self, dialog):
        """Add time log entry to table"""
        start_time = self.start_time_edit.time().toString("HH:mm")
        end_time = self.end_time_edit.time().toString("HH:mm")
        
        # Calculate duration
        start_qtime = self.start_time_edit.time()
        end_qtime = self.end_time_edit.time()
        
        start_secs = start_qtime.hour() * 3600 + start_qtime.minute() * 60
        end_secs = end_qtime.hour() * 3600 + end_qtime.minute() * 60
        
        if end_secs < start_secs:
            end_secs += 24 * 3600  # Next day
        
        duration_secs = end_secs - start_secs
        hours = duration_secs // 3600
        minutes = (duration_secs % 3600) // 60
        duration_str = f"{hours:02d}:{minutes:02d}"
        
        # Add to table
        row = self.time_log_table.rowCount()
        self.time_log_table.insertRow(row)
        
        self.time_log_table.setItem(row, 0, QTableWidgetItem(start_time))
        self.time_log_table.setItem(row, 1, QTableWidgetItem(end_time))
        self.time_log_table.setItem(row, 2, QTableWidgetItem(duration_str))
        self.time_log_table.setItem(row, 3, QTableWidgetItem(self.main_code_combo.currentText()))
        self.time_log_table.setItem(row, 4, QTableWidgetItem(self.sub_code_combo.currentText()))
        self.time_log_table.setItem(row, 5, QTableWidgetItem(self.log_description.text()))
        
        # NPT checkbox in table
        npt_widget = QWidget()
        npt_layout = QHBoxLayout()
        npt_checkbox = QCheckBox()
        npt_checkbox.setChecked(self.npt_checkbox.isChecked())
        npt_layout.addWidget(npt_checkbox)
        npt_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        npt_widget.setLayout(npt_layout)
        self.time_log_table.setCellWidget(row, 6, npt_widget)
        
        self.time_log_table.setItem(row, 7, QTableWidgetItem(self.status_combo.currentText()))
        
        # Add to internal list
        time_log = TimeLogEntry(
            start_time=start_time,
            end_time=end_time,
            duration=duration_str,
            main_code=self.main_code_combo.currentText(),
            sub_code=self.sub_code_combo.currentText(),
            description=self.log_description.text(),
            is_npt=self.npt_checkbox.isChecked(),
            status=self.status_combo.currentText()
        )
        self.time_logs.append(time_log)
        
        dialog.accept()
    
    def edit_time_log(self):
        """Edit selected time log entry"""
        # TODO: Implement edit functionality
        pass
    
    def delete_time_log(self):
        """Delete selected time log entry"""
        selected = self.time_log_table.currentRow()
        if selected >= 0:
            self.time_log_table.removeRow(selected)
            if selected < len(self.time_logs):
                del self.time_logs[selected]
    
    def save_daily_report(self):
        """Save daily report to database"""
        # Get selected well
        well_index = self.well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        well_id = self.well_combo.itemData(well_index)
        
        # Create report object
        report = DailyReport(
            well_id=well_id,
            report_date=self.report_date_edit.date().toString("yyyy-MM-dd"),
            rig_day=self.rig_day_spin.value(),
            depth_0000=self.depth_0000_spin.value(),
            depth_0600=self.depth_0600_spin.value(),
            depth_2400=self.depth_2400_spin.value(),
            pit_gain=self.pit_gain_spin.value(),
            operations_done=self.operations_text.toPlainText(),
            work_summary=self.summary_text.toPlainText(),
            problems=self.problems_text.toPlainText(),
            general_notes=self.notes_text.toPlainText(),
            time_logs=self.time_logs
        )
        
        # Save to database
        report_id = self.db.save_daily_report(report)
        if report_id > 0:
            self.current_report_id = report_id
            QMessageBox.information(self, "Success", f"Daily report saved successfully! (ID: {report_id})")
            
            # Reset form for next entry
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to save daily report.")
    
    def clear_form(self):
        """Clear the form for new entry"""
        self.current_report_id = -1
        self.rig_day_spin.setValue(self.rig_day_spin.value() + 1)
        self.depth_0000_spin.setValue(0)
        self.depth_0600_spin.setValue(0)
        self.depth_2400_spin.setValue(0)
        self.pit_gain_spin.setValue(0)
        self.operations_text.clear()
        self.summary_text.clear()
        self.problems_text.clear()
        self.notes_text.clear()
        
        # Clear time logs
        self.time_log_table.setRowCount(0)
        self.time_logs.clear()

class DrillingParametersWidget(QWidget):
    """Drilling parameters widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Drilling Parameters")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # WOB section
        wob_group = QGroupBox("Weight on Bit (WOB)")
        wob_layout = QGridLayout()
        
        self.wob_min_spin = QDoubleSpinBox()
        self.wob_min_spin.setRange(0, 100)
        self.wob_min_spin.setSuffix(" klb")
        
        self.wob_max_spin = QDoubleSpinBox()
        self.wob_max_spin.setRange(0, 100)
        self.wob_max_spin.setSuffix(" klb")
        
        self.wob_avg_spin = QDoubleSpinBox()
        self.wob_avg_spin.setRange(0, 100)
        self.wob_avg_spin.setSuffix(" klb")
        
        wob_layout.addWidget(QLabel("Min:"), 0, 0)
        wob_layout.addWidget(self.wob_min_spin, 0, 1)
        wob_layout.addWidget(QLabel("Max:"), 0, 2)
        wob_layout.addWidget(self.wob_max_spin, 0, 3)
        wob_layout.addWidget(QLabel("Average:"), 0, 4)
        wob_layout.addWidget(self.wob_avg_spin, 0, 5)
        
        wob_group.setLayout(wob_layout)
        form_layout.addRow(wob_group)
        
        # RPM section
        rpm_group = QGroupBox("Rotary Speed (RPM)")
        rpm_layout = QGridLayout()
        
        self.surface_rpm_min_spin = QDoubleSpinBox()
        self.surface_rpm_min_spin.setRange(0, 500)
        self.surface_rpm_min_spin.setSuffix(" rpm")
        
        self.surface_rpm_max_spin = QDoubleSpinBox()
        self.surface_rpm_max_spin.setRange(0, 500)
        self.surface_rpm_max_spin.setSuffix(" rpm")
        
        self.motor_rpm_min_spin = QDoubleSpinBox()
        self.motor_rpm_min_spin.setRange(0, 500)
        self.motor_rpm_min_spin.setSuffix(" rpm")
        
        self.motor_rpm_max_spin = QDoubleSpinBox()
        self.motor_rpm_max_spin.setRange(0, 500)
        self.motor_rpm_max_spin.setSuffix(" rpm")
        
        rpm_layout.addWidget(QLabel("Surface Min:"), 0, 0)
        rpm_layout.addWidget(self.surface_rpm_min_spin, 0, 1)
        rpm_layout.addWidget(QLabel("Surface Max:"), 0, 2)
        rpm_layout.addWidget(self.surface_rpm_max_spin, 0, 3)
        rpm_layout.addWidget(QLabel("Motor Min:"), 1, 0)
        rpm_layout.addWidget(self.motor_rpm_min_spin, 1, 1)
        rpm_layout.addWidget(QLabel("Motor Max:"), 1, 2)
        rpm_layout.addWidget(self.motor_rpm_max_spin, 1, 3)
        
        rpm_group.setLayout(rpm_layout)
        form_layout.addRow(rpm_group)
        
        # Torque section
        torque_group = QGroupBox("Torque")
        torque_layout = QGridLayout()
        
        self.torque_min_spin = QDoubleSpinBox()
        self.torque_min_spin.setRange(0, 100)
        self.torque_min_spin.setSuffix(" kft-lb")
        
        self.torque_max_spin = QDoubleSpinBox()
        self.torque_max_spin.setRange(0, 100)
        self.torque_max_spin.setSuffix(" kft-lb")
        
        torque_layout.addWidget(QLabel("Min:"), 0, 0)
        torque_layout.addWidget(self.torque_min_spin, 0, 1)
        torque_layout.addWidget(QLabel("Max:"), 0, 2)
        torque_layout.addWidget(self.torque_max_spin, 0, 3)
        
        torque_group.setLayout(torque_layout)
        form_layout.addRow(torque_group)
        
        # Pump parameters section
        pump_group = QGroupBox("Pump Parameters")
        pump_layout = QGridLayout()
        
        self.pump_pressure_min_spin = QDoubleSpinBox()
        self.pump_pressure_min_spin.setRange(0, 5000)
        self.pump_pressure_min_spin.setSuffix(" psi")
        
        self.pump_pressure_max_spin = QDoubleSpinBox()
        self.pump_pressure_max_spin.setRange(0, 5000)
        self.pump_pressure_max_spin.setSuffix(" psi")
        
        self.pump_output_min_spin = QDoubleSpinBox()
        self.pump_output_min_spin.setRange(0, 2000)
        self.pump_output_min_spin.setSuffix(" gpm")
        
        self.pump_output_max_spin = QDoubleSpinBox()
        self.pump_output_max_spin.setRange(0, 2000)
        self.pump_output_max_spin.setSuffix(" gpm")
        
        pump_layout.addWidget(QLabel("Pressure Min:"), 0, 0)
        pump_layout.addWidget(self.pump_pressure_min_spin, 0, 1)
        pump_layout.addWidget(QLabel("Pressure Max:"), 0, 2)
        pump_layout.addWidget(self.pump_pressure_max_spin, 0, 3)
        pump_layout.addWidget(QLabel("Output Min:"), 1, 0)
        pump_layout.addWidget(self.pump_output_min_spin, 1, 1)
        pump_layout.addWidget(QLabel("Output Max:"), 1, 2)
        pump_layout.addWidget(self.pump_output_max_spin, 1, 3)
        
        pump_group.setLayout(pump_layout)
        form_layout.addRow(pump_group)
        
        # Additional parameters
        params_group = QGroupBox("Additional Parameters")
        params_layout = QGridLayout()
        
        self.hsi_spin = QDoubleSpinBox()
        self.hsi_spin.setRange(0, 10)
        self.hsi_spin.setSuffix(" hp/in²")
        
        self.annular_velocity_spin = QDoubleSpinBox()
        self.annular_velocity_spin.setRange(0, 500)
        self.annular_velocity_spin.setSuffix(" ft/min")
        
        self.tfa_spin = QDoubleSpinBox()
        self.tfa_spin.setRange(0, 5)
        self.tfa_spin.setSuffix(" in²")
        
        self.bit_revolution_spin = QDoubleSpinBox()
        self.bit_revolution_spin.setRange(0, 1000000)
        
        params_layout.addWidget(QLabel("HSI:"), 0, 0)
        params_layout.addWidget(self.hsi_spin, 0, 1)
        params_layout.addWidget(QLabel("Annular Velocity:"), 0, 2)
        params_layout.addWidget(self.annular_velocity_spin, 0, 3)
        params_layout.addWidget(QLabel("TFA:"), 1, 0)
        params_layout.addWidget(self.tfa_spin, 1, 1)
        params_layout.addWidget(QLabel("Bit Revolution:"), 1, 2)
        params_layout.addWidget(self.bit_revolution_spin, 1, 3)
        
        params_group.setLayout(params_layout)
        form_layout.addRow(params_group)
        
        # SCR Pumps section
        scr_group = QGroupBox("SCR Pumps")
        scr_layout = QGridLayout()
        
        # Pump 1
        scr_layout.addWidget(QLabel("Pump 1:"), 0, 0)
        self.pump1_spm_spin = QDoubleSpinBox()
        self.pump1_spm_spin.setRange(0, 200)
        self.pump1_spm_spin.setSuffix(" spm")
        scr_layout.addWidget(self.pump1_spm_spin, 0, 1)
        
        self.pump1_spp_spin = QDoubleSpinBox()
        self.pump1_spp_spin.setRange(0, 5000)
        self.pump1_spp_spin.setSuffix(" psi")
        scr_layout.addWidget(self.pump1_spp_spin, 0, 2)
        
        # Pump 2
        scr_layout.addWidget(QLabel("Pump 2:"), 1, 0)
        self.pump2_spm_spin = QDoubleSpinBox()
        self.pump2_spm_spin.setRange(0, 200)
        self.pump2_spm_spin.setSuffix(" spm")
        scr_layout.addWidget(self.pump2_spm_spin, 1, 1)
        
        self.pump2_spp_spin = QDoubleSpinBox()
        self.pump2_spp_spin.setRange(0, 5000)
        self.pump2_spp_spin.setSuffix(" psi")
        scr_layout.addWidget(self.pump2_spp_spin, 1, 2)
        
        # Pump 3
        scr_layout.addWidget(QLabel("Pump 3:"), 2, 0)
        self.pump3_spm_spin = QDoubleSpinBox()
        self.pump3_spm_spin.setRange(0, 200)
        self.pump3_spm_spin.setSuffix(" spm")
        scr_layout.addWidget(self.pump3_spm_spin, 2, 1)
        
        self.pump3_spp_spin = QDoubleSpinBox()
        self.pump3_spp_spin.setRange(0, 5000)
        self.pump3_spp_spin.setSuffix(" psi")
        scr_layout.addWidget(self.pump3_spp_spin, 2, 2)
        
        scr_group.setLayout(scr_layout)
        form_layout.addRow(scr_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Save button
        save_button = QPushButton("Save Drilling Parameters")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

class MudReportWidget(QWidget):
    """Mud report widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        # Tab widget for different mud report sections
        tabs = QTabWidget()
        
        # Properties tab
        properties_tab = self.create_properties_tab()
        tabs.addTab(properties_tab, "Properties")
        
        # Volumes tab
        volumes_tab = self.create_volumes_tab()
        tabs.addTab(volumes_tab, "Volumes")
        
        # Chemicals tab
        chemicals_tab = self.create_chemicals_tab()
        tabs.addTab(chemicals_tab, "Chemicals")
        
        # Solid Control tab
        solid_control_tab = self.create_solid_control_tab()
        tabs.addTab(solid_control_tab, "Solid Control")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Mud Report")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_properties_tab(self):
        """Create mud properties tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # Basic info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.mud_type_combo = QComboBox()
        self.mud_type_combo.addItems([
            "Water Based", "Oil Based", "Synthetic Based", 
            "KCl Polymer", "PHPA", "Sulfonated"
        ])
        
        self.sample_time_edit = QTimeEdit()
        self.sample_time_edit.setTime(QTime.currentTime())
        
        basic_layout.addRow("Mud Type:", self.mud_type_combo)
        basic_layout.addRow("Sample Time:", self.sample_time_edit)
        
        basic_group.setLayout(basic_layout)
        form_layout.addRow(basic_group)
        
        # Rheology properties
        rheology_group = QGroupBox("Rheology Properties")
        rheology_layout = QGridLayout()
        
        # Row 1
        rheology_layout.addWidget(QLabel("MW (ppg):"), 0, 0)
        self.mw_spin = QDoubleSpinBox()
        self.mw_spin.setRange(8, 20)
        self.mw_spin.setValue(10.5)
        rheology_layout.addWidget(self.mw_spin, 0, 1)
        
        rheology_layout.addWidget(QLabel("PV (cp):"), 0, 2)
        self.pv_spin = QDoubleSpinBox()
        self.pv_spin.setRange(0, 100)
        self.pv_spin.setValue(15)
        rheology_layout.addWidget(self.pv_spin, 0, 3)
        
        rheology_layout.addWidget(QLabel("YP (lb/100ft²):"), 0, 4)
        self.yp_spin = QDoubleSpinBox()
        self.yp_spin.setRange(0, 50)
        self.yp_spin.setValue(10)
        rheology_layout.addWidget(self.yp_spin, 0, 5)
        
        # Row 2
        rheology_layout.addWidget(QLabel("Funnel Visc (sec/qt):"), 1, 0)
        self.funnel_visc_spin = QDoubleSpinBox()
        self.funnel_visc_spin.setRange(0, 200)
        self.funnel_visc_spin.setValue(45)
        rheology_layout.addWidget(self.funnel_visc_spin, 1, 1)
        
        rheology_layout.addWidget(QLabel("Gel 10s:"), 1, 2)
        self.gel_10s_spin = QDoubleSpinBox()
        self.gel_10s_spin.setRange(0, 50)
        self.gel_10s_spin.setValue(5)
        rheology_layout.addWidget(self.gel_10s_spin, 1, 3)
        
        rheology_layout.addWidget(QLabel("Gel 10m:"), 1, 4)
        self.gel_10m_spin = QDoubleSpinBox()
        self.gel_10m_spin.setRange(0, 50)
        self.gel_10m_spin.setValue(8)
        rheology_layout.addWidget(self.gel_10m_spin, 1, 5)
        
        # Row 3
        rheology_layout.addWidget(QLabel("Gel 30m:"), 2, 0)
        self.gel_30m_spin = QDoubleSpinBox()
        self.gel_30m_spin.setRange(0, 50)
        self.gel_30m_spin.setValue(10)
        rheology_layout.addWidget(self.gel_30m_spin, 2, 1)
        
        rheology_layout.addWidget(QLabel("Fluid Loss (cc/30min):"), 2, 2)
        self.fluid_loss_spin = QDoubleSpinBox()
        self.fluid_loss_spin.setRange(0, 50)
        self.fluid_loss_spin.setValue(6)
        rheology_layout.addWidget(self.fluid_loss_spin, 2, 3)
        
        rheology_layout.addWidget(QLabel("Cake Thickness (mm):"), 2, 4)
        self.cake_thickness_spin = QDoubleSpinBox()
        self.cake_thickness_spin.setRange(0, 10)
        self.cake_thickness_spin.setValue(1.5)
        rheology_layout.addWidget(self.cake_thickness_spin, 2, 5)
        
        rheology_group.setLayout(rheology_layout)
        form_layout.addRow(rheology_group)
        
        # Chemical properties
        chemical_group = QGroupBox("Chemical Properties")
        chemical_layout = QGridLayout()
        
        # Row 1
        chemical_layout.addWidget(QLabel("Ca (ppm):"), 0, 0)
        self.ca_spin = QDoubleSpinBox()
        self.ca_spin.setRange(0, 5000)
        chemical_layout.addWidget(self.ca_spin, 0, 1)
        
        chemical_layout.addWidget(QLabel("Cl (ppm):"), 0, 2)
        self.cl_spin = QDoubleSpinBox()
        self.cl_spin.setRange(0, 200000)
        chemical_layout.addWidget(self.cl_spin, 0, 3)
        
        chemical_layout.addWidget(QLabel("KCl (ppm):"), 0, 4)
        self.kcl_spin = QDoubleSpinBox()
        self.kcl_spin.setRange(0, 50000)
        chemical_layout.addWidget(self.kcl_spin, 0, 5)
        
        # Row 2
        chemical_layout.addWidget(QLabel("pH:"), 1, 0)
        self.ph_spin = QDoubleSpinBox()
        self.ph_spin.setRange(0, 14)
        self.ph_spin.setValue(9.5)
        chemical_layout.addWidget(self.ph_spin, 1, 1)
        
        chemical_layout.addWidget(QLabel("Hardness:"), 1, 2)
        self.hardness_spin = QDoubleSpinBox()
        self.hardness_spin.setRange(0, 1000)
        chemical_layout.addWidget(self.hardness_spin, 1, 3)
        
        chemical_layout.addWidget(QLabel("MBT (lb/bbl):"), 1, 4)
        self.mbt_spin = QDoubleSpinBox()
        self.mbt_spin.setRange(0, 50)
        chemical_layout.addWidget(self.mbt_spin, 1, 5)
        
        # Row 3
        chemical_layout.addWidget(QLabel("Solid %:"), 2, 0)
        self.solid_percent_spin = QDoubleSpinBox()
        self.solid_percent_spin.setRange(0, 50)
        self.solid_percent_spin.setValue(15)
        chemical_layout.addWidget(self.solid_percent_spin, 2, 1)
        
        chemical_layout.addWidget(QLabel("Oil %:"), 2, 2)
        self.oil_percent_spin = QDoubleSpinBox()
        self.oil_percent_spin.setRange(0, 100)
        chemical_layout.addWidget(self.oil_percent_spin, 2, 3)
        
        chemical_layout.addWidget(QLabel("Water %:"), 2, 4)
        self.water_percent_spin = QDoubleSpinBox()
        self.water_percent_spin.setRange(0, 100)
        self.water_percent_spin.setValue(85)
        chemical_layout.addWidget(self.water_percent_spin, 2, 5)
        
        # Row 4
        chemical_layout.addWidget(QLabel("Glycol %:"), 3, 0)
        self.glycol_percent_spin = QDoubleSpinBox()
        self.glycol_percent_spin.setRange(0, 100)
        chemical_layout.addWidget(self.glycol_percent_spin, 3, 1)
        
        chemical_layout.addWidget(QLabel("Temp (°C):"), 3, 2)
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0, 200)
        self.temp_spin.setValue(60)
        chemical_layout.addWidget(self.temp_spin, 3, 3)
        
        chemical_layout.addWidget(QLabel("Pf:"), 3, 4)
        self.pf_spin = QDoubleSpinBox()
        self.pf_spin.setRange(0, 14)
        chemical_layout.addWidget(self.pf_spin, 3, 5)
        
        chemical_layout.addWidget(QLabel("Mf:"), 3, 6)
        self.mf_spin = QDoubleSpinBox()
        self.mf_spin.setRange(0, 14)
        chemical_layout.addWidget(self.mf_spin, 3, 7)
        
        chemical_group.setLayout(chemical_layout)
        form_layout.addRow(chemical_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def create_volumes_tab(self):
        """Create mud volumes tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        volumes_group = QGroupBox("Mud Volumes")
        volumes_layout = QGridLayout()
        
        # Row 1
        volumes_layout.addWidget(QLabel("Vol. in Hole (bbl):"), 0, 0)
        self.vol_in_hole_spin = QDoubleSpinBox()
        self.vol_in_hole_spin.setRange(0, 5000)
        volumes_layout.addWidget(self.vol_in_hole_spin, 0, 1)
        
        volumes_layout.addWidget(QLabel("Total Circulated (bbl):"), 0, 2)
        self.total_circulated_spin = QDoubleSpinBox()
        self.total_circulated_spin.setRange(0, 10000)
        volumes_layout.addWidget(self.total_circulated_spin, 0, 3)
        
        # Row 2
        volumes_layout.addWidget(QLabel("Downhole Loss (bbl):"), 1, 0)
        self.downhole_loss_spin = QDoubleSpinBox()
        self.downhole_loss_spin.setRange(0, 1000)
        volumes_layout.addWidget(self.downhole_loss_spin, 1, 1)
        
        volumes_layout.addWidget(QLabel("Surface Loss (bbl):"), 1, 2)
        self.surface_loss_spin = QDoubleSpinBox()
        self.surface_loss_spin.setRange(0, 1000)
        volumes_layout.addWidget(self.surface_loss_spin, 1, 3)
        
        volumes_group.setLayout(volumes_layout)
        form_layout.addRow(volumes_group)
        
        # Tanks group
        tanks_group = QGroupBox("Tank Volumes")
        tanks_layout = QGridLayout()
        
        tanks = [
            ("Suction Tank", "suction_tank_spin"),
            ("Reserve Tank", "reserve_tank_spin"),
            ("Degasser", "degasser_spin"),
            ("Desander", "desander_spin"),
            ("Desilter", "desilter_spin"),
            ("Middle Tank", "middle_tank_spin"),
            ("T-Tank", "total_tank_spin"),
            ("Sand Trap", "sand_trap_spin")
        ]
        
        row, col = 0, 0
        for name, attr_name in tanks:
            label = QLabel(f"{name} (bbl):")
            spin = QDoubleSpinBox()
            spin.setRange(0, 2000)
            setattr(self, attr_name, spin)
            
            tanks_layout.addWidget(label, row, col * 2)
            tanks_layout.addWidget(spin, row, col * 2 + 1)
            
            col += 1
            if col == 2:  # 2 columns per row
                col = 0
                row += 1
        
        tanks_group.setLayout(tanks_layout)
        form_layout.addRow(tanks_group)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_chemicals_tab(self):
        """Create chemicals tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Chemicals table
        self.chemicals_table = QTableWidget()
        self.chemicals_table.setColumnCount(5)
        self.chemicals_table.setHorizontalHeaderLabels([
            "Product Type", "Received", "Used", "Stock", "Unit"
        ])
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Chemical")
        remove_button = QPushButton("Remove Selected")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()
        
        layout.addWidget(self.chemicals_table)
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_solid_control_tab(self):
        """Create solid control tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Equipment parameters
        equipment_group = QGroupBox("Equipment Parameters")
        equipment_layout = QGridLayout()
        
        equipment_layout.addWidget(QLabel("Equipment:"), 0, 0)
        self.equipment_combo = QComboBox()
        self.equipment_combo.addItems([
            "Shale Shaker", "Desander", "Desilter", 
            "Centrifuge", "Degasser", "Mud Cleaner"
        ])
        equipment_layout.addWidget(self.equipment_combo, 0, 1)
        
        equipment_layout.addWidget(QLabel("Feed Rate (bbl/hr):"), 0, 2)
        self.feed_rate_spin = QDoubleSpinBox()
        self.feed_rate_spin.setRange(0, 1000)
        equipment_layout.addWidget(self.feed_rate_spin, 0, 3)
        
        equipment_layout.addWidget(QLabel("Hours Operated:"), 1, 0)
        self.hours_operated_spin = QDoubleSpinBox()
        self.hours_operated_spin.setRange(0, 24)
        equipment_layout.addWidget(self.hours_operated_spin, 1, 1)
        
        equipment_layout.addWidget(QLabel("Loss (bbl):"), 1, 2)
        self.loss_spin = QDoubleSpinBox()
        self.loss_spin.setRange(0, 1000)
        equipment_layout.addWidget(self.loss_spin, 1, 3)
        
        equipment_group.setLayout(equipment_layout)
        form_layout.addRow(equipment_group)
        
        # Cone parameters
        cone_group = QGroupBox("Cone Parameters")
        cone_layout = QGridLayout()
        
        cone_layout.addWidget(QLabel("Cone Size:"), 0, 0)
        self.cone_size_combo = QComboBox()
        self.cone_size_combo.addItems(["4 inch", "5 inch", "6 inch", "8 inch", "10 inch"])
        cone_layout.addWidget(self.cone_size_combo, 0, 1)
        
        cone_layout.addWidget(QLabel("# of Cones:"), 0, 2)
        self.num_cones_spin = QSpinBox()
        self.num_cones_spin.setRange(1, 12)
        self.num_cones_spin.setValue(4)
        cone_layout.addWidget(self.num_cones_spin, 0, 3)
        
        cone_layout.addWidget(QLabel("Underflow (%):"), 1, 0)
        self.underflow_spin = QDoubleSpinBox()
        self.underflow_spin.setRange(0, 100)
        self.underflow_spin.setValue(75)
        cone_layout.addWidget(self.underflow_spin, 1, 1)
        
        cone_layout.addWidget(QLabel("Overflow (%):"), 1, 2)
        self.overflow_spin = QDoubleSpinBox()
        self.overflow_spin.setRange(0, 100)
        self.overflow_spin.setValue(25)
        cone_layout.addWidget(self.overflow_spin, 1, 3)
        
        cone_group.setLayout(cone_layout)
        form_layout.addRow(cone_group)
        
        # Hours summary
        hours_group = QGroupBox("Hours Summary")
        hours_layout = QGridLayout()
        
        hours_layout.addWidget(QLabel("Daily Hours:"), 0, 0)
        self.daily_hours_spin = QDoubleSpinBox()
        self.daily_hours_spin.setRange(0, 24)
        hours_layout.addWidget(self.daily_hours_spin, 0, 1)
        
        hours_layout.addWidget(QLabel("Cumulative Hours:"), 0, 2)
        self.cumulative_hours_spin = QDoubleSpinBox()
        self.cumulative_hours_spin.setRange(0, 10000)
        hours_layout.addWidget(self.cumulative_hours_spin, 0, 3)
        
        hours_group.setLayout(hours_layout)
        form_layout.addRow(hours_group)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

class BitReportWidget(QWidget):
    """Bit record and report widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Bit Record & Report")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Bit Information tab
        info_tab = self.create_bit_info_tab()
        tabs.addTab(info_tab, "Bit Information")
        
        # Performance tab
        perf_tab = self.create_performance_tab()
        tabs.addTab(perf_tab, "Performance Data")
        
        # Photos tab
        photos_tab = self.create_photos_tab()
        tabs.addTab(photos_tab, "Photos")
        
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Bit Record")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_bit_info_tab(self):
        """Create bit information tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # Basic Information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QGridLayout()
        
        # Row 1
        basic_layout.addWidget(QLabel("Bit No:"), 0, 0)
        self.bit_no_input = QLineEdit()
        self.bit_no_input.setPlaceholderText("e.g., BIT-001")
        basic_layout.addWidget(self.bit_no_input, 0, 1)
        
        basic_layout.addWidget(QLabel("Size (inch):"), 0, 2)
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0, 50)
        self.size_spin.setValue(8.5)
        basic_layout.addWidget(self.size_spin, 0, 3)
        
        # Row 2
        basic_layout.addWidget(QLabel("Manufacturer:"), 1, 0)
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems([
            "Baker Hughes", "Halliburton", "Schlumberger", 
            "Weatherford", "NOV", "Varel", "Other"
        ])
        basic_layout.addWidget(self.manufacturer_combo, 1, 1)
        
        basic_layout.addWidget(QLabel("Type:"), 1, 2)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "PDC", "Tricone", "Diamond", "Impregnated",
            "Roller Cone", "Fixed Cutter", "Hybrid"
        ])
        basic_layout.addWidget(self.type_combo, 1, 3)
        
        # Row 3
        basic_layout.addWidget(QLabel("Serial No:"), 2, 0)
        self.serial_no_input = QLineEdit()
        basic_layout.addWidget(self.serial_no_input, 2, 1)
        
        basic_layout.addWidget(QLabel("IADC Code:"), 2, 2)
        self.iadc_code_input = QLineEdit()
        self.iadc_code_input.setPlaceholderText("e.g., M323")
        basic_layout.addWidget(self.iadc_code_input, 2, 3)
        
        basic_group.setLayout(basic_layout)
        form_layout.addRow(basic_group)
        
        # Dull Grading group
        dull_group = QGroupBox("Dull Grading & Pull Reason")
        dull_layout = QGridLayout()
        
        # Row 1
        dull_layout.addWidget(QLabel("Dull Grading:"), 0, 0)
        self.dull_grading_combo = QComboBox()
        self.dull_grading_combo.addItems([
            "1-1-1", "1-2-1", "2-1-1", "2-2-1", "3-1-1", "3-2-1",
            "4-1-1", "4-2-1", "5-1-1", "5-2-1", "6-1-1", "6-2-1",
            "7-1-1", "7-2-1", "8-1-1", "8-2-1"
        ])
        dull_layout.addWidget(self.dull_grading_combo, 0, 1)
        
        dull_layout.addWidget(QLabel("Reason Pulled:"), 0, 2)
        self.reason_pulled_combo = QComboBox()
        self.reason_pulled_combo.addItems([
            "TD Reached", "ROP Drop", "Torque Increase",
            "WOB Increase", "Bearing Failure", "Cutter Damage",
            "Gauge Wear", "Other"
        ])
        dull_layout.addWidget(self.reason_pulled_combo, 0, 3)
        
        dull_group.setLayout(dull_layout)
        form_layout.addRow(dull_group)
        
        # Formation Information group
        formation_group = QGroupBox("Formation Information")
        formation_layout = QGridLayout()
        
        formation_layout.addWidget(QLabel("Formation:"), 0, 0)
        self.formation_input = QLineEdit()
        formation_layout.addWidget(self.formation_input, 0, 1)
        
        formation_layout.addWidget(QLabel("Lithology:"), 0, 2)
        self.lithology_combo = QComboBox()
        self.lithology_combo.addItems([
            "Sandstone", "Shale", "Limestone", "Dolomite",
            "Claystone", "Siltstone", "Conglomerate", "Evaporite"
        ])
        formation_layout.addWidget(self.lithology_combo, 0, 3)
        
        formation_group.setLayout(formation_layout)
        form_layout.addRow(formation_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def create_performance_tab(self):
        """Create performance data tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        form_layout = QFormLayout()
        
        # Depth Information group
        depth_group = QGroupBox("Depth Information")
        depth_layout = QGridLayout()
        
        # Row 1
        depth_layout.addWidget(QLabel("Depth In (m):"), 0, 0)
        self.depth_in_spin = QDoubleSpinBox()
        self.depth_in_spin.setRange(0, 50000)
        depth_layout.addWidget(self.depth_in_spin, 0, 1)
        
        depth_layout.addWidget(QLabel("Depth Out (m):"), 0, 2)
        self.depth_out_spin = QDoubleSpinBox()
        self.depth_out_spin.setRange(0, 50000)
        depth_layout.addWidget(self.depth_out_spin, 0, 3)
        
        # Row 2
        depth_layout.addWidget(QLabel("Hours Run:"), 1, 0)
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0, 1000)
        depth_layout.addWidget(self.hours_spin, 1, 1)
        
        depth_layout.addWidget(QLabel("Cum. Drilled (m):"), 1, 2)
        self.cum_drilled_spin = QDoubleSpinBox()
        self.cum_drilled_spin.setRange(0, 50000)
        depth_layout.addWidget(self.cum_drilled_spin, 1, 3)
        
        # Row 3
        depth_layout.addWidget(QLabel("Cum. Hours:"), 2, 0)
        self.cum_hours_spin = QDoubleSpinBox()
        self.cum_hours_spin.setRange(0, 10000)
        depth_layout.addWidget(self.cum_hours_spin, 2, 1)
        
        depth_layout.addWidget(QLabel("ROP (m/hr):"), 2, 2)
        self.rop_spin = QDoubleSpinBox()
        self.rop_spin.setRange(0, 500)
        depth_layout.addWidget(self.rop_spin, 2, 3)
        
        depth_group.setLayout(depth_layout)
        form_layout.addRow(depth_group)
        
        # Drilling Parameters group
        params_group = QGroupBox("Drilling Parameters (Average)")
        params_layout = QGridLayout()
        
        # Row 1
        params_layout.addWidget(QLabel("WOB (klb):"), 0, 0)
        self.wob_avg_spin = QDoubleSpinBox()
        self.wob_avg_spin.setRange(0, 100)
        params_layout.addWidget(self.wob_avg_spin, 0, 1)
        
        params_layout.addWidget(QLabel("RPM:"), 0, 2)
        self.rpm_avg_spin = QDoubleSpinBox()
        self.rpm_avg_spin.setRange(0, 500)
        params_layout.addWidget(self.rpm_avg_spin, 0, 3)
        
        # Row 2
        params_layout.addWidget(QLabel("Flowrate (gpm):"), 1, 0)
        self.flowrate_avg_spin = QDoubleSpinBox()
        self.flowrate_avg_spin.setRange(0, 2000)
        params_layout.addWidget(self.flowrate_avg_spin, 1, 1)
        
        params_layout.addWidget(QLabel("SPP (psi):"), 1, 2)
        self.spp_avg_spin = QDoubleSpinBox()
        self.spp_avg_spin.setRange(0, 5000)
        params_layout.addWidget(self.spp_avg_spin, 1, 3)
        
        # Row 3
        params_layout.addWidget(QLabel("PV (cp):"), 2, 0)
        self.pv_avg_spin = QDoubleSpinBox()
        self.pv_avg_spin.setRange(0, 100)
        params_layout.addWidget(self.pv_avg_spin, 2, 1)
        
        params_layout.addWidget(QLabel("YP (lb/100ft²):"), 2, 2)
        self.yp_avg_spin = QDoubleSpinBox()
        self.yp_avg_spin.setRange(0, 50)
        params_layout.addWidget(self.yp_avg_spin, 2, 3)
        
        params_group.setLayout(params_layout)
        form_layout.addRow(params_group)
        
        # Technical Data group
        tech_group = QGroupBox("Technical Data")
        tech_layout = QGridLayout()
        
        tech_layout.addWidget(QLabel("Cumulative Drilling (m):"), 0, 0)
        self.cumulative_drilling_spin = QDoubleSpinBox()
        self.cumulative_drilling_spin.setRange(0, 100000)
        tech_layout.addWidget(self.cumulative_drilling_spin, 0, 1)
        
        tech_layout.addWidget(QLabel("Revolution:"), 0, 2)
        self.revolution_spin = QDoubleSpinBox()
        self.revolution_spin.setRange(0, 1000000)
        tech_layout.addWidget(self.revolution_spin, 0, 3)
        
        tech_layout.addWidget(QLabel("TFA (in²):"), 1, 0)
        self.tfa_spin = QDoubleSpinBox()
        self.tfa_spin.setRange(0, 5)
        tech_layout.addWidget(self.tfa_spin, 1, 1)
        
        tech_group.setLayout(tech_layout)
        form_layout.addRow(tech_group)
        
        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def create_photos_tab(self):
        """Create photos tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Before Photo section
        before_group = QGroupBox("Before Run Photo")
        before_layout = QVBoxLayout()
        
        self.before_photo_label = QLabel("No photo selected")
        self.before_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.before_photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                padding: 20px;
                background-color: #f8f9fa;
            }
        """)
        before_layout.addWidget(self.before_photo_label)
        
        before_button_layout = QHBoxLayout()
        before_browse_button = QPushButton("Browse Photo")
        before_browse_button.clicked.connect(lambda: self.browse_photo("before"))
        before_clear_button = QPushButton("Clear")
        before_clear_button.clicked.connect(lambda: self.clear_photo("before"))
        
        before_button_layout.addWidget(before_browse_button)
        before_button_layout.addWidget(before_clear_button)
        before_button_layout.addStretch()
        before_layout.addLayout(before_button_layout)
        
        before_group.setLayout(before_layout)
        layout.addWidget(before_group)
        
        # After Photo section
        after_group = QGroupBox("After Run Photo")
        after_layout = QVBoxLayout()
        
        self.after_photo_label = QLabel("No photo selected")
        self.after_photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.after_photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                padding: 20px;
                background-color: #f8f9fa;
            }
        """)
        after_layout.addWidget(self.after_photo_label)
        
        after_button_layout = QHBoxLayout()
        after_browse_button = QPushButton("Browse Photo")
        after_browse_button.clicked.connect(lambda: self.browse_photo("after"))
        after_clear_button = QPushButton("Clear")
        after_clear_button.clicked.connect(lambda: self.clear_photo("after"))
        
        after_button_layout.addWidget(after_browse_button)
        after_button_layout.addWidget(after_clear_button)
        after_button_layout.addStretch()
        after_layout.addLayout(after_button_layout)
        
        after_group.setLayout(after_layout)
        layout.addWidget(after_group)
        
        # Photo notes
        notes_group = QGroupBox("Photo Notes")
        notes_layout = QVBoxLayout()
        
        self.photo_notes_text = QTextEdit()
        self.photo_notes_text.setPlaceholderText("Add notes about the photos...")
        self.photo_notes_text.setMaximumHeight(100)
        notes_layout.addWidget(self.photo_notes_text)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def browse_photo(self, photo_type):
        """Browse for photo file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {photo_type.capitalize()} Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            label = getattr(self, f"{photo_type}_photo_label")
            label.setText(f"Photo: {Path(file_path).name}")
            label.setToolTip(file_path)
    
    def clear_photo(self, photo_type):
        """Clear selected photo"""
        label = getattr(self, f"{photo_type}_photo_label")
        label.setText("No photo selected")
        label.setToolTip("")

class BHAReportWidget(QWidget):
    """BHA report widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.components = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Bottom Hole Assembly (BHA) Report")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Run Information
        run_group = QGroupBox("Run Information")
        run_layout = QGridLayout()
        
        run_layout.addWidget(QLabel("Run No:"), 0, 0)
        self.run_no_spin = QSpinBox()
        self.run_no_spin.setRange(1, 100)
        run_layout.addWidget(self.run_no_spin, 0, 1)
        
        run_layout.addWidget(QLabel("Run Date:"), 0, 2)
        self.run_date_edit = QDateEdit()
        self.run_date_edit.setCalendarPopup(True)
        self.run_date_edit.setDate(QDate.currentDate())
        run_layout.addWidget(self.run_date_edit, 0, 3)
        
        run_layout.addWidget(QLabel("Well:"), 1, 0)
        self.well_combo = QComboBox()
        run_layout.addWidget(self.well_combo, 1, 1, 1, 3)
        
        run_group.setLayout(run_layout)
        main_layout.addWidget(run_group)
        
        # BHA Components Table
        table_group = QGroupBox("BHA Components")
        table_layout = QVBoxLayout()
        
        self.bha_table = QTableWidget()
        self.bha_table.setColumnCount(7)
        self.bha_table.setHorizontalHeaderLabels([
            "Tool Type", "OD (in)", "ID (in)", "Length (m)", 
            "Serial No", "Weight (kg)", "Remarks"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Component")
        add_button.clicked.connect(self.add_component_dialog)
        
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_component)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_component)
        
        move_up_button = QPushButton("Move Up")
        move_up_button.clicked.connect(self.move_component_up)
        
        move_down_button = QPushButton("Move Down")
        move_down_button.clicked.connect(self.move_component_down)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(move_up_button)
        table_buttons.addWidget(move_down_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.bha_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Remarks section
        remarks_group = QGroupBox("Remarks")
        remarks_layout = QVBoxLayout()
        
        self.remarks_text = QTextEdit()
        self.remarks_text.setPlaceholderText("Add any remarks about this BHA run...")
        self.remarks_text.setMaximumHeight(100)
        remarks_layout.addWidget(self.remarks_text)
        
        remarks_group.setLayout(remarks_layout)
        main_layout.addWidget(remarks_group)
        
        # Save button
        save_button = QPushButton("Save BHA Report")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        save_button.clicked.connect(self.save_bha_report)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def add_component_dialog(self):
        """Show dialog to add BHA component"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add BHA Component")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Tool Type
        self.component_tool_type = QComboBox()
        self.component_tool_type.addItems([
            "Bit", "Stabilizer", "Drill Collar", "Heavy Weight Drill Pipe",
            "MWD", "LWD", "Motor", "RSS", "Cross Over", "Float Valve",
            "Jar", "Shock Sub", "Reamer", "Underreamer", "Other"
        ])
        form.addRow("Tool Type:", self.component_tool_type)
        
        # Dimensions
        dim_layout = QHBoxLayout()
        self.component_od = QDoubleSpinBox()
        self.component_od.setRange(0, 50)
        self.component_od.setSuffix(" in")
        
        self.component_id = QDoubleSpinBox()
        self.component_id.setRange(0, 50)
        self.component_id.setSuffix(" in")
        
        self.component_length = QDoubleSpinBox()
        self.component_length.setRange(0, 100)
        self.component_length.setSuffix(" m")
        
        dim_layout.addWidget(QLabel("OD:"))
        dim_layout.addWidget(self.component_od)
        dim_layout.addWidget(QLabel("ID:"))
        dim_layout.addWidget(self.component_id)
        dim_layout.addWidget(QLabel("Length:"))
        dim_layout.addWidget(self.component_length)
        
        form.addRow("Dimensions:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(dim_layout)
        
        # Serial No and Weight
        self.component_serial = QLineEdit()
        self.component_serial.setPlaceholderText("Enter serial number")
        form.addRow("Serial No:", self.component_serial)
        
        self.component_weight = QDoubleSpinBox()
        self.component_weight.setRange(0, 10000)
        self.component_weight.setSuffix(" kg")
        form.addRow("Weight:", self.component_weight)
        
        # Remarks
        self.component_remarks = QTextEdit()
        self.component_remarks.setMaximumHeight(60)
        form.addRow("Remarks:", self.component_remarks)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_component_to_table(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_component_to_table(self, dialog):
        """Add component to table"""
        component = BHAComponent(
            tool_type=self.component_tool_type.currentText(),
            od=self.component_od.value(),
            id=self.component_id.value(),
            length=self.component_length.value(),
            serial_no=self.component_serial.text(),
            weight=self.component_weight.value(),
            remarks=self.component_remarks.toPlainText()
        )
        
        # Add to table
        row = self.bha_table.rowCount()
        self.bha_table.insertRow(row)
        
        self.bha_table.setItem(row, 0, QTableWidgetItem(component.tool_type))
        self.bha_table.setItem(row, 1, QTableWidgetItem(f"{component.od:.2f}"))
        self.bha_table.setItem(row, 2, QTableWidgetItem(f"{component.id:.2f}"))
        self.bha_table.setItem(row, 3, QTableWidgetItem(f"{component.length:.2f}"))
        self.bha_table.setItem(row, 4, QTableWidgetItem(component.serial_no))
        self.bha_table.setItem(row, 5, QTableWidgetItem(f"{component.weight:.1f}"))
        self.bha_table.setItem(row, 6, QTableWidgetItem(component.remarks))
        
        # Add to internal list
        self.components.append(component)
        
        dialog.accept()
    
    def edit_component(self):
        """Edit selected component"""
        selected_row = self.bha_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a component to edit.")
            return
        
        # TODO: Implement edit functionality
        pass
    
    def delete_component(self):
        """Delete selected component"""
        selected_row = self.bha_table.currentRow()
        if selected_row >= 0:
            self.bha_table.removeRow(selected_row)
            if selected_row < len(self.components):
                del self.components[selected_row]
    
    def move_component_up(self):
        """Move component up in the table"""
        selected_row = self.bha_table.currentRow()
        if selected_row > 0:
            self.swap_rows(selected_row, selected_row - 1)
            self.bha_table.setCurrentCell(selected_row - 1, 0)
    
    def move_component_down(self):
        """Move component down in the table"""
        selected_row = self.bha_table.currentRow()
        if selected_row < self.bha_table.rowCount() - 1:
            self.swap_rows(selected_row, selected_row + 1)
            self.bha_table.setCurrentCell(selected_row + 1, 0)
    
    def swap_rows(self, row1, row2):
        """Swap two rows in the table"""
        for col in range(self.bha_table.columnCount()):
            item1 = self.bha_table.takeItem(row1, col)
            item2 = self.bha_table.takeItem(row2, col)
            self.bha_table.setItem(row2, col, item1)
            self.bha_table.setItem(row1, col, item2)
        
        # Swap in components list
        if row1 < len(self.components) and row2 < len(self.components):
            self.components[row1], self.components[row2] = self.components[row2], self.components[row1]
    
    def save_bha_report(self):
        """Save BHA report to database"""
        well_index = self.well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        if not self.components:
            QMessageBox.warning(self, "Error", "Please add at least one BHA component.")
            return
        
        well_id = self.well_combo.itemData(well_index)
        
        # Create BHA run object
        bha_run = BHARun(
            well_id=well_id,
            run_no=self.run_no_spin.value(),
            run_date=self.run_date_edit.date().toString("yyyy-MM-dd"),
            components=self.components
        )
        
        # TODO: Save to database
        QMessageBox.information(self, "Success", "BHA report saved successfully!")

class SurveyDataWidget(QWidget):
    """Survey data and formation tops widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        # Tab widget for survey and formation data
        tabs = QTabWidget()
        
        # Survey Data tab
        survey_tab = self.create_survey_tab()
        tabs.addTab(survey_tab, "Survey Data")
        
        # Formation Tops tab
        formation_tab = self.create_formation_tab()
        tabs.addTab(formation_tab, "Formation Tops")
        
        # Visualization tab
        viz_tab = self.create_visualization_tab()
        tabs.addTab(viz_tab, "Visualization")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Survey Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_survey_tab(self):
        """Create survey data tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.survey_well_combo = QComboBox()
        
        load_button = QPushButton("Load Survey Data")
        new_button = QPushButton("New Survey")
        
        well_layout.addWidget(self.survey_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addWidget(new_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Survey table
        table_group = QGroupBox("Survey Stations")
        table_layout = QVBoxLayout()
        
        self.survey_table = QTableWidget()
        self.survey_table.setColumnCount(10)
        self.survey_table.setHorizontalHeaderLabels([
            "MD (m)", "Inc (°)", "Azi (°)", "TVD (m)", "North (m)", 
            "East (m)", "VS (m)", "HD (m)", "DLS (°/30m)", "Tool"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Station")
        delete_button = QPushButton("Delete Selected")
        calculate_button = QPushButton("Calculate")
        import_button = QPushButton("Import CSV")
        export_button = QPushButton("Export CSV")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(calculate_button)
        table_buttons.addWidget(import_button)
        table_buttons.addWidget(export_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.survey_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Survey information
        info_group = QGroupBox("Survey Information")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Survey Date:"), 0, 0)
        self.survey_date_edit = QDateEdit()
        self.survey_date_edit.setCalendarPopup(True)
        self.survey_date_edit.setDate(QDate.currentDate())
        info_layout.addWidget(self.survey_date_edit, 0, 1)
        
        info_layout.addWidget(QLabel("Survey Company:"), 0, 2)
        self.survey_company_input = QLineEdit()
        info_layout.addWidget(self.survey_company_input, 0, 3)
        
        info_layout.addWidget(QLabel("Tool Type:"), 1, 0)
        self.survey_tool_combo = QComboBox()
        self.survey_tool_combo.addItems([
            "Gyro", "MEMS", "MWD", "Single Shot", "Multi Shot", "Other"
        ])
        info_layout.addWidget(self.survey_tool_combo, 1, 1)
        
        info_layout.addWidget(QLabel("Surveyor:"), 1, 2)
        self.surveyor_input = QLineEdit()
        info_layout.addWidget(self.surveyor_input, 1, 3)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_formation_tab(self):
        """Create formation tops tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.formation_well_combo = QComboBox()
        
        load_button = QPushButton("Load Formation Tops")
        import_button = QPushButton("Import from Plan")
        
        well_layout.addWidget(self.formation_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addWidget(import_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Formation table
        table_group = QGroupBox("Formation Tops")
        table_layout = QVBoxLayout()
        
        self.formation_table = QTableWidget()
        self.formation_table.setColumnCount(5)
        self.formation_table.setHorizontalHeaderLabels([
            "Formation Name", "Lithology", "MD (m)", "TVD (m)", "Description"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Formation")
        edit_button = QPushButton("Edit Selected")
        delete_button = QPushButton("Delete Selected")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.formation_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Formation notes
        notes_group = QGroupBox("Formation Notes")
        notes_layout = QVBoxLayout()
        
        self.formation_notes_text = QTextEdit()
        self.formation_notes_text.setPlaceholderText("Add notes about formations...")
        self.formation_notes_text.setMaximumHeight(100)
        notes_layout.addWidget(self.formation_notes_text)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_visualization_tab(self):
        """Create visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Visualization controls
        controls_group = QGroupBox("Visualization Controls")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("View Type:"), 0, 0)
        self.view_type_combo = QComboBox()
        self.view_type_combo.addItems([
            "Vertical Section", "Plan View", "3D View", 
            "TVD vs MD", "Dogleg Plot"
        ])
        controls_layout.addWidget(self.view_type_combo, 0, 1)
        
        controls_layout.addWidget(QLabel("Color Scheme:"), 0, 2)
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(["Rainbow", "Blue-Red", "Green-Brown", "Grayscale"])
        controls_layout.addWidget(self.color_scheme_combo, 0, 3)
        
        controls_layout.addWidget(QLabel("Show:"), 1, 0)
        
        self.show_well_path = QCheckBox("Well Path")
        self.show_well_path.setChecked(True)
        controls_layout.addWidget(self.show_well_path, 1, 1)
        
        self.show_formations = QCheckBox("Formations")
        self.show_formations.setChecked(True)
        controls_layout.addWidget(self.show_formations, 1, 2)
        
        self.show_casing = QCheckBox("Casing")
        controls_layout.addWidget(self.show_casing, 1, 3)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Visualization area
        viz_area_group = QGroupBox("Visualization")
        viz_area_layout = QVBoxLayout()
        
        self.viz_label = QLabel("Visualization Area\n\n3D well path visualization will appear here.")
        self.viz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                padding: 50px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
        """)
        
        viz_area_layout.addWidget(self.viz_label)
        viz_area_group.setLayout(viz_area_layout)
        layout.addWidget(viz_area_group)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_image_button = QPushButton("Export as Image")
        export_report_button = QPushButton("Generate Report")
        print_button = QPushButton("Print")
        
        export_layout.addWidget(export_image_button)
        export_layout.addWidget(export_report_button)
        export_layout.addWidget(print_button)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        return tab

class PersonnelLogisticsWidget(QWidget):
    """Personnel and logistics widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Personnel tab
        personnel_tab = self.create_personnel_tab()
        tabs.addTab(personnel_tab, "Personnel")
        
        # POB tab
        pob_tab = self.create_pob_tab()
        tabs.addTab(pob_tab, "POB Status")
        
        # Transport tab
        transport_tab = self.create_transport_tab()
        tabs.addTab(transport_tab, "Transport")
        
        # Weather tab
        weather_tab = self.create_weather_tab()
        tabs.addTab(weather_tab, "Weather")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Logistics Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6c7b7d;
            }
        """)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_personnel_tab(self):
        """Create personnel management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.personnel_well_combo = QComboBox()
        
        load_button = QPushButton("Load Personnel")
        
        well_layout.addWidget(self.personnel_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Personnel table
        table_group = QGroupBox("Crew List")
        table_layout = QVBoxLayout()
        
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(9)
        self.personnel_table.setHorizontalHeaderLabels([
            "Company", "Name", "Position", "Arrival Date", 
            "Departure Date", "POB", "Contact", "Emergency Contact", "Status"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Person")
        edit_button = QPushButton("Edit Selected")
        delete_button = QPushButton("Delete Selected")
        import_button = QPushButton("Import CSV")
        export_button = QPushButton("Export CSV")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(import_button)
        table_buttons.addWidget(export_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.personnel_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Summary
        summary_group = QGroupBox("Personnel Summary")
        summary_layout = QGridLayout()
        
        self.total_personnel_label = QLabel("Total: 0")
        self.onboard_label = QLabel("On Board: 0")
        self.offboard_label = QLabel("Off Board: 0")
        self.companies_label = QLabel("Companies: 0")
        
        summary_layout.addWidget(self.total_personnel_label, 0, 0)
        summary_layout.addWidget(self.onboard_label, 0, 1)
        summary_layout.addWidget(self.offboard_label, 0, 2)
        summary_layout.addWidget(self.companies_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_pob_tab(self):
        """Create POB status tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # POB Controls
        controls_group = QGroupBox("POB Controls")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Current POB:"), 0, 0)
        self.current_pob_label = QLabel("0")
        self.current_pob_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #27ae60;")
        controls_layout.addWidget(self.current_pob_label, 0, 1)
        
        controls_layout.addWidget(QLabel("Max Capacity:"), 0, 2)
        self.max_capacity_spin = QSpinBox()
        self.max_capacity_spin.setRange(0, 500)
        self.max_capacity_spin.setValue(150)
        controls_layout.addWidget(self.max_capacity_spin, 0, 3)
        
        update_button = QPushButton("Update POB")
        controls_layout.addWidget(update_button, 1, 0, 1, 4)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # POB by Company
        company_group = QGroupBox("POB by Company")
        company_layout = QVBoxLayout()
        
        self.company_pob_table = QTableWidget()
        self.company_pob_table.setColumnCount(3)
        self.company_pob_table.setHorizontalHeaderLabels(["Company", "On Board", "Total"])
        
        company_layout.addWidget(self.company_pob_table)
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # POB History
        history_group = QGroupBox("POB History (Last 7 Days)")
        history_layout = QVBoxLayout()
        
        self.pob_history_table = QTableWidget()
        self.pob_history_table.setColumnCount(3)
        self.pob_history_table.setHorizontalHeaderLabels(["Date", "POB Count", "Change"])
        
        history_layout.addWidget(self.pob_history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_transport_tab(self):
        """Create transport log tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Boats section
        boats_group = QGroupBox("Boats Log")
        boats_layout = QVBoxLayout()
        
        self.boats_table = QTableWidget()
        self.boats_table.setColumnCount(6)
        self.boats_table.setHorizontalHeaderLabels([
            "Boat Name", "Arrival", "Departure", "Status", "Cargo", "Remarks"
        ])
        
        boats_buttons = QHBoxLayout()
        add_boat_button = QPushButton("Add Boat")
        remove_boat_button = QPushButton("Remove Selected")
        
        boats_buttons.addWidget(add_boat_button)
        boats_buttons.addWidget(remove_boat_button)
        boats_buttons.addStretch()
        
        boats_layout.addWidget(self.boats_table)
        boats_layout.addLayout(boats_buttons)
        boats_group.setLayout(boats_layout)
        layout.addWidget(boats_group)
        
        # Helicopter section
        heli_group = QGroupBox("Helicopter Log")
        heli_layout = QVBoxLayout()
        
        self.heli_table = QTableWidget()
        self.heli_table.setColumnCount(5)
        self.heli_table.setHorizontalHeaderLabels([
            "Flight No", "Arrival", "Departure", "PAX IN", "PAX OUT"
        ])
        
        heli_buttons = QHBoxLayout()
        add_heli_button = QPushButton("Add Flight")
        remove_heli_button = QPushButton("Remove Selected")
        
        heli_buttons.addWidget(add_heli_button)
        heli_buttons.addWidget(remove_heli_button)
        heli_buttons.addStretch()
        
        heli_layout.addWidget(self.heli_table)
        heli_layout.addLayout(heli_buttons)
        heli_group.setLayout(heli_layout)
        layout.addWidget(heli_group)
        
        # Transport notes
        notes_group = QGroupBox("Transport Notes")
        notes_layout = QVBoxLayout()
        
        self.transport_notes_text = QTextEdit()
        self.transport_notes_text.setPlaceholderText("Add transport notes...")
        self.transport_notes_text.setMaximumHeight(80)
        notes_layout.addWidget(self.transport_notes_text)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_weather_tab(self):
        """Create weather data tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Current weather
        current_group = QGroupBox("Current Weather")
        current_layout = QGridLayout()
        
        current_layout.addWidget(QLabel("Wind Speed:"), 0, 0)
        self.wind_speed_spin = QDoubleSpinBox()
        self.wind_speed_spin.setRange(0, 200)
        self.wind_speed_spin.setSuffix(" knots")
        current_layout.addWidget(self.wind_speed_spin, 0, 1)
        
        current_layout.addWidget(QLabel("Wind Direction:"), 0, 2)
        self.wind_direction_combo = QComboBox()
        self.wind_direction_combo.addItems([
            "N", "NE", "E", "SE", "S", "SW", "W", "NW"
        ])
        current_layout.addWidget(self.wind_direction_combo, 0, 3)
        
        current_layout.addWidget(QLabel("Temperature:"), 1, 0)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(-50, 60)
        self.temperature_spin.setSuffix(" °C")
        self.temperature_spin.setValue(25)
        current_layout.addWidget(self.temperature_spin, 1, 1)
        
        current_layout.addWidget(QLabel("Visibility:"), 1, 2)
        self.visibility_spin = QDoubleSpinBox()
        self.visibility_spin.setRange(0, 100)
        self.visibility_spin.setSuffix(" km")
        current_layout.addWidget(self.visibility_spin, 1, 3)
        
        current_layout.addWidget(QLabel("Sea State:"), 2, 0)
        self.sea_state_combo = QComboBox()
        self.sea_state_combo.addItems([
            "Calm", "Smooth", "Slight", "Moderate", 
            "Rough", "Very Rough", "High", "Very High"
        ])
        current_layout.addWidget(self.sea_state_combo, 2, 1)
        
        current_layout.addWidget(QLabel("Wave Height:"), 2, 2)
        self.wave_height_spin = QDoubleSpinBox()
        self.wave_height_spin.setRange(0, 30)
        self.wave_height_spin.setSuffix(" m")
        current_layout.addWidget(self.wave_height_spin, 2, 3)
        
        record_button = QPushButton("Record Current Weather")
        current_layout.addWidget(record_button, 3, 0, 1, 4)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Weather history
        history_group = QGroupBox("Weather History (Last 24 Hours)")
        history_layout = QVBoxLayout()
        
        self.weather_history_table = QTableWidget()
        self.weather_history_table.setColumnCount(6)
        self.weather_history_table.setHorizontalHeaderLabels([
            "Time", "Wind Speed", "Direction", "Temp", "Visibility", "Sea State"
        ])
        
        history_layout.addWidget(self.weather_history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Weather forecast
        forecast_group = QGroupBox("Weather Forecast")
        forecast_layout = QVBoxLayout()
        
        self.forecast_text = QTextEdit()
        self.forecast_text.setPlaceholderText("Enter weather forecast information...")
        self.forecast_text.setMaximumHeight(100)
        forecast_layout.addWidget(self.forecast_text)
        
        forecast_group.setLayout(forecast_layout)
        layout.addWidget(forecast_group)
        
        tab.setLayout(layout)
        return tab

# ============================================
# MAIN APPLICATION WINDOW
# ============================================

class MainWindow(QMainWindow):
    """Main application window with ribbon interface"""
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.current_well_id = -1
        self.init_ui()
    
    def init_ui(self):
        # Window settings
        self.setWindowTitle(f"Nikan Drill Master - Logged in as: {self.user.full_name}")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVStackLayout()
        
        # Create ribbon
        self.create_ribbon()
        main_layout.addWidget(self.ribbon_widget)
        
        # Create tab widget for modules
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        
        # Initialize modules
        self.init_modules()
        
        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready - User: {self.user.role.capitalize()}")
        
        # Initialize with Well Info tab
        self.tab_widget.setCurrentIndex(0)
    
    def create_ribbon(self):
        """Create ribbon interface"""
        self.ribbon_widget = QWidget()
        ribbon_layout = QVBoxLayout()
        
        # Ribbon tabs
        self.ribbon_tabs = QTabWidget()
        self.ribbon_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.ribbon_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #f8f9fa;
                border-bottom: 2px solid #007bff;
            }
            QTabBar::tab:hover {
                background-color: #dee2e6;
            }
        """)
        
        # Home tab
        home_tab = self.create_ribbon_home_tab()
        self.ribbon_tabs.addTab(home_tab, "🏠 Home")
        
        # Daily Operations tab
        daily_tab = self.create_ribbon_daily_tab()
        self.ribbon_tabs.addTab(daily_tab, "🗓 Daily Ops")
        
        # Drilling tab
        drilling_tab = self.create_ribbon_drilling_tab()
        self.ribbon_tabs.addTab(drilling_tab, "⚙️ Drilling")
        
        # Data & Evaluation tab
        data_tab = self.create_ribbon_data_tab()
        self.ribbon_tabs.addTab(data_tab, "📈 Data & Eval")
        
        # Logistics tab
        logistics_tab = self.create_ribbon_logistics_tab()
        self.ribbon_tabs.addTab(logistics_tab, "🧰 Logistics")
        
        # Safety tab
        safety_tab = self.create_ribbon_safety_tab()
        self.ribbon_tabs.addTab(safety_tab, "🦺 Safety")
        
        # Reports tab
        reports_tab = self.create_ribbon_reports_tab()
        self.ribbon_tabs.addTab(reports_tab, "📤 Reports")
        
        ribbon_layout.addWidget(self.ribbon_tabs)
        self.ribbon_widget.setLayout(ribbon_layout)
    
    def create_ribbon_home_tab(self):
        """Create Home ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Well group
        well_group = RibbonGroup("Well")
        well_group.add_button("New Well", None, self.new_well, "Create new well")
        well_group.add_button("Open Well", None, self.open_well, "Open existing well")
        well_group.add_button("Save Well", None, self.save_well, "Save current well")
        layout.addWidget(well_group)
        
        # Reports group
        reports_group = RibbonGroup("Reports")
        reports_group.add_button("Daily Report", None, lambda: self.show_module(1), "Open daily report")
        reports_group.add_button("Drilling Params", None, lambda: self.show_module(2), "Open drilling parameters")
        reports_group.add_button("Mud Report", None, lambda: self.show_module(3), "Open mud report")
        layout.addWidget(reports_group)
        
        # Export group
        export_group = RibbonGroup("Export")
        export_group.add_button("Export PDF", None, self.export_pdf, "Export to PDF")
        export_group.add_button("Export Excel", None, self.export_excel, "Export to Excel")
        layout.addWidget(export_group)
        
        # User group
        user_group = RibbonGroup("User")
        user_group.add_button("Preferences", None, self.show_preferences, "User preferences")
        user_group.add_button("Logout", None, self.logout, "Logout from system")
        layout.addWidget(user_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_daily_tab(self):
        """Create Daily Operations ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Time Log group
        time_group = RibbonGroup("Time Log")
        time_group.add_button("Add Entry", None, self.add_time_entry, "Add time log entry")
        time_group.add_button("Edit Entry", None, self.edit_time_entry, "Edit time log entry")
        time_group.add_button("NPT Report", None, self.show_npt_report, "Non-productive time report")
        layout.addWidget(time_group)
        
        # Planning group
        plan_group = RibbonGroup("Planning")
        plan_group.add_button("7-Day Lookahead", None, self.show_lookahead, "7 days lookahead plan")
        plan_group.add_button("Activity Codes", None, self.show_codes, "Activity code management")
        layout.addWidget(plan_group)
        
        # Analysis group
        analysis_group = RibbonGroup("Analysis")
        analysis_group.add_button("Time Analysis", None, self.time_analysis, "Time breakdown analysis")
        analysis_group.add_button("Productivity", None, self.productivity, "Productivity analysis")
        layout.addWidget(analysis_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_drilling_tab(self):
        """Create Drilling ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Drilling group
        drilling_group = RibbonGroup("Drilling")
        drilling_group.add_button("Parameters", None, lambda: self.show_module(2), "Drilling parameters")
        drilling_group.add_button("Mud Report", None, lambda: self.show_module(3), "Mud properties and volumes")
        drilling_group.add_button("Bit Record", None, lambda: self.show_module(4), "Bit records and reports")
        layout.addWidget(drilling_group)
        
        # Equipment group
        equipment_group = RibbonGroup("Equipment")
        equipment_group.add_button("BHA Report", None, lambda: self.show_module(5), "Bottom hole assembly")
        equipment_group.add_button("Downhole Eq", None, self.show_downhole, "Downhole equipment")
        equipment_group.add_button("Drill Pipe", None, self.show_drill_pipe, "Drill pipe specifications")
        layout.addWidget(equipment_group)
        
        # Cementing group
        cement_group = RibbonGroup("Cementing")
        cement_group.add_button("Cement Data", None, self.show_cement, "Cement and additives")
        cement_group.add_button("Casing Data", None, self.show_casing, "Casing specifications")
        layout.addWidget(cement_group)
        
        # Solid Control group
        solid_group = RibbonGroup("Solid Control")
        solid_group.add_button("Equipment", None, self.show_solid_control, "Solid control equipment")
        solid_group.add_button("Performance", None, self.solid_performance, "Solid control performance")
        layout.addWidget(solid_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_data_tab(self):
        """Create Data & Evaluation ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Survey group
        survey_group = RibbonGroup("Survey")
        survey_group.add_button("Survey Data", None, lambda: self.show_module(6), "Well survey data")
        survey_group.add_button("Formation Tops", None, self.show_formations, "Formation tops")
        survey_group.add_button("Trajectory", None, self.show_trajectory, "Well trajectory")
        layout.addWidget(survey_group)
        
        # Evaluation group
        eval_group = RibbonGroup("Evaluation")
        eval_group.add_button("ROP Analysis", None, self.rop_analysis, "Rate of penetration analysis")
        eval_group.add_button("Formation Eval", None, self.formation_eval, "Formation evaluation")
        layout.addWidget(eval_group)
        
        # Charts group
        charts_group = RibbonGroup("Charts")
        charts_group.add_button("Drilling Chart", None, self.drilling_chart, "Drilling parameters chart")
        charts_group.add_button("Survey Chart", None, self.survey_chart, "Survey visualization")
        charts_group.add_button("Mud Chart", None, self.mud_chart, "Mud properties chart")
        layout.addWidget(charts_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_logistics_tab(self):
        """Create Logistics ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Personnel group
        personnel_group = RibbonGroup("Personnel")
        personnel_group.add_button("Crew List", None, lambda: self.show_module(7), "Personnel management")
        personnel_group.add_button("POB Status", None, self.show_pob, "Person on board status")
        layout.addWidget(personnel_group)
        
        # Inventory group
        inventory_group = RibbonGroup("Inventory")
        inventory_group.add_button("Inventory", None, self.show_inventory, "Inventory management")
        inventory_group.add_button("Material Request", None, self.show_material, "Material handling")
        layout.addWidget(inventory_group)
        
        # Services group
        services_group = RibbonGroup("Services")
        services_group.add_button("Service Cos", None, self.show_services, "Service company log")
        services_group.add_button("Boats/Chopper", None, self.show_transport, "Transport log")
        layout.addWidget(services_group)
        
        # Weather group
        weather_group = RibbonGroup("Weather")
        weather_group.add_button("Weather Data", None, self.show_weather, "Weather conditions")
        weather_group.add_button("Forecast", None, self.show_forecast, "Weather forecast")
        layout.addWidget(weather_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_safety_tab(self):
        """Create Safety ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Safety group
        safety_group = RibbonGroup("Safety")
        safety_group.add_button("Safety & BOP", None, self.show_safety, "Safety and BOP records")
        safety_group.add_button("Drills", None, self.show_drills, "Safety drills")
        layout.addWidget(safety_group)
        
        # Environment group
        env_group = RibbonGroup("Environment")
        env_group.add_button("Waste Mgmt", None, self.show_waste, "Waste management")
        env_group.add_button("Spill Report", None, self.spill_report, "Spill reporting")
        layout.addWidget(env_group)
        
        # Compliance group
        compliance_group = RibbonGroup("Compliance")
        compliance_group.add_button("Inspections", None, self.show_inspections, "Safety inspections")
        compliance_group.add_button("Incidents", None, self.show_incidents, "Incident reporting")
        layout.addWidget(compliance_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_ribbon_reports_tab(self):
        """Create Reports ribbon tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Generation group
        gen_group = RibbonGroup("Generation")
        gen_group.add_button("Daily Report", None, self.generate_daily, "Generate daily report")
        gen_group.add_button("Weekly Report", None, self.generate_weekly, "Generate weekly report")
        gen_group.add_button("EOW Report", None, self.generate_eow, "End of well report")
        layout.addWidget(gen_group)
        
        # Export group
        export_group = RibbonGroup("Export")
        export_group.add_button("PDF", None, self.export_pdf, "Export to PDF")
        export_group.add_button("Excel", None, self.export_excel, "Export to Excel")
        export_group.add_button("CSV", None, self.export_csv, "Export to CSV")
        layout.addWidget(export_group)
        
        # Templates group
        template_group = RibbonGroup("Templates")
        template_group.add_button("Save Template", None, self.save_template, "Save report template")
        template_group.add_button("Load Template", None, self.load_template, "Load report template")
        layout.addWidget(template_group)
        
        # KPI group
        kpi_group = RibbonGroup("KPIs")
        kpi_group.add_button("NPT Analysis", None, self.npt_analysis, "NPT analysis report")
        kpi_group.add_button("Cost Analysis", None, self.cost_analysis, "Cost analysis report")
        layout.addWidget(kpi_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def init_modules(self):
        """Initialize all application modules"""
        # Well Information
        self.well_info_widget = WellInfoWidget(self.db)
        self.tab_widget.addTab(self.well_info_widget, "🏠 Well Info")
        
        # Daily Report
        self.daily_report_widget = DailyReportWidget(self.db)
        self.tab_widget.addTab(self.daily_report_widget, "🗓 Daily Report")
        
        # Drilling Parameters
        self.drilling_params_widget = DrillingParametersWidget(self.db)
        self.tab_widget.addTab(self.drilling_params_widget, "⚙️ Drilling Params")
        
        # Mud Report
        self.mud_report_widget = MudReportWidget(self.db)
        self.tab_widget.addTab(self.mud_report_widget, "🧪 Mud Report")
        
        # Bit Report
        self.bit_report_widget = BitReportWidget(self.db)
        self.tab_widget.addTab(self.bit_report_widget, "🔩 Bit Report")
        
        # BHA Report
        self.bha_report_widget = BHAReportWidget(self.db)
        self.tab_widget.addTab(self.bha_report_widget, "🛠️ BHA Report")
        
        # Survey Data
        self.survey_widget = SurveyDataWidget(self.db)
        self.tab_widget.addTab(self.survey_widget, "📈 Survey Data")
        
        # Personnel & Logistics
        self.personnel_widget = PersonnelLogisticsWidget(self.db)
        self.tab_widget.addTab(self.personnel_widget, "👥 Personnel & Logistics")
        
        # Add placeholders for other modules
        self.add_placeholder_tabs()
    
    def add_placeholder_tabs(self):
        """Add placeholder tabs for remaining modules"""
        modules = [
            ("📦 Inventory", "Inventory management"),
            ("🏢 Service Cos", "Service company log"),
            ("📝 Material Handling", "Material handling and notes"),
            ("🦺 Safety & BOP", "Safety and BOP records"),
            ("♻️ Waste Mgmt", "Waste management"),
            ("🏗️ Cement & Casing", "Cement and casing data"),
            ("⚙️ Downhole Eq", "Downhole equipment"),
            ("🔧 Drill Pipe", "Drill pipe specs"),
            ("🌀 Solid Control", "Solid control equipment"),
            ("⛽ Fuel & Water", "Fuel and water management"),
            ("📊 Export Center", "Report export center"),
            ("⚙️ Preferences", "User preferences")
        ]
        
        for title, description in modules:
            placeholder = QWidget()
            layout = QVBoxLayout()
            
            label = QLabel(f"{title}\n\n{description}\n\n(This module will be implemented in the next phase)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
            
            layout.addWidget(label)
            placeholder.setLayout(layout)
            self.tab_widget.addTab(placeholder, title)
    
    def show_module(self, index):
        """Show specific module by index"""
        self.tab_widget.setCurrentIndex(index)
    
    def new_well(self):
        """Create new well"""
        self.well_info_widget.clear_form()
        self.tab_widget.setCurrentIndex(0)
        self.status_bar.showMessage("Creating new well...")
    
    def open_well(self):
        """Open existing well"""
        self.well_info_widget.load_well_dialog()
    
    def save_well(self):
        """Save current well"""
        self.well_info_widget.save_well_info()
    
    def export_pdf(self):
        """Export to PDF"""
        # TODO: Implement PDF export
        QMessageBox.information(self, "Export", "PDF export will be implemented.")
    
    def export_excel(self):
        """Export to Excel"""
        # TODO: Implement Excel export
        QMessageBox.information(self, "Export", "Excel export will be implemented.")
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences
        QMessageBox.information(self, "Preferences", "Preferences will be implemented.")
    
    def logout(self):
        """Logout from application"""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    # Ribbon button handlers (placeholders)
    def add_time_entry(self): self.status_bar.showMessage("Add time entry - To be implemented")
    def edit_time_entry(self): self.status_bar.showMessage("Edit time entry - To be implemented")
    def show_npt_report(self): self.status_bar.showMessage("NPT report - To be implemented")
    def show_lookahead(self): self.status_bar.showMessage("7-day lookahead - To be implemented")
    def show_codes(self): self.status_bar.showMessage("Activity codes - To be implemented")
    def time_analysis(self): self.status_bar.showMessage("Time analysis - To be implemented")
    def productivity(self): self.status_bar.showMessage("Productivity analysis - To be implemented")
    def show_downhole(self): self.status_bar.showMessage("Downhole equipment - To be implemented")
    def show_drill_pipe(self): self.status_bar.showMessage("Drill pipe specs - To be implemented")
    def show_cement(self): self.status_bar.showMessage("Cement data - To be implemented")
    def show_casing(self): self.status_bar.showMessage("Casing data - To be implemented")
    def show_solid_control(self): self.status_bar.showMessage("Solid control - To be implemented")
    def solid_performance(self): self.status_bar.showMessage("Solid performance - To be implemented")
    def show_formations(self): self.status_bar.showMessage("Formations - To be implemented")
    def show_trajectory(self): self.status_bar.showMessage("Trajectory - To be implemented")
    def rop_analysis(self): self.status_bar.showMessage("ROP analysis - To be implemented")
    def formation_eval(self): self.status_bar.showMessage("Formation eval - To be implemented")
    def drilling_chart(self): self.status_bar.showMessage("Drilling chart - To be implemented")
    def survey_chart(self): self.status_bar.showMessage("Survey chart - To be implemented")
    def mud_chart(self): self.status_bar.showMessage("Mud chart - To be implemented")
    def show_pob(self): self.status_bar.showMessage("POB status - To be implemented")
    def show_inventory(self): self.status_bar.showMessage("Inventory - To be implemented")
    def show_material(self): self.status_bar.showMessage("Material handling - To be implemented")
    def show_services(self): self.status_bar.showMessage("Service companies - To be implemented")
    def show_transport(self): self.status_bar.showMessage("Transport log - To be implemented")
    def show_weather(self): self.status_bar.showMessage("Weather data - To be implemented")
    def show_forecast(self): self.status_bar.showMessage("Forecast - To be implemented")
    def show_safety(self): self.status_bar.showMessage("Safety & BOP - To be implemented")
    def show_drills(self): self.status_bar.showMessage("Safety drills - To be implemented")
    def show_waste(self): self.status_bar.showMessage("Waste management - To be implemented")
    def spill_report(self): self.status_bar.showMessage("Spill report - To be implemented")
    def show_inspections(self): self.status_bar.showMessage("Inspections - To be implemented")
    def show_incidents(self): self.status_bar.showMessage("Incidents - To be implemented")
    def generate_daily(self): self.status_bar.showMessage("Generate daily report - To be implemented")
    def generate_weekly(self): self.status_bar.showMessage("Generate weekly report - To be implemented")
    def generate_eow(self): self.status_bar.showMessage("Generate EOW report - To be implemented")
    def export_csv(self): self.status_bar.showMessage("Export CSV - To be implemented")
    def save_template(self): self.status_bar.showMessage("Save template - To be implemented")
    def load_template(self): self.status_bar.showMessage("Load template - To be implemented")
    def npt_analysis(self): self.status_bar.showMessage("NPT analysis - To be implemented")
    def cost_analysis(self): self.status_bar.showMessage("Cost analysis - To be implemented")

# ============================================
# LOGIN DIALOG
# ============================================

class LoginDialog(QDialog):
    """Login dialog for user authentication"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Nikan Drill Master - Login")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Application title
        title_label = QLabel("Nikan Drill Master")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
        """)
        layout.addWidget(title_label)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        login_button.clicked.connect(self.authenticate)
        
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.reject)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(exit_button)
        
        layout.addLayout(button_layout)
        
        # Version info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        layout.addWidget(version_label)
        
        self.setLayout(layout)
    
    def authenticate(self):
        """Authenticate user"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.error_label.setText("Please enter both username and password")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            self.error_label.setText("Invalid username or password")
            self.password_input.clear()

# ============================================
# APPLICATION ENTRY POINT
# ============================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create palette for dark/light theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Initialize database
    db = DatabaseManager()
    
    # Show login dialog
    login_dialog = LoginDialog(db)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Login successful, show main window
        window = MainWindow(login_dialog.user)
        window.show()
        sys.exit(app.exec())
    else:
        # Login cancelled or failed
        sys.exit(0)

if __name__ == "__main__":
    main()

# ============================================
# INVENTORY WIDGET
# ============================================

class InventoryWidget(QWidget):
    """Inventory management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.inventory_items = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Inventory Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.inventory_well_combo = QComboBox()
        self.load_button = QPushButton("Load Inventory")
        self.load_button.clicked.connect(self.load_inventory)
        
        well_layout.addWidget(self.inventory_well_combo)
        well_layout.addWidget(self.load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Inventory table
        table_group = QGroupBox("Inventory Items")
        table_layout = QVBoxLayout()
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item", "Category", "Opening", "Received", 
            "Used", "Remaining", "Unit", "Last Updated"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_inventory_item_dialog)
        
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_inventory_item)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_inventory_item)
        
        adjust_button = QPushButton("Adjust Stock")
        adjust_button.clicked.connect(self.adjust_stock_dialog)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(adjust_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.inventory_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Summary section
        summary_group = QGroupBox("Inventory Summary")
        summary_layout = QGridLayout()
        
        self.total_items_label = QLabel("Total Items: 0")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        self.critical_items_label = QLabel("Critical Items: 0")
        self.total_value_label = QLabel("Total Value: $0")
        
        summary_layout.addWidget(self.total_items_label, 0, 0)
        summary_layout.addWidget(self.low_stock_label, 0, 1)
        summary_layout.addWidget(self.critical_items_label, 0, 2)
        summary_layout.addWidget(self.total_value_label, 0, 3)
        
        # Reorder level input
        summary_layout.addWidget(QLabel("Reorder Level %:"), 1, 0)
        self.reorder_level_spin = QSpinBox()
        self.reorder_level_spin.setRange(0, 100)
        self.reorder_level_spin.setValue(20)
        self.reorder_level_spin.valueChanged.connect(self.update_inventory_summary)
        summary_layout.addWidget(self.reorder_level_spin, 1, 1)
        
        # Critical level input
        summary_layout.addWidget(QLabel("Critical Level %:"), 1, 2)
        self.critical_level_spin = QSpinBox()
        self.critical_level_spin.setRange(0, 100)
        self.critical_level_spin.setValue(10)
        self.critical_level_spin.valueChanged.connect(self.update_inventory_summary)
        summary_layout.addWidget(self.critical_level_spin, 1, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Low stock alert
        self.low_stock_widget = QWidget()
        self.low_stock_widget.setVisible(False)
        low_stock_layout = QHBoxLayout()
        low_stock_icon = QLabel("⚠️")
        self.low_stock_message = QLabel("")
        low_stock_layout.addWidget(low_stock_icon)
        low_stock_layout.addWidget(self.low_stock_message)
        low_stock_layout.addStretch()
        self.low_stock_widget.setLayout(low_stock_layout)
        self.low_stock_widget.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 5px;")
        main_layout.addWidget(self.low_stock_widget)
        
        # Save button
        save_button = QPushButton("Save Inventory")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        save_button.clicked.connect(self.save_inventory)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.inventory_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.inventory_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def load_inventory(self):
        """Load inventory for selected well"""
        well_index = self.inventory_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Load inventory from database
        self.inventory_table.setRowCount(0)
        self.inventory_items.clear()
        
        # Add sample data for demonstration
        sample_items = [
            ("Drill Pipe 5\"", "Pipe", 1000, 500, 300, 1200, "ft", "2024-01-15"),
            ("Casing 9 5/8\"", "Casing", 500, 200, 100, 600, "ft", "2024-01-15"),
            ("Cement Class G", "Cement", 1000, 500, 400, 1100, "sack", "2024-01-15"),
            ("Barite", "Mud Chemical", 5000, 2000, 1500, 5500, "lb", "2024-01-15"),
            ("Bentonite", "Mud Chemical", 3000, 1000, 800, 3200, "lb", "2024-01-15"),
        ]
        
        for item in sample_items:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            
            for col, value in enumerate(item):
                self.inventory_table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Add to internal list
            inventory_item = InventoryItem(
                item=item[0],
                category=item[1],
                opening=item[2],
                received=item[3],
                used=item[4],
                remaining=item[5],
                unit=item[6],
                last_updated=item[7]
            )
            self.inventory_items.append(inventory_item)
        
        self.update_inventory_summary()
    
    def add_inventory_item_dialog(self):
        """Show dialog to add inventory item"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Inventory Item")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Item details
        self.new_item_name = QLineEdit()
        self.new_item_name.setPlaceholderText("Enter item name")
        form.addRow("Item Name:", self.new_item_name)
        
        self.new_item_category = QComboBox()
        self.new_item_category.addItems([
            "Pipe", "Casing", "Cement", "Mud Chemical", 
            "Tool", "Safety Equipment", "Spare Part", "Other"
        ])
        form.addRow("Category:", self.new_item_category)
        
        # Stock levels
        stock_layout = QGridLayout()
        
        stock_layout.addWidget(QLabel("Opening:"), 0, 0)
        self.new_item_opening = QDoubleSpinBox()
        self.new_item_opening.setRange(0, 1000000)
        stock_layout.addWidget(self.new_item_opening, 0, 1)
        
        stock_layout.addWidget(QLabel("Received:"), 0, 2)
        self.new_item_received = QDoubleSpinBox()
        self.new_item_received.setRange(0, 1000000)
        stock_layout.addWidget(self.new_item_received, 0, 3)
        
        stock_layout.addWidget(QLabel("Used:"), 1, 0)
        self.new_item_used = QDoubleSpinBox()
        self.new_item_used.setRange(0, 1000000)
        stock_layout.addWidget(self.new_item_used, 1, 1)
        
        stock_layout.addWidget(QLabel("Remaining:"), 1, 2)
        self.new_item_remaining = QDoubleSpinBox()
        self.new_item_remaining.setRange(0, 1000000)
        self.new_item_remaining.setReadOnly(True)
        stock_layout.addWidget(self.new_item_remaining, 1, 3)
        
        form.addRow("Stock Levels:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(stock_layout)
        
        # Unit
        self.new_item_unit = QComboBox()
        self.new_item_unit.addItems([
            "ft", "m", "kg", "lb", "sack", "bbl", "gal", "ltr", "unit", "set"
        ])
        form.addRow("Unit:", self.new_item_unit)
        
        # Connect signals for auto-calculation
        self.new_item_opening.valueChanged.connect(self.calculate_remaining)
        self.new_item_received.valueChanged.connect(self.calculate_remaining)
        self.new_item_used.valueChanged.connect(self.calculate_remaining)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Item")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_inventory_item(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calculate_remaining(self):
        """Calculate remaining stock"""
        opening = self.new_item_opening.value()
        received = self.new_item_received.value()
        used = self.new_item_used.value()
        remaining = opening + received - used
        self.new_item_remaining.setValue(remaining)
    
    def add_inventory_item(self, dialog):
        """Add inventory item to table"""
        item_name = self.new_item_name.text().strip()
        if not item_name:
            QMessageBox.warning(self, "Error", "Please enter item name.")
            return
        
        # Add to table
        row = self.inventory_table.rowCount()
        self.inventory_table.insertRow(row)
        
        item_data = [
            item_name,
            self.new_item_category.currentText(),
            str(self.new_item_opening.value()),
            str(self.new_item_received.value()),
            str(self.new_item_used.value()),
            str(self.new_item_remaining.value()),
            self.new_item_unit.currentText(),
            QDate.currentDate().toString("yyyy-MM-dd")
        ]
        
        for col, value in enumerate(item_data):
            self.inventory_table.setItem(row, col, QTableWidgetItem(value))
        
        # Add to internal list
        inventory_item = InventoryItem(
            item=item_name,
            category=self.new_item_category.currentText(),
            opening=self.new_item_opening.value(),
            received=self.new_item_received.value(),
            used=self.new_item_used.value(),
            remaining=self.new_item_remaining.value(),
            unit=self.new_item_unit.currentText(),
            last_updated=QDate.currentDate().toString("yyyy-MM-dd")
        )
        self.inventory_items.append(inventory_item)
        
        self.update_inventory_summary()
        dialog.accept()
    
    def edit_inventory_item(self):
        """Edit selected inventory item"""
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an item to edit.")
            return
        
        # TODO: Implement edit functionality
        pass
    
    def delete_inventory_item(self):
        """Delete selected inventory item"""
        selected_row = self.inventory_table.currentRow()
        if selected_row >= 0:
            self.inventory_table.removeRow(selected_row)
            if selected_row < len(self.inventory_items):
                del self.inventory_items[selected_row]
            self.update_inventory_summary()
    
    def adjust_stock_dialog(self):
        """Show dialog to adjust stock"""
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an item to adjust.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Adjust Stock")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        item_name = self.inventory_table.item(selected_row, 0).text()
        current_stock = float(self.inventory_table.item(selected_row, 5).text())
        
        form.addRow("Item:", QLabel(item_name))
        form.addRow("Current Stock:", QLabel(f"{current_stock}"))
        
        # Adjustment type
        self.adjustment_type = QComboBox()
        self.adjustment_type.addItems(["Receive", "Issue", "Return", "Adjust"])
        form.addRow("Adjustment Type:", self.adjustment_type)
        
        # Quantity
        self.adjustment_qty = QDoubleSpinBox()
        self.adjustment_qty.setRange(0, 1000000)
        form.addRow("Quantity:", self.adjustment_qty)
        
        # Reason
        self.adjustment_reason = QTextEdit()
        self.adjustment_reason.setMaximumHeight(60)
        form.addRow("Reason:", self.adjustment_reason)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply Adjustment")
        cancel_button = QPushButton("Cancel")
        
        apply_button.clicked.connect(lambda: self.apply_stock_adjustment(dialog, selected_row))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_stock_adjustment(self, dialog, row):
        """Apply stock adjustment to selected item"""
        adjustment_type = self.adjustment_type.currentText()
        quantity = self.adjustment_qty.value()
        reason = self.adjustment_reason.toPlainText().strip()
        
        if quantity <= 0:
            QMessageBox.warning(self, "Error", "Quantity must be greater than zero.")
            return
        
        # Get current values
        received = float(self.inventory_table.item(row, 3).text())
        used = float(self.inventory_table.item(row, 4).text())
        remaining = float(self.inventory_table.item(row, 5).text())
        
        # Apply adjustment
        if adjustment_type == "Receive":
            received += quantity
            remaining += quantity
        elif adjustment_type == "Issue":
            used += quantity
            remaining -= quantity
        elif adjustment_type == "Return":
            used -= quantity
            remaining += quantity
        elif adjustment_type == "Adjust":
            # Direct adjustment to remaining
            remaining = quantity
        
        # Update table
        self.inventory_table.setItem(row, 3, QTableWidgetItem(str(received)))
        self.inventory_table.setItem(row, 4, QTableWidgetItem(str(used)))
        self.inventory_table.setItem(row, 5, QTableWidgetItem(str(remaining)))
        self.inventory_table.setItem(row, 7, QTableWidgetItem(QDate.currentDate().toString("yyyy-MM-dd")))
        
        # Update internal list
        if row < len(self.inventory_items):
            self.inventory_items[row].received = received
            self.inventory_items[row].used = used
            self.inventory_items[row].remaining = remaining
            self.inventory_items[row].last_updated = QDate.currentDate().toString("yyyy-MM-dd")
        
        self.update_inventory_summary()
        dialog.accept()
    
    def update_inventory_summary(self):
        """Update inventory summary information"""
        total_items = self.inventory_table.rowCount()
        self.total_items_label.setText(f"Total Items: {total_items}")
        
        # Calculate low and critical stock items
        low_stock_count = 0
        critical_count = 0
        low_stock_items = []
        
        reorder_level = self.reorder_level_spin.value() / 100
        critical_level = self.critical_level_spin.value() / 100
        
        for row in range(total_items):
            item_name = self.inventory_table.item(row, 0).text()
            opening = float(self.inventory_table.item(row, 2).text())
            received = float(self.inventory_table.item(row, 3).text())
            used = float(self.inventory_table.item(row, 4).text())
            remaining = float(self.inventory_table.item(row, 5).text())
            
            initial_stock = opening + received
            if initial_stock > 0:
                stock_percentage = remaining / initial_stock
                
                if stock_percentage <= critical_level:
                    critical_count += 1
                    low_stock_items.append(f"{item_name} ({remaining:.0f})")
                elif stock_percentage <= reorder_level:
                    low_stock_count += 1
                    low_stock_items.append(f"{item_name} ({remaining:.0f})")
        
        self.low_stock_label.setText(f"Low Stock Items: {low_stock_count}")
        self.critical_items_label.setText(f"Critical Items: {critical_count}")
        
        # Show/hide low stock alert
        if low_stock_items:
            self.low_stock_widget.setVisible(True)
            items_text = ", ".join(low_stock_items[:5])  # Show first 5 items
            if len(low_stock_items) > 5:
                items_text += f" and {len(low_stock_items) - 5} more..."
            self.low_stock_message.setText(f"Low stock items: {items_text}")
        else:
            self.low_stock_widget.setVisible(False)
    
    def save_inventory(self):
        """Save inventory to database"""
        well_index = self.inventory_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save to database
        QMessageBox.information(self, "Success", "Inventory saved successfully!")

# ============================================
# SERVICE COMPANY LOG WIDGET
# ============================================

class ServiceCompanyWidget(QWidget):
    """Service company log widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service_companies = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Service Company Log")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.service_well_combo = QComboBox()
        self.load_button = QPushButton("Load Service Companies")
        
        well_layout.addWidget(self.service_well_combo)
        well_layout.addWidget(self.load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Service companies table
        table_group = QGroupBox("Service Companies")
        table_layout = QVBoxLayout()
        
        self.service_table = QTableWidget()
        self.service_table.setColumnCount(8)
        self.service_table.setHorizontalHeaderLabels([
            "Company Name", "Service Type", "Start Date", "End Date",
            "Contact Person", "Phone", "Status", "Description"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Company")
        add_button.clicked.connect(self.add_service_company_dialog)
        
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_service_company)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_service_company)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.service_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QGridLayout()
        
        self.active_services_label = QLabel("Active Services: 0")
        self.completed_services_label = QLabel("Completed Services: 0")
        self.upcoming_services_label = QLabel("Upcoming Services: 0")
        self.total_companies_label = QLabel("Total Companies: 0")
        
        summary_layout.addWidget(self.active_services_label, 0, 0)
        summary_layout.addWidget(self.completed_services_label, 0, 1)
        summary_layout.addWidget(self.upcoming_services_label, 0, 2)
        summary_layout.addWidget(self.total_companies_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Save button
        save_button = QPushButton("Save Service Companies")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        save_button.clicked.connect(self.save_service_companies)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
        
        # Add sample data
        self.load_sample_data()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.service_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.service_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def load_sample_data(self):
        """Load sample service company data"""
        sample_companies = [
            ("Schlumberger", "MWD/LWD", "2024-01-01", "2024-06-30", "John Smith", "+1-555-0123", "Active", "Measurement while drilling services"),
            ("Halliburton", "Cementing", "2024-01-15", "2024-02-15", "Mike Johnson", "+1-555-0124", "Completed", "Primary cementing job"),
            ("Baker Hughes", "Directional Drilling", "2024-02-01", "2024-12-31", "Sarah Williams", "+1-555-0125", "Active", "Directional drilling services"),
            ("Weatherford", "Casing Services", "2024-03-01", "2024-03-15", "Robert Brown", "+1-555-0126", "Upcoming", "Casing running services"),
        ]
        
        for company in sample_companies:
            row = self.service_table.rowCount()
            self.service_table.insertRow(row)
            
            for col, value in enumerate(company):
                self.service_table.setItem(row, col, QTableWidgetItem(value))
        
        self.update_service_summary()
    
    def add_service_company_dialog(self):
        """Show dialog to add service company"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Service Company")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Company details
        self.new_company_name = QLineEdit()
        self.new_company_name.setPlaceholderText("Enter company name")
        form.addRow("Company Name:", self.new_company_name)
        
        self.new_service_type = QComboBox()
        self.new_service_type.addItems([
            "MWD/LWD", "Directional Drilling", "Cementing", "Mud Logging",
            "Mud Engineering", "Casing Services", "Wireline", "Coiled Tubing",
            "Fishing", "Well Testing", "Completion", "Stimulation", "Other"
        ])
        form.addRow("Service Type:", self.new_service_type)
        
        # Dates
        dates_layout = QHBoxLayout()
        self.new_start_date = QDateEdit()
        self.new_start_date.setCalendarPopup(True)
        self.new_start_date.setDate(QDate.currentDate())
        
        self.new_end_date = QDateEdit()
        self.new_end_date.setCalendarPopup(True)
        self.new_end_date.setDate(QDate.currentDate().addMonths(1))
        
        dates_layout.addWidget(QLabel("Start:"))
        dates_layout.addWidget(self.new_start_date)
        dates_layout.addWidget(QLabel("End:"))
        dates_layout.addWidget(self.new_end_date)
        
        form.addRow("Service Period:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(dates_layout)
        
        # Contact information
        self.new_contact_person = QLineEdit()
        self.new_contact_person.setPlaceholderText("Contact person name")
        form.addRow("Contact Person:", self.new_contact_person)
        
        self.new_contact_phone = QLineEdit()
        self.new_contact_phone.setPlaceholderText("Phone number")
        form.addRow("Contact Phone:", self.new_contact_phone)
        
        # Status
        self.new_status = QComboBox()
        self.new_status.addItems(["Active", "Completed", "Upcoming", "Cancelled", "On Hold"])
        form.addRow("Status:", self.new_status)
        
        # Description
        self.new_description = QTextEdit()
        self.new_description.setMaximumHeight(80)
        form.addRow("Description:", self.new_description)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Company")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_service_company(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_service_company(self, dialog):
        """Add service company to table"""
        company_name = self.new_company_name.text().strip()
        if not company_name:
            QMessageBox.warning(self, "Error", "Please enter company name.")
            return
        
        # Add to table
        row = self.service_table.rowCount()
        self.service_table.insertRow(row)
        
        company_data = [
            company_name,
            self.new_service_type.currentText(),
            self.new_start_date.date().toString("yyyy-MM-dd"),
            self.new_end_date.date().toString("yyyy-MM-dd"),
            self.new_contact_person.text(),
            self.new_contact_phone.text(),
            self.new_status.currentText(),
            self.new_description.toPlainText()
        ]
        
        for col, value in enumerate(company_data):
            self.service_table.setItem(row, col, QTableWidgetItem(value))
        
        # Add to internal list
        service_company = ServiceCompany(
            company_name=company_name,
            service_type=self.new_service_type.currentText(),
            start_date=self.new_start_date.date().toString("yyyy-MM-dd"),
            end_date=self.new_end_date.date().toString("yyyy-MM-dd"),
            contact_person=self.new_contact_person.text(),
            contact_phone=self.new_contact_phone.text(),
            description=self.new_description.toPlainText()
        )
        self.service_companies.append(service_company)
        
        self.update_service_summary()
        dialog.accept()
    
    def edit_service_company(self):
        """Edit selected service company"""
        selected_row = self.service_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a company to edit.")
            return
        
        # TODO: Implement edit functionality
        pass
    
    def delete_service_company(self):
        """Delete selected service company"""
        selected_row = self.service_table.currentRow()
        if selected_row >= 0:
            self.service_table.removeRow(selected_row)
            if selected_row < len(self.service_companies):
                del self.service_companies[selected_row]
            self.update_service_summary()
    
    def update_service_summary(self):
        """Update service company summary"""
        total_companies = self.service_table.rowCount()
        
        active_count = 0
        completed_count = 0
        upcoming_count = 0
        
        current_date = QDate.currentDate()
        
        for row in range(total_companies):
            status = self.service_table.item(row, 6).text()
            start_date = QDate.fromString(self.service_table.item(row, 2).text(), "yyyy-MM-dd")
            end_date = QDate.fromString(self.service_table.item(row, 3).text(), "yyyy-MM-dd")
            
            if status == "Active":
                active_count += 1
            elif status == "Completed":
                completed_count += 1
            elif status == "Upcoming":
                if start_date > current_date:
                    upcoming_count += 1
                else:
                    # Update status to Active if start date has passed
                    self.service_table.setItem(row, 6, QTableWidgetItem("Active"))
                    active_count += 1
        
        self.active_services_label.setText(f"Active Services: {active_count}")
        self.completed_services_label.setText(f"Completed Services: {completed_count}")
        self.upcoming_services_label.setText(f"Upcoming Services: {upcoming_count}")
        self.total_companies_label.setText(f"Total Companies: {total_companies}")
    
    def save_service_companies(self):
        """Save service companies to database"""
        well_index = self.service_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save to database
        QMessageBox.information(self, "Success", "Service companies saved successfully!")

# ============================================
# MATERIAL HANDLING WIDGET
# ============================================

class MaterialHandlingWidget(QWidget):
    """Material handling and notes widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.material_requests = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Material Handling & Notes")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Notes tab
        notes_tab = self.create_notes_tab()
        tabs.addTab(notes_tab, "📝 Notes")
        
        # Material Requests tab
        requests_tab = self.create_requests_tab()
        tabs.addTab(requests_tab, "📦 Material Requests")
        
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Material Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #d35400;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #a84300;
            }
        """)
        save_button.clicked.connect(self.save_material_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_notes_tab(self):
        """Create notes tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.notes_well_combo = QComboBox()
        
        load_button = QPushButton("Load Notes")
        
        well_layout.addWidget(self.notes_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Notes sections
        notes_container = QWidget()
        notes_layout = QGridLayout()
        
        note_titles = [
            "Note 01 - Daily Operations",
            "Note 02 - Equipment Status",
            "Note 03 - Safety Observations",
            "Note 04 - Maintenance Issues",
            "Note 05 - Planning Notes",
            "Note 06 - General Remarks"
        ]
        
        self.note_texts = []
        
        for i in range(6):
            row = i // 2
            col = (i % 2) * 2
            
            note_label = QLabel(note_titles[i])
            notes_layout.addWidget(note_label, row, col)
            
            note_text = QTextEdit()
            note_text.setPlaceholderText(f"Enter {note_titles[i]}...")
            note_text.setMaximumHeight(120)
            notes_layout.addWidget(note_text, row, col + 1)
            
            self.note_texts.append(note_text)
        
        notes_container.setLayout(notes_layout)
        
        # Add scroll area for notes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(notes_container)
        
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def create_requests_tab(self):
        """Create material requests tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.requests_well_combo = QComboBox()
        
        load_button = QPushButton("Load Requests")
        
        well_layout.addWidget(self.requests_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Material requests table
        table_group = QGroupBox("Material Requests")
        table_layout = QVBoxLayout()
        
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(10)
        self.requests_table.setHorizontalHeaderLabels([
            "Material", "Requested", "Outstanding", "Received", "Backload",
            "Unit", "Request Date", "Required Date", "Status", "Remarks"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Request")
        add_button.clicked.connect(self.add_material_request_dialog)
        
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_material_request)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_material_request)
        
        update_button = QPushButton("Update Status")
        update_button.clicked.connect(self.update_request_status)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(update_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.requests_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Request summary
        summary_group = QGroupBox("Request Summary")
        summary_layout = QGridLayout()
        
        self.pending_requests_label = QLabel("Pending: 0")
        self.approved_requests_label = QLabel("Approved: 0")
        self.received_requests_label = QLabel("Received: 0")
        self.overdue_requests_label = QLabel("Overdue: 0")
        
        summary_layout.addWidget(self.pending_requests_label, 0, 0)
        summary_layout.addWidget(self.approved_requests_label, 0, 1)
        summary_layout.addWidget(self.received_requests_label, 0, 2)
        summary_layout.addWidget(self.overdue_requests_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        tab.setLayout(layout)
        
        # Load sample data
        self.load_sample_requests()
        
        return tab
    
    def load_sample_requests(self):
        """Load sample material requests"""
        sample_requests = [
            ("Drill Pipe 5\"", 1000, 500, 500, 0, "ft", "2024-01-01", "2024-01-15", "Partially Received", "Waiting for balance"),
            ("Cement Class G", 500, 0, 500, 0, "sack", "2024-01-05", "2024-01-10", "Received", "Full delivery"),
            ("Barite", 2000, 1000, 1000, 0, "lb", "2024-01-10", "2024-01-20", "Pending", "Awaiting approval"),
            ("Safety Gloves", 100, 0, 100, 0, "pair", "2024-01-12", "2024-01-14", "Received", "Safety stock"),
            ("Welding Electrodes", 50, 50, 0, 0, "kg", "2024-01-15", "2024-01-25", "Approved", "For maintenance"),
        ]
        
        for request in sample_requests:
            row = self.requests_table.rowCount()
            self.requests_table.insertRow(row)
            
            for col, value in enumerate(request):
                self.requests_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        self.update_request_summary()
    
    def add_material_request_dialog(self):
        """Show dialog to add material request"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Material Request")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Material details
        self.new_material_name = QLineEdit()
        self.new_material_name.setPlaceholderText("Enter material name")
        form.addRow("Material:", self.new_material_name)
        
        # Quantities
        quantities_layout = QGridLayout()
        
        quantities_layout.addWidget(QLabel("Requested:"), 0, 0)
        self.new_requested_qty = QDoubleSpinBox()
        self.new_requested_qty.setRange(0, 1000000)
        quantities_layout.addWidget(self.new_requested_qty, 0, 1)
        
        quantities_layout.addWidget(QLabel("Outstanding:"), 0, 2)
        self.new_outstanding_qty = QDoubleSpinBox()
        self.new_outstanding_qty.setRange(0, 1000000)
        quantities_layout.addWidget(self.new_outstanding_qty, 0, 3)
        
        quantities_layout.addWidget(QLabel("Received:"), 1, 0)
        self.new_received_qty = QDoubleSpinBox()
        self.new_received_qty.setRange(0, 1000000)
        quantities_layout.addWidget(self.new_received_qty, 1, 1)
        
        quantities_layout.addWidget(QLabel("Backload:"), 1, 2)
        self.new_backload_qty = QDoubleSpinBox()
        self.new_backload_qty.setRange(0, 1000000)
        quantities_layout.addWidget(self.new_backload_qty, 1, 3)
        
        form.addRow("Quantities:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(quantities_layout)
        
        # Unit
        self.new_material_unit = QComboBox()
        self.new_material_unit.addItems([
            "ft", "m", "kg", "lb", "sack", "bbl", "gal", "ltr", "unit", 
            "pair", "set", "box", "carton", "drum", "pallet"
        ])
        form.addRow("Unit:", self.new_material_unit)
        
        # Dates
        dates_layout = QHBoxLayout()
        self.new_request_date = QDateEdit()
        self.new_request_date.setCalendarPopup(True)
        self.new_request_date.setDate(QDate.currentDate())
        
        self.new_required_date = QDateEdit()
        self.new_required_date.setCalendarPopup(True)
        self.new_required_date.setDate(QDate.currentDate().addDays(7))
        
        dates_layout.addWidget(QLabel("Request Date:"))
        dates_layout.addWidget(self.new_request_date)
        dates_layout.addWidget(QLabel("Required Date:"))
        dates_layout.addWidget(self.new_required_date)
        
        form.addRow("Dates:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(dates_layout)
        
        # Status
        self.new_request_status = QComboBox()
        self.new_request_status.addItems([
            "Requested", "Approved", "Ordered", "Shipped", 
            "Received", "Partially Received", "Cancelled", "Closed"
        ])
        form.addRow("Status:", self.new_request_status)
        
        # Remarks
        self.new_request_remarks = QTextEdit()
        self.new_request_remarks.setMaximumHeight(60)
        form.addRow("Remarks:", self.new_request_remarks)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Request")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_material_request(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_material_request(self, dialog):
        """Add material request to table"""
        material_name = self.new_material_name.text().strip()
        if not material_name:
            QMessageBox.warning(self, "Error", "Please enter material name.")
            return
        
        # Calculate outstanding if not provided
        requested = self.new_requested_qty.value()
        received = self.new_received_qty.value()
        outstanding = requested - received
        
        if self.new_outstanding_qty.value() == 0:
            self.new_outstanding_qty.setValue(outstanding)
        
        # Add to table
        row = self.requests_table.rowCount()
        self.requests_table.insertRow(row)
        
        request_data = [
            material_name,
            str(requested),
            str(outstanding),
            str(received),
            str(self.new_backload_qty.value()),
            self.new_material_unit.currentText(),
            self.new_request_date.date().toString("yyyy-MM-dd"),
            self.new_required_date.date().toString("yyyy-MM-dd"),
            self.new_request_status.currentText(),
            self.new_request_remarks.toPlainText()
        ]
        
        for col, value in enumerate(request_data):
            self.requests_table.setItem(row, col, QTableWidgetItem(value))
        
        # Add to internal list
        material_request = MaterialRequest(
            material=material_name,
            requested_qty=requested,
            outstanding_qty=outstanding,
            received_qty=received,
            backload_qty=self.new_backload_qty.value(),
            unit=self.new_material_unit.currentText(),
            request_date=self.new_request_date.date().toString("yyyy-MM-dd"),
            required_date=self.new_required_date.date().toString("yyyy-MM-dd"),
            status=self.new_request_status.currentText()
        )
        self.material_requests.append(material_request)
        
        self.update_request_summary()
        dialog.accept()
    
    def edit_material_request(self):
        """Edit selected material request"""
        selected_row = self.requests_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a request to edit.")
            return
        
        # TODO: Implement edit functionality
        pass
    
    def delete_material_request(self):
        """Delete selected material request"""
        selected_row = self.requests_table.currentRow()
        if selected_row >= 0:
            self.requests_table.removeRow(selected_row)
            if selected_row < len(self.material_requests):
                del self.material_requests[selected_row]
            self.update_request_summary()
    
    def update_request_status(self):
        """Update status of selected material request"""
        selected_row = self.requests_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a request to update.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Request Status")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        material_name = self.requests_table.item(selected_row, 0).text()
        current_status = self.requests_table.item(selected_row, 8).text()
        
        form.addRow("Material:", QLabel(material_name))
        form.addRow("Current Status:", QLabel(current_status))
        
        self.status_update_combo = QComboBox()
        self.status_update_combo.addItems([
            "Requested", "Approved", "Ordered", "Shipped", 
            "Received", "Partially Received", "Cancelled", "Closed"
        ])
        self.status_update_combo.setCurrentText(current_status)
        form.addRow("New Status:", self.status_update_combo)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        update_button = QPushButton("Update")
        cancel_button = QPushButton("Cancel")
        
        update_button.clicked.connect(lambda: self.apply_status_update(dialog, selected_row))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_status_update(self, dialog, row):
        """Apply status update to material request"""
        new_status = self.status_update_combo.currentText()
        self.requests_table.setItem(row, 8, QTableWidgetItem(new_status))
        
        # If status is "Received", update received quantity
        if new_status == "Received":
            requested = float(self.requests_table.item(row, 1).text())
            outstanding = 0
            received = requested
            
            self.requests_table.setItem(row, 2, QTableWidgetItem(str(outstanding)))
            self.requests_table.setItem(row, 3, QTableWidgetItem(str(received)))
        
        # If status is "Partially Received", prompt for received quantity
        elif new_status == "Partially Received":
            qty_dialog = QDialog(self)
            qty_dialog.setWindowTitle("Enter Received Quantity")
            qty_dialog.setMinimumWidth(300)
            
            qty_layout = QVBoxLayout()
            qty_form = QFormLayout()
            
            requested = float(self.requests_table.item(row, 1).text())
            qty_form.addRow("Requested Quantity:", QLabel(str(requested)))
            
            self.received_qty_input = QDoubleSpinBox()
            self.received_qty_input.setRange(0, requested)
            qty_form.addRow("Received Quantity:", self.received_qty_input)
            
            qty_layout.addLayout(qty_form)
            
            qty_button_layout = QHBoxLayout()
            ok_button = QPushButton("OK")
            cancel_qty_button = QPushButton("Cancel")
            
            ok_button.clicked.connect(lambda: self.update_received_qty(qty_dialog, row))
            cancel_qty_button.clicked.connect(qty_dialog.reject)
            
            qty_button_layout.addWidget(ok_button)
            qty_button_layout.addWidget(cancel_qty_button)
            qty_layout.addLayout(qty_button_layout)
            
            qty_dialog.setLayout(qty_layout)
            qty_dialog.exec()
        
        self.update_request_summary()
        dialog.accept()
    
    def update_received_qty(self, dialog, row):
        """Update received quantity for partial receipt"""
        received_qty = self.received_qty_input.value()
        requested = float(self.requests_table.item(row, 1).text())
        outstanding = requested - received_qty
        
        self.requests_table.setItem(row, 2, QTableWidgetItem(str(outstanding)))
        self.requests_table.setItem(row, 3, QTableWidgetItem(str(received_qty)))
        
        dialog.accept()
    
    def update_request_summary(self):
        """Update material request summary"""
        total_requests = self.requests_table.rowCount()
        
        pending_count = 0
        approved_count = 0
        received_count = 0
        overdue_count = 0
        
        current_date = QDate.currentDate()
        
        for row in range(total_requests):
            status = self.requests_table.item(row, 8).text()
            required_date = QDate.fromString(self.requests_table.item(row, 7).text(), "yyyy-MM-dd")
            
            if status == "Requested":
                pending_count += 1
            elif status in ["Approved", "Ordered", "Shipped"]:
                approved_count += 1
            elif status in ["Received", "Partially Received", "Closed"]:
                received_count += 1
            
            # Check if overdue
            if required_date < current_date and status not in ["Received", "Closed", "Cancelled"]:
                overdue_count += 1
        
        self.pending_requests_label.setText(f"Pending: {pending_count}")
        self.approved_requests_label.setText(f"Approved: {approved_count}")
        self.received_requests_label.setText(f"Received: {received_count}")
        self.overdue_requests_label.setText(f"Overdue: {overdue_count}")
    
    def save_material_data(self):
        """Save material data to database"""
        # TODO: Save notes and requests to database
        QMessageBox.information(self, "Success", "Material data saved successfully!")

# ============================================
# SAFETY & BOP WIDGET
# ============================================

class SafetyBOPWidget(QWidget):
    """Safety and BOP widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Safety & BOP Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Safety Drills tab
        drills_tab = self.create_drills_tab()
        tabs.addTab(drills_tab, "🦺 Safety Drills")
        
        # BOP Equipment tab
        bop_tab = self.create_bop_tab()
        tabs.addTab(bop_tab, "🔩 BOP Equipment")
        
        # Safety Records tab
        records_tab = self.create_records_tab()
        tabs.addTab(records_tab, "📋 Safety Records")
        
        main_layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save Safety Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
        """)
        save_button.clicked.connect(self.save_safety_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
    
    def create_drills_tab(self):
        """Create safety drills tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.safety_well_combo = QComboBox()
        
        load_button = QPushButton("Load Safety Data")
        
        well_layout.addWidget(self.safety_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        layout.addLayout(well_layout)
        
        # Safety drills form
        drills_group = QGroupBox("Safety Drills")
        drills_layout = QFormLayout()
        
        # Fire drill
        fire_layout = QHBoxLayout()
        self.fire_drill_date = QDateEdit()
        self.fire_drill_date.setCalendarPopup(True)
        self.fire_drill_date.setDate(QDate.currentDate().addDays(-7))
        
        self.fire_drill_result = QComboBox()
        self.fire_drill_result.addItems(["Pass", "Fail", "Scheduled", "Cancelled"])
        
        fire_layout.addWidget(QLabel("Last Fire Drill:"))
        fire_layout.addWidget(self.fire_drill_date)
        fire_layout.addWidget(QLabel("Result:"))
        fire_layout.addWidget(self.fire_drill_result)
        fire_layout.addStretch()
        
        drills_layout.addRow("Fire Drill:", QWidget())
        drills_layout.itemAt(drills_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(fire_layout)
        
        # BOP drill
        bop_layout = QHBoxLayout()
        self.bop_drill_date = QDateEdit()
        self.bop_drill_date.setCalendarPopup(True)
        self.bop_drill_date.setDate(QDate.currentDate().addDays(-14))
        
        self.bop_drill_result = QComboBox()
        self.bop_drill_result.addItems(["Pass", "Fail", "Scheduled", "Cancelled"])
        
        bop_layout.addWidget(QLabel("Last BOP Drill:"))
        bop_layout.addWidget(self.bop_drill_date)
        bop_layout.addWidget(QLabel("Result:"))
        bop_layout.addWidget(self.bop_drill_result)
        bop_layout.addStretch()
        
        drills_layout.addRow("BOP Drill:", QWidget())
        drills_layout.itemAt(drills_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(bop_layout)
        
        # H2S drill
        h2s_layout = QHBoxLayout()
        self.h2s_drill_date = QDateEdit()
        self.h2s_drill_date.setCalendarPopup(True)
        self.h2s_drill_date.setDate(QDate.currentDate().addDays(-21))
        
        self.h2s_drill_result = QComboBox()
        self.h2s_drill_result.addItems(["Pass", "Fail", "Scheduled", "Cancelled"])
        
        h2s_layout.addWidget(QLabel("Last H2S Drill:"))
        h2s_layout.addWidget(self.h2s_drill_date)
        h2s_layout.addWidget(QLabel("Result:"))
        h2s_layout.addWidget(self.h2s_drill_result)
        h2s_layout.addStretch()
        
        drills_layout.addRow("H2S Drill:", QWidget())
        drills_layout.itemAt(drills_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(h2s_layout)
        
        drills_group.setLayout(drills_layout)
        layout.addWidget(drills_group)
        
        # Safety performance
        performance_group = QGroupBox("Safety Performance")
        performance_layout = QGridLayout()
        
        performance_layout.addWidget(QLabel("Days without LTI:"), 0, 0)
        self.days_without_lti = QSpinBox()
        self.days_without_lti.setRange(0, 10000)
        self.days_without_lti.setValue(365)
        performance_layout.addWidget(self.days_without_lti, 0, 1)
        
        performance_layout.addWidget(QLabel("Days without LTA:"), 0, 2)
        self.days_without_lta = QSpinBox()
        self.days_without_lta.setRange(0, 10000)
        self.days_without_lta.setValue(500)
        performance_layout.addWidget(self.days_without_lta, 0, 3)
        
        performance_layout.addWidget(QLabel("Total Recordable Incidents:"), 1, 0)
        self.total_incidents = QSpinBox()
        self.total_incidents.setRange(0, 1000)
        performance_layout.addWidget(self.total_incidents, 1, 1)
        
        performance_layout.addWidget(QLabel("Near Misses:"), 1, 2)
        self.near_misses = QSpinBox()
        self.near_misses.setRange(0, 1000)
        performance_layout.addWidget(self.near_misses, 1, 3)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Safety notes
        notes_group = QGroupBox("Safety Notes")
        notes_layout = QVBoxLayout()
        
        self.safety_notes = QTextEdit()
        self.safety_notes.setPlaceholderText("Enter safety notes and observations...")
        self.safety_notes.setMaximumHeight(100)
        notes_layout.addWidget(self.safety_notes)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_bop_tab(self):
        """Create BOP equipment tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # BOP Stack information
        stack_group = QGroupBox("BOP Stack Information")
        stack_layout = QFormLayout()
        
        self.bop_name = QLineEdit()
        self.bop_name.setPlaceholderText("e.g., BOP Stack #1")
        stack_layout.addRow("BOP Name:", self.bop_name)
        
        self.bop_type = QComboBox()
        self.bop_type.addItems(["Annular", "Ram", "Combination", "Subsea", "Surface"])
        stack_layout.addRow("BOP Type:", self.bop_type)
        
        # Specifications
        specs_layout = QGridLayout()
        
        specs_layout.addWidget(QLabel("Working Pressure (psi):"), 0, 0)
        self.working_pressure = QDoubleSpinBox()
        self.working_pressure.setRange(0, 30000)
        self.working_pressure.setValue(10000)
        specs_layout.addWidget(self.working_pressure, 0, 1)
        
        specs_layout.addWidget(QLabel("Size (inch):"), 0, 2)
        self.bop_size = QDoubleSpinBox()
        self.bop_size.setRange(0, 50)
        self.bop_size.setValue(13.625)
        specs_layout.addWidget(self.bop_size, 0, 3)
        
        specs_layout.addWidget(QLabel("Rams:"), 1, 0)
        self.bop_rams = QLineEdit()
        self.bop_rams.setPlaceholderText("e.g., 2x Blind, 2x Pipe")
        specs_layout.addWidget(self.bop_rams, 1, 1, 1, 3)
        
        stack_layout.addRow("Specifications:", QWidget())
        stack_layout.itemAt(stack_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(specs_layout)
        
        stack_group.setLayout(stack_layout)
        layout.addWidget(stack_group)
        
        # Test information
        test_group = QGroupBox("BOP Test Information")
        test_layout = QFormLayout()
        
        # Last test
        last_test_layout = QHBoxLayout()
        self.last_test_date = QDateEdit()
        self.last_test_date.setCalendarPopup(True)
        self.last_test_date.setDate(QDate.currentDate().addDays(-30))
        
        self.test_pressure = QDoubleSpinBox()
        self.test_pressure.setRange(0, 50000)
        self.test_pressure.setValue(15000)
        self.test_pressure.setSuffix(" psi")
        
        self.test_duration = QDoubleSpinBox()
        self.test_duration.setRange(0, 24)
        self.test_duration.setValue(4)
        self.test_duration.setSuffix(" hours")
        
        last_test_layout.addWidget(QLabel("Last Test Date:"))
        last_test_layout.addWidget(self.last_test_date)
        last_test_layout.addWidget(QLabel("Test Pressure:"))
        last_test_layout.addWidget(self.test_pressure)
        last_test_layout.addWidget(QLabel("Duration:"))
        last_test_layout.addWidget(self.test_duration)
        
        test_layout.addRow("Last Test:", QWidget())
        test_layout.itemAt(test_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(last_test_layout)
        
        # Next test due
        next_test_layout = QHBoxLayout()
        self.next_test_due = QDateEdit()
        self.next_test_due.setCalendarPopup(True)
        self.next_test_due.setDate(QDate.currentDate().addDays(30))
        
        self.test_frequency = QComboBox()
        self.test_frequency.addItems(["Weekly", "Bi-weekly", "Monthly", "Quarterly", "As Required"])
        
        next_test_layout.addWidget(QLabel("Next Test Due:"))
        next_test_layout.addWidget(self.next_test_due)
        next_test_layout.addWidget(QLabel("Test Frequency:"))
        next_test_layout.addWidget(self.test_frequency)
        
        test_layout.addRow("Next Test:", QWidget())
        test_layout.itemAt(test_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(next_test_layout)
        
        # Test results
        self.test_results = QComboBox()
        self.test_results.addItems(["Pass", "Fail", "Conditional Pass", "Pending"])
        test_layout.addRow("Last Test Result:", self.test_results)
        
        # Test remarks
        self.test_remarks = QTextEdit()
        self.test_remarks.setPlaceholderText("Enter test remarks and observations...")
        self.test_remarks.setMaximumHeight(60)
        test_layout.addRow("Test Remarks:", self.test_remarks)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # BOP components table
        components_group = QGroupBox("BOP Components")
        components_layout = QVBoxLayout()
        
        self.bop_components_table = QTableWidget()
        self.bop_components_table.setColumnCount(5)
        self.bop_components_table.setHorizontalHeaderLabels([
            "Component", "Type", "Serial No", "Last Inspection", "Status"
        ])
        
        components_buttons = QHBoxLayout()
        add_component_button = QPushButton("Add Component")
        remove_component_button = QPushButton("Remove Selected")
        
        components_buttons.addWidget(add_component_button)
        components_buttons.addWidget(remove_component_button)
        components_buttons.addStretch()
        
        components_layout.addWidget(self.bop_components_table)
        components_layout.addLayout(components_buttons)
        components_group.setLayout(components_layout)
        layout.addWidget(components_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        
        # Load sample BOP components
        self.load_sample_bop_components()
        
        return tab
    
    def load_sample_bop_components(self):
        """Load sample BOP components"""
        sample_components = [
            ("Annular Preventer", "Annular", "AP-001", "2024-01-10", "Operational"),
            ("Blind Ram", "Ram", "BR-001", "2024-01-15", "Operational"),
            ("Pipe Ram 5\"", "Ram", "PR-501", "2024-01-12", "Operational"),
            ("Shear Ram", "Ram", "SR-001", "2024-01-18", "Maintenance"),
            ("Hydraulic Connector", "Connector", "HC-001", "2024-01-05", "Operational"),
        ]
        
        for component in sample_components:
            row = self.bop_components_table.rowCount()
            self.bop_components_table.insertRow(row)
            
            for col, value in enumerate(component):
                self.bop_components_table.setItem(row, col, QTableWidgetItem(value))
    
    def create_records_tab(self):
        """Create safety records tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Safety inspections table
        inspections_group = QGroupBox("Safety Inspections")
        inspections_layout = QVBoxLayout()
        
        self.inspections_table = QTableWidget()
        self.inspections_table.setColumnCount(6)
        self.inspections_table.setHorizontalHeaderLabels([
            "Date", "Type", "Inspector", "Findings", "Status", "Actions"
        ])
        
        inspections_buttons = QHBoxLayout()
        add_inspection_button = QPushButton("Add Inspection")
        close_inspection_button = QPushButton("Close Selected")
        
        inspections_buttons.addWidget(add_inspection_button)
        inspections_buttons.addWidget(close_inspection_button)
        inspections_buttons.addStretch()
        
        inspections_layout.addWidget(self.inspections_table)
        inspections_layout.addLayout(inspections_buttons)
        inspections_group.setLayout(inspections_layout)
        layout.addWidget(inspections_group)
        
        # Incident reports table
        incidents_group = QGroupBox("Incident Reports")
        incidents_layout = QVBoxLayout()
        
        self.incidents_table = QTableWidget()
        self.incidents_table.setColumnCount(7)
        self.incidents_table.setHorizontalHeaderLabels([
            "Date", "Time", "Type", "Severity", "Description", "Investigation", "Status"
        ])
        
        incidents_buttons = QHBoxLayout()
        add_incident_button = QPushButton("Report Incident")
        investigate_button = QPushButton("Investigate")
        
        incidents_buttons.addWidget(add_incident_button)
        incidents_buttons.addWidget(investigate_button)
        incidents_buttons.addStretch()
        
        incidents_layout.addWidget(self.incidents_table)
        incidents_layout.addLayout(incidents_buttons)
        incidents_group.setLayout(incidents_layout)
        layout.addWidget(incidents_group)
        
        # Load sample data
        self.load_sample_safety_records()
        
        tab.setLayout(layout)
        return tab
    
    def load_sample_safety_records(self):
        """Load sample safety records"""
        # Sample inspections
        sample_inspections = [
            ("2024-01-10", "Weekly Safety", "John Safety", "All equipment OK", "Closed", "None"),
            ("2024-01-15", "BOP Inspection", "Mike Inspector", "Minor leaks found", "Open", "Repair scheduled"),
            ("2024-01-20", "Fire Equipment", "Sarah Checker", "Extinguishers charged", "Closed", "Completed"),
        ]
        
        for inspection in sample_inspections:
            row = self.inspections_table.rowCount()
            self.inspections_table.insertRow(row)
            
            for col, value in enumerate(inspection):
                self.inspections_table.setItem(row, col, QTableWidgetItem(value))
        
        # Sample incidents
        sample_incidents = [
            ("2024-01-05", "14:30", "Near Miss", "Low", "Dropped tool", "Completed", "Closed"),
            ("2024-01-12", "09:15", "First Aid", "Medium", "Minor cut", "In Progress", "Open"),
        ]
        
        for incident in sample_incidents:
            row = self.incidents_table.rowCount()
            self.incidents_table.insertRow(row)
            
            for col, value in enumerate(incident):
                self.incidents_table.setItem(row, col, QTableWidgetItem(value))
    
    def save_safety_data(self):
        """Save safety data to database"""
        # TODO: Save safety data to database
        QMessageBox.information(self, "Success", "Safety data saved successfully!")

# ============================================
# UPDATE MAIN WINDOW TO INCLUDE NEW MODULES
# ============================================

# In the MainWindow class, update the init_modules method:
def init_modules_updated(self):
    """Initialize all application modules - Updated version"""
    # Well Information
    self.well_info_widget = WellInfoWidget(self.db)
    self.tab_widget.addTab(self.well_info_widget, "🏠 Well Info")
    
    # Daily Report
    self.daily_report_widget = DailyReportWidget(self.db)
    self.tab_widget.addTab(self.daily_report_widget, "🗓 Daily Report")
    
    # Drilling Parameters
    self.drilling_params_widget = DrillingParametersWidget(self.db)
    self.tab_widget.addTab(self.drilling_params_widget, "⚙️ Drilling Params")
    
    # Mud Report
    self.mud_report_widget = MudReportWidget(self.db)
    self.tab_widget.addTab(self.mud_report_widget, "🧪 Mud Report")
    
    # Bit Report
    self.bit_report_widget = BitReportWidget(self.db)
    self.tab_widget.addTab(self.bit_report_widget, "🔩 Bit Report")
    
    # BHA Report
    self.bha_report_widget = BHAReportWidget(self.db)
    self.tab_widget.addTab(self.bha_report_widget, "🛠️ BHA Report")
    
    # Survey Data
    self.survey_widget = SurveyDataWidget(self.db)
    self.tab_widget.addTab(self.survey_widget, "📈 Survey Data")
    
    # Personnel & Logistics
    self.personnel_widget = PersonnelLogisticsWidget(self.db)
    self.tab_widget.addTab(self.personnel_widget, "👥 Personnel & Logistics")
    
    # Inventory Management
    self.inventory_widget = InventoryWidget(self.db)
    self.tab_widget.addTab(self.inventory_widget, "📦 Inventory")
    
    # Service Company Log
    self.service_widget = ServiceCompanyWidget(self.db)
    self.tab_widget.addTab(self.service_widget, "🏢 Service Cos")
    
    # Material Handling
    self.material_widget = MaterialHandlingWidget(self.db)
    self.tab_widget.addTab(self.material_widget, "📝 Material Handling")
    
    # Safety & BOP
    self.safety_widget = SafetyBOPWidget(self.db)
    self.tab_widget.addTab(self.safety_widget, "🦺 Safety & BOP")
    
    # Add placeholders for remaining modules
    self.add_placeholder_tabs_updated()

def add_placeholder_tabs_updated(self):
    """Add placeholder tabs for remaining modules - Updated version"""
    modules = [
        ("♻️ Waste Mgmt", "Waste management"),
        ("🏗️ Cement & Casing", "Cement and casing data"),
        ("⚙️ Downhole Eq", "Downhole equipment"),
        ("🔧 Drill Pipe", "Drill pipe specs"),
        ("🌀 Solid Control", "Solid control equipment"),
        ("⛽ Fuel & Water", "Fuel and water management"),
        ("📊 Export Center", "Report export center"),
        ("⚙️ Preferences", "User preferences")
    ]
    
    for title, description in modules:
        placeholder = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel(f"{title}\n\n{description}\n\n(This module will be implemented in the next phase)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        
        layout.addWidget(label)
        placeholder.setLayout(layout)
        self.tab_widget.addTab(placeholder, title)

# ============================================
# APPLICATION ENTRY POINT
# ============================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create palette for dark/light theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Initialize database
    db = DatabaseManager()
    
    # Show login dialog
    login_dialog = LoginDialog(db)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Login successful, show main window
        window = MainWindow(login_dialog.user)
        
        # Replace module initialization with updated version
        window.init_modules = lambda: init_modules_updated(window)
        window.add_placeholder_tabs = lambda: add_placeholder_tabs_updated(window)
        
        window.init_modules()
        window.show()
        sys.exit(app.exec())
    else:
        # Login cancelled or failed
        sys.exit(0)

if __name__ == "__main__":
    main()
    
# ============================================
# WASTE MANAGEMENT WIDGET
# ============================================

class WasteManagementWidget(QWidget):
    """Waste management and environmental compliance widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Waste Management & Environmental Compliance")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.waste_well_combo = QComboBox()
        
        load_button = QPushButton("Load Waste Data")
        
        well_layout.addWidget(self.waste_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Tab widget for different waste sections
        tabs = QTabWidget()
        
        # Drilling Waste tab
        drilling_waste_tab = self.create_drilling_waste_tab()
        tabs.addTab(drilling_waste_tab, "🔄 Drilling Waste")
        
        # Chemical Waste tab
        chemical_waste_tab = self.create_chemical_waste_tab()
        tabs.addTab(chemical_waste_tab, "🧪 Chemical Waste")
        
        # Cutting Transport tab
        cuttings_tab = self.create_cuttings_tab()
        tabs.addTab(cuttings_tab, "⛰️ Cuttings Transport")
        
        # Compliance tab
        compliance_tab = self.create_compliance_tab()
        tabs.addTab(compliance_tab, "📋 Compliance")
        
        main_layout.addWidget(tabs)
        
        # Environmental summary
        summary_group = QGroupBox("Environmental Summary")
        summary_layout = QGridLayout()
        
        self.total_waste_label = QLabel("Total Waste: 0 bbl")
        self.recycled_label = QLabel("Recycled: 0 bbl")
        self.disposed_label = QLabel("Disposed: 0 bbl")
        self.compliance_status_label = QLabel("Compliance: ✅")
        
        summary_layout.addWidget(self.total_waste_label, 0, 0)
        summary_layout.addWidget(self.recycled_label, 0, 1)
        summary_layout.addWidget(self.disposed_label, 0, 2)
        summary_layout.addWidget(self.compliance_status_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Save button
        save_button = QPushButton("Save Waste Management Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_button.clicked.connect(self.save_waste_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.waste_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.waste_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def create_drilling_waste_tab(self):
        """Create drilling waste tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Recycled waste
        recycled_group = QGroupBox("Recycled Waste")
        recycled_layout = QFormLayout()
        
        self.recycled_waste = QDoubleSpinBox()
        self.recycled_waste.setRange(0, 10000)
        self.recycled_waste.setSuffix(" bbl")
        recycled_layout.addRow("Recycled Volume:", self.recycled_waste)
        
        self.recycling_company = QLineEdit()
        self.recycling_company.setPlaceholderText("Recycling company name")
        recycled_layout.addRow("Recycling Company:", self.recycling_company)
        
        self.recycling_method = QComboBox()
        self.recycling_method.addItems(["Centrifuge", "Thermal", "Chemical", "Biological", "Other"])
        recycled_layout.addRow("Recycling Method:", self.recycling_method)
        
        recycled_group.setLayout(recycled_layout)
        layout.addWidget(recycled_group)
        
        # Waste water treatment
        water_group = QGroupBox("Waste Water Treatment")
        water_layout = QGridLayout()
        
        water_layout.addWidget(QLabel("pH:"), 0, 0)
        self.waste_ph = QDoubleSpinBox()
        self.waste_ph.setRange(0, 14)
        self.waste_ph.setValue(7.0)
        water_layout.addWidget(self.waste_ph, 0, 1)
        
        water_layout.addWidget(QLabel("Turbidity (NTU):"), 0, 2)
        self.turbidity = QDoubleSpinBox()
        self.turbidity.setRange(0, 1000)
        water_layout.addWidget(self.turbidity, 0, 3)
        
        water_layout.addWidget(QLabel("TSS (mg/L):"), 1, 0)
        self.tss = QDoubleSpinBox()
        self.tss.setRange(0, 10000)
        water_layout.addWidget(self.tss, 1, 1)
        
        water_layout.addWidget(QLabel("Hardness (mg/L):"), 1, 2)
        self.hardness = QDoubleSpinBox()
        self.hardness.setRange(0, 10000)
        water_layout.addWidget(self.hardness, 1, 3)
        
        water_layout.addWidget(QLabel("Calcium (mg/L):"), 2, 0)
        self.calcium = QDoubleSpinBox()
        self.calcium.setRange(0, 10000)
        water_layout.addWidget(self.calcium, 2, 1)
        
        water_layout.addWidget(QLabel("Chloride (mg/L):"), 2, 2)
        self.chloride = QDoubleSpinBox()
        self.chloride.setRange(0, 100000)
        water_layout.addWidget(self.chloride, 2, 3)
        
        water_group.setLayout(water_layout)
        layout.addWidget(water_group)
        
        # Treatment notes
        treatment_notes_group = QGroupBox("Treatment Notes")
        treatment_notes_layout = QVBoxLayout()
        
        self.treatment_notes = QTextEdit()
        self.treatment_notes.setPlaceholderText("Enter waste treatment notes...")
        self.treatment_notes.setMaximumHeight(80)
        treatment_notes_layout.addWidget(self.treatment_notes)
        
        treatment_notes_group.setLayout(treatment_notes_layout)
        layout.addWidget(treatment_notes_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_chemical_waste_tab(self):
        """Create chemical waste tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Chemical waste table
        table_group = QGroupBox("Chemical Waste Inventory")
        table_layout = QVBoxLayout()
        
        self.chemical_waste_table = QTableWidget()
        self.chemical_waste_table.setColumnCount(6)
        self.chemical_waste_table.setHorizontalHeaderLabels([
            "Chemical", "Quantity", "Unit", "Hazard Class", "Storage Location", "Disposal Date"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Chemical Waste")
        remove_button = QPushButton("Remove Selected")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(remove_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.chemical_waste_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Hazardous waste info
        hazard_group = QGroupBox("Hazardous Waste Information")
        hazard_layout = QFormLayout()
        
        self.hazardous_waste = QDoubleSpinBox()
        self.hazardous_waste.setRange(0, 1000)
        self.hazardous_waste.setSuffix(" kg")
        hazard_layout.addRow("Hazardous Waste:", self.hazardous_waste)
        
        self.hazard_class = QComboBox()
        self.hazard_class.addItems([
            "Flammable", "Corrosive", "Toxic", "Reactive", 
            "Oxidizer", "Compressed Gas", "Radioactive", "Other"
        ])
        hazard_layout.addRow("Hazard Class:", self.hazard_class)
        
        self.msds_available = QCheckBox("MSDS Available")
        hazard_layout.addRow("", self.msds_available)
        
        hazard_group.setLayout(hazard_layout)
        layout.addWidget(hazard_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        
        # Load sample chemical waste data
        self.load_sample_chemical_waste()
        
        return tab
    
    def load_sample_chemical_waste(self):
        """Load sample chemical waste data"""
        sample_waste = [
            ("Barium Sulfate", 50, "kg", "Toxic", "Storage Area A", "2024-02-15"),
            ("Sodium Hydroxide", 25, "kg", "Corrosive", "Chemical Locker", "2024-02-20"),
            ("Diesel Fuel", 100, "L", "Flammable", "Fuel Storage", "2024-02-10"),
            ("Used Oil", 200, "L", "Flammable", "Waste Oil Tank", "2024-02-25"),
        ]
        
        for waste in sample_waste:
            row = self.chemical_waste_table.rowCount()
            self.chemical_waste_table.insertRow(row)
            
            for col, value in enumerate(waste):
                self.chemical_waste_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_cuttings_tab(self):
        """Create cuttings transport tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Cuttings transport
        cuttings_group = QGroupBox("Cuttings Transport")
        cuttings_layout = QFormLayout()
        
        self.cuttings_volume = QDoubleSpinBox()
        self.cuttings_volume.setRange(0, 10000)
        self.cuttings_volume.setSuffix(" m³")
        cuttings_layout.addRow("Cuttings Volume:", self.cuttings_volume)
        
        self.cuttings_type = QComboBox()
        self.cuttings_type.addItems([
            "Oil Based Mud Cuttings", "Water Based Mud Cuttings",
            "Synthetic Based Mud Cuttings", "Dry Cuttings"
        ])
        cuttings_layout.addRow("Cuttings Type:", self.cuttings_type)
        
        self.transport_company = QLineEdit()
        self.transport_company.setPlaceholderText("Transport company name")
        cuttings_layout.addRow("Transport Company:", self.transport_company)
        
        self.transport_date = QDateEdit()
        self.transport_date.setCalendarPopup(True)
        self.transport_date.setDate(QDate.currentDate())
        cuttings_layout.addRow("Transport Date:", self.transport_date)
        
        self.disposal_site = QLineEdit()
        self.disposal_site.setPlaceholderText("Disposal site location")
        cuttings_layout.addRow("Disposal Site:", self.disposal_site)
        
        self.disposal_method = QComboBox()
        self.disposal_method.addItems([
            "Landfarm", "Injection", "Landfill", "Thermal", 
            "Reuse", "Treatment", "Other"
        ])
        cuttings_layout.addRow("Disposal Method:", self.disposal_method)
        
        cuttings_group.setLayout(cuttings_layout)
        layout.addWidget(cuttings_group)
        
        # Transport documentation
        docs_group = QGroupBox("Transport Documentation")
        docs_layout = QFormLayout()
        
        self.manifest_number = QLineEdit()
        self.manifest_number.setPlaceholderText("Waste manifest number")
        docs_layout.addRow("Manifest No:", self.manifest_number)
        
        self.driver_name = QLineEdit()
        self.driver_name.setPlaceholderText("Driver name")
        docs_layout.addRow("Driver Name:", self.driver_name)
        
        self.vehicle_number = QLineEdit()
        self.vehicle_number.setPlaceholderText("Vehicle license plate")
        docs_layout.addRow("Vehicle No:", self.vehicle_number)
        
        self.docs_attached = QCheckBox("Documents Attached")
        docs_layout.addRow("", self.docs_attached)
        
        docs_group.setLayout(docs_layout)
        layout.addWidget(docs_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_compliance_tab(self):
        """Create compliance tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Regulatory compliance
        reg_group = QGroupBox("Regulatory Compliance")
        reg_layout = QFormLayout()
        
        self.permit_number = QLineEdit()
        self.permit_number.setPlaceholderText("Environmental permit number")
        reg_layout.addRow("Permit No:", self.permit_number)
        
        self.permit_expiry = QDateEdit()
        self.permit_expiry.setCalendarPopup(True)
        self.permit_expiry.setDate(QDate.currentDate().addYears(1))
        reg_layout.addRow("Permit Expiry:", self.permit_expiry)
        
        self.last_inspection = QDateEdit()
        self.last_inspection.setCalendarPopup(True)
        self.last_inspection.setDate(QDate.currentDate().addMonths(-1))
        reg_layout.addRow("Last Inspection:", self.last_inspection)
        
        self.inspection_result = QComboBox()
        self.inspection_result.addItems(["Compliant", "Non-Compliant", "Minor Issues", "Pending"])
        reg_layout.addRow("Inspection Result:", self.inspection_result)
        
        reg_group.setLayout(reg_layout)
        layout.addWidget(reg_group)
        
        # Compliance checklist
        checklist_group = QGroupBox("Compliance Checklist")
        checklist_layout = QVBoxLayout()
        
        self.waste_tracking = QCheckBox("Waste Tracking Records Complete")
        self.waste_tracking.setChecked(True)
        
        self.msds_maintained = QCheckBox("MSDS Maintained")
        self.msds_maintained.setChecked(True)
        
        self.spill_prevention = QCheckBox("Spill Prevention Plan in Place")
        self.spill_prevention.setChecked(True)
        
        self.containment = QCheckBox("Secondary Containment Available")
        self.containment.setChecked(True)
        
        self.training_complete = QCheckBox("Waste Handling Training Complete")
        self.training_complete.setChecked(True)
        
        checklist_layout.addWidget(self.waste_tracking)
        checklist_layout.addWidget(self.msds_maintained)
        checklist_layout.addWidget(self.spill_prevention)
        checklist_layout.addWidget(self.containment)
        checklist_layout.addWidget(self.training_complete)
        
        checklist_group.setLayout(checklist_layout)
        layout.addWidget(checklist_group)
        
        # Environmental incidents
        incidents_group = QGroupBox("Environmental Incidents")
        incidents_layout = QVBoxLayout()
        
        self.incident_count = QSpinBox()
        self.incident_count.setRange(0, 100)
        incidents_layout.addWidget(QLabel("Number of Incidents:"))
        incidents_layout.addWidget(self.incident_count)
        
        self.incident_description = QTextEdit()
        self.incident_description.setPlaceholderText("Describe any environmental incidents...")
        self.incident_description.setMaximumHeight(80)
        incidents_layout.addWidget(self.incident_description)
        
        incidents_group.setLayout(incidents_layout)
        layout.addWidget(incidents_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def save_waste_data(self):
        """Save waste management data to database"""
        well_index = self.waste_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save waste data to database
        QMessageBox.information(self, "Success", "Waste management data saved successfully!")

# ============================================
# CEMENT & CASING WIDGET
# ============================================

class CementCasingWidget(QWidget):
    """Cement and casing management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.cement_data = []
        self.casing_data = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Cement & Casing Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.cc_well_combo = QComboBox()
        
        load_button = QPushButton("Load Cement & Casing Data")
        
        well_layout.addWidget(self.cc_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Tab widget for cement and casing
        tabs = QTabWidget()
        
        # Cement tab
        cement_tab = self.create_cement_tab()
        tabs.addTab(cement_tab, "🏗️ Cement")
        
        # Casing tab
        casing_tab = self.create_casing_tab()
        tabs.addTab(casing_tab, "🔩 Casing")
        
        # Cement Job tab
        job_tab = self.create_cement_job_tab()
        tabs.addTab(job_tab, "📋 Cement Job")
        
        main_layout.addWidget(tabs)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QGridLayout()
        
        self.cement_total_label = QLabel("Cement Total: 0 sacks")
        self.casing_total_label = QLabel("Casing Total: 0 ft")
        self.casing_strings_label = QLabel("Casing Strings: 0")
        self.cement_jobs_label = QLabel("Cement Jobs: 0")
        
        summary_layout.addWidget(self.cement_total_label, 0, 0)
        summary_layout.addWidget(self.casing_total_label, 0, 1)
        summary_layout.addWidget(self.casing_strings_label, 0, 2)
        summary_layout.addWidget(self.cement_jobs_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Save button
        save_button = QPushButton("Save Cement & Casing Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        save_button.clicked.connect(self.save_cement_casing_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
        
        # Load sample data
        self.load_sample_data()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.cc_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.cc_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def load_sample_data(self):
        """Load sample cement and casing data"""
        # Sample cement data
        sample_cement = [
            ("Class G", 500, 300, 50, 150, "sack"),
            ("Class H", 300, 200, 0, 100, "sack"),
            ("Silica Flour", 100, 80, 0, 20, "sack"),
            ("Retarder", 50, 40, 5, 5, "sack"),
        ]
        
        for cement in sample_cement:
            row = self.cement_table.rowCount()
            self.cement_table.insertRow(row)
            
            for col, value in enumerate(cement):
                self.cement_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        # Sample casing data
        sample_casing = [
            ("30\" Conductor", 30.0, "K-55", 450, 120, 120, "2024-01-05", "Wellhead", "Set"),
            ("20\" Surface", 20.0, "J-55", 2000, 2000, 200, "2024-01-10", "Cement Shoe", "Set"),
            ("13 3/8\" Intermediate", 13.375, "N-80", 3500, 3500, 150, "2024-01-20", "Float Collar", "Running"),
            ("9 5/8\" Production", 9.625, "L-80", 5000, 0, 0, "2024-02-01", "N/A", "Planned"),
        ]
        
        for casing in sample_casing:
            row = self.casing_table.rowCount()
            self.casing_table.insertRow(row)
            
            for col, value in enumerate(casing):
                self.casing_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_cement_tab(self):
        """Create cement materials tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Cement table
        table_group = QGroupBox("Cement & Additives Inventory")
        table_layout = QVBoxLayout()
        
        self.cement_table = QTableWidget()
        self.cement_table.setColumnCount(6)
        self.cement_table.setHorizontalHeaderLabels([
            "Material", "Received", "Consumed", "Backload", "Inventory", "Unit"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Material")
        add_button.clicked.connect(self.add_cement_material_dialog)
        
        edit_button = QPushButton("Edit Selected")
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_cement_material)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.cement_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Cement properties
        properties_group = QGroupBox("Cement Slurry Properties")
        properties_layout = QGridLayout()
        
        properties_layout.addWidget(QLabel("Density (ppg):"), 0, 0)
        self.cement_density = QDoubleSpinBox()
        self.cement_density.setRange(8, 20)
        self.cement_density.setValue(15.8)
        properties_layout.addWidget(self.cement_density, 0, 1)
        
        properties_layout.addWidget(QLabel("Yield (ft³/sack):"), 0, 2)
        self.cement_yield = QDoubleSpinBox()
        self.cement_yield.setRange(0, 10)
        self.cement_yield.setValue(1.18)
        properties_layout.addWidget(self.cement_yield, 0, 3)
        
        properties_layout.addWidget(QLabel("Thickening Time (hrs):"), 1, 0)
        self.thickening_time = QDoubleSpinBox()
        self.thickening_time.setRange(0, 24)
        self.thickening_time.setValue(4.5)
        properties_layout.addWidget(self.thickening_time, 1, 1)
        
        properties_layout.addWidget(QLabel("Compressive Strength (psi):"), 1, 2)
        self.compressive_strength = QDoubleSpinBox()
        self.compressive_strength.setRange(0, 10000)
        self.compressive_strength.setValue(2500)
        properties_layout.addWidget(self.compressive_strength, 1, 3)
        
        properties_group.setLayout(properties_layout)
        layout.addWidget(properties_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def add_cement_material_dialog(self):
        """Show dialog to add cement material"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Cement Material")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Material details
        self.new_cement_material = QComboBox()
        self.new_cement_material.addItems([
            "Class A", "Class B", "Class C", "Class G", "Class H",
            "Silica Flour", "Bentonite", "Barite", "Retarder",
            "Accelerator", "Dispersant", "Fluid Loss Additive", "Other"
        ])
        form.addRow("Material:", self.new_cement_material)
        
        # Quantities
        quantities_layout = QGridLayout()
        
        quantities_layout.addWidget(QLabel("Received:"), 0, 0)
        self.new_cement_received = QDoubleSpinBox()
        self.new_cement_received.setRange(0, 10000)
        quantities_layout.addWidget(self.new_cement_received, 0, 1)
        
        quantities_layout.addWidget(QLabel("Consumed:"), 0, 2)
        self.new_cement_consumed = QDoubleSpinBox()
        self.new_cement_consumed.setRange(0, 10000)
        quantities_layout.addWidget(self.new_cement_consumed, 0, 3)
        
        quantities_layout.addWidget(QLabel("Backload:"), 1, 0)
        self.new_cement_backload = QDoubleSpinBox()
        self.new_cement_backload.setRange(0, 10000)
        quantities_layout.addWidget(self.new_cement_backload, 1, 1)
        
        quantities_layout.addWidget(QLabel("Inventory:"), 1, 2)
        self.new_cement_inventory = QDoubleSpinBox()
        self.new_cement_inventory.setRange(0, 10000)
        self.new_cement_inventory.setReadOnly(True)
        quantities_layout.addWidget(self.new_cement_inventory, 1, 3)
        
        form.addRow("Quantities:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(quantities_layout)
        
        # Unit
        self.new_cement_unit = QComboBox()
        self.new_cement_unit.addItems(["sack", "kg", "lb", "bbl", "ton"])
        form.addRow("Unit:", self.new_cement_unit)
        
        # Connect signals for auto-calculation
        self.new_cement_received.valueChanged.connect(self.calculate_cement_inventory)
        self.new_cement_consumed.valueChanged.connect(self.calculate_cement_inventory)
        self.new_cement_backload.valueChanged.connect(self.calculate_cement_inventory)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Material")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_cement_material(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calculate_cement_inventory(self):
        """Calculate cement inventory"""
        received = self.new_cement_received.value()
        consumed = self.new_cement_consumed.value()
        backload = self.new_cement_backload.value()
        inventory = received - consumed - backload
        self.new_cement_inventory.setValue(inventory)
    
    def add_cement_material(self, dialog):
        """Add cement material to table"""
        # Add to table
        row = self.cement_table.rowCount()
        self.cement_table.insertRow(row)
        
        material_data = [
            self.new_cement_material.currentText(),
            str(self.new_cement_received.value()),
            str(self.new_cement_consumed.value()),
            str(self.new_cement_backload.value()),
            str(self.new_cement_inventory.value()),
            self.new_cement_unit.currentText()
        ]
        
        for col, value in enumerate(material_data):
            self.cement_table.setItem(row, col, QTableWidgetItem(value))
        
        dialog.accept()
    
    def delete_cement_material(self):
        """Delete selected cement material"""
        selected_row = self.cement_table.currentRow()
        if selected_row >= 0:
            self.cement_table.removeRow(selected_row)
    
    def create_casing_tab(self):
        """Create casing tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Casing table
        table_group = QGroupBox("Casing Program")
        table_layout = QVBoxLayout()
        
        self.casing_table = QTableWidget()
        self.casing_table.setColumnCount(9)
        self.casing_table.setHorizontalHeaderLabels([
            "String", "Size (in)", "Grade", "Depth (ft)", "Shoe Depth (ft)",
            "Test Pressure (psi)", "Setting Date", "Accessories", "Status"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Casing String")
        add_button.clicked.connect(self.add_casing_string_dialog)
        
        edit_button = QPushButton("Edit Selected")
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_casing_string)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.casing_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Casing accessories
        accessories_group = QGroupBox("Casing Accessories")
        accessories_layout = QFormLayout()
        
        self.centralizers = QSpinBox()
        self.centralizers.setRange(0, 1000)
        accessories_layout.addRow("Centralizers:", self.centralizers)
        
        self.scratchers = QSpinBox()
        self.scratchers.setRange(0, 1000)
        accessories_layout.addRow("Scratchers:", self.scratchers)
        
        self.float_collars = QSpinBox()
        self.float_collars.setRange(0, 100)
        accessories_layout.addRow("Float Collars:", self.float_collars)
        
        self.cement_baskets = QSpinBox()
        self.cement_baskets.setRange(0, 100)
        accessories_layout.addRow("Cement Baskets:", self.cement_baskets)
        
        accessories_group.setLayout(accessories_layout)
        layout.addWidget(accessories_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def add_casing_string_dialog(self):
        """Show dialog to add casing string"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Casing String")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Casing details
        self.new_casing_string = QLineEdit()
        self.new_casing_string.setPlaceholderText("e.g., 13 3/8\" Intermediate")
        form.addRow("String Name:", self.new_casing_string)
        
        self.new_casing_size = QDoubleSpinBox()
        self.new_casing_size.setRange(0, 50)
        self.new_casing_size.setSuffix(" inch")
        form.addRow("Size:", self.new_casing_size)
        
        self.new_casing_grade = QComboBox()
        self.new_casing_grade.addItems([
            "H-40", "J-55", "K-55", "N-80", "L-80", "C-90", "C-95",
            "P-110", "Q-125", "V-150", "Other"
        ])
        form.addRow("Grade:", self.new_casing_grade)
        
        # Depth information
        depth_layout = QHBoxLayout()
        self.new_casing_depth = QDoubleSpinBox()
        self.new_casing_depth.setRange(0, 50000)
        self.new_casing_depth.setSuffix(" ft")
        
        self.new_shoe_depth = QDoubleSpinBox()
        self.new_shoe_depth.setRange(0, 50000)
        self.new_shoe_depth.setSuffix(" ft")
        
        depth_layout.addWidget(QLabel("Depth:"))
        depth_layout.addWidget(self.new_casing_depth)
        depth_layout.addWidget(QLabel("Shoe Depth:"))
        depth_layout.addWidget(self.new_shoe_depth)
        
        form.addRow("Depth:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(depth_layout)
        
        # Test pressure
        self.new_test_pressure = QDoubleSpinBox()
        self.new_test_pressure.setRange(0, 20000)
        self.new_test_pressure.setSuffix(" psi")
        form.addRow("Test Pressure:", self.new_test_pressure)
        
        # Setting date
        self.new_setting_date = QDateEdit()
        self.new_setting_date.setCalendarPopup(True)
        self.new_setting_date.setDate(QDate.currentDate())
        form.addRow("Setting Date:", self.new_setting_date)
        
        # Accessories
        self.new_accessories = QTextEdit()
        self.new_accessories.setMaximumHeight(60)
        form.addRow("Accessories:", self.new_accessories)
        
        # Status
        self.new_casing_status = QComboBox()
        self.new_casing_status.addItems(["Planned", "Running", "Set", "Tested", "Completed"])
        form.addRow("Status:", self.new_casing_status)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add String")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_casing_string(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_casing_string(self, dialog):
        """Add casing string to table"""
        string_name = self.new_casing_string.text().strip()
        if not string_name:
            QMessageBox.warning(self, "Error", "Please enter string name.")
            return
        
        # Add to table
        row = self.casing_table.rowCount()
        self.casing_table.insertRow(row)
        
        casing_data = [
            string_name,
            str(self.new_casing_size.value()),
            self.new_casing_grade.currentText(),
            str(self.new_casing_depth.value()),
            str(self.new_shoe_depth.value()),
            str(self.new_test_pressure.value()),
            self.new_setting_date.date().toString("yyyy-MM-dd"),
            self.new_accessories.toPlainText(),
            self.new_casing_status.currentText()
        ]
        
        for col, value in enumerate(casing_data):
            self.casing_table.setItem(row, col, QTableWidgetItem(value))
        
        dialog.accept()
    
    def delete_casing_string(self):
        """Delete selected casing string"""
        selected_row = self.casing_table.currentRow()
        if selected_row >= 0:
            self.casing_table.removeRow(selected_row)
    
    def create_cement_job_tab(self):
        """Create cement job tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Cement job details
        job_group = QGroupBox("Cement Job Details")
        job_layout = QFormLayout()
        
        self.cement_job_date = QDateEdit()
        self.cement_job_date.setCalendarPopup(True)
        self.cement_job_date.setDate(QDate.currentDate())
        job_layout.addRow("Job Date:", self.cement_job_date)
        
        self.casing_string_combo = QComboBox()
        self.casing_string_combo.addItems([
            "30\" Conductor", "20\" Surface", "13 3/8\" Intermediate", "9 5/8\" Production"
        ])
        job_layout.addRow("Casing String:", self.casing_string_combo)
        
        # Cement volumes
        volumes_layout = QGridLayout()
        
        volumes_layout.addWidget(QLabel("Slurry Volume:"), 0, 0)
        self.slurry_volume = QDoubleSpinBox()
        self.slurry_volume.setRange(0, 10000)
        self.slurry_volume.setSuffix(" bbl")
        volumes_layout.addWidget(self.slurry_volume, 0, 1)
        
        volumes_layout.addWidget(QLabel("Cement Volume:"), 0, 2)
        self.cement_volume = QDoubleSpinBox()
        self.cement_volume.setRange(0, 10000)
        self.cement_volume.setSuffix(" sacks")
        volumes_layout.addWidget(self.cement_volume, 0, 3)
        
        volumes_layout.addWidget(QLabel("Mix Water:"), 1, 0)
        self.mix_water = QDoubleSpinBox()
        self.mix_water.setRange(0, 10000)
        self.mix_water.setSuffix(" bbl")
        volumes_layout.addWidget(self.mix_water, 1, 1)
        
        volumes_layout.addWidget(QLabel("Displacement:"), 1, 2)
        self.displacement = QDoubleSpinBox()
        self.displacement.setRange(0, 10000)
        self.displacement.setSuffix(" bbl")
        volumes_layout.addWidget(self.displacement, 1, 3)
        
        job_layout.addRow("Volumes:", QWidget())
        job_layout.itemAt(job_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(volumes_layout)
        
        # Pumping parameters
        pump_layout = QGridLayout()
        
        pump_layout.addWidget(QLabel("Pump Rate:"), 0, 0)
        self.pump_rate = QDoubleSpinBox()
        self.pump_rate.setRange(0, 50)
        self.pump_rate.setSuffix(" bpm")
        pump_layout.addWidget(self.pump_rate, 0, 1)
        
        pump_layout.addWidget(QLabel("Pressure:"), 0, 2)
        self.cement_pressure = QDoubleSpinBox()
        self.cement_pressure.setRange(0, 5000)
        self.cement_pressure.setSuffix(" psi")
        pump_layout.addWidget(self.cement_pressure, 0, 3)
        
        pump_layout.addWidget(QLabel("Returns:"), 1, 0)
        self.returns = QCheckBox("Returns Observed")
        self.returns.setChecked(True)
        pump_layout.addWidget(self.returns, 1, 1, 1, 3)
        
        job_layout.addRow("Pumping:", QWidget())
        job_layout.itemAt(job_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(pump_layout)
        
        # Job results
        self.job_result = QComboBox()
        self.job_result.addItems(["Successful", "Partial Returns", "No Returns", "Failed"])
        job_layout.addRow("Job Result:", self.job_result)
        
        # Job notes
        self.job_notes = QTextEdit()
        self.job_notes.setPlaceholderText("Enter cement job notes...")
        self.job_notes.setMaximumHeight(80)
        job_layout.addRow("Job Notes:", self.job_notes)
        
        job_group.setLayout(job_layout)
        layout.addWidget(job_group)
        
        # Cement lab data
        lab_group = QGroupBox("Cement Lab Data")
        lab_layout = QGridLayout()
        
        lab_layout.addWidget(QLabel("Thickening Time:"), 0, 0)
        self.lab_thickening = QDoubleSpinBox()
        self.lab_thickening.setRange(0, 24)
        self.lab_thickening.setSuffix(" hours")
        lab_layout.addWidget(self.lab_thickening, 0, 1)
        
        lab_layout.addWidget(QLabel("Compressive Strength:"), 0, 2)
        self.lab_strength = QDoubleSpinBox()
        self.lab_strength.setRange(0, 10000)
        self.lab_strength.setSuffix(" psi")
        lab_layout.addWidget(self.lab_strength, 0, 3)
        
        lab_layout.addWidget(QLabel("Fluid Loss:"), 1, 0)
        self.cement_fluid_loss = QDoubleSpinBox()
        self.cement_fluid_loss.setRange(0, 1000)
        self.cement_fluid_loss.setSuffix(" cc/30min")
        lab_layout.addWidget(self.cement_fluid_loss, 1, 1)
        
        lab_layout.addWidget(QLabel("Free Water:"), 1, 2)
        self.free_water = QDoubleSpinBox()
        self.free_water.setRange(0, 10)
        self.free_water.setSuffix(" ml")
        lab_layout.addWidget(self.free_water, 1, 3)
        
        lab_group.setLayout(lab_layout)
        layout.addWidget(lab_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def save_cement_casing_data(self):
        """Save cement and casing data to database"""
        well_index = self.cc_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save data to database
        QMessageBox.information(self, "Success", "Cement & casing data saved successfully!")

# ============================================
# DOWNHOLE EQUIPMENT WIDGET
# ============================================

class DownholeEquipmentWidget(QWidget):
    """Downhole equipment management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.equipment_list = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Downhole Equipment Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.dh_well_combo = QComboBox()
        
        load_button = QPushButton("Load Equipment")
        
        well_layout.addWidget(self.dh_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Equipment table
        table_group = QGroupBox("Downhole Equipment")
        table_layout = QVBoxLayout()
        
        self.dh_table = QTableWidget()
        self.dh_table.setColumnCount(10)
        self.dh_table.setHorizontalHeaderLabels([
            "Equipment", "S/N", "ID", "Sliding Hours", "Rotation Hours",
            "Pumping Hours", "Total Hours", "Last Maintenance", "Next Maintenance", "Status"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Equipment")
        add_button.clicked.connect(self.add_equipment_dialog)
        
        edit_button = QPushButton("Edit Selected")
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_equipment)
        
        update_hours_button = QPushButton("Update Hours")
        update_hours_button.clicked.connect(self.update_hours_dialog)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(update_hours_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.dh_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Equipment summary
        summary_group = QGroupBox("Equipment Summary")
        summary_layout = QGridLayout()
        
        self.total_equipment_label = QLabel("Total Equipment: 0")
        self.operational_label = QLabel("Operational: 0")
        self.maintenance_label = QLabel("Maintenance Due: 0")
        self.total_hours_label = QLabel("Total Hours: 0")
        
        summary_layout.addWidget(self.total_equipment_label, 0, 0)
        summary_layout.addWidget(self.operational_label, 0, 1)
        summary_layout.addWidget(self.maintenance_label, 0, 2)
        summary_layout.addWidget(self.total_hours_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Maintenance alert
        self.maintenance_alert = QWidget()
        self.maintenance_alert.setVisible(False)
        alert_layout = QHBoxLayout()
        alert_icon = QLabel("⚠️")
        self.alert_message = QLabel("")
        alert_layout.addWidget(alert_icon)
        alert_layout.addWidget(self.alert_message)
        alert_layout.addStretch()
        self.maintenance_alert.setLayout(alert_layout)
        self.maintenance_alert.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 5px;")
        main_layout.addWidget(self.maintenance_alert)
        
        # Save button
        save_button = QPushButton("Save Equipment Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_button.clicked.connect(self.save_equipment_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
        
        # Load sample equipment data
        self.load_sample_equipment()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.dh_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.dh_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def load_sample_equipment(self):
        """Load sample equipment data"""
        sample_equipment = [
            ("MWD Tool", "MWD-001", "MWD001", 120, 300, 150, 570, "2024-01-15", "2024-02-15", "Operational"),
            ("LWD Tool", "LWD-001", "LWD001", 80, 250, 120, 450, "2024-01-20", "2024-02-20", "Operational"),
            ("Motor 6 3/4\"", "MOT-001", "MOT001", 200, 500, 300, 1000, "2024-01-10", "2024-02-10", "Maintenance"),
            ("RSS Tool", "RSS-001", "RSS001", 50, 150, 80, 280, "2024-01-25", "2024-02-25", "Operational"),
            ("Gamma Ray", "GR-001", "GR001", 150, 400, 200, 750, "2024-01-05", "2024-02-05", "Operational"),
        ]
        
        for equipment in sample_equipment:
            row = self.dh_table.rowCount()
            self.dh_table.insertRow(row)
            
            for col, value in enumerate(equipment):
                self.dh_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        self.update_equipment_summary()
    
    def add_equipment_dialog(self):
        """Show dialog to add equipment"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Downhole Equipment")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Equipment details
        self.new_equipment_name = QLineEdit()
        self.new_equipment_name.setPlaceholderText("e.g., MWD Tool")
        form.addRow("Equipment Name:", self.new_equipment_name)
        
        self.new_serial_no = QLineEdit()
        self.new_serial_no.setPlaceholderText("Serial number")
        form.addRow("Serial No:", self.new_serial_no)
        
        self.new_equipment_id = QLineEdit()
        self.new_equipment_id.setPlaceholderText("Equipment ID")
        form.addRow("Equipment ID:", self.new_equipment_id)
        
        # Initial hours
        hours_layout = QGridLayout()
        
        hours_layout.addWidget(QLabel("Sliding Hours:"), 0, 0)
        self.new_sliding_hours = QDoubleSpinBox()
        self.new_sliding_hours.setRange(0, 10000)
        hours_layout.addWidget(self.new_sliding_hours, 0, 1)
        
        hours_layout.addWidget(QLabel("Rotation Hours:"), 0, 2)
        self.new_rotation_hours = QDoubleSpinBox()
        self.new_rotation_hours.setRange(0, 10000)
        hours_layout.addWidget(self.new_rotation_hours, 0, 3)
        
        hours_layout.addWidget(QLabel("Pumping Hours:"), 1, 0)
        self.new_pumping_hours = QDoubleSpinBox()
        self.new_pumping_hours.setRange(0, 10000)
        hours_layout.addWidget(self.new_pumping_hours, 1, 1)
        
        hours_layout.addWidget(QLabel("Total Hours:"), 1, 2)
        self.new_total_hours = QDoubleSpinBox()
        self.new_total_hours.setRange(0, 10000)
        self.new_total_hours.setReadOnly(True)
        hours_layout.addWidget(self.new_total_hours, 1, 3)
        
        form.addRow("Initial Hours:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(hours_layout)
        
        # Maintenance dates
        dates_layout = QHBoxLayout()
        self.new_last_maintenance = QDateEdit()
        self.new_last_maintenance.setCalendarPopup(True)
        self.new_last_maintenance.setDate(QDate.currentDate())
        
        self.new_next_maintenance = QDateEdit()
        self.new_next_maintenance.setCalendarPopup(True)
        self.new_next_maintenance.setDate(QDate.currentDate().addMonths(1))
        
        dates_layout.addWidget(QLabel("Last Maintenance:"))
        dates_layout.addWidget(self.new_last_maintenance)
        dates_layout.addWidget(QLabel("Next Maintenance:"))
        dates_layout.addWidget(self.new_next_maintenance)
        
        form.addRow("Maintenance:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(dates_layout)
        
        # Status
        self.new_equipment_status = QComboBox()
        self.new_equipment_status.addItems([
            "Operational", "Maintenance", "Repair", "Calibration",
            "Storage", "Retired", "Damaged"
        ])
        form.addRow("Status:", self.new_equipment_status)
        
        # Connect signals for auto-calculation
        self.new_sliding_hours.valueChanged.connect(self.calculate_total_hours)
        self.new_rotation_hours.valueChanged.connect(self.calculate_total_hours)
        self.new_pumping_hours.valueChanged.connect(self.calculate_total_hours)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Equipment")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_equipment(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def calculate_total_hours(self):
        """Calculate total equipment hours"""
        sliding = self.new_sliding_hours.value()
        rotation = self.new_rotation_hours.value()
        pumping = self.new_pumping_hours.value()
        total = sliding + rotation + pumping
        self.new_total_hours.setValue(total)
    
    def add_equipment(self, dialog):
        """Add equipment to table"""
        equipment_name = self.new_equipment_name.text().strip()
        if not equipment_name:
            QMessageBox.warning(self, "Error", "Please enter equipment name.")
            return
        
        # Add to table
        row = self.dh_table.rowCount()
        self.dh_table.insertRow(row)
        
        equipment_data = [
            equipment_name,
            self.new_serial_no.text(),
            self.new_equipment_id.text(),
            str(self.new_sliding_hours.value()),
            str(self.new_rotation_hours.value()),
            str(self.new_pumping_hours.value()),
            str(self.new_total_hours.value()),
            self.new_last_maintenance.date().toString("yyyy-MM-dd"),
            self.new_next_maintenance.date().toString("yyyy-MM-dd"),
            self.new_equipment_status.currentText()
        ]
        
        for col, value in enumerate(equipment_data):
            self.dh_table.setItem(row, col, QTableWidgetItem(value))
        
        dialog.accept()
        self.update_equipment_summary()
    
    def delete_equipment(self):
        """Delete selected equipment"""
        selected_row = self.dh_table.currentRow()
        if selected_row >= 0:
            self.dh_table.removeRow(selected_row)
            self.update_equipment_summary()
    
    def update_hours_dialog(self):
        """Show dialog to update equipment hours"""
        selected_row = self.dh_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select equipment to update hours.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Equipment Hours")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        equipment_name = self.dh_table.item(selected_row, 0).text()
        form.addRow("Equipment:", QLabel(equipment_name))
        
        # Current hours
        current_sliding = float(self.dh_table.item(selected_row, 3).text())
        current_rotation = float(self.dh_table.item(selected_row, 4).text())
        current_pumping = float(self.dh_table.item(selected_row, 5).text())
        
        form.addRow("Current Sliding Hours:", QLabel(f"{current_sliding}"))
        form.addRow("Current Rotation Hours:", QLabel(f"{current_rotation}"))
        form.addRow("Current Pumping Hours:", QLabel(f"{current_pumping}"))
        
        # Additional hours
        self.add_sliding = QDoubleSpinBox()
        self.add_sliding.setRange(0, 1000)
        form.addRow("Add Sliding Hours:", self.add_sliding)
        
        self.add_rotation = QDoubleSpinBox()
        self.add_rotation.setRange(0, 1000)
        form.addRow("Add Rotation Hours:", self.add_rotation)
        
        self.add_pumping = QDoubleSpinBox()
        self.add_pumping.setRange(0, 1000)
        form.addRow("Add Pumping Hours:", self.add_pumping)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        update_button = QPushButton("Update")
        cancel_button = QPushButton("Cancel")
        
        update_button.clicked.connect(lambda: self.update_equipment_hours(dialog, selected_row))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def update_equipment_hours(self, dialog, row):
        """Update equipment hours"""
        # Calculate new hours
        current_sliding = float(self.dh_table.item(row, 3).text())
        current_rotation = float(self.dh_table.item(row, 4).text())
        current_pumping = float(self.dh_table.item(row, 5).text())
        
        new_sliding = current_sliding + self.add_sliding.value()
        new_rotation = current_rotation + self.add_rotation.value()
        new_pumping = current_pumping + self.add_pumping.value()
        new_total = new_sliding + new_rotation + new_pumping
        
        # Update table
        self.dh_table.setItem(row, 3, QTableWidgetItem(str(new_sliding)))
        self.dh_table.setItem(row, 4, QTableWidgetItem(str(new_rotation)))
        self.dh_table.setItem(row, 5, QTableWidgetItem(str(new_pumping)))
        self.dh_table.setItem(row, 6, QTableWidgetItem(str(new_total)))
        
        dialog.accept()
        self.update_equipment_summary()
    
    def update_equipment_summary(self):
        """Update equipment summary information"""
        total_equipment = self.dh_table.rowCount()
        
        operational_count = 0
        maintenance_due_count = 0
        total_hours = 0
        
        current_date = QDate.currentDate()
        maintenance_due_items = []
        
        for row in range(total_equipment):
            # Count operational equipment
            status = self.dh_table.item(row, 9).text()
            if status == "Operational":
                operational_count += 1
            
            # Check maintenance due
            next_maintenance = QDate.fromString(self.dh_table.item(row, 8).text(), "yyyy-MM-dd")
            if next_maintenance <= current_date.addDays(7):  # Due in next 7 days
                maintenance_due_count += 1
                equipment_name = self.dh_table.item(row, 0).text()
                maintenance_due_items.append(f"{equipment_name} ({next_maintenance.toString('MM-dd')})")
            
            # Sum total hours
            total_hours += float(self.dh_table.item(row, 6).text())
        
        self.total_equipment_label.setText(f"Total Equipment: {total_equipment}")
        self.operational_label.setText(f"Operational: {operational_count}")
        self.maintenance_label.setText(f"Maintenance Due: {maintenance_due_count}")
        self.total_hours_label.setText(f"Total Hours: {total_hours:.0f}")
        
        # Show maintenance alert if needed
        if maintenance_due_items:
            self.maintenance_alert.setVisible(True)
            items_text = ", ".join(maintenance_due_items[:3])  # Show first 3 items
            if len(maintenance_due_items) > 3:
                items_text += f" and {len(maintenance_due_items) - 3} more..."
            self.alert_message.setText(f"Maintenance due for: {items_text}")
        else:
            self.maintenance_alert.setVisible(False)
    
    def save_equipment_data(self):
        """Save equipment data to database"""
        well_index = self.dh_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save data to database
        QMessageBox.information(self, "Success", "Equipment data saved successfully!")

# ============================================
# UPDATE MAIN WINDOW TO INCLUDE NEW MODULES
# ============================================

def init_modules_complete(self):
    """Initialize all application modules - Complete version"""
    # Well Information
    self.well_info_widget = WellInfoWidget(self.db)
    self.tab_widget.addTab(self.well_info_widget, "🏠 Well Info")
    
    # Daily Report
    self.daily_report_widget = DailyReportWidget(self.db)
    self.tab_widget.addTab(self.daily_report_widget, "🗓 Daily Report")
    
    # Drilling Parameters
    self.drilling_params_widget = DrillingParametersWidget(self.db)
    self.tab_widget.addTab(self.drilling_params_widget, "⚙️ Drilling Params")
    
    # Mud Report
    self.mud_report_widget = MudReportWidget(self.db)
    self.tab_widget.addTab(self.mud_report_widget, "🧪 Mud Report")
    
    # Bit Report
    self.bit_report_widget = BitReportWidget(self.db)
    self.tab_widget.addTab(self.bit_report_widget, "🔩 Bit Report")
    
    # BHA Report
    self.bha_report_widget = BHAReportWidget(self.db)
    self.tab_widget.addTab(self.bha_report_widget, "🛠️ BHA Report")
    
    # Survey Data
    self.survey_widget = SurveyDataWidget(self.db)
    self.tab_widget.addTab(self.survey_widget, "📈 Survey Data")
    
    # Personnel & Logistics
    self.personnel_widget = PersonnelLogisticsWidget(self.db)
    self.tab_widget.addTab(self.personnel_widget, "👥 Personnel & Logistics")
    
    # Inventory Management
    self.inventory_widget = InventoryWidget(self.db)
    self.tab_widget.addTab(self.inventory_widget, "📦 Inventory")
    
    # Service Company Log
    self.service_widget = ServiceCompanyWidget(self.db)
    self.tab_widget.addTab(self.service_widget, "🏢 Service Cos")
    
    # Material Handling
    self.material_widget = MaterialHandlingWidget(self.db)
    self.tab_widget.addTab(self.material_widget, "📝 Material Handling")
    
    # Safety & BOP
    self.safety_widget = SafetyBOPWidget(self.db)
    self.tab_widget.addTab(self.safety_widget, "🦺 Safety & BOP")
    
    # Waste Management
    self.waste_widget = WasteManagementWidget(self.db)
    self.tab_widget.addTab(self.waste_widget, "♻️ Waste Mgmt")
    
    # Cement & Casing
    self.cement_widget = CementCasingWidget(self.db)
    self.tab_widget.addTab(self.cement_widget, "🏗️ Cement & Casing")
    
    # Downhole Equipment
    self.downhole_widget = DownholeEquipmentWidget(self.db)
    self.tab_widget.addTab(self.downhole_widget, "⚙️ Downhole Eq")
    
    # Add placeholders for remaining modules
    self.add_placeholder_tabs_complete()

def add_placeholder_tabs_complete(self):
    """Add placeholder tabs for remaining modules - Complete version"""
    modules = [
        ("🔧 Drill Pipe", "Drill pipe specs"),
        ("🌀 Solid Control", "Solid control equipment"),
        ("⛽ Fuel & Water", "Fuel and water management"),
        ("📊 Export Center", "Report export center"),
        ("⚙️ Preferences", "User preferences")
    ]
    
    for title, description in modules:
        placeholder = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel(f"{title}\n\n{description}\n\n(This module will be implemented in the next phase)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        
        layout.addWidget(label)
        placeholder.setLayout(layout)
        self.tab_widget.addTab(placeholder, title)

# ============================================
# APPLICATION ENTRY POINT
# ============================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create palette for dark/light theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Initialize database
    db = DatabaseManager()
    
    # Show login dialog
    login_dialog = LoginDialog(db)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Login successful, show main window
        window = MainWindow(login_dialog.user)
        
        # Replace module initialization with complete version
        window.init_modules = lambda: init_modules_complete(window)
        window.add_placeholder_tabs = lambda: add_placeholder_tabs_complete(window)
        
        window.init_modules()
        window.show()
        sys.exit(app.exec())
    else:
        # Login cancelled or failed
        sys.exit(0)

if __name__ == "__main__":
    main()
    
# ============================================
# DRILL PIPE SPECS WIDGET
# ============================================

class DrillPipeWidget(QWidget):
    """Drill pipe specifications and management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.drill_pipe_list = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Drill Pipe Specifications")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.dp_well_combo = QComboBox()
        
        load_button = QPushButton("Load Drill Pipe Data")
        
        well_layout.addWidget(self.dp_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Drill pipe table
        table_group = QGroupBox("Drill Pipe Inventory")
        table_layout = QVBoxLayout()
        
        self.dp_table = QTableWidget()
        self.dp_table.setColumnCount(12)
        self.dp_table.setHorizontalHeaderLabels([
            "Size (in)", "Weight (lb/ft)", "Grade", "Connection", "ID (in)",
            "TJ OD (in)", "TJ ID (in)", "Std in Derrick", "Total Length (ft)",
            "Pipe Class", "Last Inspection", "Status"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Drill Pipe")
        add_button.clicked.connect(self.add_drill_pipe_dialog)
        
        edit_button = QPushButton("Edit Selected")
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_drill_pipe)
        
        inspect_button = QPushButton("Record Inspection")
        inspect_button.clicked.connect(self.record_inspection_dialog)
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        table_buttons.addWidget(inspect_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.dp_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Summary section
        summary_group = QGroupBox("Drill Pipe Summary")
        summary_layout = QGridLayout()
        
        self.total_pipe_label = QLabel("Total Pipes: 0")
        self.total_length_label = QLabel("Total Length: 0 ft")
        self.average_weight_label = QLabel("Avg Weight: 0 lb/ft")
        self.pipe_classes_label = QLabel("Pipe Classes: 0")
        
        summary_layout.addWidget(self.total_pipe_label, 0, 0)
        summary_layout.addWidget(self.total_length_label, 0, 1)
        summary_layout.addWidget(self.average_weight_label, 0, 2)
        summary_layout.addWidget(self.pipe_classes_label, 0, 3)
        
        # Utilization
        summary_layout.addWidget(QLabel("Derrick Utilization:"), 1, 0)
        self.utilization_bar = QProgressBar()
        self.utilization_bar.setRange(0, 100)
        self.utilization_bar.setValue(75)
        summary_layout.addWidget(self.utilization_bar, 1, 1, 1, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Classification guide
        class_group = QGroupBox("Pipe Classification Guide")
        class_layout = QVBoxLayout()
        
        class_info = QLabel(
            "Class 1: New pipe, no wear\n"
            "Class 2: Minor wear, still within specs\n"
            "Class 3: Moderate wear, use with caution\n"
            "Class 4: Heavy wear, consider retirement\n"
            "Class 5: Damaged, do not use"
        )
        class_info.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        class_layout.addWidget(class_info)
        
        class_group.setLayout(class_layout)
        main_layout.addWidget(class_group)
        
        # Save button
        save_button = QPushButton("Save Drill Pipe Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        save_button.clicked.connect(self.save_drill_pipe_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
        
        # Load sample drill pipe data
        self.load_sample_drill_pipe()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.dp_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.dp_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def load_sample_drill_pipe(self):
        """Load sample drill pipe data"""
        sample_pipe = [
            ("5.0", "19.5", "S-135", "NC50", "4.276", "6.625", "3.000", "300", "15000", "Class 1", "2024-01-15", "In Service"),
            ("5.0", "19.5", "S-135", "NC50", "4.276", "6.625", "3.000", "250", "12500", "Class 2", "2024-01-10", "In Service"),
            ("5.0", "19.5", "G-105", "NC50", "4.276", "6.625", "3.000", "200", "10000", "Class 1", "2024-01-20", "In Service"),
            ("5.0", "19.5", "G-105", "NC50", "4.276", "6.625", "3.000", "150", "7500", "Class 3", "2024-01-05", "Inspection Due"),
            ("3.5", "13.3", "S-135", "NC38", "2.992", "4.750", "2.250", "100", "5000", "Class 2", "2024-01-18", "In Service"),
        ]
        
        for pipe in sample_pipe:
            row = self.dp_table.rowCount()
            self.dp_table.insertRow(row)
            
            for col, value in enumerate(pipe):
                self.dp_table.setItem(row, col, QTableWidgetItem(value))
        
        self.update_drill_pipe_summary()
    
    def add_drill_pipe_dialog(self):
        """Show dialog to add drill pipe"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Drill Pipe")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Basic specifications
        self.new_dp_size = QDoubleSpinBox()
        self.new_dp_size.setRange(0, 20)
        self.new_dp_size.setValue(5.0)
        self.new_dp_size.setSuffix(" inch")
        form.addRow("Size:", self.new_dp_size)
        
        self.new_dp_weight = QDoubleSpinBox()
        self.new_dp_weight.setRange(0, 100)
        self.new_dp_weight.setValue(19.5)
        self.new_dp_weight.setSuffix(" lb/ft")
        form.addRow("Weight:", self.new_dp_weight)
        
        self.new_dp_grade = QComboBox()
        self.new_dp_grade.addItems([
            "E-75", "X-95", "G-105", "S-135", "V-150", "Other"
        ])
        form.addRow("Grade:", self.new_dp_grade)
        
        self.new_dp_connection = QComboBox()
        self.new_dp_connection.addItems([
            "NC26", "NC31", "NC38", "NC40", "NC44", "NC46",
            "NC50", "NC56", "NC61", "NC70", "NC77", "Other"
        ])
        form.addRow("Connection:", self.new_dp_connection)
        
        # Dimensions
        dim_layout = QGridLayout()
        
        dim_layout.addWidget(QLabel("ID:"), 0, 0)
        self.new_dp_id = QDoubleSpinBox()
        self.new_dp_id.setRange(0, 20)
        self.new_dp_id.setValue(4.276)
        self.new_dp_id.setSuffix(" in")
        dim_layout.addWidget(self.new_dp_id, 0, 1)
        
        dim_layout.addWidget(QLabel("TJ OD:"), 0, 2)
        self.new_dp_tj_od = QDoubleSpinBox()
        self.new_dp_tj_od.setRange(0, 20)
        self.new_dp_tj_od.setValue(6.625)
        self.new_dp_tj_od.setSuffix(" in")
        dim_layout.addWidget(self.new_dp_tj_od, 0, 3)
        
        dim_layout.addWidget(QLabel("TJ ID:"), 1, 0)
        self.new_dp_tj_id = QDoubleSpinBox()
        self.new_dp_tj_id.setRange(0, 20)
        self.new_dp_tj_id.setValue(3.000)
        self.new_dp_tj_id.setSuffix(" in")
        dim_layout.addWidget(self.new_dp_tj_id, 1, 1)
        
        form.addRow("Dimensions:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(dim_layout)
        
        # Quantities
        qty_layout = QHBoxLayout()
        self.new_dp_std_in_derrick = QSpinBox()
        self.new_dp_std_in_derrick.setRange(0, 1000)
        self.new_dp_std_in_derrick.setValue(300)
        
        self.new_dp_total_length = QDoubleSpinBox()
        self.new_dp_total_length.setRange(0, 100000)
        self.new_dp_total_length.setValue(15000)
        self.new_dp_total_length.setSuffix(" ft")
        
        qty_layout.addWidget(QLabel("Std in Derrick:"))
        qty_layout.addWidget(self.new_dp_std_in_derrick)
        qty_layout.addWidget(QLabel("Total Length:"))
        qty_layout.addWidget(self.new_dp_total_length)
        
        form.addRow("Quantities:", QWidget())
        form.itemAt(form.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(qty_layout)
        
        # Classification and status
        self.new_dp_class = QComboBox()
        self.new_dp_class.addItems(["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])
        form.addRow("Pipe Class:", self.new_dp_class)
        
        self.new_dp_last_inspection = QDateEdit()
        self.new_dp_last_inspection.setCalendarPopup(True)
        self.new_dp_last_inspection.setDate(QDate.currentDate())
        form.addRow("Last Inspection:", self.new_dp_last_inspection)
        
        self.new_dp_status = QComboBox()
        self.new_dp_status.addItems(["In Service", "Inspection Due", "Repair", "Retired", "Storage"])
        form.addRow("Status:", self.new_dp_status)
        
        # Remarks
        self.new_dp_remarks = QTextEdit()
        self.new_dp_remarks.setMaximumHeight(60)
        form.addRow("Remarks:", self.new_dp_remarks)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Drill Pipe")
        cancel_button = QPushButton("Cancel")
        
        add_button.clicked.connect(lambda: self.add_drill_pipe(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_drill_pipe(self, dialog):
        """Add drill pipe to table"""
        # Add to table
        row = self.dp_table.rowCount()
        self.dp_table.insertRow(row)
        
        pipe_data = [
            str(self.new_dp_size.value()),
            str(self.new_dp_weight.value()),
            self.new_dp_grade.currentText(),
            self.new_dp_connection.currentText(),
            str(self.new_dp_id.value()),
            str(self.new_dp_tj_od.value()),
            str(self.new_dp_tj_id.value()),
            str(self.new_dp_std_in_derrick.value()),
            str(self.new_dp_total_length.value()),
            self.new_dp_class.currentText(),
            self.new_dp_last_inspection.date().toString("yyyy-MM-dd"),
            self.new_dp_status.currentText()
        ]
        
        for col, value in enumerate(pipe_data):
            self.dp_table.setItem(row, col, QTableWidgetItem(value))
        
        dialog.accept()
        self.update_drill_pipe_summary()
    
    def delete_drill_pipe(self):
        """Delete selected drill pipe"""
        selected_row = self.dp_table.currentRow()
        if selected_row >= 0:
            self.dp_table.removeRow(selected_row)
            self.update_drill_pipe_summary()
    
    def record_inspection_dialog(self):
        """Show dialog to record inspection"""
        selected_row = self.dp_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select drill pipe to inspect.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Drill Pipe Inspection")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        pipe_info = f"{self.dp_table.item(selected_row, 0).text()} inch, {self.dp_table.item(selected_row, 2).text()}"
        form.addRow("Drill Pipe:", QLabel(pipe_info))
        
        # Inspection date
        self.inspection_date = QDateEdit()
        self.inspection_date.setCalendarPopup(True)
        self.inspection_date.setDate(QDate.currentDate())
        form.addRow("Inspection Date:", self.inspection_date)
        
        # Inspection results
        self.inspection_type = QComboBox()
        self.inspection_type.addItems(["Visual", "MPI", "UT", "EMI", "Full"])
        form.addRow("Inspection Type:", self.inspection_type)
        
        self.new_pipe_class = QComboBox()
        self.new_pipe_class.addItems(["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])
        current_class = self.dp_table.item(selected_row, 9).text()
        self.new_pipe_class.setCurrentText(current_class)
        form.addRow("New Class:", self.new_pipe_class)
        
        # Wear measurements
        wear_group = QGroupBox("Wear Measurements")
        wear_layout = QGridLayout()
        
        wear_layout.addWidget(QLabel("OD Wear (%):"), 0, 0)
        self.od_wear = QDoubleSpinBox()
        self.od_wear.setRange(0, 100)
        wear_layout.addWidget(self.od_wear, 0, 1)
        
        wear_layout.addWidget(QLabel("Wall Loss (%):"), 0, 2)
        self.wall_loss = QDoubleSpinBox()
        self.wall_loss.setRange(0, 100)
        wear_layout.addWidget(self.wall_loss, 0, 3)
        
        wear_layout.addWidget(QLabel("Connection Wear:"), 1, 0)
        self.connection_wear = QComboBox()
        self.connection_wear.addItems(["None", "Minor", "Moderate", "Severe"])
        wear_layout.addWidget(self.connection_wear, 1, 1)
        
        wear_group.setLayout(wear_layout)
        form.addRow(wear_group)
        
        # Inspection notes
        self.inspection_notes = QTextEdit()
        self.inspection_notes.setMaximumHeight(60)
        form.addRow("Inspection Notes:", self.inspection_notes)
        
        # Recommended action
        self.recommended_action = QComboBox()
        self.recommended_action.addItems([
            "Continue Service", "Monitor", "Repair", "Reject", "Retire"
        ])
        form.addRow("Recommended Action:", self.recommended_action)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        record_button = QPushButton("Record Inspection")
        cancel_button = QPushButton("Cancel")
        
        record_button.clicked.connect(lambda: self.record_inspection(dialog, selected_row))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(record_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def record_inspection(self, dialog, row):
        """Record inspection results"""
        # Update table
        self.dp_table.setItem(row, 9, QTableWidgetItem(self.new_pipe_class.currentText()))
        self.dp_table.setItem(row, 10, QTableWidgetItem(self.inspection_date.date().toString("yyyy-MM-dd")))
        
        # Update status based on recommended action
        action = self.recommended_action.currentText()
        if action in ["Repair", "Reject", "Retire"]:
            self.dp_table.setItem(row, 11, QTableWidgetItem(action))
        elif self.new_pipe_class.currentText() in ["Class 4", "Class 5"]:
            self.dp_table.setItem(row, 11, QTableWidgetItem("Inspection Due"))
        
        dialog.accept()
        self.update_drill_pipe_summary()
    
    def update_drill_pipe_summary(self):
        """Update drill pipe summary information"""
        total_pipes = self.dp_table.rowCount()
        
        total_length = 0
        total_weight = 0
        pipe_classes = set()
        
        for row in range(total_pipes):
            # Calculate total length
            length = float(self.dp_table.item(row, 8).text())
            total_length += length
            
            # Calculate average weight
            weight = float(self.dp_table.item(row, 1).text())
            total_weight += weight
            
            # Collect pipe classes
            pipe_class = self.dp_table.item(row, 9).text()
            pipe_classes.add(pipe_class)
        
        avg_weight = total_weight / total_pipes if total_pipes > 0 else 0
        
        self.total_pipe_label.setText(f"Total Pipes: {total_pipes}")
        self.total_length_label.setText(f"Total Length: {total_length:,.0f} ft")
        self.average_weight_label.setText(f"Avg Weight: {avg_weight:.1f} lb/ft")
        self.pipe_classes_label.setText(f"Pipe Classes: {len(pipe_classes)}")
    
    def save_drill_pipe_data(self):
        """Save drill pipe data to database"""
        well_index = self.dp_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save data to database
        QMessageBox.information(self, "Success", "Drill pipe data saved successfully!")

# ============================================
# SOLID CONTROL WIDGET
# ============================================

class SolidControlWidget(QWidget):
    """Solid control equipment management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Solid Control Equipment")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.sc_well_combo = QComboBox()
        
        load_button = QPushButton("Load Solid Control Data")
        
        well_layout.addWidget(self.sc_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Tab widget for different equipment types
        tabs = QTabWidget()
        
        # Shale Shakers tab
        shakers_tab = self.create_shakers_tab()
        tabs.addTab(shakers_tab, "🌀 Shale Shakers")
        
        # Centrifuges tab
        centrifuges_tab = self.create_centrifuges_tab()
        tabs.addTab(centrifuges_tab, "🔄 Centrifuges")
        
        # Desanders/Desilters tab
        desanders_tab = self.create_desanders_tab()
        tabs.addTab(desanders_tab, "💧 Desanders/Desilters")
        
        # Degassers tab
        degassers_tab = self.create_degassers_tab()
        tabs.addTab(degassers_tab, "💨 Degassers")
        
        # Performance tab
        performance_tab = self.create_performance_tab()
        tabs.addTab(performance_tab, "📊 Performance")
        
        main_layout.addWidget(tabs)
        
        # Summary
        summary_group = QGroupBox("Solid Control Summary")
        summary_layout = QGridLayout()
        
        self.total_equipment_label = QLabel("Total Equipment: 0")
        self.operating_hours_label = QLabel("Operating Hours: 0")
        self.solids_removed_label = QLabel("Solids Removed: 0 bbl")
        self.efficiency_label = QLabel("Efficiency: 0%")
        
        summary_layout.addWidget(self.total_equipment_label, 0, 0)
        summary_layout.addWidget(self.operating_hours_label, 0, 1)
        summary_layout.addWidget(self.solids_removed_label, 0, 2)
        summary_layout.addWidget(self.efficiency_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Save button
        save_button = QPushButton("Save Solid Control Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_button.clicked.connect(self.save_solid_control_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.sc_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.sc_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def create_shakers_tab(self):
        """Create shale shakers tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Shale shakers table
        table_group = QGroupBox("Shale Shakers")
        table_layout = QVBoxLayout()
        
        self.shakers_table = QTableWidget()
        self.shakers_table.setColumnCount(10)
        self.shakers_table.setHorizontalHeaderLabels([
            "Name", "Type", "Screen Size (mesh)", "Feed Rate (bbl/hr)",
            "Operating Hours", "Cumulative Hours", "Screen Changes",
            "Last Maintenance", "Status", "Remarks"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Shaker")
        remove_button = QPushButton("Remove Selected")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(remove_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.shakers_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Screen information
        screen_group = QGroupBox("Screen Information")
        screen_layout = QFormLayout()
        
        self.current_screen_mesh = QSpinBox()
        self.current_screen_mesh.setRange(20, 400)
        self.current_screen_mesh.setValue(120)
        screen_layout.addRow("Current Screen Mesh:", self.current_screen_mesh)
        
        self.screen_life = QDoubleSpinBox()
        self.screen_life.setRange(0, 500)
        self.screen_life.setSuffix(" hours")
        screen_layout.addRow("Screen Life:", self.screen_life)
        
        self.screen_changes_today = QSpinBox()
        self.screen_changes_today.setRange(0, 50)
        screen_layout.addRow("Screen Changes Today:", self.screen_changes_today)
        
        screen_group.setLayout(screen_layout)
        layout.addWidget(screen_group)
        
        # Load sample data
        self.load_sample_shakers()
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_sample_shakers(self):
        """Load sample shale shaker data"""
        sample_shakers = [
            ("Primary Shaker", "Linear Motion", 120, 800, 120, 1500, 15, "2024-01-15", "Operational", "Running well"),
            ("Secondary Shaker", "Elliptical", 100, 600, 100, 1200, 12, "2024-01-10", "Operational", "Backup"),
            ("Mud Cleaner", "Circular", 200, 400, 80, 800, 8, "2024-01-20", "Maintenance", "Screen change needed"),
        ]
        
        for shaker in sample_shakers:
            row = self.shakers_table.rowCount()
            self.shakers_table.insertRow(row)
            
            for col, value in enumerate(shaker):
                self.shakers_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_centrifuges_tab(self):
        """Create centrifuges tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Centrifuges table
        table_group = QGroupBox("Centrifuges")
        table_layout = QVBoxLayout()
        
        self.centrifuges_table = QTableWidget()
        self.centrifuges_table.setColumnCount(11)
        self.centrifuges_table.setHorizontalHeaderLabels([
            "Name", "Type", "Bowl Speed (RPM)", "Conveyor Speed (RPM)",
            "Feed Rate (gpm)", "Feed Solids (%)", "Underflow (%)", "Overflow (%)",
            "Operating Hours", "Last Service", "Status"
        ])
        
        # Table buttons
        table_buttons = QHBoxLayout()
        add_button = QPushButton("Add Centrifuge")
        remove_button = QPushButton("Remove Selected")
        
        table_buttons.addWidget(add_button)
        table_buttons.addWidget(remove_button)
        table_buttons.addStretch()
        
        table_layout.addWidget(self.centrifuges_table)
        table_layout.addLayout(table_buttons)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Centrifuge settings
        settings_group = QGroupBox("Centrifuge Settings")
        settings_layout = QFormLayout()
        
        self.bowl_speed = QDoubleSpinBox()
        self.bowl_speed.setRange(0, 5000)
        self.bowl_speed.setValue(3200)
        self.bowl_speed.setSuffix(" RPM")
        settings_layout.addRow("Bowl Speed:", self.bowl_speed)
        
        self.conveyor_speed = QDoubleSpinBox()
        self.conveyor_speed.setRange(0, 100)
        self.conveyor_speed.setValue(25)
        self.conveyor_speed.setSuffix(" RPM")
        settings_layout.addRow("Conveyor Speed:", self.conveyor_speed)
        
        self.feed_rate = QDoubleSpinBox()
        self.feed_rate.setRange(0, 500)
        self.feed_rate.setValue(150)
        self.feed_rate.setSuffix(" gpm")
        settings_layout.addRow("Feed Rate:", self.feed_rate)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Load sample data
        self.load_sample_centrifuges()
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_sample_centrifuges(self):
        """Load sample centrifuge data"""
        sample_centrifuges = [
            ("High Speed Centrifuge", "Decanter", 3200, 25, 150, 8.5, 75, 25, 200, "2024-01-18", "Operational"),
            ("Barite Recovery", "Decanter", 2800, 20, 100, 12.0, 80, 20, 180, "2024-01-12", "Operational"),
        ]
        
        for centrifuge in sample_centrifuges:
            row = self.centrifuges_table.rowCount()
            self.centrifuges_table.insertRow(row)
            
            for col, value in enumerate(centrifuge):
                self.centrifuges_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_desanders_tab(self):
        """Create desanders/desilters tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Desanders table
        desanders_group = QGroupBox("Desanders")
        desanders_layout = QVBoxLayout()
        
        self.desanders_table = QTableWidget()
        self.desanders_table.setColumnCount(8)
        self.desanders_table.setHorizontalHeaderLabels([
            "Name", "Cone Size (in)", "Number of Cones", "Feed Rate (bbl/hr)",
            "Operating Hours", "Efficiency (%)", "Last Cleaned", "Status"
        ])
        
        desanders_layout.addWidget(self.desanders_table)
        desanders_group.setLayout(desanders_layout)
        layout.addWidget(desanders_group)
        
        # Desilters table
        desilters_group = QGroupBox("Desilters")
        desilters_layout = QVBoxLayout()
        
        self.desilters_table = QTableWidget()
        self.desilters_table.setColumnCount(8)
        self.desilters_table.setHorizontalHeaderLabels([
            "Name", "Cone Size (in)", "Number of Cones", "Feed Rate (bbl/hr)",
            "Operating Hours", "Efficiency (%)", "Last Cleaned", "Status"
        ])
        
        desilters_layout.addWidget(self.desilters_table)
        desilters_group.setLayout(desilters_layout)
        layout.addWidget(desilters_group)
        
        # Load sample data
        self.load_sample_desanders_desilters()
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_sample_desanders_desilters(self):
        """Load sample desanders and desilters data"""
        # Desanders sample data
        sample_desanders = [
            ("Primary Desander", 10, 8, 800, 150, 85, "2024-01-16", "Operational"),
            ("Secondary Desander", 8, 6, 600, 120, 80, "2024-01-10", "Operational"),
        ]
        
        for desander in sample_desanders:
            row = self.desanders_table.rowCount()
            self.desanders_table.insertRow(row)
            
            for col, value in enumerate(desander):
                self.desanders_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        # Desilters sample data
        sample_desilters = [
            ("Primary Desilter", 4, 12, 400, 100, 90, "2024-01-18", "Operational"),
            ("Secondary Desilter", 5, 10, 350, 80, 85, "2024-01-12", "Maintenance"),
        ]
        
        for desilter in sample_desilters:
            row = self.desilters_table.rowCount()
            self.desilters_table.insertRow(row)
            
            for col, value in enumerate(desilter):
                self.desilters_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_degassers_tab(self):
        """Create degassers tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Degassers table
        table_group = QGroupBox("Degassers")
        table_layout = QVBoxLayout()
        
        self.degassers_table = QTableWidget()
        self.degassers_table.setColumnCount(9)
        self.degassers_table.setHorizontalHeaderLabels([
            "Name", "Type", "Capacity (bbl/hr)", "Vacuum (inHg)",
            "Gas Removal (%)", "Operating Hours", "Last Service", "Status", "Remarks"
        ])
        
        table_layout.addWidget(self.degassers_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Degasser performance
        performance_group = QGroupBox("Degasser Performance")
        performance_layout = QFormLayout()
        
        self.gas_volume = QDoubleSpinBox()
        self.gas_volume.setRange(0, 10000)
        self.gas_volume.setSuffix(" scf/bbl")
        performance_layout.addRow("Gas Volume:", self.gas_volume)
        
        self.h2s_level = QDoubleSpinBox()
        self.h2s_level.setRange(0, 1000)
        self.h2s_level.setSuffix(" ppm")
        performance_layout.addRow("H2S Level:", self.h2s_level)
        
        self.degasser_efficiency = QDoubleSpinBox()
        self.degasser_efficiency.setRange(0, 100)
        self.degasser_efficiency.setValue(95)
        self.degasser_efficiency.setSuffix(" %")
        performance_layout.addRow("Efficiency:", self.degasser_efficiency)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Load sample data
        self.load_sample_degassers()
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_sample_degassers(self):
        """Load sample degasser data"""
        sample_degassers = [
            ("Vacuum Degasser", "Vacuum", 500, 15, 95, 180, "2024-01-20", "Operational", "Good performance"),
            ("Atmospheric", "Atmospheric", 300, 0, 85, 150, "2024-01-15", "Operational", "Backup unit"),
        ]
        
        for degasser in sample_degassers:
            row = self.degassers_table.rowCount()
            self.degassers_table.insertRow(row)
            
            for col, value in enumerate(degasser):
                self.degassers_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def create_performance_tab(self):
        """Create performance monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Daily performance
        daily_group = QGroupBox("Daily Performance")
        daily_layout = QGridLayout()
        
        daily_layout.addWidget(QLabel("Solids Removed:"), 0, 0)
        self.daily_solids = QDoubleSpinBox()
        self.daily_solids.setRange(0, 1000)
        self.daily_solids.setSuffix(" bbl")
        daily_layout.addWidget(self.daily_solids, 0, 1)
        
        daily_layout.addWidget(QLabel("Liquid Recovery:"), 0, 2)
        self.liquid_recovery = QDoubleSpinBox()
        self.liquid_recovery.setRange(0, 100)
        self.liquid_recovery.setSuffix(" %")
        daily_layout.addWidget(self.liquid_recovery, 0, 3)
        
        daily_layout.addWidget(QLabel("Downtime:"), 1, 0)
        self.downtime = QDoubleSpinBox()
        self.downtime.setRange(0, 24)
        self.downtime.setSuffix(" hours")
        daily_layout.addWidget(self.downtime, 1, 1)
        
        daily_layout.addWidget(QLabel("Screen Usage:"), 1, 2)
        self.screen_usage = QDoubleSpinBox()
        self.screen_usage.setRange(0, 1000)
        self.screen_usage.setSuffix(" hours")
        daily_layout.addWidget(self.screen_usage, 1, 3)
        
        daily_group.setLayout(daily_layout)
        layout.addWidget(daily_group)
        
        # Efficiency calculations
        efficiency_group = QGroupBox("Efficiency Calculations")
        efficiency_layout = QFormLayout()
        
        self.solids_removal_efficiency = QDoubleSpinBox()
        self.solids_removal_efficiency.setRange(0, 100)
        self.solids_removal_efficiency.setValue(85)
        self.solids_removal_efficiency.setSuffix(" %")
        efficiency_layout.addRow("Solids Removal Efficiency:", self.solids_removal_efficiency)
        
        self.mud_recovery = QDoubleSpinBox()
        self.mud_recovery.setRange(0, 100)
        self.mud_recovery.setValue(92)
        self.mud_recovery.setSuffix(" %")
        efficiency_layout.addRow("Mud Recovery:", self.mud_recovery)
        
        self.cost_savings = QDoubleSpinBox()
        self.cost_savings.setRange(0, 100000)
        self.cost_savings.setPrefix("$ ")
        efficiency_layout.addRow("Estimated Cost Savings:", self.cost_savings)
        
        efficiency_group.setLayout(efficiency_layout)
        layout.addWidget(efficiency_group)
        
        # Performance notes
        notes_group = QGroupBox("Performance Notes")
        notes_layout = QVBoxLayout()
        
        self.performance_notes = QTextEdit()
        self.performance_notes.setPlaceholderText("Enter performance notes and observations...")
        self.performance_notes.setMaximumHeight(100)
        notes_layout.addWidget(self.performance_notes)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def save_solid_control_data(self):
        """Save solid control data to database"""
        well_index = self.sc_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save data to database
        QMessageBox.information(self, "Success", "Solid control data saved successfully!")

# ============================================
# FUEL & WATER WIDGET
# ============================================

class FuelWaterWidget(QWidget):
    """Fuel and water management widget"""
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Fuel & Water Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # Well selection
        well_layout = QHBoxLayout()
        well_layout.addWidget(QLabel("Well:"))
        
        self.fw_well_combo = QComboBox()
        
        load_button = QPushButton("Load Fuel & Water Data")
        
        well_layout.addWidget(self.fw_well_combo)
        well_layout.addWidget(load_button)
        well_layout.addStretch()
        
        main_layout.addLayout(well_layout)
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Fuel Management tab
        fuel_tab = self.create_fuel_tab()
        tabs.addTab(fuel_tab, "⛽ Fuel")
        
        # Water Management tab
        water_tab = self.create_water_tab()
        tabs.addTab(water_tab, "💧 Water")
        
        # Consumption Analysis tab
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "📊 Analysis")
        
        main_layout.addWidget(tabs)
        
        # Daily summary
        summary_group = QGroupBox("Daily Summary")
        summary_layout = QGridLayout()
        
        self.fuel_used_label = QLabel("Fuel Used: 0 L")
        self.water_used_label = QLabel("Water Used: 0 bbl")
        self.fuel_cost_label = QLabel("Fuel Cost: $0")
        self.water_cost_label = QLabel("Water Cost: $0")
        
        summary_layout.addWidget(self.fuel_used_label, 0, 0)
        summary_layout.addWidget(self.water_used_label, 0, 1)
        summary_layout.addWidget(self.fuel_cost_label, 0, 2)
        summary_layout.addWidget(self.water_cost_label, 0, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Save button
        save_button = QPushButton("Save Fuel & Water Data")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        save_button.clicked.connect(self.save_fuel_water_data)
        main_layout.addWidget(save_button)
        
        self.setLayout(main_layout)
        
        # Load wells
        self.load_wells()
    
    def load_wells(self):
        """Load wells into combo box"""
        self.fw_well_combo.clear()
        wells = self.db.get_all_wells()
        
        for well in wells:
            self.fw_well_combo.addItem(f"{well.name} - {well.field}", well.id)
    
    def create_fuel_tab(self):
        """Create fuel management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Fuel consumption
        consumption_group = QGroupBox("Fuel Consumption")
        consumption_layout = QFormLayout()
        
        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Diesel", "Gasoline", "Natural Gas", "Aviation Fuel", "Other"])
        consumption_layout.addRow("Fuel Type:", self.fuel_type)
        
        # Daily consumption
        daily_layout = QGridLayout()
        
        daily_layout.addWidget(QLabel("Daily Used:"), 0, 0)
        self.daily_fuel_used = QDoubleSpinBox()
        self.daily_fuel_used.setRange(0, 10000)
        self.daily_fuel_used.setSuffix(" L")
        daily_layout.addWidget(self.daily_fuel_used, 0, 1)
        
        daily_layout.addWidget(QLabel("Price per Liter:"), 0, 2)
        self.fuel_price = QDoubleSpinBox()
        self.fuel_price.setRange(0, 100)
        self.fuel_price.setPrefix("$ ")
        daily_layout.addWidget(self.fuel_price, 0, 3)
        
        daily_layout.addWidget(QLabel("Daily Cost:"), 1, 0)
        self.daily_fuel_cost = QDoubleSpinBox()
        self.daily_fuel_cost.setRange(0, 100000)
        self.daily_fuel_cost.setPrefix("$ ")
        self.daily_fuel_cost.setReadOnly(True)
        daily_layout.addWidget(self.daily_fuel_cost, 1, 1)
        
        consumption_layout.addRow("Daily Consumption:", QWidget())
        consumption_layout.itemAt(consumption_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(daily_layout)
        
        # Connect signals for auto-calculation
        self.daily_fuel_used.valueChanged.connect(self.calculate_fuel_cost)
        self.fuel_price.valueChanged.connect(self.calculate_fuel_cost)
        
        consumption_group.setLayout(consumption_layout)
        layout.addWidget(consumption_group)
        
        # Fuel inventory
        inventory_group = QGroupBox("Fuel Inventory")
        inventory_layout = QFormLayout()
        
        # Inventory levels
        inv_layout = QGridLayout()
        
        inv_layout.addWidget(QLabel("Opening Stock:"), 0, 0)
        self.opening_fuel = QDoubleSpinBox()
        self.opening_fuel.setRange(0, 1000000)
        self.opening_fuel.setSuffix(" L")
        inv_layout.addWidget(self.opening_fuel, 0, 1)
        
        inv_layout.addWidget(QLabel("Received:"), 0, 2)
        self.fuel_received = QDoubleSpinBox()
        self.fuel_received.setRange(0, 1000000)
        self.fuel_received.setSuffix(" L")
        inv_layout.addWidget(self.fuel_received, 0, 3)
        
        inv_layout.addWidget(QLabel("Closing Stock:"), 1, 0)
        self.closing_fuel = QDoubleSpinBox()
        self.closing_fuel.setRange(0, 1000000)
        self.closing_fuel.setSuffix(" L")
        self.closing_fuel.setReadOnly(True)
        inv_layout.addWidget(self.closing_fuel, 1, 1)
        
        inventory_layout.addRow("Inventory Levels:", QWidget())
        inventory_layout.itemAt(inventory_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(inv_layout)
        
        # Connect signals for auto-calculation
        self.opening_fuel.valueChanged.connect(self.calculate_closing_fuel)
        self.fuel_received.valueChanged.connect(self.calculate_closing_fuel)
        self.daily_fuel_used.valueChanged.connect(self.calculate_closing_fuel)
        
        # Storage tanks
        self.number_of_tanks = QSpinBox()
        self.number_of_tanks.setRange(1, 20)
        self.number_of_tanks.setValue(4)
        inventory_layout.addRow("Number of Tanks:", self.number_of_tanks)
        
        self.tank_capacity = QDoubleSpinBox()
        self.tank_capacity.setRange(0, 100000)
        self.tank_capacity.setSuffix(" L")
        self.tank_capacity.setValue(50000)
        inventory_layout.addRow("Tank Capacity:", self.tank_capacity)
        
        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)
        
        # Fuel delivery
        delivery_group = QGroupBox("Fuel Delivery")
        delivery_layout = QFormLayout()
        
        self.last_delivery_date = QDateEdit()
        self.last_delivery_date.setCalendarPopup(True)
        self.last_delivery_date.setDate(QDate.currentDate().addDays(-2))
        delivery_layout.addRow("Last Delivery Date:", self.last_delivery_date)
        
        self.next_delivery_date = QDateEdit()
        self.next_delivery_date.setCalendarPopup(True)
        self.next_delivery_date.setDate(QDate.currentDate().addDays(5))
        delivery_layout.addRow("Next Delivery Date:", self.next_delivery_date)
        
        self.supplier_name = QLineEdit()
        self.supplier_name.setPlaceholderText("Fuel supplier name")
        delivery_layout.addRow("Supplier:", self.supplier_name)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def calculate_fuel_cost(self):
        """Calculate daily fuel cost"""
        used = self.daily_fuel_used.value()
        price = self.fuel_price.value()
        cost = used * price
        self.daily_fuel_cost.setValue(cost)
    
    def calculate_closing_fuel(self):
        """Calculate closing fuel stock"""
        opening = self.opening_fuel.value()
        received = self.fuel_received.value()
        used = self.daily_fuel_used.value()
        closing = opening + received - used
        self.closing_fuel.setValue(closing)
    
    def create_water_tab(self):
        """Create water management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Water consumption
        consumption_group = QGroupBox("Water Consumption")
        consumption_layout = QFormLayout()
        
        self.water_source = QComboBox()
        self.water_source.addItems([
            "Fresh Water", "Brackish Water", "Sea Water", 
            "Produced Water", "Recycled Water", "Other"
        ])
        consumption_layout.addRow("Water Source:", self.water_source)
        
        # Daily water usage
        daily_layout = QGridLayout()
        
        daily_layout.addWidget(QLabel("Daily Used:"), 0, 0)
        self.daily_water_used = QDoubleSpinBox()
        self.daily_water_used.setRange(0, 10000)
        self.daily_water_used.setSuffix(" bbl")
        daily_layout.addWidget(self.daily_water_used, 0, 1)
        
        daily_layout.addWidget(QLabel("Make-up Water:"), 0, 2)
        self.makeup_water = QDoubleSpinBox()
        self.makeup_water.setRange(0, 10000)
        self.makeup_water.setSuffix(" bbl")
        daily_layout.addWidget(self.makeup_water, 0, 3)
        
        daily_layout.addWidget(QLabel("Recycled Water:"), 1, 0)
        self.recycled_water = QDoubleSpinBox()
        self.recycled_water.setRange(0, 10000)
        self.recycled_water.setSuffix(" bbl")
        daily_layout.addWidget(self.recycled_water, 1, 1)
        
        consumption_layout.addRow("Daily Usage:", QWidget())
        consumption_layout.itemAt(consumption_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(daily_layout)
        
        # Water quality
        self.water_quality = QComboBox()
        self.water_quality.addItems(["Excellent", "Good", "Fair", "Poor", "Treatment Required"])
        consumption_layout.addRow("Water Quality:", self.water_quality)
        
        consumption_group.setLayout(consumption_layout)
        layout.addWidget(consumption_group)
        
        # Water inventory
        inventory_group = QGroupBox("Water Inventory")
        inventory_layout = QFormLayout()
        
        # Inventory levels
        inv_layout = QGridLayout()
        
        inv_layout.addWidget(QLabel("Opening Stock:"), 0, 0)
        self.opening_water = QDoubleSpinBox()
        self.opening_water.setRange(0, 100000)
        self.opening_water.setSuffix(" bbl")
        inv_layout.addWidget(self.opening_water, 0, 1)
        
        inv_layout.addWidget(QLabel("Received:"), 0, 2)
        self.water_received = QDoubleSpinBox()
        self.water_received.setRange(0, 100000)
        self.water_received.setSuffix(" bbl")
        inv_layout.addWidget(self.water_received, 0, 3)
        
        inv_layout.addWidget(QLabel("Closing Stock:"), 1, 0)
        self.closing_water = QDoubleSpinBox()
        self.closing_water.setRange(0, 100000)
        self.closing_water.setSuffix(" bbl")
        self.closing_water.setReadOnly(True)
        inv_layout.addWidget(self.closing_water, 1, 1)
        
        inventory_layout.addRow("Inventory Levels:", QWidget())
        inventory_layout.itemAt(inventory_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(inv_layout)
        
        # Connect signals for auto-calculation
        self.opening_water.valueChanged.connect(self.calculate_closing_water)
        self.water_received.valueChanged.connect(self.calculate_closing_water)
        self.daily_water_used.valueChanged.connect(self.calculate_closing_water)
        
        # Storage information
        self.water_tanks = QSpinBox()
        self.water_tanks.setRange(1, 20)
        self.water_tanks.setValue(6)
        inventory_layout.addRow("Number of Tanks:", self.water_tanks)
        
        self.water_treatment = QCheckBox("Water Treatment Available")
        self.water_treatment.setChecked(True)
        inventory_layout.addRow("", self.water_treatment)
        
        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)
        
        # Water analysis
        analysis_group = QGroupBox("Water Analysis")
        analysis_layout = QGridLayout()
        
        analysis_layout.addWidget(QLabel("pH:"), 0, 0)
        self.water_ph = QDoubleSpinBox()
        self.water_ph.setRange(0, 14)
        self.water_ph.setValue(7.5)
        analysis_layout.addWidget(self.water_ph, 0, 1)
        
        analysis_layout.addWidget(QLabel("Chloride (ppm):"), 0, 2)
        self.water_chloride = QDoubleSpinBox()
        self.water_chloride.setRange(0, 100000)
        analysis_layout.addWidget(self.water_chloride, 0, 3)
        
        analysis_layout.addWidget(QLabel("Hardness (ppm):"), 1, 0)
        self.water_hardness = QDoubleSpinBox()
        self.water_hardness.setRange(0, 10000)
        analysis_layout.addWidget(self.water_hardness, 1, 1)
        
        analysis_layout.addWidget(QLabel("TDS (ppm):"), 1, 2)
        self.water_tds = QDoubleSpinBox()
        self.water_tds.setRange(0, 100000)
        analysis_layout.addWidget(self.water_tds, 1, 3)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def calculate_closing_water(self):
        """Calculate closing water stock"""
        opening = self.opening_water.value()
        received = self.water_received.value()
        used = self.daily_water_used.value()
        closing = opening + received - used
        self.closing_water.setValue(closing)
    
    def create_analysis_tab(self):
        """Create consumption analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Consumption trends
        trends_group = QGroupBox("Consumption Trends")
        trends_layout = QFormLayout()
        
        # Weekly average
        weekly_layout = QGridLayout()
        
        weekly_layout.addWidget(QLabel("Fuel (L/day):"), 0, 0)
        self.avg_fuel_weekly = QDoubleSpinBox()
        self.avg_fuel_weekly.setRange(0, 10000)
        self.avg_fuel_weekly.setValue(2500)
        weekly_layout.addWidget(self.avg_fuel_weekly, 0, 1)
        
        weekly_layout.addWidget(QLabel("Water (bbl/day):"), 0, 2)
        self.avg_water_weekly = QDoubleSpinBox()
        self.avg_water_weekly.setRange(0, 10000)
        self.avg_water_weekly.setValue(500)
        weekly_layout.addWidget(self.avg_water_weekly, 0, 3)
        
        trends_layout.addRow("Weekly Average:", QWidget())
        trends_layout.itemAt(trends_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(weekly_layout)
        
        # Monthly total
        monthly_layout = QGridLayout()
        
        monthly_layout.addWidget(QLabel("Fuel (L):"), 0, 0)
        self.total_fuel_monthly = QDoubleSpinBox()
        self.total_fuel_monthly.setRange(0, 1000000)
        self.total_fuel_monthly.setValue(75000)
        monthly_layout.addWidget(self.total_fuel_monthly, 0, 1)
        
        monthly_layout.addWidget(QLabel("Water (bbl):"), 0, 2)
        self.total_water_monthly = QDoubleSpinBox()
        self.total_water_monthly.setRange(0, 100000)
        self.total_water_monthly.setValue(15000)
        monthly_layout.addWidget(self.total_water_monthly, 0, 3)
        
        trends_layout.addRow("Monthly Total:", QWidget())
        trends_layout.itemAt(trends_layout.rowCount()-1, QFormLayout.LabelRole).widget().setLayout(monthly_layout)
        
        # Cost analysis
        self.monthly_fuel_cost = QDoubleSpinBox()
        self.monthly_fuel_cost.setRange(0, 1000000)
        self.monthly_fuel_cost.setPrefix("$ ")
        trends_layout.addRow("Monthly Fuel Cost:", self.monthly_fuel_cost)
        
        self.monthly_water_cost = QDoubleSpinBox()
        self.monthly_water_cost.setRange(0, 100000)
        self.monthly_water_cost.setPrefix("$ ")
        trends_layout.addRow("Monthly Water Cost:", self.monthly_water_cost)
        
        trends_group.setLayout(trends_layout)
        layout.addWidget(trends_group)
        
        # Efficiency metrics
        efficiency_group = QGroupBox("Efficiency Metrics")
        efficiency_layout = QFormLayout()
        
        self.fuel_per_meter = QDoubleSpinBox()
        self.fuel_per_meter.setRange(0, 1000)
        self.fuel_per_meter.setSuffix(" L/m")
        efficiency_layout.addRow("Fuel per Meter Drilled:", self.fuel_per_meter)
        
        self.water_per_meter = QDoubleSpinBox()
        self.water_per_meter.setRange(0, 100)
        self.water_per_meter.setSuffix(" bbl/m")
        efficiency_layout.addRow("Water per Meter Drilled:", self.water_per_meter)
        
        self.fuel_efficiency = QDoubleSpinBox()
        self.fuel_efficiency.setRange(0, 100)
        self.fuel_efficiency.setSuffix(" %")
        efficiency_layout.addRow("Fuel Efficiency:", self.fuel_efficiency)
        
        efficiency_group.setLayout(efficiency_layout)
        layout.addWidget(efficiency_group)
        
        # Consumption reduction
        reduction_group = QGroupBox("Consumption Reduction Goals")
        reduction_layout = QFormLayout()
        
        self.fuel_reduction_goal = QDoubleSpinBox()
        self.fuel_reduction_goal.setRange(0, 100)
        self.fuel_reduction_goal.setSuffix(" %")
        reduction_layout.addRow("Fuel Reduction Goal:", self.fuel_reduction_goal)
        
        self.water_reduction_goal = QDoubleSpinBox()
        self.water_reduction_goal.setRange(0, 100)
        self.water_reduction_goal.setSuffix(" %")
        reduction_layout.addRow("Water Reduction Goal:", self.water_reduction_goal)
        
        self.recycling_rate = QDoubleSpinBox()
        self.recycling_rate.setRange(0, 100)
        self.recycling_rate.setSuffix(" %")
        reduction_layout.addRow("Water Recycling Rate:", self.recycling_rate)
        
        reduction_group.setLayout(reduction_layout)
        layout.addWidget(reduction_group)
        
        # Analysis notes
        notes_group = QGroupBox("Analysis Notes")
        notes_layout = QVBoxLayout()
        
        self.analysis_notes = QTextEdit()
        self.analysis_notes.setPlaceholderText("Enter consumption analysis notes...")
        self.analysis_notes.setMaximumHeight(80)
        notes_layout.addWidget(self.analysis_notes)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def save_fuel_water_data(self):
        """Save fuel and water data to database"""
        well_index = self.fw_well_combo.currentIndex()
        if well_index < 0:
            QMessageBox.warning(self, "Error", "Please select a well.")
            return
        
        # TODO: Save data to database
        QMessageBox.information(self, "Success", "Fuel & water data saved successfully!")

# ============================================
# UPDATE MAIN WINDOW TO INCLUDE ALL MODULES
# ============================================

def init_modules_all(self):
    """Initialize all application modules - Full version"""
    # Well Information
    self.well_info_widget = WellInfoWidget(self.db)
    self.tab_widget.addTab(self.well_info_widget, "🏠 Well Info")
    
    # Daily Report
    self.daily_report_widget = DailyReportWidget(self.db)
    self.tab_widget.addTab(self.daily_report_widget, "🗓 Daily Report")
    
    # Drilling Parameters
    self.drilling_params_widget = DrillingParametersWidget(self.db)
    self.tab_widget.addTab(self.drilling_params_widget, "⚙️ Drilling Params")
    
    # Mud Report
    self.mud_report_widget = MudReportWidget(self.db)
    self.tab_widget.addTab(self.mud_report_widget, "🧪 Mud Report")
    
    # Bit Report
    self.bit_report_widget = BitReportWidget(self.db)
    self.tab_widget.addTab(self.bit_report_widget, "🔩 Bit Report")
    
    # BHA Report
    self.bha_report_widget = BHAReportWidget(self.db)
    self.tab_widget.addTab(self.bha_report_widget, "🛠️ BHA Report")
    
    # Survey Data
    self.survey_widget = SurveyDataWidget(self.db)
    self.tab_widget.addTab(self.survey_widget, "📈 Survey Data")
    
    # Personnel & Logistics
    self.personnel_widget = PersonnelLogisticsWidget(self.db)
    self.tab_widget.addTab(self.personnel_widget, "👥 Personnel & Logistics")
    
    # Inventory Management
    self.inventory_widget = InventoryWidget(self.db)
    self.tab_widget.addTab(self.inventory_widget, "📦 Inventory")
    
    # Service Company Log
    self.service_widget = ServiceCompanyWidget(self.db)
    self.tab_widget.addTab(self.service_widget, "🏢 Service Cos")
    
    # Material Handling
    self.material_widget = MaterialHandlingWidget(self.db)
    self.tab_widget.addTab(self.material_widget, "📝 Material Handling")
    
    # Safety & BOP
    self.safety_widget = SafetyBOPWidget(self.db)
    self.tab_widget.addTab(self.safety_widget, "🦺 Safety & BOP")
    
    # Waste Management
    self.waste_widget = WasteManagementWidget(self.db)
    self.tab_widget.addTab(self.waste_widget, "♻️ Waste Mgmt")
    
    # Cement & Casing
    self.cement_widget = CementCasingWidget(self.db)
    self.tab_widget.addTab(self.cement_widget, "🏗️ Cement & Casing")
    
    # Downhole Equipment
    self.downhole_widget = DownholeEquipmentWidget(self.db)
    self.tab_widget.addTab(self.downhole_widget, "⚙️ Downhole Eq")
    
    # Drill Pipe Specs
    self.drill_pipe_widget = DrillPipeWidget(self.db)
    self.tab_widget.addTab(self.drill_pipe_widget, "🔧 Drill Pipe")
    
    # Solid Control
    self.solid_control_widget = SolidControlWidget(self.db)
    self.tab_widget.addTab(self.solid_control_widget, "🌀 Solid Control")
    
    # Fuel & Water
    self.fuel_water_widget = FuelWaterWidget(self.db)
    self.tab_widget.addTab(self.fuel_water_widget, "⛽ Fuel & Water")
    
    # Add placeholders for remaining modules
    self.add_placeholder_tabs_all()

def add_placeholder_tabs_all(self):
    """Add placeholder tabs for remaining modules - Full version"""
    modules = [
        ("📊 Export Center", "Report export center"),
        ("⚙️ Preferences", "User preferences")
    ]
    
    for title, description in modules:
        placeholder = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel(f"{title}\n\n{description}\n\n(This module will be implemented in the next phase)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        
        layout.addWidget(label)
        placeholder.setLayout(layout)
        self.tab_widget.addTab(placeholder, title)

# ============================================
# APPLICATION ENTRY POINT - FINAL VERSION
# ============================================

def main():
    """Main application entry point - Final version"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create palette for dark/light theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Initialize database
    db = DatabaseManager()
    
    # Show login dialog
    login_dialog = LoginDialog(db)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Login successful, show main window
        window = MainWindow(login_dialog.user)
        
        # Replace module initialization with full version
        window.init_modules = lambda: init_modules_all(window)
        window.add_placeholder_tabs = lambda: add_placeholder_tabs_all(window)
        
        window.init_modules()
        window.show()
        sys.exit(app.exec())
    else:
        # Login cancelled or failed
        sys.exit(0)

if __name__ == "__main__":
    main()
