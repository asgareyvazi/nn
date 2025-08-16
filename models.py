# models.py
"""
Comprehensive SQLAlchemy models for Nikan Drill Master
Designed to cover the full feature set: well/project/section hierarchy,
daily reports, timelogs, codes, drilling parameters, mud, bit records,
BHA, inventory, personnel/logistics, safety/BOP, surveys, export signoffs, preferences, etc.

Notes:
 - Use Database.sessionmaker() in database.py to provide sessions.
 - If you run migrations, prefer Alembic and use the migration script generated earlier.
"""

from sqlalchemy import (
    Column, Integer, Float, String, Text, Date, DateTime, Boolean,
    ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship, backref, declarative_base
from datetime import datetime

Base = declarative_base()

# ---------------------------------------------------------------------
# Basic entities: Company, Project, Well, Section
# ---------------------------------------------------------------------
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    address = Column(String(512))
    contact = Column(String(256))
    email = Column(String(256))

    projects = relationship("Project", back_populates="company", cascade="all,delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    name = Column(String(256), nullable=False)
    field = Column(String(256))
    description = Column(Text)

    company = relationship("Company", back_populates="projects")
    wells = relationship("Well", back_populates="project", cascade="all,delete-orphan")


class Well(Base):
    __tablename__ = "wells"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    name = Column(String(200), nullable=False, index=True)
    rig_name = Column(String(200))
    operator = Column(String(200))
    well_type = Column(String(50))  # onshore/offshore
    well_shape = Column(String(50)) # vertical/deviated/horizontal
    hole_size_in = Column(Float)
    estimated_final_depth_md_m = Column(Float)
    offshore_water_depth_m = Column(Float)

    spud_date = Column(Date)
    start_hole_date = Column(Date)
    rig_move_date = Column(Date)
    report_date = Column(Date)

    # relationships
    project = relationship("Project", back_populates="wells")
    sections = relationship("Section", back_populates="well", cascade="all,delete-orphan")
    signoffs = relationship("Signoff", back_populates="well", cascade="all,delete-orphan")

# Section = logical division within well (e.g. casing section)
class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"))
    name = Column(String(200), nullable=False)  # e.g., "Surface", "Intermediate", "Production"
    description = Column(Text)
    start_md = Column(Float)  # measured depth start
    end_md = Column(Float)    # measured depth end

    well = relationship("Well", back_populates="sections")
    daily_reports = relationship("DailyReport", back_populates="section", cascade="all,delete-orphan")
    bit_records = relationship("BitRecord", back_populates="section", cascade="all,delete-orphan")
    bha_runs = relationship("BHARun", back_populates="section", cascade="all,delete-orphan")

# ---------------------------------------------------------------------
# Preferences & Signoff
# ---------------------------------------------------------------------
class Preferences(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True)
    default_units = Column(String(32), default="metric")
    theme = Column(String(32), default="dark")
    load_previous_report = Column(Boolean, default=True)
    logo_company = Column(String(1024), nullable=True)
    logo_client = Column(String(1024), nullable=True)
    default_report_template = Column(String(1024), nullable=True)


class Signoff(Base):
    __tablename__ = "signoffs"
    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"), nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True)
    supervisor_name = Column(String(256))
    operation_manager = Column(String(256))
    approved = Column(Boolean, default=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(256), nullable=True)
    sign_image_path = Column(String(1024), nullable=True)
    notes = Column(Text, nullable=True)

    well = relationship("Well", back_populates="signoffs")
    section = relationship("Section")

# ---------------------------------------------------------------------
# Code Management (for TimeLog Cascade ComboBoxes)
# ---------------------------------------------------------------------
class MainPhaseCode(Base):
    __tablename__ = "main_phase_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(200))
    description = Column(Text)

    sub_codes = relationship("SubCode", back_populates="main_code", cascade="all,delete-orphan")


class SubCode(Base):
    __tablename__ = "sub_codes"
    id = Column(Integer, primary_key=True)
    main_code_id = Column(Integer, ForeignKey("main_phase_codes.id", ondelete="CASCADE"))
    code = Column(String(50), nullable=False)
    name = Column(String(200))
    description = Column(Text)

    main_code = relationship("MainPhaseCode", back_populates="sub_codes")

# ---------------------------------------------------------------------
# Daily Report & TimeLog
# ---------------------------------------------------------------------
class DailyReport(Base):
    __tablename__ = "daily_reports"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"))
    report_date = Column(Date, nullable=False)
    rig_day = Column(Integer, nullable=True)
    depth_at_0000_ft = Column(Float, nullable=True)
    depth_at_0600_ft = Column(Float, nullable=True)
    depth_at_2400_ft = Column(Float, nullable=True)
    pit_gain = Column(Float, nullable=True)
    operations_done = Column(Text, nullable=True)
    work_summary = Column(Text, nullable=True)
    alerts = Column(Text, nullable=True)
    general_notes = Column(Text, nullable=True)
    created_by = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="daily_reports")
    well = relationship("Well")
    timelogs = relationship("TimeLog", back_populates="daily_report", cascade="all,delete-orphan")


class TimeLog(Base):
    __tablename__ = "time_logs"
    id = Column(Integer, primary_key=True)
    daily_report_id = Column(Integer, ForeignKey("daily_reports.id", ondelete="CASCADE"))
    from_time = Column(String(32))  # store HH:MM or ISO time string
    to_time = Column(String(32))
    duration_minutes = Column(Integer)
    main_phase_code_id = Column(Integer, ForeignKey("main_phase_codes.id", ondelete="SET NULL"))
    sub_code_id = Column(Integer, ForeignKey("sub_codes.id", ondelete="SET NULL"))
    description = Column(String(512))
    is_npt = Column(Boolean, default=False)
    status = Column(String(64))

    daily_report = relationship("DailyReport", back_populates="timelogs")
    main_code = relationship("MainPhaseCode")
    sub_code = relationship("SubCode")

# ---------------------------------------------------------------------
# Time Breakdown summary (aggregated)
# ---------------------------------------------------------------------
class TimeBreakdown(Base):
    __tablename__ = "time_breakdowns"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    code = Column(String(128))
    total_minutes = Column(Integer)
    summary = Column(Text)

# ---------------------------------------------------------------------
# Drilling Parameters
# ---------------------------------------------------------------------
class DrillingParameters(Base):
    __tablename__ = "drilling_parameters"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    # common parameters (min/max)
    wob_min = Column(Float); wob_max = Column(Float)
    rpm_surface_min = Column(Float); rpm_surface_max = Column(Float)
    rpm_motor_min = Column(Float); rpm_motor_max = Column(Float)
    torque_min = Column(Float); torque_max = Column(Float)
    pump_pressure_min = Column(Float); pump_pressure_max = Column(Float)
    pump_output_min = Column(Float); pump_output_max = Column(Float)
    hsi = Column(Float)
    annular_velocity = Column(Float)
    tfa = Column(Float)
    bit_revolution = Column(Float)

    section = relationship("Section")

# ---------------------------------------------------------------------
# Mud Report & Chemicals
# ---------------------------------------------------------------------
class MudReport(Base):
    __tablename__ = "mud_reports"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    sample_time = Column(DateTime)
    mud_type = Column(String(128))
    mw_pcf = Column(Float)   # mud weight
    pv = Column(Float)
    yp = Column(Float)
    funnel_vis = Column(Float)
    gel_10s = Column(Float); gel_10m = Column(Float); gel_30m = Column(Float)
    fl_api = Column(Float)
    cake_thickness = Column(Float)
    ca = Column(Float); chloride = Column(Float); kcl = Column(Float)
    ph = Column(Float)
    hardness = Column(Float)
    mbt = Column(Float)
    solid_percent = Column(Float)
    oil_water_glycol_percent = Column(Float)
    temperature = Column(Float)
    pf_mf = Column(Float)

    section = relationship("Section", backref=backref("mud_reports", cascade="all,delete-orphan"))
    chemicals = relationship("MudChemical", back_populates="mud_report", cascade="all,delete-orphan")


class MudChemical(Base):
    __tablename__ = "mud_chemicals"
    id = Column(Integer, primary_key=True)
    mud_report_id = Column(Integer, ForeignKey("mud_reports.id", ondelete="CASCADE"))
    product_type = Column(String(200))
    received = Column(Float)
    used = Column(Float)
    stock = Column(Float)
    unit = Column(String(50))

    mud_report = relationship("MudReport", back_populates="chemicals")

# ---------------------------------------------------------------------
# Bit record & per-run reports
# ---------------------------------------------------------------------
class BitRecord(Base):
    __tablename__ = "bit_records"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    bit_no = Column(String(64))
    size_in = Column(Float)
    manufacturer = Column(String(128))
    type = Column(String(128))
    serial_no = Column(String(256))
    iadc_code = Column(String(64))
    dull_grading = Column(String(128))
    reason_pulled = Column(String(256))
    depth_in = Column(Float)
    depth_out = Column(Float)
    hours = Column(Float)
    cum_drilled = Column(Float)
    cum_hours = Column(Float)
    rop = Column(Float)
    formation = Column(String(256))
    lithology = Column(String(256))

    section = relationship("Section", back_populates="bit_records")
    reports = relationship("BitRunReport", back_populates="bit", cascade="all,delete-orphan")


class BitRunReport(Base):
    __tablename__ = "bit_run_reports"
    id = Column(Integer, primary_key=True)
    bit_id = Column(Integer, ForeignKey("bit_records.id", ondelete="CASCADE"))
    wob = Column(Float); rpm = Column(Float); flowrate = Column(Float); spp = Column(Float)
    pv = Column(Float); yp = Column(Float)
    cumulative_drilling = Column(Float); rop = Column(Float); tfa = Column(Float); revolution = Column(Float)
    photo_before = Column(String(1024), nullable=True)
    photo_after = Column(String(1024), nullable=True)
    notes = Column(Text)

    bit = relationship("BitRecord", back_populates="reports")

# ---------------------------------------------------------------------
# BHA runs and tools
# ---------------------------------------------------------------------
class BHARun(Base):
    __tablename__ = "bha_runs"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)

    section = relationship("Section", back_populates="bha_runs")
    tools = relationship("BHATool", back_populates="run", cascade="all,delete-orphan")


