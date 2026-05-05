# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# )
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from datetime import date
# import os

# # ===============================
# # PATH SETUP
# # ===============================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# OUTPUT_DIR = os.path.join(BASE_DIR, "output")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# FILE_PATH = os.path.join(
#     OUTPUT_DIR,
#     "legal_notice_eviction_ramesh_vs_suresh.pdf"
# )

# # ===============================
# # DOCUMENT SETUP
# # ===============================
# doc = SimpleDocTemplate(
#     FILE_PATH,
#     pagesize=A4,
#     leftMargin=1 * inch,
#     rightMargin=1 * inch,
#     topMargin=1 * inch,
#     bottomMargin=1 * inch
# )

# styles = getSampleStyleSheet()

# # ===============================
# # STYLES (STRICT COMPLIANCE)
# # ===============================
# TITLE = ParagraphStyle(
#     "TITLE",
#     fontName="Times-Bold",
#     fontSize=14,
#     alignment=TA_CENTER,
#     spaceAfter=10
# )

# SUBTITLE = ParagraphStyle(
#     "SUBTITLE",
#     fontName="Times-Bold",
#     fontSize=12,
#     alignment=TA_CENTER,
#     spaceAfter=12
# )

# BODY = ParagraphStyle(
#     "BODY",
#     fontName="Times-Roman",
#     fontSize=12,
#     leading=18,
#     alignment=TA_JUSTIFY,
#     spaceAfter=10
# )

# RIGHT = ParagraphStyle(
#     "RIGHT",
#     fontName="Times-Roman",
#     fontSize=12,
#     alignment=TA_RIGHT,
#     spaceAfter=10
# )

# story = []

# # ===============================
# # ADVOCATE HEADER BOX
# # ===============================
# advocate_box = Table(
#     [[
#         Paragraph(
#             "<b>ADVOCATE NAME</b><br/>"
#             "Office Address: _______________________________<br/>"
#             "Contact No.: _______________________________",
#             BODY
#         )
#     ]],
#     colWidths=[doc.width]
# )

# advocate_box.setStyle(TableStyle([
#     ("BOX", (0, 0), (-1, -1), 1, colors.black),
#     ("LEFTPADDING", (0, 0), (-1, -1), 8),
#     ("RIGHTPADDING", (0, 0), (-1, -1), 8),
#     ("TOPPADDING", (0, 0), (-1, -1), 6),
#     ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
# ]))

# story.append(advocate_box)
# story.append(Spacer(1, 16))

# # ===============================
# # LEGAL NOTICE TITLE
# # ===============================
# story.append(Paragraph("LEGAL NOTICE", TITLE))
# story.append(Paragraph("WITHOUT PREJUDICE", SUBTITLE))
# story.append(Spacer(1, 12))

# # ===============================
# # FROM / TO
# # ===============================
# story.append(Paragraph(
#     "<b>From:</b><br/>"
#     "Mr. Ramesh Sharma,<br/>"
#     "Through his Advocate.",
#     BODY
# ))

# story.append(Spacer(1, 10))

# story.append(Paragraph(
#     "<b>To,</b><br/>"
#     "Mr. Suresh Sharma,<br/>"
#     "Resident of ____________________________",
#     BODY
# ))

# story.append(Spacer(1, 12))

# # ===============================
# # SUBJECT
# # ===============================
# story.append(Paragraph(
#     "<b>Subject:</b> Legal Notice for Eviction and Damages for Illegal Possession "
#     "of Ancestral Property at Lucknow.",
#     BODY
# ))

# story.append(Spacer(1, 14))

# # ===============================
# # BODY CONTENT
# # ===============================
# story.append(Paragraph(
#     "<b>Sir,</b><br/><br/>"
#     "Under instructions and on behalf of my client <b>Mr. Ramesh Sharma</b>, "
#     "I hereby issue this legal notice as under:",
#     BODY
# ))

# story.append(Paragraph(
#     "1. That my client is the younger son of Late <b>Mr. Dhanraj Sharma</b>, "
#     "who was the absolute owner of the ancestral property situated at Lucknow.",
#     BODY
# ))

