"""
Seed realistic demo data for LegalAI platform.
Run: python backend/manage.py shell < backend/seed_data.py
Or:  python backend/seed_data.py (standalone)
"""
import os
import sys
import django
from decimal import Decimal

# ── Django setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legalai.settings")
django.setup()

from apps.cases.models import Case
from apps.timeline.models import TimelineEvent, MedicalSummary
from apps.drafts.models import Draft

print("Seeding LegalAI demo data...")

# ── Clear existing demo data ──────────────────────────────────────────────────
Case.objects.all().delete()
print("  Cleared existing data.")

# ── Case 1: MACT — Kumar vs National Insurance ────────────────────────────────
case1 = Case.objects.create(
    title          = "Kumar vs National Insurance Co.",
    case_no        = "M.A.C.P. No. 882/2024",
    case_type      = Case.MACT,
    status         = Case.ACTIVE,
    description    = "Motor accident claim arising out of road traffic accident on 12 March 2024 at ABC Road, Pune.",
    client_name    = "Dummy Kumar",
    client_age     = "34 Years",
    client_address = "House No. 123, ABC Colony, Shivaji Nagar, Pune – 411005",
    father_name    = "Ram Kumar",
    occupation     = "Driver",
    accident_date  = "2024-03-12",
    accident_place = "ABC Road, Pune, Maharashtra",
    vehicle_no     = "MH-12-AB-4567",
    fir_no         = "FIR No. 142/2024",
    hospital       = "Sanjeevani Hospital, Pune",
    tribunal       = "Motor Accident Claims Tribunal, Pune",
    claim_amount   = Decimal("850000.00"),
    injuries       = [
        "Fracture of Right Femur",
        "Head Injury (Minor Concussion)",
        "Multiple Abrasions on Left Arm",
    ],
    compensation   = [
        {"head": "Hospital Bills & Medical Expenses",    "amount": "₹ 1,25,000"},
        {"head": "Future Medical Expenses",              "amount": "₹ 75,000"},
        {"head": "Loss of Income during Treatment",      "amount": "₹ 1,00,000"},
        {"head": "Pain and Suffering",                   "amount": "₹ 1,00,000"},
        {"head": "Loss of Amenities of Life",            "amount": "₹ 75,000"},
        {"head": "Special Diet, Attendant & Conveyance", "amount": "₹ 90,000"},
    ],
)
print(f"  Created Case 1: {case1}")

# Timeline events for Case 1
events1 = [
    TimelineEvent(
        case        = case1,
        date        = "2024-03-12",
        title       = "Neighbors Emergency Center",
        doctor      = "Dr. Fronk",
        description = "Patient was evaluated by Dr. Fronk who performed a physical examination, documented significant pain levels, and prescribed new medications including Gabapentin, Medrol, and Tizandine.",
        tag         = TimelineEvent.EMERGENCY,
        medications = ["Gabapentin", "Medrol", "Tizandine"],
        order       = 1,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-03-19",
        title       = "Pain Care Physicians",
        doctor      = "Dr. Benjamin Fronk",
        description = "Specialist consultation for ongoing pain management. Physical examination performed. Significant pain levels documented. Medication regimen continued and adjusted.",
        tag         = TimelineEvent.SPECIALIST,
        medications = ["Gabapentin 300mg", "Medrol 4mg", "Tizandine 4mg"],
        order       = 2,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-03-24",
        title       = "Neighbors Emergency Center",
        doctor      = "Lo, Long, MD",
        description = "Patient received emergency treatment for acute traumatic thoracic back pain including pain medications, anti-inflammatory medication, and anti-nausea medication with improvement in symptoms.",
        tag         = TimelineEvent.EMERGENCY,
        medications = ["IV Pain Medications", "Anti-inflammatory", "Anti-nausea"],
        order       = 3,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-03-27",
        title       = "Pro-Care Medical Center",
        doctor      = "Dr. Smith",
        description = "Chiropractic evaluation and treatment for spinal injuries sustained in the accident. Patient reported moderate improvement in mobility after session.",
        tag         = TimelineEvent.CHIROPRACTIC,
        medications = [],
        order       = 4,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-04-05",
        title       = "Sanjeevani Hospital, Pune",
        doctor      = "Dr. R. Mehta (Orthopedic)",
        description = "Orthopedic consultation for fracture of right femur. ORIF (Open Reduction Internal Fixation) surgery recommended. Pre-operative workup initiated including blood tests, X-rays, and ECG.",
        tag         = TimelineEvent.SPECIALIST,
        medications = ["Analgesics", "Antibiotics (prophylactic)"],
        order       = 5,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-04-10",
        title       = "Sanjeevani Hospital — Surgery",
        doctor      = "Dr. R. Mehta (Orthopedic)",
        description = "ORIF surgery performed for right femur fracture under general anesthesia. Surgery successful. Patient admitted to ICU post-operatively for monitoring.",
        tag         = TimelineEvent.SURGERY,
        medications = ["Post-op Antibiotics", "Pain Management Protocol", "Anticoagulants"],
        order       = 6,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-04-18",
        title       = "Sanjeevani Hospital — Discharge",
        doctor      = "Dr. R. Mehta",
        description = "Patient discharged after 8 days of post-operative care. Wound healing satisfactory. Advised bed rest for 6 weeks, physiotherapy, and follow-up after 2 weeks.",
        tag         = TimelineEvent.DISCHARGE,
        medications = ["Oral Antibiotics", "Calcium + Vitamin D", "Analgesics"],
        order       = 7,
    ),
    TimelineEvent(
        case        = case1,
        date        = "2024-05-02",
        title       = "Physiotherapy Center, Pune",
        doctor      = "Physiotherapist Sharma",
        description = "Commenced physiotherapy sessions for post-operative rehabilitation. Range of motion exercises initiated. Patient tolerating well.",
        tag         = TimelineEvent.PHYSIOTHERAPY,
        medications = [],
        order       = 8,
    ),
]
TimelineEvent.objects.bulk_create(events1)
print(f"  Created {len(events1)} timeline events for Case 1.")