class BHATool(Base):
    __tablename__ = "bha_tools"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("bha_runs.id", ondelete="CASCADE"))
    tool_type = Column(String(128))
    od_in = Column(Float); id_in = Column(Float); length_m = Column(Float)
    serial_no = Column(String(256)); weight_kg = Column(Float); remarks = Column(String(512))

    run = relationship("BHARun", back_populates="tools")

# ---------------------------------------------------------------------
# Inventory, Cement, Material handling
# ---------------------------------------------------------------------
class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    item = Column(String(256))
    opening = Column(Float)
    received = Column(Float)
    used = Column(Float)
    remaining = Column(Float)
    unit = Column(String(32))

    section = relationship("Section")


class CementInventory(Base):
    __tablename__ = "cement_inventory"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    material = Column(String(256))
    received = Column(Float); consumed = Column(Float); backload = Column(Float); last_inventory = Column(Float)

    section = relationship("Section")


class MaterialNote(Base):
    __tablename__ = "material_notes"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    note_no = Column(Integer)
    text = Column(Text)

    section = relationship("Section")

# ---------------------------------------------------------------------
# POB / Personnel / Logistics / Boats / Choppers
# ---------------------------------------------------------------------
class Crew(Base):
    __tablename__ = "crew"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    company = Column(String(256))
    service = Column(String(256))
    count = Column(Integer)
    date_in = Column(Date)
    total_pob = Column(Integer)

    section = relationship("Section")


