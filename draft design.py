from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import date
import os

# ===============================
# OUTPUT PATH
# ===============================
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_PATH = os.path.join(OUTPUT_DIR, "MACT_Claim_Petition.pdf")

# ===============================
# CASE DATA (TRIAL DEMO DATA)
# Later AI will fill this
# ===============================
case_data = {
    "petitioner": "Dummy Kumar",
    "age": "34 Years",
    "address": "ABC Colony, Shivaji Nagar, Pune – 411005",
    "accident_date": "12 March 2024",
    "place": "Pune, Maharashtra",
    "injuries": [
        "Fracture of Right Femur",
        "Head Injury (Minor Concussion)",
        "Multiple Abrasions on Left Arm"
    ],
    "hospital": "Sanjeevani Hospital, Pune",
    "surgery": "ORIF – Open Reduction and Internal Fixation",
    "claim_amount": "Rs. 10,00,000/-"
}

# ===============================
# PDF GENERATION
# ===============================
c = canvas.Canvas(FILE_PATH, pagesize=A4)
width, height = A4

x_margin = 1 * inch
y = height - 1 * inch

def draw_line(text, bold=False, space=14):
    global y
    if bold:
        c.setFont("Times-Bold", 11)
    else:
        c.setFont("Times-Roman", 11)

    c.drawString(x_margin, y, text)
    y -= space

# ===============================
# HEADER
# ===============================
c.setFont("Times-Bold", 13)
c.drawCentredString(width / 2, y, "BEFORE THE HON'BLE MOTOR ACCIDENT CLAIMS TRIBUNAL, PUNE")
y -= 25

c.setFont("Times-Bold", 12)
c.drawCentredString(width / 2, y, "CLAIM PETITION UNDER SECTION 166 OF MOTOR VEHICLES ACT, 1988")
y -= 30

# ===============================
# PETITION DETAILS
# ===============================
draw_line("IN THE MATTER OF:", bold=True)
y -= 10

draw_line(f"Shri. {case_data['petitioner']}, Age: {case_data['age']}")
draw_line(f"Resident of: {case_data['address']}")
draw_line("...PETITIONER")

y -= 15
draw_line("VERSUS", bold=True)
y -= 15

draw_line("1. Driver of Offending Vehicle")
draw_line("2. Owner of Offending Vehicle")
draw_line("3. Insurance Company")
draw_line("...RESPONDENTS")

y -= 20

# ===============================
# FACTS OF ACCIDENT
# ===============================
draw_line("FACTS OF THE CASE:", bold=True)
y -= 10

draw_line(
    f"That on {case_data['accident_date']}, the Petitioner met with a road traffic accident at "
    f"{case_data['place']} due to rash and negligent driving of the offending vehicle."
)

y -= 10
draw_line(
    f"That the Petitioner sustained grievous injuries and was immediately admitted to "
    f"{case_data['hospital']}."
)

# ===============================
# MEDICAL DETAILS
# ===============================
y -= 15
draw_line("MEDICAL TREATMENT & INJURIES:", bold=True)
y -= 10

for injury in case_data["injuries"]:
    draw_line(f"- {injury}")

y -= 10
draw_line(f"That the Petitioner underwent surgery: {case_data['surgery']}.")

# ===============================
# COMPENSATION
# ===============================
y -= 20
draw_line("COMPENSATION CLAIMED:", bold=True)
y -= 10

draw_line(
    f"The Petitioner claims a total compensation of {case_data['claim_amount']} "
    "towards medical expenses, pain and suffering, loss of income, and future disability."
)

# ===============================
# PRAYER
# ===============================
y -= 20
draw_line("PRAYER:", bold=True)
y -= 10

draw_line(
    "In view of the above facts, the Hon’ble Tribunal may kindly be pleased to award "
    f"compensation of {case_data['claim_amount']} along with interest and costs."
)

# ===============================
# VERIFICATION
# ===============================
y -= 30
draw_line("VERIFICATION", bold=True)
y -= 10

draw_line(
    "I, the above named Petitioner, do hereby verify that the contents of this petition "
    "are true and correct to my knowledge."
)

y -= 30
draw_line(f"Place: Pune")
draw_line(f"Date: {date.today().strftime('%d %B %Y')}")

y -= 40
draw_line("Petitioner Signature: _______________________")

# ===============================
# SAVE PDF
# ===============================
c.showPage()
c.save()

print(" MACT Draft PDF generated successfully!")
print(f" File saved at: {FILE_PATH}")
