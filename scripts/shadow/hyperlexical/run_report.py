import json
import os
import sys
from datetime import datetime

ENV = "HLX_RUN_REPORT"


def safe_inputs(d):
    """Return a copy of *d* with sensitive or large list values sanitized."""
    out = {}
    for k, v in d.items():
        if k in ("text", "rows"):
            continue
        if isinstance(v, list) and len(v) > 50:
            out[k] = f"<list len={len(v)}>"
        else:
            out[k] = v
    return out


class RunReport:
    def __init__(self, tool, inputs, path=None):
        self.tool = tool
        self.inputs = safe_inputs(inputs)
        self.path = path if path is not None else os.environ.get(ENV)
        self.counts = {}
        self.scores = {}
        self.validity = None
        self.warnings = []
        self.status = None
        self.started = None

    def __enter__(self):
        self.started = datetime.now().astimezone()
        return self

    def set_counts(self, **kw):
        self.counts.update(kw)

    def set_scores(self, **kw):
        self.scores.update(kw)

    def set_validity(self, valid, invalid, reasons=None):
        total = valid + invalid
        valid_rate = round(valid / total, 4) if total > 0 else None
        self.validity = {
            "valid": valid,
            "invalid": invalid,
            "valid_rate": valid_rate,
        }
        if reasons is not None:
            self.validity["reasons"] = reasons

    def warn(self, msg):
        self.warnings.append(msg)

    def set_status(self, s):
        self.status = s

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path is None:
            return False

        finished = datetime.now().astimezone()
        duration_ms = int(round((finished - self.started).total_seconds() * 1000))
        status = self.status if self.status is not None else ("error" if exc_type is not None else "ok")
        errors = []
        if exc_type is not None:
            errors.append(f"{exc_type.__name__}: {exc_val}")

        data = {
            "schema": "run_report.v1",
            "tool": self.tool,
            "started_at": self.started.isoformat(timespec="seconds"),
            "finished_at": finished.isoformat(timespec="seconds"),
            "duration_ms": duration_ms,
            "status": status,
            "inputs": self.inputs,
            "counts": self.counts,
            "scores": self.scores,
            "validity": self.validity,
            "warnings": self.warnings,
            "errors": errors,
        }

        try:
            path = os.path.abspath(self.path)
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"Failed to write run report: {e}\n")

        return False
