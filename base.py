# -*- coding: utf-8 -*-
"""
base.py

Base module system for Nikan Drill Master.

Provides:
- ModuleBase: QObject-based base class for UI/visible modules and headless modules.
- ModuleRegistry: thread-safe singleton registry for registering / lazy-loading modules.
- import_string utility for dynamic import.
- register_module decorator for convenience.

Target: PySide6 (Qt6). If you still need PySide2 support, change imports accordingly.
"""
from __future__ import annotations

import importlib
import logging
import threading
from typing import Any, Dict, Optional, Type

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


def import_string(dotted_path: str) -> Any:
    """
    Import a class or object specified by dotted path 'package.module:ClassName' or
    'package.module.ClassName'
    """
    if ":" in dotted_path:
        module_path, attr = dotted_path.split(":", 1)
    else:
        *parts, attr = dotted_path.split(".")
        module_path = ".".join(parts)
    if not module_path:
        raise ImportError(f"Invalid import string: {dotted_path}")
    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise ImportError(f"Module '{module_path}' has no attribute '{attr}'") from exc


class ModuleBase(QObject):
    """
    Base class for all modules.

    - Inherit from this class for both UI modules (which expose `.widget`) and non-UI modules.
    - Use Qt signals for lifecycle events so MainWindow can connect and react.
    - Keep heavy I/O off the GUI thread (use QThreadPool/QRunnable or concurrent.futures).
    """

    activated = Signal()     # emitted when module is activated (brought to front)
    deactivated = Signal()   # emitted when module is hidden/deactivated
    closed = Signal()        # emitted on module close/cleanup
    state_changed = Signal() # emitted when module internal state changes (for autosave/dirty flag)

    def __init__(self, db: Optional[Any] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.db = db
        self.parent = parent
        self.name: str = self.__class__.__name__
        self.display_name: str = getattr(self, "display_name", self.name)
        self.widget: Optional[Any] = None  # UI widget (QWidget) if applicable; lazy create
        self._dirty: bool = False
        self._lock = threading.RLock()

    # ---------- lifecycle hooks (override in subclasses) ----------
    def on_register(self, main_window: Any) -> None:
        """
        Called by MainWindow when the module is registered.
        Avoid long/blocking work here — prefer lazy load in activate().
        """
        self.main_window = main_window

    def activate(self) -> None:
        """
        Called when user activates the module.
        Default implementation emits activated signal and brings widget to front if available.
        """
        logger.debug("Activating module: %s", self.name)
        if hasattr(self, "main_window") and getattr(self, "widget", None) is not None:
            try:
                # Let main_window handle setting the central widget
                self.activated.emit()
            except Exception:
                logger.exception("Error emitting activated signal for %s", self.name)
        else:
            self.activated.emit()

    def deactivate(self) -> None:
        """Called when module is hidden or switched away."""
        logger.debug("Deactivating module: %s", self.name)
        self.deactivated.emit()

    def save(self) -> None:
        """
        Persist module state to DB/storage.
        Override to implement concrete save logic.
        Should be fast or run in background thread.
        """
        logger.debug("Save called on module: %s", self.name)
        # default: no-op

    def close(self) -> None:
        """Cleanup resources. MainWindow should call before exit."""
        logger.debug("Closing module: %s", self.name)
        self.closed.emit()

    # ---------- state helpers ----------
    def mark_dirty(self, is_dirty: bool = True) -> None:
        with self._lock:
            if self._dirty != is_dirty:
                self._dirty = is_dirty
                try:
                    self.state_changed.emit()
                except Exception:
                    logger.exception("state_changed emit failed for %s", self.name)

    def is_dirty(self) -> bool:
        with self._lock:
            return self._dirty

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable dict representing lightweight state (e.g., filters, last open file).
        Not intended for full DB export — modules should manage DB entities via models/repositories.
        """
        return {"name": self.name, "display_name": self.display_name}

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Restore minimal UI state from dict returned by to_dict().
        """
        # default: no-op; override if needed
        pass


# ---------- Module registry (singleton-like) ----------
class ModuleRegistry:
    """
    Simple thread-safe registry for module instances or import paths.

    Usage:
        ModuleRegistry.register_instance("WellInfo", WellInfoModule(db))
        ModuleRegistry.register_path("DailyReport", "modules.daily_report:DailyReportModule")
        mod = ModuleRegistry.get("DailyReport")  # returns instance, lazy-importing if needed
    """

    _instance: Optional[ModuleRegistry] = None
    _lock = threading.RLock()

    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._paths: Dict[str, str] = {}
        self._registry_lock = threading.RLock()

    @classmethod
    def instance(cls) -> "ModuleRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = ModuleRegistry()
        return cls._instance

    def register_instance(self, name: str, module_obj: ModuleBase) -> None:
        with self._registry_lock:
            self._modules[name] = module_obj
            logger.debug("Registered module instance: %s", name)

    def register_path(self, name: str, import_path: str) -> None:
        """
        Register a dotted import path for lazy-loading.
        import_path examples: 'modules.daily_report:DailyReportModule' or 'modules.daily_report.DailyReportModule'
        """
        with self._registry_lock:
            self._paths[name] = import_path
            logger.debug("Registered module path: %s -> %s", name, import_path)

    def get(self, name: str) -> Optional[ModuleBase]:
        """
        Return module instance. If registered as path, import & instantiate lazily.
        If instance registered, return it.
        """
        with self._registry_lock:
            if name in self._modules:
                return self._modules[name]

            if name in self._paths:
                path = self._paths[name]
                try:
                    cls_or_factory = import_string(path)
                    # If it's a class, instantiate it without args (prefer factory pattern otherwise)
                    if isinstance(cls_or_factory, type):
                        instance = cls_or_factory()
                    else:
                        instance = cls_or_factory()  # expecting a callable
                    if not isinstance(instance, ModuleBase):
                        logger.warning("Loaded object for %s is not ModuleBase: %r", name, instance)
                    self._modules[name] = instance
                    logger.info("Lazily loaded module %s from %s", name, path)
                    return instance
                except Exception:
                    logger.exception("Failed to lazy-load module %s from %s", name, path)
                    return None
            logger.warning("Module %s not found in registry", name)
            return None

    def all_modules(self) -> Dict[str, ModuleBase]:
        with self._registry_lock:
            # return only instances
            return {k: v for k, v in self._modules.items() if isinstance(v, ModuleBase)}


def register_module(name: Optional[str] = None):
    """
    Decorator to register a module class at import time.
    Usage:
        @register_module("WellInfo")
        class WellInfoModule(ModuleBase): ...
    """
    def _decorator(cls: Type[ModuleBase]) -> Type[ModuleBase]:
        mod_name = name or cls.__name__
        try:
            instance = cls()
            ModuleRegistry.instance().register_instance(mod_name, instance)
            logger.debug("Auto-registered module class: %s", mod_name)
        except Exception:
            logger.exception("Failed to auto-instantiate/register module: %s", mod_name)
        return cls
    return _decorator


# ---------- small smoke test when run directly ----------
if __name__ == "__main__":  # pragma: no cover - smoke only
    logging.basicConfig(level=logging.DEBUG)
    reg = ModuleRegistry.instance()
    logger.info("ModuleRegistry created: %r", reg)
    # Demonstrate dynamic import failure handling (doesn't raise)
    reg.register_path("NonExisting", "modules.unknown:Missing")
    got = reg.get("NonExisting")
    logger.info("Got NonExisting -> %r", got)

