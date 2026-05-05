from flask import Flask, request, render_template
from uploader import extract_text
from brain import analyze_case

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    result = None
    if request.method == "POST":
        f = request.files["file"]
        f.save("case.pdf")
        result = analyze_case(extract_text("case.pdf"))
    return render_template("index.html", result=result)

app.run(debug=True)
