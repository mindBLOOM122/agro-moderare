from flask import Flask, render_template, request, send_file, url_for
import pdfkit
import os
from jinja2 import Environment, FileSystemLoader
import tempfile
from markupsafe import Markup

app = Flask(__name__)

# Calea către executabilul wkhtmltopdf (modifică dacă este diferită)
path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

PDFKIT_OPTIONS = {
    'enable-local-file-access': None,
    'page-size': 'A4',
    'encoding': 'UTF-8'
}

# Definire filtru nl2br pentru template-uri HTML
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s:
        return Markup(s.replace('\n', '<br>\n'))
    return ''

@app.route('/', methods=['GET'])
def index():
    client = {
        'cod_client': '',
        'cif': '',
        'reprezentant': '',
        'data_moderare': '',
        'email': '',
        'telefon': '',
        'tip_client': 'Companie',
        'status': 'În Așteptare',
        'documente': [],
        'verificari_text': '',
        'observatii': '',
        'moderator': '',
        'verificare_baza_legala': False
    }
    return render_template("fisa_client.html", client=client, form_action=url_for('genereaza_pdf'))

@app.route('/genereaza_pdf', methods=['POST'])
def genereaza_pdf():
    # Preluare date din formular
    verificare_baza_legala = request.form.get('verificare_baza_legala')
    verificare_baza_legala_bool = bool(verificare_baza_legala)

    client = {
        'cod_client': request.form.get('cod_client'),
        'cif': request.form.get('cif'),
        'nume_companie': request.form.get('nume_companie'),  # asigură-te că ai și acest câmp în formular
        'reprezentant': request.form.get('reprezentant'),
        'data_moderare': request.form.get('data_moderare'),
        'email': request.form.get('email'),
        'telefon': request.form.get('telefon'),
        'tip_client': request.form.get('tip_client'),
        'status': request.form.get('status'),
        'documente': request.form.getlist('documente'),
        'verificari_text': request.form.get('verificari_text'),
        'observatii': request.form.get('observatii'),
        'moderator': request.form.get('moderator'),
        'verificare_baza_legala': verificare_baza_legala_bool
    }

    # Inițializare Jinja2 Environment separat pentru PDF și adăugare filtru
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters['nl2br'] = nl2br_filter  # <- Înregistrăm manual filtrul

    # Imagine logo - cale absolută pentru PDF
    logo_path = f"file:///{os.path.abspath('static/logo.png')}".replace('\\', '/')

    # Randare HTML pentru PDF
    template = env.get_template("fisa_client_pdf.html")
    rendered_html = template.render(client=client, logo_path=logo_path)

    # Creare PDF temporar
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdfkit.from_string(rendered_html, tmp_pdf.name, options=PDFKIT_OPTIONS, configuration=config)
        tmp_pdf_path = tmp_pdf.name

    # 🔽 Schimbare doar aici – nume PDF din nume companie + CIF
    return send_file(tmp_pdf_path, as_attachment=True, download_name=f"{client['nume_companie']} - {client['cif']}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