# Medical Summary for Case 1
MedicalSummary.objects.create(
    case             = case1,
    injuries         = [
        "Fracture of Right Femur (S72.0)",
        "Head Injury — Minor Concussion (S09.9)",
        "Multiple Abrasions — Left Arm (S40.0)",
        "Acute Traumatic Thoracic Back Pain (M54.6)",
    ],
    treatments       = [
        {"type": "Emergency Treatment", "detail": "Pain management, anti-inflammatory, anti-nausea"},
        {"type": "Surgery",             "detail": "ORIF — Open Reduction Internal Fixation, Right Femur"},
        {"type": "Physiotherapy",       "detail": "Post-operative rehabilitation, 12 sessions"},
        {"type": "Chiropractic",        "detail": "Spinal adjustment, 4 sessions"},
    ],
    medications      = ["Gabapentin 300mg", "Medrol 4mg", "Tizandine 4mg", "Calcium + Vitamin D"],
    icd_codes        = [
        {"code": "S72.0",  "desc": "Fracture of neck of femur"},
        {"code": "S09.9",  "desc": "Unspecified injury of head"},
        {"code": "S40.0",  "desc": "Contusion of shoulder and upper arm"},
        {"code": "M54.6",  "desc": "Pain in thoracic spine"},
    ],
    economic_damages = {
        "hospital_bills":    125000,
        "medicines":         35000,
        "physiotherapy":     18000,
        "future_medical":    75000,
        "income_loss":       100000,
        "total_economic":    353000,
    },
    non_economic_damages = {
        "pain_suffering":    100000,
        "loss_amenities":    75000,
        "attendant_charges": 45000,
        "conveyance_diet":   45000,
        "total_non_economic": 265000,
    },
    missing_docs     = [
        "Disability Certificate from Government Hospital",
        "Income Proof (Salary Slips / ITR)",
        "Final Police Charge Sheet",
        "Insurance Policy Copy",
    ],
    case_strength    = "Strong",
    legal_strategy   = "File MACT petition immediately. Obtain disability certificate. Attach all medical bills. Cite Sarla Verma formula for income loss calculation. Demand interim compensation under Section 140.",
    notes            = "Strong MACT case. Clear negligence established via FIR. Multiple injuries documented. Surgery performed. Claim of ₹8,50,000 is well-supported by medical evidence.",
)
print("  Created Medical Summary for Case 1.")

