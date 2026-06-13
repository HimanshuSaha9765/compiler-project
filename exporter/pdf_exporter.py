from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

def generate_pdf_report(analysis_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    y = height - 30*mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, y, "CompilerX - Analysis Report")
    y -= 10*mm
    
    d = analysis_data.get('diagnostics', {})
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, y, f"Health Score: {d.get('health_score', '--')} ({d.get('health_label','')})"); y -= 6*mm
    c.drawString(20*mm, y, f"Summary: {d.get('summary','')}"); y -= 8*mm
    
    lexer = analysis_data.get('lexer', {})
    parser = analysis_data.get('parser', {})
    c.drawString(20*mm, y, f"Tokens: {lexer.get('total_count',0)}  |  Syntax Errors: {parser.get('total_errors',0)}"); y -= 10*mm
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, "Top Tokens:"); y -= 6*mm
    c.setFont("Helvetica", 9)
    for t in lexer.get('tokens', [])[:30]:
        if y < 25*mm:
            c.showPage(); y = height - 25*mm; c.setFont("Helvetica", 9)
        txt = f"{t['token_id']:3}  {t['token_value'][:20]:20}  {t['token_type'][:12]:12}  Line {t['line_number']}"
        c.drawString(20*mm, y, txt)
        y -= 4.5*mm
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
