
# =========================================
# file: nikan_drill_master/models.py
# =========================================
from __future__ import annotations
from datetime import date, datetime, time
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, DateTime, Time, Float, ForeignKey, Boolean, UniqueConstraint, Index, Text

class Base(DeclarativeBase):
    pass

# --- Org hierarchy ---
class Company(Base):
    __tablename__ = "company"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    projects: Mapped[list["Project"]] = relationship(back_populates="company", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    company: Mapped[Company] = relationship(back_populates="projects")
    wells: Mapped[list["Well"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_project_company_name"),)

class Well(Base):
    __tablename__ = "well"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    rig_name: Mapped[Optional[str]] = mapped_column(String(200))
    operator: Mapped[Optional[str]] = mapped_column(String(200))
    field_name: Mapped[Optional[str]] = mapped_column(String(200))
    well_type: Mapped[Optional[str]] = mapped_column(String(50))  # Onshore/Offshore
    rig_type: Mapped[Optional[str]] = mapped_column(String(50))   # Land/Jackup/...
    well_shape: Mapped[Optional[str]] = mapped_column(String(50)) # Vertical/Deviated/Horizontal
    derrick_height_ft: Mapped[Optional[int]] = mapped_column(Integer)

    gle: Mapped[Optional[float]] = mapped_column(Float)
    rte: Mapped[Optional[float]] = mapped_column(Float)
    msl: Mapped[Optional[float]] = mapped_column(Float)
    kop1: Mapped[Optional[float]] = mapped_column(Float)
    kop2: Mapped[Optional[float]] = mapped_column(Float)

    latitude: Mapped[Optional[str]] = mapped_column(String(64))
    longitude: Mapped[Optional[str]] = mapped_column(String(64))
    northing: Mapped[Optional[float]] = mapped_column(Float)
    easting: Mapped[Optional[float]] = mapped_column(Float)

    hole_size_in: Mapped[Optional[float]] = mapped_column(Float)
    est_final_depth_md_m: Mapped[Optional[float]] = mapped_column(Float)
    offshore_water_depth_m: Mapped[Optional[float]] = mapped_column(Float)

    spud_date: Mapped[Optional[date]] = mapped_column(Date)
    start_hole_date: Mapped[Optional[date]] = mapped_column(Date)
    rig_move_date: Mapped[Optional[date]] = mapped_column(Date)

    supervisor_day: Mapped[Optional[str]] = mapped_column(String(200))
    supervisor_night: Mapped[Optional[str]] = mapped_column(String(200))
    toolpusher_day: Mapped[Optional[str]] = mapped_column(String(200))
    toolpusher_night: Mapped[Optional[str]] = mapped_column(String(200))
    operation_manager: Mapped[Optional[str]] = mapped_column(String(200))
    geologist1: Mapped[Optional[str]] = mapped_column(String(200))
    geologist2: Mapped[Optional[str]] = mapped_column(String(200))
    client_rep: Mapped[Optional[str]] = mapped_column(String(200))

    objectives: Mapped[Optional[str]] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="wells")
    sections: Mapped[list["Section"]] = relationship(back_populates="well", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_well_project_name"),)

class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("well.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))  # user-defined
    well: Mapped[Well] = relationship(back_populates="sections")
    daily_reports: Mapped[list["DailyReport"]] = relationship(back_populates="section", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("well_id", "name", name="uq_section_well_name"),)

class DailyReport(Base):
    __tablename__ = "daily_report"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    report_date: Mapped[date] = mapped_column(Date, index=True)
    rig_day: Mapped[Optional[int]] = mapped_column(Integer)
    depth_0000_ft: Mapped[Optional[int]] = mapped_column(Integer)
    depth_0600_ft: Mapped[Optional[int]] = mapped_column(Integer)
    depth_2400_ft: Mapped[Optional[int]] = mapped_column(Integer)
    pit_gain: Mapped[Optional[float]] = mapped_column(Float)
    operations_done: Mapped[Optional[str]] = mapped_column(Text)
    work_summary: Mapped[Optional[str]] = mapped_column(Text)
    alerts: Mapped[Optional[str]] = mapped_column(Text)
    general_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    section: Mapped[Section] = relationship(back_populates="daily_reports")
    time_logs: Mapped[list["TimeLog"]] = relationship(back_populates="daily_report", cascade="all, delete-orphan")
    drilling_params: Mapped[Optional["DrillingParameters"]] = relationship(back_populates="daily_report", uselist=False, cascade="all, delete-orphan")
    mud_report: Mapped[Optional["MudReport"]] = relationship(back_populates="daily_report", uselist=False, cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("section_id", "report_date", name="uq_section_date"),)

class CodeMain(Base):
    __tablename__ = "code_main"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phase: Mapped[str] = mapped_column(String(100), index=True)    # e.g., Drilling, Tripping
    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    subs: Mapped[list["CodeSub"]] = relationship(back_populates="main", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("phase", "code", name="uq_phase_code"),)

class CodeSub(Base):
    __tablename__ = "code_sub"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    main_id: Mapped[int] = mapped_column(ForeignKey("code_main.id", ondelete="CASCADE"), index=True)
    sub_code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    main: Mapped[CodeMain] = relationship(back_populates="subs")
    __table_args__ = (UniqueConstraint("main_id", "sub_code", name="uq_main_subcode"),)

class TimeLog(Base):
    __tablename__ = "time_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), index=True)
    time_from: Mapped[time] = mapped_column(Time)
    time_to: Mapped[time] = mapped_column(Time)
    duration_min: Mapped[int] = mapped_column(Integer)  # auto-calc
    main_code_id: Mapped[int] = mapped_column(ForeignKey("code_main.id"))
    sub_code_id: Mapped[Optional[int]] = mapped_column(ForeignKey("code_sub.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_npt: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., Done/Continue/Pending

    daily_report: Mapped[DailyReport] = relationship(back_populates="time_logs")
    main_code: Mapped[CodeMain] = relationship()
    sub_code: Mapped[Optional[CodeSub]] = relationship()
    __table_args__ = (Index("ix_time_log_dr_date", "daily_report_id"),)

class DrillingParameters(Base):
    __tablename__ = "drilling_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), unique=True)
    wob_min: Mapped[Optional[float]] = mapped_column(Float)
    wob_max: Mapped[Optional[float]] = mapped_column(Float)
    surf_rpm_min: Mapped[Optional[float]] = mapped_column(Float)
    surf_rpm_max: Mapped[Optional[float]] = mapped_column(Float)
    motor_rpm_min: Mapped[Optional[float]] = mapped_column(Float)
    motor_rpm_max: Mapped[Optional[float]] = mapped_column(Float)
    torque_min: Mapped[Optional[float]] = mapped_column(Float)
    torque_max: Mapped[Optional[float]] = mapped_column(Float)
    pump_press_min: Mapped[Optional[float]] = mapped_column(Float)
    pump_press_max: Mapped[Optional[float]] = mapped_column(Float)
    pump_out_min: Mapped[Optional[float]] = mapped_column(Float)
    pump_out_max: Mapped[Optional[float]] = mapped_column(Float)
    hsi: Mapped[Optional[float]] = mapped_column(Float)
    annular_velocity: Mapped[Optional[float]] = mapped_column(Float)
    tfa: Mapped[Optional[float]] = mapped_column(Float)
    bit_revolution: Mapped[Optional[float]] = mapped_column(Float)
    scr_spm1: Mapped[Optional[float]] = mapped_column(Float)
    scr_spp1: Mapped[Optional[float]] = mapped_column(Float)
    scr_spm2: Mapped[Optional[float]] = mapped_column(Float)
    scr_spp2: Mapped[Optional[float]] = mapped_column(Float)
    scr_spm3: Mapped[Optional[float]] = mapped_column(Float)
    scr_spp3: Mapped[Optional[float]] = mapped_column(Float)
    daily_report: Mapped[DailyReport] = relationship(back_populates="drilling_params")

class MudReport(Base):
    __tablename__ = "mud_report"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), unique=True)
    mud_type: Mapped[Optional[str]] = mapped_column(String(100))
    sample_time: Mapped[Optional[time]] = mapped_column(Time)
    mw_pcf: Mapped[Optional[float]] = mapped_column(Float)
    pv: Mapped[Optional[float]] = mapped_column(Float)
    yp: Mapped[Optional[float]] = mapped_column(Float)
    funnel_vis: Mapped[Optional[float]] = mapped_column(Float)
    gel_10s: Mapped[Optional[float]] = mapped_column(Float)
    gel_10m: Mapped[Optional[float]] = mapped_column(Float)
    gel_30m: Mapped[Optional[float]] = mapped_column(Float)
    fl_api: Mapped[Optional[float]] = mapped_column(Float)
    cake_thickness: Mapped[Optional[float]] = mapped_column(Float)
    ca: Mapped[Optional[float]] = mapped_column(Float)
    chloride: Mapped[Optional[float]] = mapped_column(Float)
    kcl: Mapped[Optional[float]] = mapped_column(Float)
    ph: Mapped[Optional[float]] = mapped_column(Float)
    hardness: Mapped[Optional[float]] = mapped_column(Float)
    mbt: Mapped[Optional[float]] = mapped_column(Float)
    solid_pct: Mapped[Optional[float]] = mapped_column(Float)
    oil_pct: Mapped[Optional[float]] = mapped_column(Float)
    water_pct: Mapped[Optional[float]] = mapped_column(Float)
    glycol_pct: Mapped[Optional[float]] = mapped_column(Float)
    temp_c: Mapped[Optional[float]] = mapped_column(Float)
    pf: Mapped[Optional[float]] = mapped_column(Float)
    mf: Mapped[Optional[float]] = mapped_column(Float)
    vol_in_hole: Mapped[Optional[float]] = mapped_column(Float)
    total_circulated: Mapped[Optional[float]] = mapped_column(Float)
    loss_downhole: Mapped[Optional[float]] = mapped_column(Float)
    loss_surface: Mapped[Optional[float]] = mapped_column(Float)
    daily_report: Mapped[DailyReport] = relationship(back_populates="mud_report")
    chemicals: Mapped[list["MudChemical"]] = relationship(back_populates="mud_report", cascade="all, delete-orphan")

class MudChemical(Base):
    __tablename__ = "mud_chemical"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mud_report_id: Mapped[int] = mapped_column(ForeignKey("mud_report.id", ondelete="CASCADE"), index=True)
    product_type: Mapped[str] = mapped_column(String(100))
    received: Mapped[Optional[float]] = mapped_column(Float)
    used: Mapped[Optional[float]] = mapped_column(Float)
    stock: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    mud_report: Mapped[MudReport] = relationship(back_populates="chemicals")

class BHAItem(Base):
    __tablename__ = "bha_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    tool_type: Mapped[str] = mapped_column(String(100))
    od_in: Mapped[Optional[float]] = mapped_column(Float)
    id_in: Mapped[Optional[float]] = mapped_column(Float)
    length_m: Mapped[Optional[float]] = mapped_column(Float)
    serial_no: Mapped[Optional[str]] = mapped_column(String(100))
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    remarks: Mapped[Optional[str]] = mapped_column(Text)

class InventoryItem(Base):
    __tablename__ = "inventory_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    item: Mapped[str] = mapped_column(String(200))
    opening: Mapped[Optional[float]] = mapped_column(Float)
    received: Mapped[Optional[float]] = mapped_column(Float)
    used: Mapped[Optional[float]] = mapped_column(Float)
    remaining: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

class Survey(Base):
    __tablename__ = "survey"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    md: Mapped[Optional[float]] = mapped_column(Float)
    inc: Mapped[Optional[float]] = mapped_column(Float)
    tvd: Mapped[Optional[float]] = mapped_column(Float)
    azi: Mapped[Optional[float]] = mapped_column(Float)
    north: Mapped[Optional[float]] = mapped_column(Float)
    east: Mapped[Optional[float]] = mapped_column(Float)
    vs_hd: Mapped[Optional[float]] = mapped_column(Float)
    dls: Mapped[Optional[float]] = mapped_column(Float)
    tool: Mapped[Optional[str]] = mapped_column(String(100))

class POBEntry(Base):
    __tablename__ = "pob_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    company_name: Mapped[str] = mapped_column(String(200))
    service: Mapped[Optional[str]] = mapped_column(String(200))
    count: Mapped[int] = mapped_column(Integer)
    date_in: Mapped[Optional[date]] = mapped_column(Date)
    category: Mapped[Optional[str]] = mapped_column(String(50))  # Client/Contractor/Service

class Preferences(Base):
    __tablename__ = "preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_units: Mapped[Optional[str]] = mapped_column(String(20))  # SI/Field
    load_previous_report: Mapped[bool] = mapped_column(Boolean, default=True)
    theme: Mapped[Optional[str]] = mapped_column(String(20))  # dark/light
    logo_path: Mapped[Optional[str]] = mapped_column(String(500))

class SupervisorSignature(Base):
    __tablename__ = "supervisor_signature"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), unique=True)
    supervisor_name: Mapped[Optional[str]] = mapped_column(String(200))
    operation_manager: Mapped[Optional[str]] = mapped_column(String(200))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

# --- NPT Report ---
class NPTEntry(Base):
    __tablename__ = "npt_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), index=True)
    time_from: Mapped[time] = mapped_column(Time)
    time_to: Mapped[time] = mapped_column(Time)
    duration_min: Mapped[int] = mapped_column(Integer)
    main_code_id: Mapped[int] = mapped_column(ForeignKey("code_main.id"))
    sub_code_id: Mapped[Optional[int]] = mapped_column(ForeignKey("code_sub.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    responsible_party: Mapped[Optional[str]] = mapped_column(String(200))

# --- Service Company Log ---
class ServiceCompanyLog(Base):
    __tablename__ = "service_company_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), index=True)
    company_name: Mapped[str] = mapped_column(String(200))
    service_type: Mapped[Optional[str]] = mapped_column(String(200))
    start_dt: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_dt: Mapped[Optional[datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)

# --- Fuel & Water ---
class FuelWaterDailyItem(Base):
    __tablename__ = "fuel_water_daily_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(String(200))
    consumed: Mapped[Optional[float]] = mapped_column(Float)
    stock: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

class FuelWaterBulk(Base):
    __tablename__ = "fuel_water_bulk"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_report_id: Mapped[int] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))   # e.g., FW, DW, Fuel(Rig), Fuel(Camp), Silica Flour, Cement
    stock: Mapped[Optional[float]] = mapped_column(Float)
    used: Mapped[Optional[float]] = mapped_column(Float)
    received: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

# --- Downhole Equipment ---
class DownholeEquipment(Base):
    __tablename__ = "downhole_equipment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id", ondelete="CASCADE"), index=True)
    equipment_name: Mapped[str] = mapped_column(String(200))
    serial_no: Mapped[Optional[str]] = mapped_column(String(100))
    tool_id: Mapped[Optional[str]] = mapped_column(String(100))
    sliding_hours: Mapped[Optional[float]] = mapped_column(Float)
    cum_rotation: Mapped[Optional[float]] = mapped_column(Float)
    cum_pumping: Mapped[Optional[float]] = mapped_column(Float)
    cum_total_hours: Mapped[Optional[float]] = mapped_column(Float)
