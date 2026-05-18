"""
PARASITE EVOLVED — Progress Tracking
Thread-safe progress store for real-time scan status updates.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ScanProgress:
    session_id: str
    phase: str = "INITIALIZING"
    total_files: int = 0
    files_scanned: int = 0
    current_file: str = ""
    functions_found: int = 0
    privilege_ops_found: int = 0
    start_time: float = 0.0
    eta_seconds: float = 0.0
    complete: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        elapsed = time.time() - self.start_time if self.start_time else 0
        pct = (self.files_scanned / max(self.total_files, 1)) * 100
        return {
            "session_id": self.session_id,
            "phase": self.phase,
            "total_files": self.total_files,
            "files_scanned": self.files_scanned,
            "current_file": self.current_file,
            "functions_found": self.functions_found,
            "privilege_ops_found": self.privilege_ops_found,
            "percent": round(pct, 1),
            "elapsed_seconds": round(elapsed, 1),
            "eta_seconds": round(self.eta_seconds, 1),
            "complete": self.complete,
            "error": self.error,
        }


class ProgressStore:
    """Thread-safe global progress store."""

    def __init__(self):
        self._store: Dict[str, ScanProgress] = {}
        self._lock = threading.Lock()

    def create(self, session_id: str) -> ScanProgress:
        progress = ScanProgress(
            session_id=session_id,
            start_time=time.time(),
        )
        with self._lock:
            self._store[session_id] = progress
        return progress

    def get(self, session_id: str) -> Optional[ScanProgress]:
        with self._lock:
            return self._store.get(session_id)

    def update(self, session_id: str, **kwargs):
        with self._lock:
            p = self._store.get(session_id)
            if p:
                for k, v in kwargs.items():
                    if hasattr(p, k):
                        setattr(p, k, v)
                # Calculate ETA
                if p.files_scanned > 0 and p.total_files > 0:
                    elapsed = time.time() - p.start_time
                    rate = p.files_scanned / elapsed
                    remaining = p.total_files - p.files_scanned
                    p.eta_seconds = remaining / rate if rate > 0 else 0

    def complete(self, session_id: str):
        self.update(session_id, phase="COMPLETE", complete=True)

    def error(self, session_id: str, msg: str):
        self.update(session_id, phase="ERROR", error=msg, complete=True)


# Global singleton
progress_store = ProgressStore()
