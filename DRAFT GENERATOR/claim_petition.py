from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from datetime import date

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_PATH = os.path.join(OUTPUT_DIR, "claim_petition_166.pdf")

# ===============================
# DOCUMENT
# ===============================
doc = SimpleDocTemplate(
    FILE_PATH,
    pagesize=A4,
    leftMargin=1*inch,
    rightMargin=1*inch,
    topMargin=1*inch,
    bottomMargin=1*inch
)

styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "TITLE",
    fontName="Times-Bold",
    fontSize=13,
    alignment=TA_CENTER,
    spaceAfter=10
)

SUB = ParagraphStyle(
    "SUB",
    fontName="Times-Bold",
    fontSize=11,
    alignment=TA_CENTER,
    spaceAfter=10
)

BODY = ParagraphStyle(
    "BODY",
    fontName="Times-Roman",
    fontSize=11,
    leading=15,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

RIGHT = ParagraphStyle(
    "RIGHT",
    fontName="Times-Roman",
    fontSize=11,
    alignment=TA_RIGHT,
    spaceAfter=6
)

story = []

# ===============================
# TITLE
# ===============================
story.append(Paragraph(
    "BEFORE THE HON’BLE MOTOR ACCIDENT CLAIMS TRIBUNAL, PUNE",
    TITLE
))
story.append(Paragraph("M.A.C.P. No. ______ of 2024", SUB))
story.append(Spacer(1, 12))

# ===============================
# BETWEEN
# ===============================
story.append(Paragraph("<b>BETWEEN</b>", SUB))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "<b>Mr. Dummy Kumar</b><br/>"
    "S/o Ram Kumar<br/>"
    "Age: 34 Years<br/>"
    "Resident of: House No. 123, ABC Colony,<br/>"
    "Shivaji Nagar, Pune – 411005.",
    BODY
))
story.append(Paragraph("…CLAIMANT", RIGHT))
story.append(Spacer(1, 14))

story.append(Paragraph("<b>AND</b>", SUB))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "1. Mr. Anil Sharma<br/>"
    "Driver of Car No. MH-12-AB-4567<br/>"
    "Resident of XYZ Nagar, Pune.<br/><br/>"
    "2. Mr. Rahul Jain<br/>"
    "Owner of Car No. MH-12-AB-4567<br/>"
    "Resident of ABC Nagar, Pune.<br/><br/>"
    "3. XYZ General Insurance Co. Ltd.<br/>"
    "Insurer of Car No. MH-12-AB-4567<br/>"
    "Branch Office: Pune.",
    BODY
))
story.append(Paragraph("…RESPONDENTS", RIGHT))

story.append(Spacer(1, 16))

# ===============================
# PETITION TITLE
# ===============================
story.append(Paragraph(
    "CLAIM PETITION UNDER SECTION 166 OF THE MOTOR VEHICLES ACT, 1988",
    SUB
))
story.append(Spacer(1, 12))

story.append(Paragraph(
    "<b>MAY IT PLEASE THIS HON’BLE TRIBUNAL</b>",
    SUB
))
story.append(Spacer(1, 14))

# ===============================
# FACTS OF THE CASE
# ===============================
story.append(Paragraph("<b>1. FACTS OF THE CASE</b>", BODY))

story.append(Paragraph(
    "(a) On 12th March 2024, at about 2:30 PM, the Petitioner was driving his "
    "two-wheeler bearing registration No. MH-01-XY-123 on ABC Road, Pune, "
    "when the Respondent No.1 driving Car No. MH-12-AB-4567 in a rash and "
    "negligent manner dashed the petitioner’s vehicle from behind.",
    BODY
))

story.append(Paragraph(
    "(b) Due to the violent impact, the petitioner fell on the road and "
    "sustained multiple grievous injuries. He was immediately shifted to "
    "Sanjeevani Hospital, Pune by bystanders and police.",
    BODY
))

story.append(Paragraph(
    "(c) An FIR bearing No. ___/2024 was registered at the concerned Police "
    "Station under Sections 279 and 338 of IPC against Respondent No.1 on "
    "the basis of eyewitness statements.",
    BODY
))

# ===============================
# MEDICAL HISTORY
# ===============================
story.append(Spacer(1, 10))
story.append(Paragraph("<b>2. MEDICAL HISTORY</b>", BODY))

story.append(Paragraph(
    "The petitioner sustained Fracture of Right Femur, Head Injury and "
    "multiple abrasions. He underwent surgical treatment and prolonged "
    "medical care and is still under follow-up treatment.",
    BODY
))

# ===============================
# COMPENSATION TABLE
# ===============================
story.append(Spacer(1, 12))
story.append(Paragraph("<b>3. COMPENSATION CLAIMED</b>", BODY))

table_data = [
    ["Head of Compensation", "Amount (₹)"],
    ["Hospital Bills & Medical Expenses", "1,25,000"],
    ["Future Medical Expenses", "75,000"],
    ["Loss of Income", "1,00,000"],
    ["Pain and Suffering", "1,00,000"],
    ["Loss of Amenities of Life", "75,000"],
    ["Special Diet, Attendant & Conveyance", "90,000"],
    ["Loss of Future Earning Capacity", "—"],
    ["TOTAL", "8,50,000"],
]

comp_table = Table(table_data, colWidths=[doc.width*0.7, doc.width*0.3])
comp_table.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 1, colors.black),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ("FONT", (0,0), (-1,0), "Times-Bold"),
    ("FONT", (0,-1), (-1,-1), "Times-Bold"),
]))

story.append(comp_table)

# ===============================
# PRAYER
# ===============================
story.append(Spacer(1, 14))
story.append(Paragraph("<b>4. PRAYER</b>", BODY))

story.append(Paragraph(
    "The petitioner therefore humbly prays that this Hon’ble Tribunal may "
    "be pleased to award compensation of ₹ 8,50,000/- along with interest "
    "and costs and pass such other order as deemed fit in the interest of "
    "justice.",
    BODY
))

# ===============================
# VERIFICATION
# ===============================
story.append(Spacer(1, 18))
story.append(Paragraph("<b>VERIFICATION</b>", BODY))

story.append(Paragraph(
    "I, Dummy Kumar, the petitioner herein, do hereby verify that the "
    "contents of this petition are true and correct to my knowledge and belief.",
    BODY
))

story.append(Spacer(1, 24))
story.append(Paragraph(
    f"Place: Pune<br/>Date: {date.today().strftime('%d %B %Y')}",
    BODY
))
story.append(Spacer(1, 20))
story.append(Paragraph(
    "Petitioner",
    RIGHT
))

# ===============================
# BUILD
# ===============================
doc.build(story)

print(" CLAIM PETITION u/s 166 GENERATED")
print(f" Saved at: {FILE_PATH}")
