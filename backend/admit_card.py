"""PDF admit card generation using reportlab - PWNSAT 2026 format."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line, Rect
from reportlab.graphics import renderPDF
from io import BytesIO
from datetime import datetime
import logging
import os

logger = logging.getLogger("admit_card")

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "pw-logo.PNG")


class AdmitCardGenerator:
    """Generate PDF admit cards using reportlab - PWNSAT 2026 format."""
    
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN = 0.8 * cm
    TOP_MARGIN = 0.5 * cm
    
    # Colors matching the design
    RED_COLOR = colors.HexColor('#C41E3A')
    DARK_TEXT = colors.HexColor('#333333')
    
    @staticmethod
    def generate_pdf(
        roll_no: str,
        name: str,
        father_name: str,
        medium: str,
        course: str,
        exam_date: str,
        exam_centre: str
    ) -> BytesIO:
        """
        Generate admit card PDF as BytesIO matching PWNSAT 2026 format.
        
        Args:
            roll_no: Student roll number
            name: Student name
            father_name: Father's name
            medium: Medium of exam
            course: Course opted
            exam_date: Date of exam
            exam_centre: Exam centre
            
        Returns:
            BytesIO object containing PDF
        """
        try:
            # Create PDF in memory
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=AdmitCardGenerator.MARGIN,
                leftMargin=AdmitCardGenerator.MARGIN,
                topMargin=AdmitCardGenerator.TOP_MARGIN,
                bottomMargin=AdmitCardGenerator.MARGIN
            )
            
            # Container for PDF elements
            story = []
            styles = getSampleStyleSheet()
            
            # ===== HEADER WITH LOGO =====
            # Check if logo exists
            if os.path.exists(LOGO_PATH):
                try:
                    logo = Image(LOGO_PATH, width=18*cm, height=3*cm)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                except Exception as e:
                    logger.warning(f"Could not load logo: {e}")
                    # Fallback header text
                    header_style = ParagraphStyle(
                        'Header',
                        parent=styles['Heading1'],
                        fontSize=18,
                        textColor=AdmitCardGenerator.RED_COLOR,
                        alignment=TA_CENTER,
                        fontName='Helvetica-Bold',
                        spaceAfter=6
                    )
                    story.append(Paragraph("SVPS &nbsp;&nbsp;&nbsp; PW VIDYAPEETH", header_style))
            else:
                # Fallback header text
                header_style = ParagraphStyle(
                    'Header',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=AdmitCardGenerator.RED_COLOR,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold',
                    spaceAfter=6
                )
                story.append(Paragraph("SVPS &nbsp;&nbsp;&nbsp; PW VIDYAPEETH", header_style))
            
            # ===== MAIN TITLE =====
            main_title_style = ParagraphStyle(
                'MainTitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=AdmitCardGenerator.DARK_TEXT,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=4
            )
            story.append(Paragraph("PHYSICS WALLAH NATIONAL SCHOLARSHIP CUM ADMISSION TEST - 2026", main_title_style))
            
            # ===== PWNSAT (Admit Card) =====
            admit_title_style = ParagraphStyle(
                'AdmitTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=AdmitCardGenerator.RED_COLOR,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=8
            )
            story.append(Paragraph("PWNSAT (Admit Card)", admit_title_style))
            
            # ===== PHOTO BOX (right aligned) =====
            photo_box_style = ParagraphStyle(
                'PhotoBox',
                parent=styles['Normal'],
                fontSize=9,
                textColor=AdmitCardGenerator.DARK_TEXT,
                alignment=TA_CENTER,
                leading=12
            )
            
            photo_text = Paragraph(
                "Affix your<br/>recent passport<br/>size colour<br/>photograph<br/>here.",
                photo_box_style
            )
            
            # Create table with photo box centered
            photo_table_data = [[photo_text]]
            photo_table = Table(photo_table_data, colWidths=[4*cm], rowHeights=[3*cm])
            photo_table.setStyle(TableStyle([
                ('BOX', (0, 0), (0, 0), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ]))
            photo_table.hAlign = 'CENTER'
            story.append(photo_table)
            
            story.append(Spacer(1, 0.3 * cm))
            
            # ===== FORM FIELDS WITH UNDERLINES =====
            field_label_style = ParagraphStyle(
                'FieldLabel',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                fontName='Helvetica-Bold'
            )
            
            field_value_style = ParagraphStyle(
                'FieldValue',
                parent=styles['Normal'],
                fontSize=12,
                textColor=AdmitCardGenerator.DARK_TEXT,
                fontName='Helvetica'
            )
            
            # Create form fields
            fields = [
                ("Roll No.", roll_no),
                ("Name of the Student", name),
                ("Father's Name", father_name),
                ("Medium", medium),
                ("Course Opted for", course),
                ("Date of Exam", exam_date),
                ("Exam Centre", exam_centre),
            ]
            
            for label, value in fields:
                # Create row with label and value with underline
                field_data = [[
                    Paragraph(f"<b>{label}</b>", field_label_style),
                    Paragraph(value, field_value_style)
                ]]
                
                field_table = Table(field_data, colWidths=[5*cm, 12*cm])
                field_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(field_table)
            
            story.append(Spacer(1, 0.4 * cm))
            
            # ===== INSTRUCTIONS SECTION =====
            instructions_title = ParagraphStyle(
                'InstructionsTitle',
                parent=styles['Heading2'],
                fontSize=11,
                textColor=AdmitCardGenerator.RED_COLOR,
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("INSTRUCTIONS FOR CANDIDATES", instructions_title))
            
            instructions_text = ParagraphStyle(
                'InstructionsText',
                parent=styles['Normal'],
                fontSize=9,
                spaceAfter=2,
                leftIndent=0.3 * cm,
                textColor=AdmitCardGenerator.DARK_TEXT
            )
            
            instructions = [
                "1. This admit card must be brought to the examination centre.",
                "2. Arrive at the examination centre 30 minutes before the examination starts.",
                "3. Carry a valid identity proof (Aadhar/School ID) along with this admit card.",
                "4. Write your roll number on all answer sheets.",
                "5. Follow all instructions given by the invigilator.",
                "6. Any malpractice will result in disqualification.",
                "7. Mobile phones and electronic devices are strictly prohibited inside the exam hall.",
            ]
            
            for instruction in instructions:
                story.append(Paragraph(instruction, instructions_text))
            
            story.append(Spacer(1, 0.5 * cm))
            
            # ===== SIGNATURE SECTION =====
            signature_data = [
                ['_______________________', '_______________________'],
                ["Student's Signature", "Authorized Signature"]
            ]
            
            signature_table = Table(
                signature_data,
                colWidths=[9 * cm, 9 * cm]
            )
            signature_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('HALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(signature_table)
            
            # Build PDF
            doc.build(story)
            
            # Reset buffer position
            pdf_buffer.seek(0)
            logger.info(f"Admit card generated for roll_no: {roll_no}")
            
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"Error generating admit card: {str(e)}")
            raise
