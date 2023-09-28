import platform
maj, mini, patch = [int(x) for x in platform.python_version_tuple()]

if maj == 3 and mini >= 11:
    # module = importlib.import_module("excursor.core._process")
    from excursor.core._process import Run
elif maj == 3 and mini >= 9:
    # module = importlib.import_module("excursor.core._process_39")
    from excursor.core._process_39 import Run
else:
    raise Exception("Invalid python version")


__all__ = ["Run"]