# story.append(Paragraph(
#     "2. That my client took care of his ailing father continuously for a period "
#     "of more than ten years prior to his demise, attending to all his medical "
#     "and personal needs.",
#     BODY
# ))

# story.append(Paragraph(
#     "3. That just prior to his death, Late Mr. Dhanraj Sharma, while in a sound "
#     "and disposing state of mind, duly executed a <b>Will</b> bequeathing the "
#     "entire ancestral property exclusively in favour of my client.",
#     BODY
# ))

# story.append(Paragraph(
#     "4. That after the demise of Late Mr. Dhanraj Sharma, you unlawfully disputed "
#     "the said Will by falsely alleging it to be forged, despite having been "
#     "excluded therefrom for valid reasons.",
#     BODY
# ))

# story.append(Paragraph(
#     "5. That you thereafter forcibly and illegally occupied the said property "
#     "without any right, title or interest and dispossessed my client.",
#     BODY
# ))

# story.append(Paragraph(
#     "6. That my client was constrained to file a suit for possession and permanent "
#     "injunction before the competent Civil Court, which was decided in favour "
#     "of my client by upholding the validity of the Will.",
#     BODY
# ))

# story.append(Paragraph(
#     "7. That though the Trial Court rightly decreed the suit, the Hon’ble High Court "
#     "reversed the said judgment on alleged suspicious circumstances, which decision "
#     "my client is in the process of challenging before the Hon’ble Supreme Court "
#     "by filing a Special Leave Petition under Article 136 of the Constitution of India.",
#     BODY
# ))

# story.append(Paragraph(
#     "8. That during pendency of further legal proceedings, your continued occupation "
#     "of the property is wholly illegal and amounts to trespass and unlawful enrichment.",
#     BODY
# ))

# story.append(Paragraph(
#     "9. You are hereby called upon to <b>vacate the suit property within 15 days</b> "
#     "from receipt of this notice and hand over peaceful possession to my client, "
#     "failing which appropriate civil and criminal proceedings shall be initiated "
#     "against you at your sole risk as to costs and consequences.",
#     BODY
# ))

# story.append(Paragraph(
#     "10. You are further called upon to compensate my client for damages arising "
#     "out of illegal occupation, harassment, and loss of lawful enjoyment of property.",
#     BODY
# ))

# # ===============================
# # FOOTER
# # ===============================
# story.append(Spacer(1, 20))

# story.append(Paragraph(
#     f"Place: Lucknow<br/>"
#     f"Date: {date.today().strftime('%d %B %Y')}",
#     BODY
# ))

# story.append(Spacer(1, 30))

# story.append(Paragraph(
#     "<b>Advocate for Mr. Ramesh Sharma</b>",
#     RIGHT
# ))

# # ===============================
# # BUILD PDF
# # ===============================
# doc.build(story)

# print("LEGAL NOTICE GENERATED SUCCESSFULLY")
# print(f"Saved at: {FILE_PATH}")



# 2)
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT, TA_LEFT
# from reportlab.lib.units import inch
# import os
# from datetime import date

# # ===============================
# # PATH SETUP
# # ===============================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# FILE_PATH = os.path.join(OUTPUT_DIR, "legal_notice_exact_format.pdf")

# # ===============================
# # DOCUMENT
# # ===============================
# doc = SimpleDocTemplate(
#     FILE_PATH,
#     pagesize=A4,
#     leftMargin=1*inch,
#     rightMargin=1*inch,
#     topMargin=0.8*inch,
#     bottomMargin=1*inch
# )

# styles = getSampleStyleSheet()

# ADV_NAME = ParagraphStyle(
#     "ADV_NAME",
#     fontName="Times-Bold",
#     fontSize=18,
#     alignment=TA_CENTER,
#     textColor="#9B1C1C",
#     spaceAfter=4
# )

# ADV_SUB = ParagraphStyle(
#     "ADV_SUB",
#     fontName="Times-Bold",
#     fontSize=11,
#     alignment=TA_CENTER,
#     spaceAfter=4
# )

