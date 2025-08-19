import sqlite3
from pathlib import Path
import logging

DB_PATH = Path(__file__).parent / "nikan_drill_master.db"

class DatabaseManager:
    def __init__(self):
        self.connection = self._create_connection()
        self._setup_database()
        self._enable_foreign_keys()
        self._configure_connection()
        
    def _create_connection(self):
        """Create database connection with error handling"""
        try:
            return sqlite3.connect(DB_PATH)
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise

    def _enable_foreign_keys(self):
        """Enable foreign key support"""
        try:
            self.connection.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            logging.error(f"Failed to enable foreign keys: {str(e)}")

    def _configure_connection(self):
        """Configure connection settings"""
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode = WAL;")
        self.connection.execute("PRAGMA busy_timeout = 5000;")

    def _setup_database(self):
        """Create database schema with improved structure"""
        cursor = self.connection.cursor()
        
        # Enable Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL;")
        
        # Create tables with improved constraints and indexing
        self._create_well_info_table(cursor)
        self._create_daily_reports_table(cursor)
        self._create_time_logs_table(cursor)
        self._create_drilling_params_table(cursor)
        self._create_mud_reports_table(cursor)
        self._create_bit_records_table(cursor)
        self._create_bha_tables(cursor)
        self._create_npt_reports_table(cursor)
        self._create_personnel_table(cursor)
        self._create_safety_table(cursor)
        self._create_inventory_table(cursor)
        self._create_service_company_table(cursor)
        self._create_export_center_table(cursor)
        self._create_signatures_table(cursor)
        self._create_lookahead_table(cursor)
        self._create_code_management_table(cursor)
        self._create_downhole_equipment_table(cursor)
        self._create_waste_management_table(cursor)
        self._create_cement_additives_table(cursor)
        self._create_formation_data_table(cursor)
        self._create_solid_control_table(cursor)
        self._create_fuel_water_table(cursor)
        self._create_drill_pipe_table(cursor)
        self._create_survey_data_table(cursor)
        self._create_material_handling_table(cursor)
        self._create_pob_table(cursor)
        self._create_weather_table(cursor)
        self._create_transport_table(cursor)
        self._create_preferences_table(cursor)
        self._create_trajectory_table(cursor)
        
        # Create indexes for faster queries
        self._create_indexes(cursor)
        
        self.connection.commit()

    def _create_well_info_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS well_info (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            well_name       TEXT NOT NULL UNIQUE,
            rig_name        TEXT,
            operator        TEXT,
            field           TEXT,
            project         TEXT,
            well_type       TEXT CHECK(well_type IN ('Onshore', 'Offshore')),
            rig_type        TEXT,
            well_shape      TEXT,
            derrick_height  REAL,
            gle             REAL,
            rte             REAL,
            msl             REAL,
            kop1            REAL,
            kop2            REAL,
            latitude        REAL,
            longitude       REAL,
            northing        REAL,
            easting         REAL,
            hole_size       REAL,
            final_depth     REAL,
            water_depth     REAL,
            spud_date       TEXT,
            start_hole_date TEXT,
            rig_move_date   TEXT,
            supervisor1     TEXT,
            supervisor2     TEXT,
            toolpusher1     TEXT,
            toolpusher2     TEXT,
            manager         TEXT,
            geologist1      TEXT,
            geologist2      TEXT,
            client_rep      TEXT,
            objectives      TEXT
        )""")

    def _create_daily_reports_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            well_id       INTEGER NOT NULL,
            report_date   TEXT NOT NULL,
            rig_day       INTEGER,
            depth_0000    REAL,
            depth_2400    REAL,
            depth_0600    REAL,
            pit_gain      REAL,
            operations_done TEXT,
            work_summary  TEXT,
            alerts        TEXT,
            notes         TEXT,
            FOREIGN KEY(well_id) REFERENCES well_info(id) ON DELETE CASCADE,
            UNIQUE(well_id, report_date)
        )""")

    def _create_time_logs_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id   INTEGER NOT NULL,
            start_time  TEXT NOT NULL,
            end_time    TEXT NOT NULL,
            main_phase  TEXT,
            sub_code    TEXT,
            description TEXT,
            npt         INTEGER DEFAULT 0 CHECK(npt IN (0, 1)),
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_drilling_params_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS drilling_parameters (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            wob_min           REAL,
            wob_max           REAL,
            surface_rpm_min   REAL,
            surface_rpm_max   REAL,
            motor_rpm_min     REAL,
            motor_rpm_max     REAL,
            torque_min        REAL,
            torque_max        REAL,
            pump_pressure_min REAL,
            pump_pressure_max REAL,
            pump_output_min   REAL,
            pump_output_max   REAL,
            hsi               REAL,
            annular_velocity  REAL,
            tfa               REAL,
            bit_revolution    REAL,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_mud_reports_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mud_reports (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            mud_type          TEXT CHECK(mud_type IN ('Water Based', 'Oil Based', 'Synthetic')),
            sample_time       TEXT,
            mw                REAL,
            pv                REAL,
            yp                REAL,
            funnel_vis        REAL,
            gel_10s           REAL,
            gel_10m           REAL,
            gel_30m           REAL,
            fl_api            REAL,
            cake_thickness    REAL,
            ca                REAL,
            chloride          REAL,
            kcl               REAL,
            ph                REAL,
            hardness          REAL,
            mbt               REAL,
            solid_pct         REAL,
            oil_pct           REAL,
            water_pct         REAL,
            glycol_pct        REAL,
            temp              REAL,
            pf                REAL,
            mf                REAL,
            vol_in_hole       REAL,
            total_circulated  REAL,
            loss_downhole     REAL,
            loss_surface      REAL,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_bit_records_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bit_records (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id           INTEGER NOT NULL,
            bit_no              INTEGER,
            size                REAL,
            manufacturer        TEXT,
            type                TEXT,
            serial_no           TEXT,
            iadc_code           TEXT,
            reason_pulled       TEXT,
            depth_in            REAL,
            depth_out           REAL,
            hours               REAL,
            cum_drilled         REAL,
            cum_hrs             REAL,
            rop                 REAL,
            formation           TEXT,
            lithology           TEXT,
            inner_cutters       TEXT,
            outer_cutters       TEXT,
            dull_characteristics TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_bha_tables(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bha_records (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            bha_no        INTEGER,
            run_no        INTEGER,
            date_run      TEXT,
            description   TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bha_components (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            bha_id        INTEGER NOT NULL,
            tool_type     TEXT,
            od            REAL,
            idiameter     REAL,
            length        REAL,
            serial_no     TEXT,
            weight        REAL,
            FOREIGN KEY(bha_id) REFERENCES bha_records(id) ON DELETE CASCADE
        )""")

    def _create_npt_reports_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS npt_reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id       INTEGER NOT NULL,
            start_time      TEXT,
            end_time        TEXT,
            duration        REAL,
            category        TEXT,
            sub_category    TEXT,
            description     TEXT,
            responsible     TEXT,
            action_taken    TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_personnel_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            name          TEXT NOT NULL,
            position      TEXT,
            company       TEXT,
            shift         TEXT CHECK(shift IN ('Day', 'Night')),
            status        TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_safety_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_records (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            incident_type TEXT,
            description   TEXT,
            date_occurred TEXT,
            corrective_action TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_inventory_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            item_name     TEXT NOT NULL,
            quantity      REAL,
            unit          TEXT,
            status        TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_service_company_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_company_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            company_name  TEXT NOT NULL,
            activity      TEXT,
            log_date      TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_export_center_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS export_center (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER,
            export_type   TEXT,
            file_path     TEXT UNIQUE,
            export_date   TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE SET NULL
        )""")

    def _create_signatures_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS supervisor_signatures (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL UNIQUE,
            supervisor    TEXT NOT NULL,
            signature     BLOB,
            signed_on     TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_lookahead_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lookahead_plans (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            well_id       INTEGER NOT NULL,
            plan_date     TEXT,
            details       TEXT,
            FOREIGN KEY(well_id) REFERENCES well_info(id) ON DELETE CASCADE
        )""")

    def _create_code_management_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_management (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            code          TEXT NOT NULL,
            description   TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_downhole_equipment_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS downhole_equipment (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id     INTEGER NOT NULL,
            equipment     TEXT NOT NULL,
            status        TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_waste_management_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_management (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            waste_type        TEXT NOT NULL,
            quantity          REAL,
            disposal_method   TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_cement_additives_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cement_additives (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            additive_type     TEXT NOT NULL,
            dosage            REAL,
            remarks           TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_formation_data_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS formation_data (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            formation_type    TEXT NOT NULL,
            porosity          REAL,
            permeability      REAL,
            remarks           TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_solid_control_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS solid_control (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            parameter         TEXT NOT NULL,
            value             REAL,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_fuel_water_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_water (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            fuel_used         REAL,
            water_used        REAL,
            log_date          TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_drill_pipe_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS drill_pipe_specs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            pipe_length       REAL,
            diameter          REAL,
            manufacturer      TEXT,
            grade             TEXT,
            remarks           TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_survey_data_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_data (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            md                REAL,
            inclination       REAL,
            azimuth           REAL,
            tvd               REAL,
            northing          REAL,
            easting           REAL,
            survey_date       TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_material_handling_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_handling (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            material          TEXT NOT NULL,
            quantity          REAL,
            unit              TEXT,
            remarks           TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_pob_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pob (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            person_name       TEXT NOT NULL,
            role              TEXT,
            count             INTEGER,
            log_date          TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_weather_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            temperature       REAL,
            pressure          REAL,
            wind_speed        REAL,
            wind_direction    TEXT,
            humidity          REAL,
            recorded_at       TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_transport_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS boats_chopper_log (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL,
            vehicle           TEXT CHECK(vehicle IN ('Boat', 'Chopper')),
            departure_time    TEXT,
            arrival_time      TEXT,
            notes             TEXT,
            FOREIGN KEY(report_id) REFERENCES daily_reports(id) ON DELETE CASCADE
        )""")

    def _create_preferences_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user              TEXT NOT NULL,
            key               TEXT NOT NULL,
            value             TEXT,
            UNIQUE(user, key)
        )""")

    def _create_trajectory_table(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trajectory (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            well_id           INTEGER NOT NULL,
            measured_depth    REAL,
            inclination       REAL,
            azimuth           REAL,
            tvd               REAL,
            northing          REAL,
            easting           REAL,
            entry_date        TEXT,
            FOREIGN KEY(well_id) REFERENCES well_info(id) ON DELETE CASCADE
        )""")

    def _create_indexes(self, cursor):
        """Create indexes for faster queries"""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_reports_well ON daily_reports(well_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_logs_report ON time_logs(report_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mud_reports_report ON mud_reports(report_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bit_records_report ON bit_records(report_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bha_components_bha ON bha_components(bha_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_npt_reports_report ON npt_reports(report_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trajectory_well ON trajectory(well_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preferences_user ON preferences(user);")

    def execute_query(self, query: str, params: tuple = None) -> int:
        """Execute a query and return lastrowid with error handling"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Query failed: {query} | Error: {str(e)}")
            raise

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all results with error handling"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Fetch failed: {query} | Error: {str(e)}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> sqlite3.Row:
        """Fetch a single result with error handling"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Fetch failed: {query} | Error: {str(e)}")
            return None

    def close(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
        except sqlite3.Error as e:
            logging.error(f"Failed to close connection: {str(e)}")
