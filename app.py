from flask import Flask, render_template, request, make_response, jsonify
import pdfkit
import io
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/get_ai_summary', methods=['POST'])
def ai_summary_route():
    data = request.get_json()
    skills = data.get('skills', 'core competencies')
    summary = f"Enthusiastic engineering graduate with strong programming and problem-solving skills. Skilled in {skills}. Focused on delivering high-quality solutions and scalable AI applications."
    return jsonify({'summary': summary})

@app.route('/scan_uploaded_pdf', methods=['POST'])
def scan_uploaded_pdf():
    if 'resume_file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['resume_file']
    jd_text = request.form.get('jd')
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
    project_name = request.form.get('project_name', '')
    project_date = request.form.get('project_date', '')
    project_desc = request.form.get('project_desc', '')
    experience = request.form.get('experience', '')
    degree = request.form.get('degree', '')
    college = request.form.get('college', '')
    edu_date = request.form.get('edu_date', '')
    skills = request.form.get('skills', '')
    certifications = request.form.get('certifications', '')
    template_style = request.form.get('template_style', 'classic')
    action = request.form.get('action')

    # CSS with ONLY Top Header Line
    if template_style == "classic":
        style_css = """
            @page { margin: 35px; size: A4; }
            body { font-family: 'Arial', sans-serif; color: #1a1a1a; line-height: 1.5; }
            .header { text-align: center; border-bottom: 1.5px solid #000; padding-bottom: 10px; margin-bottom: 15px; }
            .header h1 { margin: 0; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
            .contact { font-size: 10.5px; margin-top: 5px; }
            .section-title { font-size: 13px; font-weight: bold; text-transform: uppercase; margin-top: 20px; margin-bottom: 5px; } /* No underline */
            .text { font-size: 11.5px; white-space: pre-line; margin-bottom: 10px; }
            .flex-row { display: flex; justify-content: space-between; font-weight: bold; font-size: 12px; }
        """
    else:
        style_css = """
            @page { margin: 0; }
            body { font-family: 'Helvetica', sans-serif; margin: 0; padding: 0; color: #333; }
            .header { background: #1a1a1a; color: #ffffff; padding: 30px; border-bottom: 5px solid #007bff; text-align: center; }
            .header h1 { margin: 0; font-size: 24px; }
            .section-title { font-size: 12px; font-weight: bold; color: #007bff; text-transform: uppercase; margin-top: 20px; }
            .text { font-size: 11px; white-space: pre-line; padding: 0 40px; }
        """

    html_content = f"""
    <html>
    <head><style>{style_css}</style></head>
    <body>
        <div class="header">
            <h1>{name}</h1>
            <div class="contact">{phone} | {email} | {links} <br> {address}</div>
        </div>
        <div style="padding: 0 30px;">
            {f'<div class="section-title">Professional Objective</div><div class="text">{objective}</div>' if objective else ''}
            {f'<div class="section-title">Education</div><div class="flex-row"><span>{college}</span><span>{edu_date}</span></div><div class="text"><i>{degree}</i></div>' if college else ''}
            {f'<div class="section-title">Skills</div><div class="text">{skills}</div>' if skills else ''}
            {f'<div class="section-title">Experience</div><div class="text">{experience}</div>' if experience else ''}
            {f'<div class="section-title">Projects</div><div class="flex-row"><span>{project_name}</span><span>{project_date}</span></div><div class="text">{project_desc}</div>' if project_name else ''}
            {f'<div class="section-title">Certifications</div><div class="text">{certifications}</div>' if certifications else ''}
        </div>
    </body>
    </html>
    """
    
    config = pdfkit.configuration(wkhtmltopdf=r'D:\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    res = make_response(pdf)
    res.headers['Content-Type'] = 'application/pdf'
    safe_name = name.replace(" ", "_") if name else "Titan"
    res.headers['Content-Disposition'] = f"{'inline' if action=='preview' else 'attachment'}; filename={safe_name}_Resume.pdf"
    return res

if __name__ == '__main__':
    app.run(debug=True)