# ADV_ADDR = ParagraphStyle(
#     "ADV_ADDR",
#     fontName="Times-Roman",
#     fontSize=10,
#     alignment=TA_CENTER,
#     spaceAfter=10
# )

# RIGHT = ParagraphStyle(
#     "RIGHT",
#     fontName="Times-Roman",
#     fontSize=11,
#     alignment=TA_RIGHT,
#     spaceAfter=8
# )

# CENTER_BOLD = ParagraphStyle(
#     "CENTER_BOLD",
#     fontName="Times-Bold",
#     fontSize=12,
#     alignment=TA_CENTER,
#     spaceAfter=6
# )

# BODY = ParagraphStyle(
#     "BODY",
#     fontName="Times-Roman",
#     fontSize=12,
#     leading=18,  # 1.5 spacing feel
#     alignment=TA_JUSTIFY,
#     spaceAfter=10
# )

# LEFT = ParagraphStyle(
#     "LEFT",
#     fontName="Times-Roman",
#     fontSize=12,
#     alignment=TA_LEFT,
#     spaceAfter=8
# )

# story = []

# # ===============================
# # ADVOCATE HEADER
# # ===============================
# story.append(Paragraph("MANNAM SUDHEER KUMAR", ADV_NAME))
# story.append(Paragraph("HIGH COURT ADVOCATE & THF MEMBER", ADV_SUB))
# story.append(Paragraph(
#     "SHOP NO. 1, S C S COMPLEX, OPP ABM DEGREE COLLEGE, ONGOL E – A.P.",
#     ADV_ADDR
# ))

# story.append(Paragraph("Cell: 9703082882", RIGHT))
# story.append(Spacer(1, 6))

# # ===============================
# # DATE
# # ===============================
# story.append(Paragraph(
#     f"Date: {date.today().strftime('%d-%m-%Y')}",
#     RIGHT
# ))
# story.append(Spacer(1, 10))

# # ===============================
# # NOTICE HEADINGS
# # ===============================
# story.append(Paragraph(
#     "BY REGD. POST WITH ACK. DUE",
#     CENTER_BOLD
# ))
# story.append(Paragraph(
#     "<u>LEGAL NOTICE</u>",
#     CENTER_BOLD
# ))
# story.append(Spacer(1, 16))

# # ===============================
# # TO BLOCK
# # ===============================
# story.append(Paragraph(
#     "<b>TO,</b><br/>"
#     "<b>THE BRANCH MANAGER,</b><br/>"
#     "CANARA BANK,<br/>"
#     "BRANCH : KAKARLA MAIN ROAD,<br/>"
#     "PODILI MANDAL, KAKARLA – 523253<br/>"
#     "PRAKASAM DISTRICT, A.P.",
#     LEFT
# ))
# story.append(Spacer(1, 12))

# # ===============================
# # SUBJECT
# # ===============================
# story.append(Paragraph(
#     "<b><u>SUBJECT : LEGAL NOTICE FOR DEFICIENCY OF YOUR SERVICE ON CYBER FRAUD "
#     "& DEBITED RS.10688/- WITHOUT KNOWLEDGE</u></b>",
#     LEFT
# ))
# story.append(Spacer(1, 14))

# # ===============================
# # BODY
# # ===============================
# story.append(Paragraph("Sir,", BODY))

# story.append(Paragraph(
#     "Under instructions and authority from my client Mr. Ambati Anandpaul "
#     "S/o A. Yesobu, Address Sivaranjunipeta, Kakarla, Podili (M), Prakasam "
#     "District, I serve upon you the following Legal Notice:",
#     BODY
# ))

# story.append(Paragraph(
#     "1. That my client has opened a student account bearing No. 36862200054118 "
#     "at Kakarla Branch with your bank on 12-10-2021 and has been doing his daily "
#     "transactions trusting your bank for safe and secure transactions.",
#     BODY
# ))

