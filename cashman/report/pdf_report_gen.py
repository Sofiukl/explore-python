from fpdf import FPDF


class PdfReportGenerator:
    def __init__(self, filename):
        self.filename = filename

    def generate(self, data):
        pdf=FPDF(format='letter', unit='in')
        pdf.add_page()
        pdf.set_font('Times','',10.0) 
        epw = pdf.w - 2*pdf.l_margin
        col_width = epw/2

        
        # Text height is the same as current font size
        th = pdf.font_size
        
        pdf.ln(4*th)
        pdf.set_font('Times','B',14.0) 
        pdf.cell(epw, 0.0, 'Your cashman transactions', align='C')
        pdf.set_font('Times','',10.0) 
        pdf.ln(0.5)
        
        # Here we add more padding by passing 2*th as height
        for row in data:
            for datum in row:
                pdf.cell(col_width, 2*th, str(datum), border=1)
        
            pdf.ln(2*th)
        
        pdf.output(self.filename,'F')
