"""
Professional Medical Record PDF Generator
Creates a realistic medical record for motor vehicle accident testing
"""

from fpdf import FPDF
from datetime import datetime, timedelta
import random

class MedicalRecordPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'CITY GENERAL HOSPITAL', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, '123 Medical Center Drive, Mumbai - 400001', 0, 1, 'C')
        self.cell(0, 5, 'Phone: +91-22-1234-5678 | Emergency: 108', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_medical_record(filename="test_medical_record.pdf"):
    pdf = MedicalRecordPDF()
    pdf.add_page()
    
    # Accident and admission dates
    accident_date = datetime.now() - timedelta(days=7)
    admission_date = accident_date
    discharge_date = accident_date + timedelta(days=5)
    
    # Patient Information Section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'MEDICAL LEGAL CASE (MLC) REPORT', 0, 1, 'C')
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'PATIENT INFORMATION', 0, 1)
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 10)
    patient_info = [
        ['MLC No.:', 'MLC/2026/00542', 'Date of Admission:', admission_date.strftime('%d-%m-%Y')],
        ['Patient Name:', 'Mr. Rajesh Kumar Sharma', 'Age/Sex:', '34 Years / Male'],
        ['Address:', '456, Sector 12, Vashi, Navi Mumbai', 'Contact:', '+91-9876543210'],
        ['Emergency Contact:', 'Mrs. Priya Sharma (Wife)', 'Phone:', '+91-9876543211'],
        ['Blood Group:', 'O Positive', 'Aadhaar No.:', 'XXXX-XXXX-4523']
    ]
    
    for row in patient_info:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(45, 6, row[0], 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(50, 6, row[1], 0, 0)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(45, 6, row[2], 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(50, 6, row[3], 0, 1)
    
    pdf.ln(5)
    
    # Accident Details
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'ACCIDENT DETAILS', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f'''Date & Time of Accident: {accident_date.strftime('%d-%m-%Y, %I:%M %p')}
Place of Accident: Mumbai-Pune Expressway, Near Panvel Toll Plaza
Type of Vehicle: Two-wheeler (Honda Activa - MH 02 AX 1234)
Nature of Accident: Road Traffic Accident - Patient hit by a four-wheeler from behind
Police Station Informed: Panvel City Police Station, FIR No. 245/2026
Brought by: 108 Ambulance Service
Time of Arrival at Hospital: {(accident_date + timedelta(hours=1, minutes=15)).strftime('%I:%M %p')}
Condition on Arrival: Conscious, Moderate distress, Active bleeding from head injury''')
    
    pdf.ln(5)
    
    # Clinical Examination
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'INITIAL CLINICAL EXAMINATION', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Vital Signs:', 0, 1)
    pdf.set_font('Arial', '', 10)
    vitals = [
        'Blood Pressure: 140/90 mmHg',
        'Pulse Rate: 98 bpm (Regular)',
        'Respiratory Rate: 22/min',
        'Temperature: 98.6°F',
        'SpO2: 95% on room air',
        'GCS Score: 14/15 (E4V4M6)'
    ]
    for vital in vitals:
        pdf.cell(10, 5, '', 0, 0)
        pdf.cell(0, 5, f'- {vital}', 0, 1)
    
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Physical Examination Findings:', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    findings = [
        'Head: Lacerated wound 5cm x 2cm on right parietal region with active bleeding',
        'Face: Multiple abrasions on right cheek and forehead',
        'Chest: Tenderness over right 6th and 7th ribs, respiratory movements reduced on right side',
        'Abdomen: Soft, non-tender, no guarding or rigidity',
        'Right Upper Limb: Deformity of right forearm, swelling, tenderness, crepitus positive',
        'Right Lower Limb: Abrasions over right knee, tenderness over right ankle',
        'Left Limbs: Normal examination',
        'Spine: No tenderness or deformity',
        'Neurological: Alert and oriented, pupils equal and reactive, no focal deficit'
    ]
    for finding in findings:
        pdf.cell(10, 5, '', 0, 0)
        pdf.cell(0, 5, f'- {finding}', 0, 1)
    
    pdf.ln(5)
    
    # Investigations
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'INVESTIGATIONS CONDUCTED', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, '1. Radiology:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(10, 5, '', 0, 0)
    pdf.cell(0, 5, '- X-ray Skull AP/Lateral: No fracture seen, soft tissue swelling present', 0, 1)
    pdf.cell(10, 5, '', 0, 0)
    pdf.cell(0, 5, '- X-ray Chest PA: Fracture right 6th and 7th ribs, no pneumothorax', 0, 1)
    pdf.cell(10, 5, '', 0, 0)
    pdf.cell(0, 5, '- X-ray Right Forearm AP/Lateral: Fracture shaft of radius and ulna, displaced', 0, 1)
    pdf.cell(10, 5, '', 0, 0)
    pdf.cell(0, 5, '- X-ray Right Ankle: Soft tissue swelling, no fracture', 0, 1)
    
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, '2. CT Scan Head: No intracranial bleed, no skull fracture', 0, 1)
    
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, '3. Laboratory Investigations:', 0, 1)
    pdf.set_font('Arial', '', 10)
    labs = [
        'Hemoglobin: 11.2 g/dL',
        'TLC: 13,500/cumm',
        'Blood Sugar (Random): 124 mg/dL',
        'Blood Urea: 32 mg/dL',
        'Serum Creatinine: 1.1 mg/dL',
        'Alcohol Test: Negative'
    ]
    for lab in labs:
        pdf.cell(10, 5, '', 0, 0)
        pdf.cell(0, 5, f'- {lab}', 0, 1)
    
    pdf.ln(5)
    
    # Add new page for treatment
    pdf.add_page()
    
    # Treatment Given
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'TREATMENT ADMINISTERED', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Emergency Management:', 0, 1)
    pdf.set_font('Arial', '', 10)
    emergency = [
        'Primary survey and resuscitation as per ATLS protocol',
        'IV line secured, IV fluids started (Ringer Lactate)',
        'Tetanus Toxoid 0.5 ml IM given',
        'Analgesics: Inj. Diclofenac 75mg IM',
        'Antibiotics: Inj. Ceftriaxone 1g IV BD started',
        'Head wound cleaned, sutured (8 stitches) under local anesthesia',
        'Right forearm fracture - closed reduction and above elbow POP cast applied',
        'Chest: Supportive management, incentive spirometry advised'
    ]
    for item in emergency:
        pdf.cell(10, 5, '', 0, 0)
        pdf.cell(0, 5, f'- {item}', 0, 1)
    
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Hospital Course:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, '''Patient was admitted to Orthopedic ward. Daily wound dressing done. Pain management continued. 
Physiotherapy for chest and limbs started from Day 2. Patient showed good recovery. Vitals stable. 
No signs of infection. Chest pain reduced. Patient able to move around with support by Day 4.''')
    
    pdf.ln(5)
    
    # Diagnosis
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'FINAL DIAGNOSIS', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 10)
    diagnosis = [
        '1. History of Road Traffic Accident',
        '2. Lacerated wound right parietal region - Sutured (Simple injury under IPC 325)',
        '3. Fracture shaft of right radius and ulna - Managed conservatively',
        '4. Fracture right 6th and 7th ribs',
        '5. Multiple abrasions face and right lower limb'
    ]
    for diag in diagnosis:
        pdf.cell(10, 5, '', 0, 0)
        pdf.cell(0, 5, diag, 0, 1)
    
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Nature of Injury: Simple (Non-Grievous) as per IPC Section 325', 0, 1)
    
    pdf.ln(5)
    
    # Discharge Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DISCHARGE SUMMARY', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f'''Date of Discharge: {discharge_date.strftime('%d-%m-%Y')}
