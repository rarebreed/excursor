import platform
import importlib
maj, mini, patch = [int(x) for x in platform.python_version_tuple()]
print(f"Using python {maj}.{mini}.{patch}")

if maj == 3 and mini >= 11:
    module = importlib.import_module("excursor.core._process")
elif maj == 3 and mini >= 9:
    module = importlib.import_module("excursor.core._process_39")
else:
    raise Exception("Invalid python version")

Run = module.Run

__all__ = ["Run"]
