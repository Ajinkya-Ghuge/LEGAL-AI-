import flask
print("Flask OK:", flask.__version__ if hasattr(flask, '__version__') else "installed")