# story.append(Paragraph(
#     "2. That on 23-09-2024 my client received fake and fraudulent calls from "
#     "cyber criminals asking for OTP, ATM card and other bank information. "
#     "My client did not disclose any information and immediately disconnected "
#     "the calls.",
#     BODY
# ))

# story.append(Paragraph(
#     "3. To the utter shock and surprise of my client, your bank authorities "
#     "without proper verification of records and without prior notice debited "
#     "an amount of Rs.10,688/- from my client’s account.",
#     BODY
# ))

# story.append(Paragraph(
#     "4. That my client informed you several times regarding the fake notice and "
#     "illegal debit, but you have failed to take corrective action till date.",
#     BODY
# ))

# story.append(Paragraph(
#     "5. That due to your deficiency of service and negligence, my client has "
#     "suffered mental agony, financial loss and hardship and is entitled to "
#     "refund of the debited amount along with interest as per law.",
#     BODY
# ))

# # ===============================
# # CLOSING
# # ===============================
# story.append(Spacer(1, 16))
# story.append(Paragraph(
#     "Therefore, you are hereby called upon to refund the said amount immediately "
#     "failing which my client will be constrained to initiate appropriate legal "
#     "proceedings against you at your risk as to costs and consequences.",
#     BODY
# ))

# story.append(Spacer(1, 30))
# story.append(Paragraph(
#     "<b>Advocate for the Notice Sender</b>",
#     RIGHT
# ))

# # ===============================
# # BUILD
# # ===============================
# doc.build(story)

# print(" LEGAL NOTICE GENERATED IN EXACT FORMAT")
# print(f" Saved at: {FILE_PATH}")


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch
import os
from datetime import date

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_PATH = os.path.join(OUTPUT_DIR, "legal_notice_property_exact_format.pdf")

# ===============================
# DOCUMENT
# ===============================
doc = SimpleDocTemplate(
    FILE_PATH,
    pagesize=A4,
    leftMargin=1*inch,
    rightMargin=1*inch,
    topMargin=0.8*inch,
    bottomMargin=1*inch
)

styles = getSampleStyleSheet()

ADV_NAME = ParagraphStyle(
    "ADV_NAME",
    fontName="Times-Bold",
    fontSize=18,
    alignment=TA_CENTER,
    textColor="#9B1C1C",
    spaceAfter=4
)

ADV_SUB = ParagraphStyle(
    "ADV_SUB",
    fontName="Times-Bold",
    fontSize=11,
    alignment=TA_CENTER,
    spaceAfter=4
)

ADV_ADDR = ParagraphStyle(
    "ADV_ADDR",
    fontName="Times-Roman",
    fontSize=10,
    alignment=TA_CENTER,
    spaceAfter=10
)

RIGHT = ParagraphStyle(
    "RIGHT",
    fontName="Times-Roman",
    fontSize=11,
    alignment=TA_RIGHT,
    spaceAfter=8
)

CENTER_BOLD = ParagraphStyle(
    "CENTER_BOLD",
    fontName="Times-Bold",
    fontSize=12,
    alignment=TA_CENTER,
    spaceAfter=6
)

BODY = ParagraphStyle(
    "BODY",
    fontName="Times-Roman",
    fontSize=12,
    leading=18,
    alignment=TA_JUSTIFY,
    spaceAfter=10
)

LEFT = ParagraphStyle(
    "LEFT",
    fontName="Times-Roman",
    fontSize=12,
    alignment=TA_LEFT,
    spaceAfter=8
)

story = []

# ===============================
# ADVOCATE HEADER
# ===============================
story.append(Paragraph("ADITYA TAYDE", ADV_NAME))
story.append(Paragraph("HIGH COURT ADVOCATE & THF MEMBER", ADV_SUB))
story.append(Paragraph(
    "SHOP NO. 1, S C S COMPLEX, OPP ABM DEGREE COLLEGE, ONGOL E – A.P.",
    ADV_ADDR
))

story.append(Paragraph("Cell: 9703082882", RIGHT))
story.append(Spacer(1, 6))

