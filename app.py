from flask import Flask, render_template, request, make_response, jsonify
import pdfkit
import io
import os
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/scan_uploaded_pdf', methods=['POST'])
def scan_uploaded_pdf():
    if 'resume_file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['resume_file']
    jd_text = request.form.get('jd', '')
    try:
        pdf_content = file.read()
        resume_text = extract_text(io.BytesIO(pdf_content))
        text_list = [resume_text, jd_text]
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(text_list)
        match_percentage = round(cosine_similarity(count_matrix)[0][1] * 100, 2)
        
        jd_words = set(jd_text.lower().replace(',', '').replace('.', '').split())
        resume_words = set(resume_text.lower().replace(',', '').replace('.', '').split())
        missing = [word for word in jd_words if word not in resume_words and len(word) > 3]
        
        return jsonify({'score': match_percentage, 'missing': missing[:10]})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', '').upper()
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    links = request.form.get('links', '')
    objective = request.form.get('objective', '')
    skills = request.form.get('skills', '')
    experience = request.form.get('experience', '')
    template_style = request.form.get('template_style', 'classic')
    action = request.form.get('action')

    # Multi-Entry Processing
    colleges = request.form.getlist('college')
    edu_dates = request.form.getlist('edu_date')
    degrees = request.form.getlist('degree')
    edu_html = "".join([f'<div class="flex-row"><span>{c}</span><span>{t}</span></div><div class="text"><i>{d}</i></div>' for c, t, d in zip(colleges, edu_dates, degrees) if c.strip()])

    p_names = request.form.getlist('project_name')
    p_dates = request.form.getlist('project_date')
    p_descs = request.form.getlist('project_desc')
    proj_html = "".join([f'<div class="flex-row"><span>{n}</span><span>{t}</span></div><div class="text">{d}</div>' for n, t, d in zip(p_names, p_dates, p_descs) if n.strip()])

    c_titles = request.form.getlist('cert_title')
    c_descs = request.form.getlist('cert_desc')
    cert_html = "".join([f'<div class="flex-row"><span>{title}</span></div><div class="text">{desc}</div>' for title, desc in zip(c_titles, c_descs) if title.strip()])

    contact_line = f"{phone} | {email}"
    if links: contact_line += f" | {links}"

    if template_style == "classic":
        style_css = """
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            @page { margin: 35px; size: A4; }
            body { font-family: 'Roboto', sans-serif; color: #1a1a1a; line-height: 1.5; }
            .header { text-align: center; border-bottom: 1.5px solid #000; padding-bottom: 10px; margin-bottom: 15px; }
            .header h1 { margin: 0; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }
            .contact { font-size: 10px; margin-top: 5px; }
            .section-title { font-size: 12px; font-weight: bold; text-transform: uppercase; margin-top: 18px; margin-bottom: 4px; }
            .text { font-size: 10.5px; white-space: pre-line; margin-bottom: 8px; }
            .flex-row { display: flex; justify-content: space-between; font-weight: bold; font-size: 11px; }
        """
    else:
        style_css = """
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            @page { margin: 0; }
            body { font-family: 'Roboto', sans-serif; margin: 0; padding: 0; color: #333; }
            .header { background: #1a1a1a; color: #ffffff; padding: 25px; border-bottom: 5px solid #007bff; text-align: center; }
            .header h1 { margin: 0; font-size: 20px; }
            .contact { font-size: 10px; margin-top: 5px; }
            .section-title { font-size: 11px; font-weight: bold; color: #007bff; text-transform: uppercase; margin-top: 18px; padding: 0 40px; }
            .text { font-size: 10px; white-space: pre-line; padding: 0 40px; margin-bottom: 8px; }
            .flex-row { display: flex; justify-content: space-between; font-weight: bold; font-size: 10.5px; padding: 0 40px; }
        """

    html_content = f"""
    <html>
    <head><style>{style_css}</style></head>
    <body>
        <div class="header">
            <h1>{name}</h1>
            <div class="contact">{contact_line}</div>
            <div class="contact">{address}</div>
        </div>
        <div style="padding: 0 30px;">
            {f'<div class="section-title">Professional Objective</div><div class="text">{objective}</div>' if objective else ''}
            <div class="section-title">Education</div>{edu_html}
            {f'<div class="section-title">Skills</div><div class="text">{skills}</div>' if skills else ''}
            {f'<div class="section-title">Experience</div><div class="text">{experience}</div>' if experience else ''}
            <div class="section-title">Projects</div>{proj_html}
            <div class="section-title">Certifications</div>{cert_html}
        </div>
    </body>
    </html>
    """
    
    path_wkhtmltopdf = os.environ.get('WKHTMLTOPDF_PATH', r'D:\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {'quiet': '', 'no-outline': None, 'enable-local-file-access': None, 'disable-smart-shrinking': None}
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(html_content, False, configuration=config, options=options)
    
    res = make_response(pdf)
    res.headers['Content-Type'] = 'application/pdf'
    # Format filename as Name_Resume.pdf
    safe_filename = f"{name.replace(' ', '_')}_Resume.pdf" if name else "Resume.pdf"
    res.headers['Content-Disposition'] = f"{'inline' if action=='preview' else 'attachment'}; filename={safe_filename}"
    return res

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