class BoatLog(Base):
    __tablename__ = "boat_logs"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    name = Column(String(256))
    arrival = Column(DateTime); departure = Column(DateTime)
    status = Column(String(128))

    section = relationship("Section")


class ChopperLog(Base):
    __tablename__ = "chopper_logs"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    name = Column(String(256))
    arrival = Column(DateTime); departure = Column(DateTime)
    pax_in = Column(Integer)

    section = relationship("Section")

# ---------------------------------------------------------------------
# Safety & Waste management & BOP
# ---------------------------------------------------------------------
class BOPRecord(Base):
    __tablename__ = "bop_records"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    last_fire = Column(Date); last_bop = Column(Date); last_h2s = Column(Date)
    days_without_lti = Column(Integer); days_without_lta = Column(Integer)
    rams = Column(String(256)); pressure_test = Column(String(256)); koomey_test = Column(String(256))
    bop_stack_name = Column(String(256)); bop_type = Column(String(128)); wp = Column(String(64)); size = Column(String(64))

    section = relationship("Section")


class WasteManagement(Base):
    __tablename__ = "waste_management"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    recycled_bbl = Column(Float); ph = Column(Float); turbidity_tss = Column(Float); hardness_ca = Column(Float); cutting_trans_m3 = Column(Float)

    section = relationship("Section")