# Draft for Case 1
Draft.objects.create(
    case         = case1,
    title        = "Claim Petition u/s 166 MV Act — Kumar vs National Insurance",
    draft_type   = Draft.CLAIM_PETITION,
    content      = """BEFORE THE HON'BLE MOTOR ACCIDENT CLAIMS TRIBUNAL, PUNE

M.A.C.P. No. ______ of 2024

BETWEEN

Mr. Dummy Kumar
S/o Ram Kumar, Age: 34 Years
Resident of: House No. 123, ABC Colony, Shivaji Nagar, Pune – 411005.
                                                                    …CLAIMANT

AND

1. Mr. Anil Sharma, Driver of Car No. MH-12-AB-4567
2. Mr. Rahul Jain, Owner of Car No. MH-12-AB-4567
3. XYZ General Insurance Co. Ltd., Insurer of Car No. MH-12-AB-4567
                                                                    …RESPONDENTS

CLAIM PETITION UNDER SECTION 166 OF THE MOTOR VEHICLES ACT, 1988

MAY IT PLEASE THIS HON'BLE TRIBUNAL

1. FACTS OF THE CASE

(a) On 12th March 2024, at about 2:30 PM, the Petitioner was driving his two-wheeler bearing registration No. MH-01-XY-123 on ABC Road, Pune, when the Respondent No.1 driving Car No. MH-12-AB-4567 in a rash and negligent manner dashed the petitioner's vehicle from behind.

(b) Due to the violent impact, the petitioner fell on the road and sustained multiple grievous injuries. He was immediately shifted to Sanjeevani Hospital, Pune by bystanders and police.

2. PRAYER

The petitioner humbly prays that this Hon'ble Tribunal may be pleased to award compensation of ₹ 8,50,000/- along with interest @ 9% p.a. and costs.""",
    version      = 1,
    status       = Draft.STATUS_DRAFT,
    ai_generated = False,
    ref_no       = "2024-1-CP",
)
print("  Created Draft for Case 1.")

# ── Case 2: Property Dispute ──────────────────────────────────────────────────
case2 = Case.objects.create(
    title          = "Ramesh vs Suresh — Ancestral Property Dispute",
    case_no        = "CS No. 45/2024",
    case_type      = Case.PROPERTY,
    status         = Case.PENDING,
    description    = "Property dispute regarding ancestral property at Lucknow. Will validity challenged.",
    client_name    = "Ramesh Sharma",
    client_age     = "52 Years",
    client_address = "Lucknow, Uttar Pradesh",
    father_name    = "Late Dhanraj Sharma",
    occupation     = "Businessman",
    accident_date  = None,
    accident_place = "Lucknow, UP",
    tribunal       = "Civil Court, Lucknow",
    claim_amount   = Decimal("4500000.00"),
    injuries       = [],
    compensation   = [
        {"head": "Property Value",   "amount": "₹ 40,00,000"},
        {"head": "Damages & Losses", "amount": "₹ 5,00,000"},
    ],
)
print(f"  Created Case 2: {case2}")

# ── Case 3: Consumer — Cyber Fraud ────────────────────────────────────────────
case3 = Case.objects.create(
    title          = "Anandpaul vs Canara Bank — Cyber Fraud",
    case_no        = "CC No. 12/2024",
    case_type      = Case.CONSUMER,
    status         = Case.ACTIVE,
    description    = "Consumer complaint against Canara Bank for deficiency of service in cyber fraud case. Unauthorized debit of ₹10,688/-.",
    client_name    = "Ambati Anandpaul",
    client_age     = "28 Years",
    client_address = "Sivaranjunipeta, Kakarla, Podili, Prakasam District, A.P.",
    father_name    = "A. Yesobu",
    occupation     = "Student",
    accident_date  = "2024-09-23",
    accident_place = "Kakarla, A.P.",
    fir_no         = "Cyber Crime Report No. CC/2024/1234",
    tribunal       = "District Consumer Disputes Redressal Commission, Prakasam",
    claim_amount   = Decimal("40688.00"),
    injuries       = [],
    compensation   = [
        {"head": "Fraudulent Debit Amount",   "amount": "₹ 10,688"},
        {"head": "Mental Agony & Harassment", "amount": "₹ 25,000"},
        {"head": "Legal Costs",               "amount": "₹ 5,000"},
    ],
)
print(f"  Created Case 3: {case3}")

print("\n✅ Seed data complete!")
print(f"   Cases created: 3")
print(f"   Timeline events: {len(events1)}")
print(f"   Medical summaries: 1")
print(f"   Drafts: 1")
print("\n   Run the server: python backend/manage.py runserver 8000")
print("   Admin panel:    http://127.0.0.1:8000/admin/")
print("   API root:       http://127.0.0.1:8000/api/")
