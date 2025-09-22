# Make sure tests are in a proper package
# If your tests are just loose .py files, imports may behave inconsistently.
# Adding an empty __init__.py in your tests/ folder ensures consistent package resolution.

# import sys, importlib, pathlib

# # Force clean pycache for modules under current package name.
# for name in list(sys.modules):
#     if name.startswith("test"):
#         importlib.reload(sys.modules[name])

# # Optional: nuke .pyc files on import.
# for pycache in pathlib.Path(__file__).parents[1].rglob("__pycache__"):
#     for f in pycache.glob("*.pyc"):
#         f.unlink(missing_ok=True)
