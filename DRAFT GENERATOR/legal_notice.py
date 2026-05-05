from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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

FILE_PATH = os.path.join(OUTPUT_DIR, "legal_notice.pdf")

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
# ADVOCATE HEADER BOX (LIKE IMAGE)
# ===============================
adv_table = Table(
    [[
        Paragraph("<b>ADVOCATE NAME</b><br/>"
                  "Office Address: ___________________<br/>"
                  "Contact No.: ___________________", BODY)
    ]],
    colWidths=[doc.width]
)

adv_table.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, colors.black),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))

story.append(adv_table)
story.append(Spacer(1, 16))

# ===============================
# TRIBUNAL TITLE
# ===============================
story.append(Paragraph(
    "BEFORE THE HON’BLE MOTOR ACCIDENT CLAIMS TRIBUNAL, PUNE",
    TITLE
))
story.append(Paragraph("M.A.C.P. No. ______ of 2024", SUB))
story.append(Spacer(1, 10))

# ===============================
# NOTICE TITLE
# ===============================
story.append(Paragraph(
    "LEGAL NOTICE (INSURANCE / OWNER)",
    TITLE
))
story.append(Spacer(1, 14))

# ===============================
# TO + SUBJECT
# ===============================
story.append(Paragraph(
    "<b>To,</b><br/>"
    "1. The Owner of the Offending Vehicle<br/>"
    "2. The Insurance Company of the Offending Vehicle<br/><br/>",
    BODY
))

story.append(Paragraph(
    "<b>Subject:</b> Legal Notice for demand of compensation arising out of "
    "motor vehicular accident under the Motor Vehicles Act, 1988.<br/><br/>",
    BODY
))

# ===============================
# BODY (MATCHING IMAGE DENSITY)
# ===============================
story.append(Paragraph(
    "<b>Sir/Madam,</b><br/><br/>"
    "Under instructions and on behalf of my client <b>Mr. Dummy Kumar</b>, "
    "S/o Ram Kumar, Age: 34 Years, Resident of House No. 123, ABC Colony, "
    "Shivaji Nagar, Pune – 411005, I hereby issue this legal notice as under:",
    BODY
))

story.append(Paragraph(
    "1. That on 12th March 2024 at about 2:30 PM, my client was proceeding on "
    "his two-wheeler in a lawful manner when the offending vehicle bearing "
    "registration No. MH-12-AB-4567 came from behind at high speed and in a "
    "rash and negligent manner and dashed my client’s vehicle.",
    BODY
))

story.append(Paragraph(
    "2. That due to the violent impact, my client fell on the road and sustained "
    "multiple grievous injuries. He was immediately taken to Sanjeevani Hospital, "
    "Pune by bystanders and police where he was admitted and treated.",
    BODY
))

story.append(Paragraph(
    "3. That an FIR bearing No. ___/2024 was registered with the concerned police "
    "station under Sections 279, 338 of IPC against the driver of the offending "
    "vehicle on the basis of eyewitness statements.",
    BODY
))

story.append(Paragraph(
    "4. That my client suffered Fracture of Right Femur, Head Injury and multiple "
    "abrasions and had to undergo prolonged medical treatment, rest and follow-ups, "
    "thereby suffering physical pain, mental agony and loss of income.",
    BODY
))

story.append(Paragraph(
    "5. That the accident occurred solely due to rash and negligent driving of the "
    "offending vehicle and therefore you being the owner and insurer are jointly "
    "and severally liable to compensate my client.",
    BODY
))

story.append(Paragraph(
    "6. Hence, you are hereby called upon to pay a sum of <b>₹ 8,50,000/-</b> "
    "(Rupees Eight Lakh Fifty Thousand Only) towards compensation within "
    "<b>15 days</b> from receipt of this notice, failing which my client shall "
    "be constrained to initiate appropriate proceedings before the Hon’ble "
    "Motor Accident Claims Tribunal at your risk as to costs and consequences.",
    BODY
))

# ===============================
# FOOTER
# ===============================
story.append(Spacer(1, 14))

story.append(Paragraph(
    "This notice is issued without prejudice to all other legal rights and "
    "remedies available to my client in law and equity.",
    BODY
))

story.append(Spacer(1, 20))

story.append(Paragraph(
    f"Place: Pune<br/>Date: {date.today().strftime('%d %B %Y')}",
    BODY
))

story.append(Spacer(1, 24))

story.append(Paragraph(
    "<b>Advocate for the Notice Sender</b>",
    RIGHT
))

# ===============================
# BUILD
# ===============================
doc.build(story)

print(" LEGAL NOTICE GENERATED")
print(f" Saved at: {FILE_PATH}")
