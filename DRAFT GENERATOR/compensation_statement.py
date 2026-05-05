from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_PATH = os.path.join(OUTPUT_DIR, "compensation_statement.pdf")

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
    spaceAfter=12
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
    spaceAfter=8
)

story = []

# ===============================
# TITLE
# ===============================
story.append(Paragraph(
    "STATEMENT OF COMPENSATION",
    TITLE
))
story.append(Paragraph(
    "(Filed along with Claim Petition u/s 166 of the Motor Vehicles Act, 1988)",
    BODY
))
story.append(Spacer(1, 14))

# ===============================
# INTRO
# ===============================
story.append(Paragraph(
    "The petitioner respectfully submits the following statement of compensation "
    "claimed under various heads as a result of the motor vehicle accident:",
    BODY
))

# ===============================
# COMPENSATION TABLE
# ===============================
table_data = [
    ["Sr. No.", "Head of Compensation", "Amount Claimed (₹)"],
    ["1", "Hospital Bills and Medical Expenses", "1,25,000"],
    ["2", "Estimated Future Medical Expenses", "75,000"],
    ["3", "Loss of Income during Treatment Period", "1,00,000"],
    ["4", "Pain and Suffering", "1,00,000"],
    ["5", "Loss of Amenities and Enjoyment of Life", "75,000"],
    ["6", "Special Diet, Attendant Charges and Conveyance", "90,000"],
    ["7", "Future Loss of Earning Capacity due to Disability", "Pending Medical Opinion"],
    ["", "TOTAL COMPENSATION CLAIMED", "₹ 8,50,000/-"],
]

comp_table = Table(
    table_data,
    colWidths=[doc.width*0.12, doc.width*0.58, doc.width*0.30]
)

comp_table.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 1, colors.black),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONT", (0,0), (-1,0), "Times-Bold"),
    ("FONT", (0,-1), (-1,-1), "Times-Bold"),
    ("ALIGN", (2,1), (-1,-1), "RIGHT"),
    ("SPAN", (0,-1), (1,-1)),
]))

story.append(comp_table)

# ===============================
# FOOTER
# ===============================
story.append(Spacer(1, 20))
story.append(Paragraph(
    "The above amounts are claimed bona fide and are subject to revision based "
    "on medical evidence and further developments during trial.",
    BODY
))

story.append(Spacer(1, 30))
story.append(Paragraph(
    "Petitioner",
    RIGHT
))

# ===============================
# BUILD
# ===============================
doc.build(story)

print(" COMPENSATION STATEMENT GENERATED")
print(f" Saved at: {FILE_PATH}")