# ---------------------------------------------------------------------
# Solid control, Fuel & Water, Drill pipe specs, Survey
# ---------------------------------------------------------------------
class SolidControlUnit(Base):
    __tablename__ = "solid_control_units"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    equipment = Column(String(256)); feed_bbl_hr = Column(Float); hours = Column(Float); loss_bbl = Column(Float)
    size_cones = Column(String(64)); daily_hours = Column(Float); cum_hours = Column(Float)

    section = relationship("Section")


class FuelWater(Base):
    __tablename__ = "fuel_water"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    consumed = Column(Float); stock = Column(Float)

    section = relationship("Section")


class DrillPipeSpec(Base):
    __tablename__ = "drill_pipe_specs"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    size_weight = Column(String(128)); connection = Column(String(128)); inner_d_in = Column(Float); grade = Column(String(64))
    tj_od = Column(Float); tj_id = Column(Float); std_no_in_derrick = Column(Integer)

    section = relationship("Section")


class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    md = Column(Float); inc = Column(Float); tvd = Column(Float); azi = Column(Float); azimuth = Column(Float)
    north = Column(Float); east = Column(Float); vs_hd = Column(Float); dls = Column(Float)
    tool = Column(String(128))

    section = relationship("Section")

# ---------------------------------------------------------------------
# NPT entries
# ---------------------------------------------------------------------
class NPTEntry(Base):
    __tablename__ = "npt_entries"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    from_time = Column(DateTime); to_time = Column(DateTime)
    code_id = Column(Integer, ForeignKey("main_phase_codes.id", ondelete="SET NULL"))
    sub_code_id = Column(Integer, ForeignKey("sub_codes.id", ondelete="SET NULL"))
    description = Column(Text)
    responsible = Column(String(256))

    section = relationship("Section")
    code = relationship("MainPhaseCode")
    sub_code = relationship("SubCode")

# ---------------------------------------------------------------------
# Time breakdown (summary) - already above as TimeBreakdown
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Misc: formation tops, solid control, material handling already covered
# ---------------------------------------------------------------------
class FormationTop(Base):
    __tablename__ = "formation_tops"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    name = Column(String(256)); lithology = Column(String(256)); top_md = Column(Float)

    section = relationship("Section")


class FormationTopData(Base):
    __tablename__ = "formation_top_data"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"))
    name = Column(String(256)); md = Column(Float); tvd = Column(Float); lithology = Column(String(256))

    section = relationship("Section")

# ---------------------------------------------------------------------
# Utility / meta
# ---------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True)
    display_name = Column(String(256))
    email = Column(String(256))
    role = Column(String(64))  # admin, supervisor, user

# ---------------------------------------------------------------------
# Add any unique constraints / indices as needed
# ---------------------------------------------------------------------
