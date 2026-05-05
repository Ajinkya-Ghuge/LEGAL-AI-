from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch
import os
from datetime import date

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_PATH = os.path.join(OUTPUT_DIR, "affidavit_claimant.pdf")

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
    spaceAfter=10
)

RIGHT = ParagraphStyle(
    "RIGHT",
    fontName="Times-Roman",
    fontSize=11,
    alignment=TA_RIGHT,
    spaceAfter=10
)

story = []

# ===============================
# TITLE
# ===============================
story.append(Paragraph(
    "AFFIDAVIT OF THE CLAIMANT",
    TITLE
))
story.append(Spacer(1, 14))

# ===============================
# AFFIDAVIT BODY
# ===============================
story.append(Paragraph(
    "I, Mr. Dummy Kumar, S/o Ram Kumar, Age: 34 Years, Occupation: __________, "
    "Resident of House No. 123, ABC Colony, Shivaji Nagar, Pune – 411005, "
    "do hereby solemnly affirm and state on oath as under:",
    BODY
))

story.append(Paragraph(
    "1. That I am the petitioner in the accompanying Claim Petition filed under "
    "Section 166 of the Motor Vehicles Act, 1988 and am well acquainted with the "
    "facts and circumstances of the case.",
    BODY
))

story.append(Paragraph(
    "2. That the contents of the Claim Petition, Statement of Compensation and "
    "other documents filed along with the petition are true and correct to my "
    "knowledge and belief.",
    BODY
))

story.append(Paragraph(
    "3. That the accident occurred due to the rash and negligent driving of the "
    "offending vehicle and I have not contributed to the said accident in any manner.",
    BODY
))

story.append(Paragraph(
    "4. That I have incurred medical expenses, suffered loss of income, pain, "
    "mental agony and hardship due to the injuries sustained in the accident.",
    BODY
))

story.append(Paragraph(
    "5. That this affidavit is filed in support of the Claim Petition and the "
    "Statement of Compensation.",
    BODY
))

# ===============================
# VERIFICATION
# ===============================
story.append(Spacer(1, 16))
story.append(Paragraph(
    "<b>VERIFICATION</b>",
    BODY
))

story.append(Paragraph(
    "I, the deponent above named, do hereby verify that the contents of this "
    "affidavit are true and correct to my knowledge and belief and nothing "
    "material has been concealed therefrom.",
    BODY
))

story.append(Spacer(1, 20))
story.append(Paragraph(
    f"Place: Pune<br/>Date: {date.today().strftime('%d %B %Y')}",
    BODY
))

story.append(Spacer(1, 30))
story.append(Paragraph(
    "DEPONENT",
    RIGHT
))

# ===============================
# BUILD
# ===============================
doc.build(story)

print(" AFFIDAVIT GENERATED")
print(f" Saved at: {FILE_PATH}")
