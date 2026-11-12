"""Collect installed dependency notices into the local release payload."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
import sys

target = Path(__file__).resolve().parents[1] / "vendor" / "licenses" / "python"
target.mkdir(parents=True, exist_ok=True)
for distribution in distributions():
    for entry in distribution.files or ():
        if any(word in entry.name.lower() for word in ("license", "copying", "notice")):
            source = Path(distribution.locate_file(entry))
            if source.is_file():
                destination = target / distribution.metadata["Name"] / str(entry).replace("../", "")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
python_license = Path(sys.base_prefix) / "LICENSE.txt"
if not python_license.is_file():
    raise SystemExit(f"Missing Python license: {python_license}")
shutil.copy2(python_license, target / "PYTHON-LICENSE.txt")
for name in ("tcl8.6", "tk8.6"):
    source = Path(sys.base_prefix) / "tcl" / name / "license.terms"
    if source.is_file():
        shutil.copy2(source, target / f"{name}-license.terms")
