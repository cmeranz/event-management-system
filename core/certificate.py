from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from datetime import datetime
import os
from django.conf import settings


def generate_certificate(application):

    event = application.application_event or application.event_ID
    student = application.application_applicant
    
    if not event or not student:
        raise ValueError("Application must have both event and student")
    
    # Create directory if it doesn't exist
    cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    # Generate filename
    filename = f"cert_{application.id}_{student.id}_{event.id}.pdf"
    filepath = os.path.join(cert_dir, filename)
    relative_path = os.path.join('certificates', filename)
    
    # Create landscape PDF
    page_width, page_height = landscape(letter)
    
    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    
    # Set font and colors
    c.setFont("Helvetica-Bold", 48)
    
    # Add decorative border
    c.setLineWidth(3)
    c.setStrokeColorRGB(11/255, 42/255, 80/255)  # UM Blue
    c.rect(0.4 * inch, 0.4 * inch, page_width - 0.8 * inch, page_height - 0.8 * inch)
    
    c.setLineWidth(1)
    c.rect(0.5 * inch, 0.5 * inch, page_width - 1.0 * inch, page_height - 1.0 * inch)
    
    # Title
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(page_width / 2, page_height - 1.5 * inch, "Certificate of Attendance")
    
    # Subtitle
    c.setFont("Helvetica", 18)
    c.setFillColorRGB(11/255, 42/255, 80/255)
    c.drawCentredString(page_width / 2, page_height - 2.0 * inch, "UM Engage")
    
    # Main text
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(page_width / 2, page_height - 2.8 * inch, "This certificate is proudly presented to")
    
    # Student name
    c.setFont("Helvetica-Bold", 32)
    student_name = student.get_full_name() or student.username
    c.drawCentredString(page_width / 2, page_height - 3.5 * inch, student_name)
    
    # Event details
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(
        page_width / 2, 
        page_height - 4.2 * inch, 
        f"For successful completion and attendance of"
    )
    
    # Event title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - 4.7 * inch, event.event_title)
    
    # Event details
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0, 0, 0)
    event_date = event.event_date.strftime("%B %d, %Y")
    c.drawCentredString(page_width / 2, page_height - 5.2 * inch, f"Event Date: {event_date}")
    
    
    # Certificate ID and date
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0, 0)
    current_date = datetime.now().strftime("%B %d, %Y")
    c.drawString(0.6 * inch, 0.7 * inch, f"Certificate ID: {application.id}")
    c.drawString(page_width - 2.5 * inch, 0.7 * inch, f"Generated: {current_date}")
    
    # Save the PDF
    c.save()
    
    return relative_path