# ===============================
# DATE
# ===============================
story.append(Paragraph(
    f"Date: {date.today().strftime('%d-%m-%Y')}",
    RIGHT
))
story.append(Spacer(1, 10))

# ===============================
# NOTICE HEADINGS
# ===============================
story.append(Paragraph(
    "BY REGD. POST WITH ACK. DUE",
    CENTER_BOLD
))
story.append(Paragraph(
    "<u>LEGAL NOTICE</u>",
    CENTER_BOLD
))
story.append(Spacer(1, 16))

# ===============================
# TO BLOCK
# ===============================
story.append(Paragraph(
    "<b>TO,</b><br/>"
    "<b>MR. SURESH SHARMA,</b><br/>"
    "Resident of ____________,<br/>"
    "Lucknow, Uttar Pradesh.",
    LEFT
))
story.append(Spacer(1, 12))

# ===============================
# SUBJECT
# ===============================
story.append(Paragraph(
    "<b><u>SUBJECT : LEGAL NOTICE FOR EVICTION FROM ANCESTRAL PROPERTY AND "
    "DAMAGES FOR ILLEGAL POSSESSION</u></b>",
    LEFT
))
story.append(Spacer(1, 14))

# ===============================
# BODY
# ===============================
story.append(Paragraph("Sir,", BODY))

story.append(Paragraph(
    "Under instructions and authority from my client <b>Mr. Ramesh Sharma</b>, "
    "S/o Late Mr. Dhanraj Sharma, Resident of ____________, Lucknow, Uttar Pradesh, "
    "I hereby serve upon you the following Legal Notice:",
    BODY
))

story.append(Paragraph(
    "1. That my client is the younger son of Late Mr. Dhanraj Sharma and had been "
    "taking continuous care of his ailing father for more than ten (10) years "
    "prior to his demise, providing medical, emotional and financial support.",
    BODY
))

story.append(Paragraph(
    "2. That appreciating the care and devotion rendered by my client, Late "
    "Mr. Dhanraj Sharma, while in a sound disposing state of mind, executed his "
    "last Will and Testament bequeathing the entire ancestral property situated "
    "at Lucknow exclusively in favour of my client.",
    BODY
))

story.append(Paragraph(
    "3. That after the demise of Late Mr. Dhanraj Sharma, you, being the elder "
    "brother, have falsely alleged that the said Will is forged and have forcibly "
    "occupied the said property without any lawful authority.",
    BODY
))

story.append(Paragraph(
    "4. That my client was constrained to file a suit for possession and permanent "
    "injunction before the competent Civil Court, which after full trial upheld "
    "the validity of the Will and decreed the suit in favour of my client.",
    BODY
))

story.append(Paragraph(
    "5. That though the Hon’ble High Court has reversed the Trial Court judgment "
    "on alleged suspicious circumstances, my client is in the process of "
    "challenging the same before the Hon’ble Supreme Court of India by filing "
    "a Special Leave Petition under Article 136 of the Constitution of India.",
    BODY
))

story.append(Paragraph(
    "6. That your continued illegal occupation of the property amounts to "
    "trespass, harassment and unlawful deprivation of my client’s lawful rights, "
    "causing him immense mental agony and financial loss.",
    BODY
))

# ===============================
# CLOSING
# ===============================
story.append(Spacer(1, 16))
story.append(Paragraph(
    "Therefore, you are hereby called upon to vacate the said ancestral property "
    "and hand over peaceful possession to my client within <b>15 (Fifteen) days</b> "
    "from the receipt of this notice, failing which my client shall be constrained "
    "to initiate appropriate civil and criminal proceedings against you at your "
    "sole risk as to costs and consequences.",
    BODY
))

story.append(Spacer(1, 30))
story.append(Paragraph(
    "<b>Advocate for the Notice Sender</b>",
    RIGHT
))

# ===============================
# BUILD
# ===============================
doc.build(story)

print("LEGAL NOTICE (PROPERTY DISPUTE) GENERATED IN EXACT FORMAT")
print(f"Saved at: {FILE_PATH}")
