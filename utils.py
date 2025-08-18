
# =========================================
# file: nikan_drill_master/utils.py
# =========================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable, Any
from datetime import time, datetime, date
import csv
from pathlib import Path
from PySide6.QtWidgets import QMessageBox

def minutes_between(t1: time, t2: time) -> int:
    """چرا: محاسبه دقیق Duration با عبور از نیمه‌شب"""
    d = date.today()
    dt1 = datetime.combine(d, t1)
    dt2 = datetime.combine(d, t2)
    if dt2 < dt1:
        dt2 = dt2.replace(day=dt2.day + 1)
    return int((dt2 - dt1).total_seconds() // 60)

def info_message(parent, title: str, text: str) -> None:
    QMessageBox.information(parent, title, text)

def warn_message(parent, title: str, text: str) -> None:
    QMessageBox.warning(parent, title, text)

def export_table_to_csv(headers: list[str], rows: Iterable[Iterable[Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(list(r))

def optional_float(s: str | None) -> float | None:
    if s is None or s.strip() == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None
