import sys
try:
    import flask
    print("flask OK:", flask.__version__)
except ImportError as e:
    print("flask MISSING:", e)

try:
    import fitz
    print("PyMuPDF OK:", fitz.__version__)
except ImportError as e:
    print("PyMuPDF MISSING:", e)

try:
    import google.generativeai
    print("google-generativeai OK")
except ImportError as e:
    print("google-generativeai MISSING:", e)

print("Python:", sys.version)