Condition on Discharge: Stable, Ambulatory with support
Duration of Hospitalization: 5 days

Advice on Discharge:
- Continue oral antibiotics (Tab. Cefixime 200mg BD) for 5 days
- Analgesics: Tab. Paracetamol 650mg TDS as needed for pain
- Keep wound clean and dry, suture removal after 7 days
- POP cast to be kept for 6 weeks, follow-up X-ray after 6 weeks
- Avoid strenuous activities, adequate rest advised
- Follow-up in Orthopedic OPD after 1 week
- Medical fitness for work after 8-10 weeks
- Permanent disability: To be assessed after complete healing (approx 3 months)

Medical Certificate: Medical Leave recommended for 45 days from date of accident.''')
    
    pdf.ln(5)
    
    # Medical Officer Details
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Examined and Treated by:', 0, 1)
    pdf.ln(3)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Dr. Amit Deshmukh', 0, 1)
    pdf.cell(0, 5, 'MBBS, MS (Ortho)', 0, 1)
    pdf.cell(0, 5, 'Consultant Orthopedic Surgeon', 0, 1)
    pdf.cell(0, 5, 'Reg. No.: MCI-12345', 0, 1)
    pdf.cell(0, 5, f'Date: {discharge_date.strftime("%d-%m-%Y")}', 0, 1)
    
    pdf.ln(10)
    pdf.cell(0, 5, 'Signature: _______________________', 0, 1)
    pdf.cell(0, 5, '(Medical Officer)', 0, 1)
    
    # Save PDF
    pdf.output(filename)
    print(f"✅ Medical record PDF created: {filename}")
    return filename

if __name__ == "__main__":
    filename = create_medical_record("test_medical_record.pdf")
    print(f"\n📄 Professional medical record generated!")
    print(f"📁 Location: {filename}")
    print(f"\n🧪 You can now test this with:")
    print(f"   • Legal AI: http://127.0.0.1:8000")
    print(f"   • MedCompliance: http://127.0.0.1:7000/analyze")
