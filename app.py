# ...existing code...


from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import render_template_string
from xhtml2pdf import pisa
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import tempfile
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.rol not in roles:
                flash('Acceso denegado: permisos insuficientes.', 'danger')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Nuevo decorador para permisos granulares
def permission_required(modulo, accion):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            
            # Verificar si el usuario tiene el permiso específico
            tiene_permiso = False
            # Para administradores, permitir todo
            if current_user.rol == 'administrador':
                tiene_permiso = True
            else:
                # Verificar permisos específicos del usuario
                permiso_usuario = PermisoUsuario.query.join(Permiso).filter(
                    PermisoUsuario.usuario_id == current_user.id,
                    Permiso.modulo == modulo,
                    Permiso.accion == accion
                ).first()
                
                if permiso_usuario:
                    if accion == 'crear' and permiso_usuario.puede_crear:
                        tiene_permiso = True
                    elif accion == 'leer' and permiso_usuario.puede_leer:
                        tiene_permiso = True
                    elif accion == 'actualizar' and permiso_usuario.puede_actualizar:
                        tiene_permiso = True
                    elif accion == 'eliminar' and permiso_usuario.puede_eliminar:
                        tiene_permiso = True
            
            if not tiene_permiso:
                flash('Acceso denegado: permisos insuficientes.', 'danger')
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

from config import config
import os

db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(config['development'])
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Modelo para Bioanalista
class Bioanalista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rutas de chat privado y lista de usuarios (después de inicialización de Flask)
@app.route('/chat/usuarios')
@login_required
def chat_usuarios():
    usuarios = Usuario.query.filter(Usuario.username != current_user.username).all()
    return jsonify([{'username': u.username, 'nombre': u.nombre_completo} for u in usuarios])

@app.route('/chat/<destinatario>')
@login_required
def chat_privado(destinatario):
    mensajes = MensajeChat.query.filter(
        ((MensajeChat.remitente == current_user.username) & (MensajeChat.destinatario == destinatario)) |
        ((MensajeChat.remitente == destinatario) & (MensajeChat.destinatario == current_user.username))
    ).order_by(MensajeChat.fecha.asc()).all()
    return render_template('chat_privado.html', username=current_user.username, destinatario=destinatario, mensajes=mensajes)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Modelos de la base de datos

# Modelos para Administración

# --- PDF y envío de correo ---
def generar_pdf_receta(nombre_paciente, medicamentos, instrucciones):
    # Renderizar HTML de receta (puedes personalizar este HTML para que sea igual al de impresión)
    from datetime import datetime
    empresa = None
    try:
        from app import Empresa
        empresa = Empresa.query.first()
    except Exception:
        pass
    fecha = datetime.now().strftime('%d/%m/%Y')
    empresa_html = ''
    if empresa:
        empresa_html = f"""
            <div class='empresa'>
                {empresa.razon_social}<br>
                RIF: {empresa.rif}<br>
                {empresa.direccion}
            </div>
        """
    else:
        empresa_html = "<div class='empresa'>RECETA MÉDICA</div>"
    # Medicamentos como lista
    if medicamentos:
        meds_html = ''.join(f'<li>{m.strip()}</li>' for m in medicamentos.split(',') if m.strip())
    else:
        meds_html = '<li>No especificados</li>'
    html = f'''
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .receta-container {{ max-width: 700px; margin: auto; border: 2px solid #000; padding: 30px; }}
            .titulo {{ text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 20px; }}
            .empresa {{ text-align: center; font-size: 16px; margin-bottom: 10px; }}
            .datos-paciente {{ margin-bottom: 20px; }}
            .seccion {{ margin-bottom: 18px; }}
            .medicamentos-lista {{ margin-left: 20px; }}
            .firma {{ margin-top: 40px; text-align: right; }}
            .firma-linea {{ margin-top: 40px; border-top: 1px solid #000; width: 250px; float: right; }}
        </style>
    </head>
    <body>
        <div class="receta-container">
            {empresa_html}
            <div class="titulo">Receta Médica</div>
            <div class="datos-paciente">
                <strong>Paciente:</strong> {nombre_paciente}<br>
                <strong>Fecha:</strong> {fecha}
            </div>
            <div class="seccion">
                <strong>Medicamentos:</strong>
                <ul class="medicamentos-lista">
                    {meds_html}
                </ul>
            </div>
            <div class="seccion">
                <strong>Instrucciones:</strong><br>
                {instrucciones.replace('\n', '<br>')}
            </div>
            <div class="firma">
                <div class="firma-linea"></div>
                <div>Firma y Sello</div>
            </div>
        </div>
    </body>
    </html>
    '''
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    with open(temp.name, "w+b") as pdf_file:
        pisa.CreatePDF(html, dest=pdf_file)
    return temp.name

def enviar_email_con_pdf(destinatario, asunto, cuerpo, pdf_path):
    empresa = Empresa.query.first()
    if not empresa or not empresa.correo_emisor or not empresa.correo_password or not empresa.smtp_server or not empresa.smtp_port:
        raise Exception('No hay configuración de correo emisor en la base de datos.')
    remitente = (empresa.correo_emisor or '').strip()
    password = (empresa.correo_password or '').strip()
    smtp_server = (empresa.smtp_server or '').strip()
    smtp_port = int(empresa.smtp_port or 587)
    destinatario = (destinatario or '').strip()
    print(f"Remitente: {remitente}, Destinatario: {destinatario}, SMTP: {smtp_server}, Puerto: {smtp_port}")
    if not remitente or not destinatario:
        print(f"[DEBUG] remitente='{remitente}' destinatario='{destinatario}'")
        raise Exception(f'El correo emisor o destinatario está vacío o mal escrito. remitente="{remitente}" destinatario="{destinatario}"')
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
    with open(pdf_path, 'rb') as f:
        part = MIMEBase('application', 'pdf')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='receta.pdf')
        msg.attach(part)
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(remitente, password)
    smtp.sendmail(remitente, [destinatario], msg.as_string())
    smtp.quit()

@app.route('/validar_correo', methods=['POST'])
@login_required
def validar_correo():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')
    smtp = data.get('smtp')
    port = int(data.get('port'))
    try:
        server = smtplib.SMTP(smtp, port, timeout=10)
        server.starttls()
        server.login(correo, password)
        server.quit()
        return jsonify(ok=True, msg='¡Conexión y autenticación exitosa!')
    except Exception as e:
        return jsonify(ok=False, msg=f'Error: {str(e)}')


@app.route('/orden_laboratorio', methods=['POST'])
@login_required
def orden_laboratorio():
    None

@app.route('/emergencias/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_emergencia():
    motivos_precargados = [
        "Accidente de tránsito",
        "Caída",
        "Dolor torácico",
        "Dificultad respiratoria",
        "Convulsiones",
        "Trauma",
        "Hemorragia",
        "Fiebre alta",
        "Otros"
    ]
    medicamentos_list = Medicamento.query.all()
    insumos_list = Insumo.query.all()
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()

    if request.method == 'POST':
        paciente_id = int(request.form['paciente_id'])
        medico_id = int(request.form['medico_id'])
        motivos = request.form.getlist('motivos[]')
        motivo = ', '.join(motivos)
        medicamentos_aplicados = request.form.get('medicamentos_aplicados', '')
        instrumentos_aplicados = request.form.get('instrumentos_aplicados', '')
        tiempo_observacion = request.form.get('tiempo_observacion', '')
        tratamiento_aplicado = request.form.get('tratamiento_aplicado') == 'on'
        observaciones = request.form.get('observaciones', '')
        enfermeras_ids = request.form.getlist('enfermeras[]')
        hospitalizar = request.form.get('hospitalizar') == 'on'
        emergencia = Emergencia(
            paciente_id=paciente_id,
            medico_id=medico_id,
            motivo=motivo,
            medicamentos_aplicados=medicamentos_aplicados,
            instrumentos_aplicados=instrumentos_aplicados,
            tiempo_observacion=tiempo_observacion,
            tratamiento_aplicado=tratamiento_aplicado,
            observaciones=observaciones
        )
        db.session.add(emergencia)
        db.session.commit()

        # Relacionar enfermeras que atendieron (puedes crear una tabla EmergenciaEnfermera si quieres guardar varias)
        # Ejemplo: emergencia_enfermera = EmergenciaEnfermera(emergencia_id=emergencia.id, enfermera_id=enf_id)
        # for enf_id in enfermeras_ids: ...

        # Si amerita hospitalización, registrar hospitalización y pasar datos
        if hospitalizar:
            hospitalizacion = Hospitalizacion(
                paciente_id=paciente_id,
                medico_id=medico_id,
                enfermera_id=int(enfermeras_ids[0]) if enfermeras_ids else None,
                fecha_ingreso=datetime.utcnow(),
                dias_hospitalizado=1,
                observaciones=f'Hospitalización por emergencia #{emergencia.id}'
            )
            db.session.add(hospitalizacion)
            db.session.commit()
            flash('Emergencia y hospitalización registrada exitosamente')
            return redirect(url_for('hospitalizaciones'))
        flash('Emergencia registrada exitosamente')
        return redirect(url_for('buscar_emergencias'))

    return render_template(
        'emergencias/nuevo.html',
        motivos_precargados=motivos_precargados,
        medicamentos_list=medicamentos_list,
        insumos_list=insumos_list,
        pacientes=pacientes_list,
        medicos=medicos_list,
        enfermeras_list=enfermeras_list
    )
    try:
        data = request.get_json()
        consulta_id = data.get('consulta_id')
        examenes = data.get('examenes', [])
        if not consulta_id or not examenes:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400

        # Buscar la consulta
        consulta = Consulta.query.get(consulta_id)
        if not consulta:
            return jsonify({'success': False, 'error': 'Consulta no encontrada'}), 404

        # Crear la orden de laboratorio usando el modelo Examen personalizado
        for ex in examenes:
            nuevo_examen = Examen(
                paciente_id=consulta.paciente_id,
                medico_solicitante_id=consulta.medico_id,
                fecha_solicitud=datetime.utcnow(),
                motivo=ex.get('descripcion', ''),
                tipo_examen=ex.get('tipo', ''),
                valores_resultados="",
                estado="solicitado",
                observaciones=""
            )
            db.session.add(nuevo_examen)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/enviar_receta/<int:paciente_id>', methods=['POST'])
@login_required
def enviar_receta(paciente_id):
    from flask import jsonify
    nombre_paciente = request.form.get('nombre_paciente', 'Paciente')
    instrucciones = request.form.get('instrucciones', '')
    destinatario = request.form.get('email', 'destino@correo.com')
    tratamientos_json = request.form.get('tratamientos_json', None)
    detalles_html = ''
    if tratamientos_json:
        import json
        try:
            tratamientos = json.loads(tratamientos_json)
            detalles_html = '<ul class="medicamentos-lista">'
            for tr in tratamientos:
                nombre = tr.get('medicamento', tr.get('nombre', ''))
                dosis = tr.get('dosis', '')
                frecuencia = tr.get('frecuencia', '')
                duracion = tr.get('duracion', '')
                # Ejemplo: Paracetamol 500mg, 1 tableta cada 8 horas por 5 días
                linea = f"<li>{nombre} {dosis}, {frecuencia} por {duracion}</li>"
                detalles_html += linea
            detalles_html += '</ul>'
        except Exception:
            detalles_html = '<ul><li>Error al procesar tratamientos</li></ul>'
    pdf_path = generar_pdf_receta_detallada(nombre_paciente, detalles_html, instrucciones)
    try:
        enviar_email_con_pdf(destinatario, 'Receta Médica', 'Adjunto su receta en PDF.', pdf_path)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True)
        else:
            flash('Receta enviada por correo electrónico.', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, error=str(e))
        else:
            flash(f'Error al enviar la receta: {e}', 'danger')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=False, error='Error desconocido')
    return redirect(url_for('nueva_consulta'))
@app.route('/enviar_orden_examenes/<int:paciente_id>', methods=['POST'])
@login_required
def enviar_orden_examenes(paciente_id):
    from flask import jsonify
    nombre_paciente = request.form.get('nombre_paciente', 'Paciente')
    instrucciones = request.form.get('instrucciones', '')
    destinatario = request.form.get('email', 'destino@correo.com')
    examenes_json = request.form.get('examenes_json', None)
    detalles_html = ''
    if examenes_json:
        import json
        try:
            examenes = json.loads(examenes_json)
            detalles_html = '<ul>'
            for ex in examenes:
                detalles_html += f'<li><b>Tipo de Examen:</b> {ex.get("tipo", "")} '
                if ex.get('valores'):
                    detalles_html += f'| <b>Valores:</b> {ex.get("valores", "")}'
                detalles_html += '</li>'
            detalles_html += '</ul>'
        except Exception:
            detalles_html = '<i>Error al procesar exámenes</i>'
    pdf_path = generar_pdf_orden_examenes(nombre_paciente, detalles_html, instrucciones)
    try:
        enviar_email_con_pdf(destinatario, 'Orden de Exámenes', 'Adjunto su orden de exámenes en PDF.', pdf_path)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True)
        else:
            flash('Orden de exámenes enviada por correo electrónico.', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, error=str(e))
        else:
            flash(f'Error al enviar el correo: {str(e)}', 'danger')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=False, error='Error desconocido')
    return redirect(url_for('nueva_consulta'))

# Nueva función para PDF de orden de exámenes
def generar_pdf_orden_examenes(nombre_paciente, detalles_html, instrucciones):
    from datetime import datetime
    empresa = None
    try:
        from app import Empresa
        empresa = Empresa.query.first()
    except Exception:
        pass
    fecha = datetime.now().strftime('%d/%m/%Y')
    empresa_html = ''
    if empresa:
        empresa_html = f"""
            <div class='empresa'>
                {empresa.razon_social}<br>
                RIF: {empresa.rif}<br>
                {empresa.direccion}
            </div>
        """
    else:
        empresa_html = "<div class='empresa'>ORDEN DE EXÁMENES</div>"
    html = f'''
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .orden-container {{ max-width: 700px; margin: auto; border: 2px solid #000; padding: 30px; }}
            .titulo {{ text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 20px; }}
            .empresa {{ text-align: center; font-size: 16px; margin-bottom: 10px; }}
            .datos-paciente {{ margin-bottom: 20px; }}
            .seccion {{ margin-bottom: 18px; }}
            .examenes-lista {{ margin-left: 20px; }}
            .firma {{ margin-top: 40px; text-align: right; }}
            .firma-linea {{ margin-top: 40px; border-top: 1px solid #000; width: 250px; float: right; }}
        </style>
    </head>
    <body>
        <div class="orden-container">
            {empresa_html}
            <div class="titulo">Orden de Exámenes</div>
            <div class="datos-paciente">
                <strong>Paciente:</strong> {nombre_paciente}<br>
                <strong>Fecha:</strong> {fecha}
            </div>
            <div class="seccion">
                <strong>Exámenes Solicitados:</strong>
                {detalles_html}
            </div>
            <div class="seccion">
                <strong>Instrucciones:</strong><br>
                {instrucciones.replace('\n', '<br>')}
            </div>
            <div class="firma">
                <div class="firma-linea"></div>
                <div>Médico</div>
            </div>
        </div>
    </body>
    </html>
    '''
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
        pisa.CreatePDF(html, dest=temp)
        return temp.name
    from flask import jsonify
    nombre_paciente = request.form.get('nombre_paciente', 'Paciente')
    instrucciones = request.form.get('instrucciones', 'Tomar cada 8 horas')
    destinatario = request.form.get('email', 'destino@correo.com')
    tratamientos_json = request.form.get('tratamientos_json', None)
    medicamentos = ''
    detalles_html = ''
    if tratamientos_json:
        import json
        try:
            tratamientos = json.loads(tratamientos_json)
            detalles_html = ''
            for t in tratamientos:
                if t.get('motivo'):
                    detalles_html += f"<div style='margin-bottom:6px;'><b>Motivo:</b> {t.get('motivo','')}</div>"
                detalles_html += '<ul style="margin-left:20px;">'
                for med in t.get('medicamentos', []):
                    linea = f"{med.get('medicamento_id','')} {med.get('dosis','')}, {med.get('frecuencia','')} por {med.get('duracion','')}"
                    detalles_html += f'<li>{linea.strip()}</li>'
                detalles_html += '</ul>'
            medicamentos = ', '.join(
                med.get('medicamento_id', '')
                for t in tratamientos for med in t.get('medicamentos', [])
            )
        except Exception:
            detalles_html = '<i>Error al procesar tratamientos</i>'
    else:
        medicamentos = request.form.get('medicamentos', 'Paracetamol')
    pdf_path = generar_pdf_receta_detallada(nombre_paciente, detalles_html, instrucciones)
    try:
        enviar_email_con_pdf(destinatario, 'Receta Médica', 'Adjunto su receta en PDF.', pdf_path)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True)
        else:
            flash('Receta/orden enviada por correo electrónico.', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, error=str(e))
        else:
            flash(f'Error al enviar el correo: {str(e)}', 'danger')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=False, error='Error desconocido')
    return redirect(url_for('nueva_consulta'))

# Nueva función para PDF detallado
def generar_pdf_receta_detallada(nombre_paciente, detalles_html, instrucciones):
    from datetime import datetime
    empresa = None
    try:
        from app import Empresa
        empresa = Empresa.query.first()
    except Exception:
        pass
    fecha = datetime.now().strftime('%d/%m/%Y')
    empresa_html = ''
    if empresa:
        empresa_html = f"""
            <div class='empresa'>
                {empresa.razon_social}<br>
                RIF: {empresa.rif}<br>
                {empresa.direccion}
            </div>
        """
    else:
        empresa_html = "<div class='empresa'>RECETA MÉDICA</div>"
    html = f'''
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .receta-container {{ max-width: 700px; margin: auto; border: 2px solid #000; padding: 30px; }}
            .titulo {{ text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 20px; }}
            .empresa {{ text-align: center; font-size: 16px; margin-bottom: 10px; }}
            .datos-paciente {{ margin-bottom: 20px; }}
            .seccion {{ margin-bottom: 18px; }}
            .medicamentos-lista {{ margin-left: 20px; }}
            .firma {{ margin-top: 40px; text-align: right; }}
            .firma-linea {{ margin-top: 40px; border-top: 1px solid #000; width: 250px; float: right; }}
        </style>
    </head>
    <body>
        <div class="receta-container">
            {empresa_html}
            <div class="titulo">Receta Médica</div>
            <div class="datos-paciente">
                <strong>Paciente:</strong> {nombre_paciente}<br>
                <strong>Fecha:</strong> {fecha}
            </div>
            <div class="seccion">
                <strong>Medicamentos:</strong>
                {detalles_html}
            </div>
            <div class="seccion">
                <strong>Instrucciones:</strong><br>
                {instrucciones.replace('\n', '<br>')}
            </div>
            <div class="firma">
                <div class="firma-linea"></div>
                <div>Médico</div>
            </div>
        </div>
    </body>
    </html>
    '''
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
        pisa.CreatePDF(html, dest=temp)
        return temp.name
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, anulada
    paciente = db.relationship('Paciente', backref='facturas')
    # ...existing code...


# Modelo para mensajes de chat privado
class MensajeChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remitente = db.Column(db.String(100), nullable=False)
    destinatario = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class CuentaPorCobrar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada, vencida
    paciente = db.relationship('Paciente', backref='cuentas_por_cobrar')

class Hospitalizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    enfermera_id = db.Column(db.Integer, db.ForeignKey('enfermera.id'), nullable=False)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    dias_hospitalizado = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='hospitalizaciones')
    medico = db.relationship('Medico', backref='hospitalizaciones')
    enfermera = db.relationship('Enfermera', backref='hospitalizaciones')

# Modelo para Cirugias
class Cirugia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    enfermera_id = db.Column(db.Integer, db.ForeignKey('enfermera.id'), nullable=False)
    fecha_cirugia = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_cirugia = db.Column(db.String(100), nullable=False)
    duracion_horas = db.Column(db.Float, nullable=False)
    cantidad_medicos = db.Column(db.Integer, nullable=False, default=1)
    insumos_usados = db.Column(db.Text)  # JSON string: lista de insumos y cantidades
    medicamentos_aplicados = db.Column(db.Text)  # JSON string: lista de medicamentos y dosis
    complicacion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='cirugias')
    medico = db.relationship('Medico', backref='cirugias')
    enfermera = db.relationship('Enfermera', backref='cirugias')

# === Rutas para Evaluaciones ===
@app.route('/evaluaciones')
@login_required
def evaluaciones():
    return render_template('evaluaciones/index.html')

@app.route('/evaluaciones/laboratorio')
@login_required
def evaluaciones_laboratorio():
    # Mostrar solo exámenes de laboratorio según los tipos definidos en TipoExamen
    tipos_lab = TipoExamen.query.filter(TipoExamen.categoria.ilike('%lab%'), TipoExamen.activo==True).all()
    nombres_lab = [t.nombre for t in tipos_lab]
    if nombres_lab:
        examenes = Examen.query.filter(Examen.tipo_examen.in_(nombres_lab)).all()
    else:
        examenes = []
    return render_template('evaluaciones/laboratorio/index.html', examenes=examenes)

@app.route('/evaluaciones/laboratorio/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_laboratorio():
    if request.method == 'POST':
        # Aquí deberías guardar el nuevo examen de laboratorio si corresponde
        # ... (lógica de guardado si aplica) ...
        flash('Examen de laboratorio registrado exitosamente')
        return redirect(url_for('evaluaciones_laboratorio'))
    pacientes = Paciente.query.all()
    tipos_examen = TipoExamen.query.filter(TipoExamen.categoria.ilike('%lab%'), TipoExamen.activo==True).all()
    # Importar Usuario solo si no está ya en el contexto
    bioanalistas = Usuario.query.filter_by(rol='bioanalista').all()
    return render_template('evaluaciones/laboratorio/nuevo.html', pacientes=pacientes, tipos_examen=tipos_examen, bioanalistas=bioanalistas)

@app.route('/evaluaciones/imagenologia')
@login_required
def evaluaciones_imagenologia():
    examenes = Examen.query.filter(Examen.tipo_examen.ilike('%imagen%')).all() if hasattr(Examen, 'tipo_examen') else []
    return render_template('evaluaciones/imagenologia/index.html', examenes=examenes)

@app.route('/evaluaciones/imagenologia/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_imagenologia():
    if request.method == 'POST':
        examen = Examen(
            paciente_id=int(request.form['paciente_id']),
            tipo_examen=request.form['tipo_examen'],
            fecha_solicitud=datetime.strptime(request.form['fecha_solicitud'], '%Y-%m-%d'),
            valores_resultados=request.form['valores_resultados']
        )
        db.session.add(examen)
        db.session.commit()
        flash('Examen de imagenología registrado exitosamente')
        return redirect(url_for('evaluaciones_imagenologia'))
    pacientes = Paciente.query.all()
    return render_template('evaluaciones/imagenologia/nuevo.html', pacientes=pacientes)
# Rutas para Cirugías
@app.route('/cirugias')
@login_required
def cirugias():
    cirugias_list = Cirugia.query.all()
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    medicamentos_list = Medicamento.query.all()
    insumos_list = Insumo.query.all()
    return render_template('cirugias/index.html', cirugias=cirugias_list, pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list, medicamentos=medicamentos_list, insumos=insumos_list)

# Ruta para procesar cirugía (modal)
@app.route('/cirugias/<int:id>/procesar', methods=['POST'])
@login_required
def procesar_cirugia(id):
    import json
    cirugia = Cirugia.query.get_or_404(id)
    # Medicamentos
    medicamentos_ids = request.form.getlist('medicamentos[]')
    medicamentos_data = []
    for mid in medicamentos_ids:
        medicamento = Medicamento.query.get(int(mid))
        if medicamento:
            medicamentos_data.append({"id": medicamento.id, "nombre": medicamento.nombre})
    cirugia.medicamentos_aplicados = json.dumps(medicamentos_data, ensure_ascii=False)
    # Insumos
    insumos_ids = request.form.getlist('insumos[]')
    insumos_data = []
    for iid in insumos_ids:
        insumo = Insumo.query.get(int(iid))
        if insumo:
            insumos_data.append({"id": insumo.id, "nombre": insumo.nombre})
    cirugia.insumos_usados = json.dumps(insumos_data, ensure_ascii=False)
    # Médicos participantes
    medicos_ids = request.form.getlist('medicos_participantes[]')
    cirugia.cantidad_medicos = 1 + len(medicos_ids)  # 1 principal + adicionales
    # Resultado de la operación
    cirugia.complicacion = request.form.get('resultado_operacion', '')
    # Si se solicita hospitalización
    if request.form.get('hospitalizar') == '1':
        try:
            dias_hosp = int(request.form.get('dias_hospitalizar', '1'))
            hospitalizacion = Hospitalizacion(
                paciente_id=cirugia.paciente_id,
                medico_id=cirugia.medico_id,
                enfermera_id=cirugia.enfermera_id,
                fecha_ingreso=datetime.utcnow(),
                dias_hospitalizado=dias_hosp,
                observaciones=f'Por cirugía #{cirugia.id}'
            )
            db.session.add(hospitalizacion)
            flash('Hospitalización registrada correctamente')
        except Exception as e:
            flash(f'Error al registrar hospitalización: {e}', 'danger')
    db.session.commit()
    flash('Cirugía procesada y actualizada correctamente')
    return redirect(url_for('cirugias'))

@app.route('/cirugias/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_cirugia():
    if request.method == 'POST':
        cirugia = Cirugia(
            paciente_id=int(request.form['paciente_id']),
            medico_id=int(request.form['medico_id']),
            enfermera_id=int(request.form['enfermera_id']),
            fecha_cirugia=datetime.strptime(request.form['fecha_cirugia'], '%Y-%m-%dT%H:%M') if request.form.get('fecha_cirugia') else datetime.utcnow(),
            tipo_cirugia=request.form['tipo_cirugia'],
            duracion_horas=float(request.form['duracion_horas']),
            observaciones=request.form['observaciones']
        )
        db.session.add(cirugia)
        db.session.commit()
        flash('Cirugía registrada exitosamente')
        return redirect(url_for('cirugias'))
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    return render_template('cirugias/nuevo.html', pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list)

@app.route('/cirugias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cirugia(id):
    cirugia = Cirugia.query.get_or_404(id)
    if request.method == 'POST':
        cirugia.paciente_id = int(request.form['paciente_id'])
        cirugia.medico_id = int(request.form['medico_id'])
        cirugia.enfermera_id = int(request.form['enfermera_id'])
        cirugia.fecha_cirugia = datetime.strptime(request.form['fecha_cirugia'], '%Y-%m-%dT%H:%M') if request.form.get('fecha_cirugia') else cirugia.fecha_cirugia
        cirugia.tipo_cirugia = request.form['tipo_cirugia']
        cirugia.duracion_horas = float(request.form['duracion_horas'])
        cirugia.observaciones = request.form['observaciones']
        db.session.commit()
        flash('Cirugía actualizada exitosamente')
        return redirect(url_for('cirugias'))
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    return render_template('cirugias/editar.html', cirugia=cirugia, pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list)

@app.route('/cirugias/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_cirugia(id):
    cirugia = Cirugia.query.get_or_404(id)
    db.session.delete(cirugia)
    db.session.commit()
    flash('Cirugía eliminada exitosamente')
    return redirect(url_for('cirugias'))

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), default='usuario')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    # New fields for enhanced security
    nombre_completo = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    # Relationship with permissions
    permisos = db.relationship('PermisoUsuario', backref='usuario', lazy='dynamic')
    # Relationship with shortcuts
    accesos_directos = db.relationship('AccesoDirecto', backref='usuario', lazy='dynamic')

# Modelo para Permisos
class Permiso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)  # crear, leer, actualizar, eliminar

# Modelo para asignar permisos a usuarios
class PermisoUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permiso.id'), nullable=False)
    # Campos para permisos granulares
    puede_crear = db.Column(db.Boolean, default=False)
    puede_leer = db.Column(db.Boolean, default=True)
    puede_actualizar = db.Column(db.Boolean, default=False)
    puede_eliminar = db.Column(db.Boolean, default=False)
    # Relaciones
    permiso = db.relationship('Permiso', backref='permisos_usuario')

# Modelo para Accesos Directos personalizables
class AccesoDirecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    icono = db.Column(db.String(50), default='fas fa-link')
    orden = db.Column(db.Integer, default=0)

# Modelo para Logs de Auditoría
class LogAuditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    accion = db.Column(db.String(100), nullable=False)
    modulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    # Relación con usuario
    usuario = db.relationship('Usuario', backref='logs_auditoria')

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(10), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    direccion = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    historial_medico = db.relationship('HistorialMedico', backref='paciente', lazy=True)

class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    honorarios = db.relationship('HonorarioMedico', backref='medico', lazy=True)

class Insumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Medicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    principio_activo = db.Column(db.String(100))
    presentacion = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class HonorarioMedico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class ServicioClinico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class HistorialMedico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    fecha_consulta = db.Column(db.DateTime, default=datetime.utcnow)
    sintomas = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    fecha_consulta = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text, nullable=False)
    examenes_realizados = db.Column(db.Text)
    tratamiento_aplicado = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    ordenes_medicas = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='consultas')
    medico = db.relationship('Medico', backref='consultas_realizadas')

class Emergencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    fecha_emergencia = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text, nullable=False)
    medicamentos_aplicados = db.Column(db.Text)
    instrumentos_aplicados = db.Column(db.Text)
    tiempo_observacion = db.Column(db.String(50))
    tratamiento_aplicado = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='emergencias')
    medico = db.relationship('Medico', backref='emergencias_atendidas')

class Tratamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    enfermera_id = db.Column(db.Integer, db.ForeignKey('enfermera.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    medicamentos_suministrados = db.Column(db.Text)
    instrumentos_utilizados = db.Column(db.Text)
    estado = db.Column(db.String(20), default='activo')  # activo, completado, suspendido
    observaciones = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='tratamientos')
    medico = db.relationship('Medico', backref='tratamientos_prescritos')
    enfermera = db.relationship('Enfermera', backref='tratamientos_asignados')

class Enfermera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Examen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_solicitante_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_realizacion = db.Column(db.DateTime)
    motivo = db.Column(db.Text, nullable=False)
    tipo_examen = db.Column(db.String(100), nullable=False)
    valores_resultados = db.Column(db.Text)
    estado = db.Column(db.String(20), default='solicitado')  # solicitado, en_proceso, completado
    observaciones = db.Column(db.Text)
    paciente = db.relationship('Paciente', backref='examenes')
    medico_solicitante = db.relationship('Medico', backref='examenes_solicitados')

# Modelo para Empresa (configuración)
class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(200), nullable=False)
    rif = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(200))  # Ruta del logo
    correo_emisor = db.Column(db.String(120))
    correo_password = db.Column(db.String(120))
    smtp_server = db.Column(db.String(120))
    smtp_port = db.Column(db.String(10))

# Modelo para tipos de examen
class TipoExamen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(100))
    precio = db.Column(db.Float, default=0.0)
    tiempo_estimado = db.Column(db.String(50))
    preparacion_requerida = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
# Rutas para Configuración y Usuarios (pie de página)

import werkzeug
@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    empresa = Empresa.query.first()
    if request.method == 'POST':
        razon_social = request.form['razon_social']
        rif = request.form['rif']
        direccion = request.form['direccion']
        logo_file = request.files.get('logo')
        logo_path = empresa.logo if empresa and empresa.logo else None
        if logo_file and logo_file.filename:
            filename = werkzeug.utils.secure_filename(logo_file.filename)
            logo_path = os.path.join('static', 'logos', filename)
            os.makedirs(os.path.dirname(logo_path), exist_ok=True)
            logo_file.save(logo_path)
        correo_emisor = request.form.get('correo_emisor')
        correo_password = request.form.get('correo_password')
        smtp_server = request.form.get('smtp_server')
        smtp_port = request.form.get('smtp_port')
        if empresa:
            empresa.razon_social = razon_social
            empresa.rif = rif
            empresa.direccion = direccion
            empresa.logo = logo_path
            empresa.correo_emisor = correo_emisor
            empresa.correo_password = correo_password
            empresa.smtp_server = smtp_server
            empresa.smtp_port = smtp_port
        else:
            empresa = Empresa(
                razon_social=razon_social,
                rif=rif,
                direccion=direccion,
                logo=logo_path,
                correo_emisor=correo_emisor,
                correo_password=correo_password,
                smtp_server=smtp_server,
                smtp_port=smtp_port
            )
            db.session.add(empresa)
        db.session.commit()
        flash('Datos de la empresa actualizados correctamente.')
        return redirect(url_for('configuracion'))
    return render_template('configuracion.html', empresa=empresa)


# Ejemplo: solo administradores pueden ver la lista de usuarios
@app.route('/usuarios')
@login_required
@role_required('administrador')
def usuarios():
    usuarios_list = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios_list)

# Ruta para crear nuevo usuario (solo admin)
@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def nuevo_usuario():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('nuevo_usuario'))
        if Usuario.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('nuevo_usuario'))
        user = Usuario(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            rol=rol
        )
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios'))
    return render_template('usuarios_nuevo.html')

@app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.email = request.form['email']
        usuario.rol = request.form['rol']
        if request.form.get('password'):
            usuario.password_hash = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios'))
    return render_template('usuarios_editar.html', usuario=usuario)
@app.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('administrador')
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.username == 'admin':
        flash('No se puede eliminar el usuario administrador.', 'danger')
        return redirect(url_for('usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuarios'))

# (Las rutas de editar/eliminar usuario se moverán después de la inicialización de Flask y los decoradores)
 

    return Usuario.query.get(int(user_id))

# Filtros personalizados de Jinja2
@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        try:
            import json
            return json.loads(value)
        except:
            return None
    return None

# Rutas principales
@app.route('/')
@login_required
def index():
    # Obtener conteos reales usando modelos SQLAlchemy
    pacientes_count = db.session.query(Paciente).count()
    medicos_count = db.session.query(Medico).count()
    laboratorio_count = db.session.query(Examen).filter(Examen.tipo_examen.ilike('%laboratorio%')).count()
    imagenologia_count = db.session.query(Examen).filter(Examen.tipo_examen.ilike('%imagenolog%')).count()
    return render_template(
        'index.html',
        pacientes_count=pacientes_count,
        medicos_count=medicos_count,
        laboratorio_count=laboratorio_count,
        imagenologia_count=imagenologia_count
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

# Ruta para registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    from werkzeug.security import generate_password_hash
    error = None
    success = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        nombre_completo = request.form.get('nombre_completo')
        password = request.form.get('password')
        rol = request.form.get('rol', 'usuario')
        if not username or not email or not password or not nombre_completo:
            error = 'Todos los campos son obligatorios.'
        else:
            # Verificar si el usuario ya existe
            if Usuario.query.filter_by(username=username).first():
                error = 'El usuario ya existe.'
            elif Usuario.query.filter_by(email=email).first():
                error = 'El email ya está registrado.'
            else:
                nuevo_usuario = Usuario(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    rol=rol,
                    nombre_completo=nombre_completo,
                    activo=True
                )
                try:
                    db.session.add(nuevo_usuario)
                    db.session.commit()
                    success = 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.'
                except Exception as e:
                    db.session.rollback()
                    error = f'Error al registrar usuario: {str(e)}'
    return render_template('register.html', error=error, success=success)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas para Pacientes
@app.route('/pacientes')
@login_required
@role_required('administrador', 'medico', 'enfermera', 'recepcion')
def pacientes():
    pacientes_list = Paciente.query.all()
    return render_template('pacientes/index.html', pacientes=pacientes_list)
    
# Ruta para permisos
@app.route('/permisos', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def permisos():
    usuarios = Usuario.query.all()
    permisos = Permiso.query.all()
    if request.method == 'POST':
        for usuario in usuarios:
            for permiso in permisos:
                key = f"permiso_{usuario.id}_{permiso.id}"
                puede_crear = request.form.get(f"crear_{key}") == 'on'
                puede_leer = request.form.get(f"leer_{key}") == 'on'
                puede_actualizar = request.form.get(f"actualizar_{key}") == 'on'
                puede_eliminar = request.form.get(f"eliminar_{key}") == 'on'
                pu = PermisoUsuario.query.filter_by(usuario_id=usuario.id, permiso_id=permiso.id).first()
                if not pu:
                    pu = PermisoUsuario(usuario_id=usuario.id, permiso_id=permiso.id)
                    db.session.add(pu)
                pu.puede_crear = puede_crear
                pu.puede_leer = puede_leer
                pu.puede_actualizar = puede_actualizar
                pu.puede_eliminar = puede_eliminar
        db.session.commit()
        flash('Permisos actualizados correctamente.', 'success')
        return redirect(url_for('permisos'))
    permisos_usuario = {}
    for usuario in usuarios:
        permisos_usuario[usuario.id] = {}
        for permiso in permisos:
            pu = PermisoUsuario.query.filter_by(usuario_id=usuario.id, permiso_id=permiso.id).first()
            permisos_usuario[usuario.id][permiso.id] = pu
    return render_template('permisos.html', usuarios=usuarios, permisos=permisos, permisos_usuario=permisos_usuario)
    
# Ruta para auditoria
@app.route('/auditoria')
def auditoria():
    return render_template('auditoria/index.html')

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_paciente():
    if request.method == 'POST':
        dni = request.form['dni']
        if Paciente.query.filter_by(dni=dni).first():
            flash('Ya existe un paciente con ese DNI.', 'danger')
            return render_template('pacientes/nuevo.html')
        paciente = Paciente(
            dni=dni,
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date(),
            genero=request.form['genero'],
            telefono=request.form['telefono'],
            email=request.form['email'],
            direccion=request.form['direccion']
        )
        db.session.add(paciente)
        db.session.commit()
        flash('Paciente registrado exitosamente')
        return redirect(url_for('pacientes'))
    
    return render_template('pacientes/nuevo.html')

# Rutas para Médicos
@app.route('/medicos')
@login_required
@role_required('administrador', 'medico', 'enfermera', 'recepcion')
def medicos():
    medicos_list = Medico.query.all()
    return render_template('medicos/index.html', medicos=medicos_list)

@app.route('/medicos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_medico():
    if request.method == 'POST':
        medico = Medico(
            dni=request.form['dni'],
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            especialidad=request.form['especialidad'],
            telefono=request.form['telefono'],
            email=request.form['email']
        )
        db.session.add(medico)
        db.session.commit()
        flash('Médico registrado exitosamente')
        return redirect(url_for('medicos'))
    
    return render_template('medicos/nuevo.html')

# Rutas para Insumos
@app.route('/insumos')
@login_required
@role_required('administrador', 'enfermera')
def insumos():
    insumos_list = Insumo.query.all()
    return render_template('insumos/index.html', insumos=insumos_list)

@app.route('/insumos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_insumo():
    if request.method == 'POST':
        insumo = Insumo(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            stock=int(request.form['stock']),
            stock_minimo=int(request.form['stock_minimo']),
            precio_unitario=float(request.form['precio_unitario'])
        )
        db.session.add(insumo)
        db.session.commit()
        flash('Insumo registrado exitosamente')
        return redirect(url_for('insumos'))
    
    return render_template('insumos/nuevo.html')


# Rutas para Medicamentos
@app.route('/medicamentos')
@login_required
@role_required('administrador', 'enfermera')
def medicamentos():
    medicamentos_list = Medicamento.query.all()
    return render_template('medicamentos/index.html', medicamentos=medicamentos_list)
@app.route('/accesos_directos')
@login_required
def accesos_directos():
    accesos = obtener_accesos_directos_usuario(current_user.id)
    return render_template('accesos_directos/index.html', accesos=accesos)

@app.route('/medicamentos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_medicamento():
    if request.method == 'POST':
        medicamento = Medicamento(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            principio_activo=request.form['principio_activo'],
            presentacion=request.form['presentacion'],
            stock=int(request.form['stock']),
            stock_minimo=int(request.form['stock_minimo']),
            precio_unitario=float(request.form['precio_unitario']),
            fecha_vencimiento=datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date() if request.form['fecha_vencimiento'] else None
        )
        db.session.add(medicamento)
        db.session.commit()
        flash('Medicamento registrado exitosamente')
        return redirect(url_for('medicamentos'))
    
    return render_template('medicamentos/nuevo.html')

@app.route('/medicamentos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_medicamento(id):
    medicamento = Medicamento.query.get_or_404(id)
    
    if request.method == 'POST':
        medicamento.codigo = request.form['codigo']
        medicamento.nombre = request.form['nombre']
        medicamento.descripcion = request.form['descripcion']
        medicamento.principio_activo = request.form['principio_activo']
        medicamento.presentacion = request.form['presentacion']
        medicamento.stock = int(request.form['stock'])
        medicamento.stock_minimo = int(request.form['stock_minimo'])
        medicamento.precio_unitario = float(request.form['precio_unitario'])
        
        if request.form.get('fecha_vencimiento'):
            medicamento.fecha_vencimiento = datetime.strptime(request.form['fecha_vencimiento'], '%Y-%m-%d').date()
        else:
            medicamento.fecha_vencimiento = None
        
        db.session.commit()
        flash('Medicamento actualizado exitosamente')
        return redirect(url_for('medicamentos'))
    
    return render_template('medicamentos/editar.html', medicamento=medicamento)

@app.route('/medicamentos/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_medicamento(id):
    medicamento = Medicamento.query.get_or_404(id)
    nombre = medicamento.nombre
    
    try:
        db.session.delete(medicamento)
        db.session.commit()
        flash(f'Medicamento "{nombre}" eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el medicamento: {str(e)}', 'error')
    
    return redirect(url_for('medicamentos'))

# Rutas para Honorarios Médicos
@app.route('/honorarios')
@login_required
def honorarios():
    honorarios_list = HonorarioMedico.query.all()
    return render_template('honorarios/index.html', honorarios=honorarios_list)

@app.route('/honorarios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_honorario():
    if request.method == 'POST':
        honorario = HonorarioMedico(
            medico_id=int(request.form['medico_id']),
            servicio=request.form['servicio'],
            precio=float(request.form['precio']),
            descripcion=request.form['descripcion']
        )
        db.session.add(honorario)
        db.session.commit()
        flash('Honorario registrado exitosamente')
        return redirect(url_for('honorarios'))
    
    medicos_list = Medico.query.all()
    return render_template('honorarios/nuevo.html', medicos=medicos_list)

# Rutas para Servicios Clínicos
@app.route('/servicios')
@login_required
def servicios():
    servicios_list = ServicioClinico.query.all()
    return render_template('servicios/index.html', servicios=servicios_list)

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    if request.method == 'POST':
        servicio = ServicioClinico(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            precio=float(request.form['precio']),
            categoria=request.form['categoria']
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio registrado exitosamente')
        return redirect(url_for('servicios'))
    
    return render_template('servicios/nuevo.html')

# Rutas para Enfermeras
@app.route('/enfermeras')
@login_required
def enfermeras():
    enfermeras_list = Enfermera.query.all()
    return render_template('enfermeras/index.html', enfermeras=enfermeras_list)

@app.route('/enfermeras/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_enfermera():
    if request.method == 'POST':
        enfermera = Enfermera(
            dni=request.form['dni'],
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            especialidad=request.form['especialidad'],
            telefono=request.form['telefono'],
            email=request.form['email']
        )
        db.session.add(enfermera)
        db.session.commit()
        flash('Enfermera registrada exitosamente')
        return redirect(url_for('enfermeras'))
    
    return render_template('enfermeras/nuevo.html')

# Rutas para Historias Médicas
@app.route('/historias')
@login_required
def historias():
    return render_template('historias/index.html')

# Rutas para Consultas
@app.route('/consultas')
@login_required
def consultas():
    consultas_list = Consulta.query.all()
    return render_template('consultas/index.html', consultas=consultas_list)

@app.route('/consultas/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_consulta():
    if request.method == 'POST':
        # Crear la consulta
        consulta = Consulta(
            paciente_id=int(request.form['paciente_id']),
            medico_id=int(request.form['medico_id']),
            motivo=request.form['motivo'],
            examenes_realizados=request.form.get('examenes_realizados', ''),
            tratamiento_aplicado=request.form.get('tratamiento_aplicado', ''),
            observaciones=request.form['observaciones'],
            ordenes_medicas=request.form['ordenes_medicas']
        )
        db.session.add(consulta)
        db.session.flush()  # Para obtener el ID de la consulta

        # Procesar tratamientos si existen
        tratamientos_data = request.form.getlist('tratamientos[]')
        for tratamiento_data in tratamientos_data:
            if tratamiento_data.strip():
                try:
                    import json
                    tratamiento_info = json.loads(tratamiento_data)
                    tratamiento = Tratamiento(
                        paciente_id=int(tratamiento_info['paciente_id']),
                        medico_id=int(tratamiento_info['medico_id']),
                        enfermera_id=1,  # ID por defecto, se puede modificar después
                        fecha_inicio=datetime.utcnow(),
                        medicamentos_suministrados=json.dumps(tratamiento_info['medicamentos'], ensure_ascii=False),
                        instrumentos_utilizados='',
                        estado='activo',
                        observaciones=tratamiento_info.get('observaciones', '')
                    )
                    db.session.add(tratamiento)
                except Exception as e:
                    print(f"Error procesando tratamiento: {e}")
                    continue

        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, consulta_id=consulta.id)
        flash('Consulta registrada exitosamente')
        return redirect(url_for('consultas'))
    
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    medicamentos_list = Medicamento.query.all()
    # Crear diccionario para JS
    pacientes_dict = {str(p.id): {"email": p.email, "nombre": f"{p.nombre} {p.apellido}"} for p in pacientes_list} if pacientes_list else {}
    return render_template('consultas/nuevo.html', 
                         pacientes=pacientes_list, 
                         medicos=medicos_list,
                         medicamentos=medicamentos_list,
                         pacientes_dict=pacientes_dict)

@app.route('/consultas/<int:id>')
@login_required
def ver_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    
    # Buscar exámenes relacionados (por ahora solo los que coinciden con paciente y médico)
    examenes = Examen.query.filter_by(
        paciente_id=consulta.paciente_id,
        medico_solicitante_id=consulta.medico_id
    ).all()
    
    # Buscar tratamientos relacionados (por ahora solo los que coinciden con paciente y médico)
    tratamientos = Tratamiento.query.filter_by(
        paciente_id=consulta.paciente_id,
        medico_id=consulta.medico_id
    ).all()
    
    # Preparar datos para JSON
    consulta_data = {
        'id': consulta.id,
        'paciente': {
            'id': consulta.paciente.id,
            'nombre': consulta.paciente.nombre,
            'apellido': consulta.paciente.apellido,
            'dni': consulta.paciente.dni,
            'telefono': consulta.paciente.telefono,
            'email': consulta.paciente.email,
            'direccion': consulta.paciente.direccion,
            'fecha_nacimiento': consulta.paciente.fecha_nacimiento.strftime('%d/%m/%Y') if consulta.paciente.fecha_nacimiento else None
        },
        'medico': {
            'id': consulta.medico.id,
            'nombre': consulta.medico.nombre,
            'apellido': consulta.medico.apellido,
            'especialidad': consulta.medico.especialidad,
            'telefono': consulta.medico.telefono,
            'email': consulta.medico.email
        },
        'fecha_consulta': consulta.fecha_consulta.strftime('%d/%m/%Y %H:%M'),
        'motivo': consulta.motivo,
        'examenes_realizados': consulta.examenes_realizados,
        'tratamiento_aplicado': consulta.tratamiento_aplicado,
        'observaciones': consulta.observaciones,
        'ordenes_medicas': consulta.ordenes_medicas,
        'examenes': [
            {
                'id': ex.id,
                'tipo_examen': ex.tipo_examen,
                'valores_resultados': ex.valores_resultados,
                'estado': ex.estado,
                'fecha_solicitud': ex.fecha_solicitud.strftime('%d/%m/%Y') if ex.fecha_solicitud else None,
                'fecha_realizacion': ex.fecha_realizacion.strftime('%d/%m/%Y') if ex.fecha_realizacion else None,
                'observaciones': ex.observaciones
            } for ex in examenes
        ],
        'tratamientos': [
            {
                'id': tr.id,
                'fecha_inicio': tr.fecha_inicio.strftime('%d/%m/%Y') if tr.fecha_inicio else None,
                'fecha_fin': tr.fecha_fin.strftime('%d/%m/%Y') if tr.fecha_fin else None,
                'medicamentos_suministrados': tr.medicamentos_suministrados,
                'instrumentos_utilizados': tr.instrumentos_utilizados,
                'estado': tr.estado,
                'observaciones': tr.observaciones
            } for tr in tratamientos
        ]
    }
    
    # Debug: imprimir en consola para ver qué datos se están enviando
    print("=== DEBUG: Datos de consulta ===")
    print(f"Exámenes realizados (texto): {consulta.examenes_realizados}")
    print(f"Tratamiento aplicado (texto): {consulta.tratamiento_aplicado}")
    print(f"Exámenes encontrados: {len(examenes)}")
    print(f"Tratamientos encontrados: {len(tratamientos)}")
    
    return jsonify(consulta_data)

@app.route('/hospitalizaciones/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_hospitalizacion(id):
    hospitalizacion = Hospitalizacion.query.get_or_404(id)
    db.session.delete(hospitalizacion)
    db.session.commit()
    flash('Hospitalización eliminada exitosamente')
    return redirect(url_for('hospitalizaciones'))


@app.route('/emergencias/nuevo', methods=['GET', 'POST'])

@app.route('/emergencias/<int:id>')
@login_required
def ver_emergencia(id):
    emergencia = Emergencia.query.get_or_404(id)
    return render_template('emergencias/ver.html', emergencia=emergencia)

@app.route('/emergencias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_emergencia(id):
    emergencia = Emergencia.query.get_or_404(id)
    
    if request.method == 'POST':
        emergencia.paciente_id = int(request.form['paciente_id'])
        emergencia.medico_id = int(request.form['medico_id'])
        emergencia.motivo = request.form['motivo']
        emergencia.medicamentos_aplicados = request.form['medicamentos_aplicados']
        emergencia.instrumentos_aplicados = request.form['instrumentos_aplicados']
        emergencia.tiempo_observacion = request.form['tiempo_observacion']
        emergencia.tratamiento_aplicado = request.form.get('tratamiento_aplicado') == 'on'
        emergencia.observaciones = request.form['observaciones']
        
        db.session.commit()
        flash('Emergencia actualizada exitosamente')
        return redirect(url_for('emergencias'))
    
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    return render_template('emergencias/editar.html', emergencia=emergencia, pacientes=pacientes_list, medicos=medicos_list)

@app.route('/emergencias/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_emergencia(id):
    emergencia = Emergencia.query.get_or_404(id)
    db.session.delete(emergencia)
    db.session.commit()
    flash('Emergencia eliminada exitosamente')
    return redirect(url_for('emergencias'))

@app.route('/emergencias/buscar')
@login_required
def buscar_emergencias():
    paciente_id = request.args.get('paciente_id', type=int)
    medico_id = request.args.get('medico_id', type=int)

    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    query = Emergencia.query
    
    if paciente_id:
        query = query.filter(Emergencia.paciente_id == paciente_id)
    if medico_id:
        query = query.filter(Emergencia.medico_id == medico_id)
    if fecha_desde:
        query = query.filter(Emergencia.fecha_emergencia >= datetime.strptime(fecha_desde, '%Y-%m-%d'))
    if fecha_hasta:
        query = query.filter(Emergencia.fecha_emergencia <= datetime.strptime(fecha_hasta, '%Y-%m-%d'))
    
    emergencias_list = query.all()
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    # Calcular fecha límite para emergencias recientes (24 horas atrás)
    fecha_limite = datetime.now() - timedelta(hours=24)
    return render_template('emergencias/index.html', emergencias=emergencias_list, pacientes=pacientes_list, medicos=medicos_list, fecha_limite=fecha_limite)

# Rutas para Tratamientos
@app.route('/tratamientos')
@login_required
def tratamientos():
    tratamientos_list = Tratamiento.query.all()
    medicamentos_list = Medicamento.query.all()
    return render_template('tratamientos/index.html', 
                         tratamientos=tratamientos_list,
                         medicamentos_list=medicamentos_list)

@app.route('/tratamientos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_tratamiento():
    if request.method == 'POST':
        # Procesar medicamentos del formulario
        medicamentos_data = []
        medicamentos_ids = request.form.getlist('medicamento_id[]')
        dosis = request.form.getlist('dosis[]')
        frecuencia = request.form.getlist('frecuencia[]')
        comentarios = request.form.getlist('comentarios[]')
        forma_suministro = request.form.getlist('forma_suministro[]')
        estatus = request.form.getlist('estatus[]')
        
        for i in range(len(medicamentos_ids)):
            if medicamentos_ids[i]:  # Solo agregar si hay medicamento seleccionado
                medicamento_info = {
                    'id': medicamentos_ids[i],
                    'dosis': dosis[i],
                    'frecuencia': frecuencia[i],
                    'comentarios': comentarios[i],
                    'forma_suministro': forma_suministro[i],
                    'estatus': estatus[i]
                }
                medicamentos_data.append(medicamento_info)
        
        # Procesar insumos del formulario
        insumos_data = []
        insumos_ids = request.form.getlist('insumo_id[]')
        cantidades = request.form.getlist('cantidad[]')
        unidades = request.form.getlist('unidad[]')
        comentarios_insumos = request.form.getlist('comentarios_insumo[]')
        
        for i in range(len(insumos_ids)):
            if insumos_ids[i]:  # Solo agregar si hay insumo seleccionado
                insumo_info = {
                    'id': insumos_ids[i],
                    'cantidad': cantidades[i],
                    'unidad': unidades[i],
                    'comentarios': comentarios_insumos[i]
                }
                insumos_data.append(insumo_info)
        
        # Convertir a JSON para almacenar en la base de datos
        import json
        medicamentos_json = json.dumps(medicamentos_data, ensure_ascii=False)
        insumos_json = json.dumps(insumos_data, ensure_ascii=False)
        
        # Procesar fecha de inicio
        fecha_inicio_str = request.form['fecha_inicio']
        if fecha_inicio_str:
            # Convertir formato datetime-local a datetime
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M')
        else:
            fecha_inicio = datetime.now()
        
        tratamiento = Tratamiento(
            paciente_id=int(request.form['paciente_id']),
            medico_id=int(request.form['medico_id']),
            enfermera_id=int(request.form['enfermera_id']),
            fecha_inicio=fecha_inicio,
            medicamentos_suministrados=medicamentos_json,
            instrumentos_utilizados=insumos_json,  # Ahora almacena los insumos
            estado=request.form['estado'],
            observaciones=request.form['observaciones']
        )
        
        if request.form.get('fecha_fin'):
            tratamiento.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d')
        
        db.session.add(tratamiento)
        db.session.commit()
        flash('Tratamiento registrado exitosamente')
        return redirect(url_for('tratamientos'))
    
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    medicamentos_list = Medicamento.query.all()
    insumos_list = Insumo.query.all()
    return render_template('tratamientos/nuevo.html', 
                         pacientes=pacientes_list, 
                         medicos=medicos_list, 
                         enfermeras=enfermeras_list,
                         medicamentos=medicamentos_list,
                         insumos=insumos_list)

# Rutas para Exámenes
@app.route('/examenes')
@login_required
def examenes():
    examenes_list = Examen.query.all()
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    return render_template('examenes/index.html', 
                         examenes=examenes_list,
                         pacientes=pacientes_list,
                         medicos=medicos_list)

@app.route('/examenes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_examen():
    if request.method == 'POST':
        # Procesar múltiples exámenes
        examenes_data = request.form.getlist('examenes[]')
        paciente_id = int(request.form['paciente_id'])
        medico_solicitante_id = int(request.form['medico_solicitante_id'])
        motivo = request.form['motivo']
        observaciones = request.form['observaciones']
        
        for examen_data in examenes_data:
            if examen_data.strip():
                # Parsear los datos del examen (formato: tipo_examen|valores_resultados)
                partes = examen_data.split('|')
                tipo_examen = partes[0]
                valores_resultados = partes[1] if len(partes) > 1 else ""
                
                examen = Examen(
                    paciente_id=paciente_id,
                    medico_solicitante_id=medico_solicitante_id,
                    motivo=motivo,
                    tipo_examen=tipo_examen,
                    valores_resultados=valores_resultados,
                    estado='solicitado',
                    observaciones=observaciones
                )
                db.session.add(examen)
        
        db.session.commit()
        flash('Exámenes registrados exitosamente')
        return redirect(url_for('examenes'))
    
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    tipos_examen_list = TipoExamen.query.filter_by(activo=True).all()
    return render_template('examenes/nuevo.html', 
                         pacientes=pacientes_list, 
                         medicos=medicos_list,
                         tipos_examen=tipos_examen_list)

@app.route('/examenes/obtener_tipos')
@login_required
def obtener_tipos_examen():
    """API para obtener tipos de examen agrupados por categoría"""
    tipos = TipoExamen.query.filter_by(activo=True).all()
    
    # Agrupar por categoría
    categorias = {}
    for tipo in tipos:
        if tipo.categoria not in categorias:
            categorias[tipo.categoria] = []
        categorias[tipo.categoria].append({
            'id': tipo.id,
            'codigo': tipo.codigo,
            'nombre': tipo.nombre,
            'descripcion': tipo.descripcion,
            'precio': tipo.precio,
            'tiempo_estimado': tipo.tiempo_estimado,
            'preparacion_requerida': tipo.preparacion_requerida
        })
    
    return jsonify(categorias)

# Rutas para Tipos de Examen
@app.route('/tipos_examen')
@login_required
def tipos_examen():
    tipos_list = TipoExamen.query.all()
    return render_template('tipos_examen/index.html', tipos=tipos_list)

@app.route('/tipos_examen/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_tipo_examen():
    if request.method == 'POST':
        tipo_examen = TipoExamen(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            categoria=request.form['categoria'],
            precio=float(request.form['precio']),
            tiempo_estimado=request.form['tiempo_estimado'],
            preparacion_requerida=request.form['preparacion_requerida']
        )
        db.session.add(tipo_examen)
        db.session.commit()
        flash('Tipo de examen registrado exitosamente')
        return redirect(url_for('tipos_examen'))
    
    return render_template('tipos_examen/nuevo.html')

@app.route('/tipos_examen/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_tipo_examen(id):
    tipo_examen = TipoExamen.query.get_or_404(id)
    if request.method == 'POST':
        tipo_examen.codigo = request.form['codigo']
        tipo_examen.nombre = request.form['nombre']
        tipo_examen.descripcion = request.form['descripcion']
        tipo_examen.categoria = request.form['categoria']
        tipo_examen.precio = float(request.form['precio'])
        tipo_examen.tiempo_estimado = request.form['tiempo_estimado']
        tipo_examen.preparacion_requerida = request.form['preparacion_requerida']
        tipo_examen.activo = 'activo' in request.form
        
        db.session.commit()
        flash('Tipo de examen actualizado exitosamente')
        return redirect(url_for('tipos_examen'))
    
    return render_template('tipos_examen/editar.html', tipo_examen=tipo_examen)

@app.route('/tipos_examen/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_tipo_examen(id):
    tipo_examen = TipoExamen.query.get_or_404(id)
    db.session.delete(tipo_examen)
    db.session.commit()
    flash('Tipo de examen eliminado exitosamente')
    return redirect(url_for('tipos_examen'))


# Rutas para Hospitalizaciones
@app.route('/hospitalizaciones')
@login_required
def hospitalizaciones():
    hospitalizaciones_list = Hospitalizacion.query.all()
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    return render_template('hospitalizaciones/index.html', hospitalizaciones=hospitalizaciones_list, pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list)

# Ruta para actualizar evolución de hospitalización (modal editable)
@app.route('/hospitalizaciones/<int:id>/evolucion', methods=['POST'])
@login_required
def actualizar_evolucion_hospitalizacion(id):
    hospitalizacion = Hospitalizacion.query.get_or_404(id)
    # Se espera que el campo 'observaciones' sea el campo de evolución editable
    hospitalizacion.observaciones = request.form.get('evolucion', '')
    db.session.commit()
    flash('Evolución actualizada exitosamente')
    return redirect(url_for('hospitalizaciones'))

@app.route('/hospitalizaciones/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_hospitalizacion():
    if request.method == 'POST':
        hospitalizacion = Hospitalizacion(
            paciente_id=int(request.form['paciente_id']),
            medico_id=int(request.form['medico_id']),
            enfermera_id=int(request.form['enfermera_id']),
            fecha_ingreso=datetime.strptime(request.form['fecha_ingreso'], '%Y-%m-%dT%H:%M') if request.form.get('fecha_ingreso') else datetime.utcnow(),
            dias_hospitalizado=int(request.form['dias_hospitalizado']),
            observaciones=request.form['observaciones']
        )
        db.session.add(hospitalizacion)
        db.session.commit()
        flash('Hospitalización registrada exitosamente')
        return redirect(url_for('hospitalizaciones'))
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    return render_template('hospitalizaciones/nuevo.html', pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list)

@app.route('/hospitalizaciones/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_hospitalizacion(id):
    hospitalizacion = Hospitalizacion.query.get_or_404(id)
    if request.method == 'POST':
        hospitalizacion.paciente_id = int(request.form['paciente_id'])
        hospitalizacion.medico_id = int(request.form['medico_id'])
        hospitalizacion.enfermera_id = int(request.form['enfermera_id'])
        hospitalizacion.dias_hospitalizado = int(request.form['dias_hospitalizado'])
        # Procesar evoluciones dinámicas
        from datetime import datetime
        import json
        fechas = request.form.getlist('evolucion_fecha[]')
        medicamentos = request.form.getlist('evolucion_medicamentos[]')
        insumos = request.form.getlist('evolucion_insumos[]')
        evaluaciones = request.form.getlist('evolucion_evaluacion[]')
        evoluciones = []
        for i in range(len(fechas)):
            evo = {
                'fecha': fechas[i],
                'medicamentos': medicamentos[i],
                'insumos': insumos[i],
                'evaluacion': evaluaciones[i]
            }
            evoluciones.append(evo)
        hospitalizacion.observaciones = json.dumps(evoluciones, ensure_ascii=False)
        db.session.commit()
        flash('Hospitalización actualizada exitosamente')
        return redirect(url_for('hospitalizaciones'))
    pacientes_list = Paciente.query.all()
    medicos_list = Medico.query.all()
    enfermeras_list = Enfermera.query.all()
    return render_template('hospitalizaciones/editar.html', hospitalizacion=hospitalizacion, pacientes=pacientes_list, medicos=medicos_list, enfermeras=enfermeras_list)

@app.route('/administracion/facturacion/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    if request.method == 'POST':
        factura = Factura(
            paciente_id=int(request.form['paciente_id']),
            concepto=request.form['concepto'],
            monto=float(request.form['monto']),
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d') if request.form.get('fecha') else datetime.utcnow(),
            estado=request.form.get('estado', 'pendiente')
        )
        db.session.add(factura)
        db.session.commit()
        flash('Factura registrada exitosamente')
        return redirect(url_for('facturacion'))
    pacientes_list = Paciente.query.all()
    medicamentos_list = [
        {'id': m.id, 'nombre': m.nombre, 'precio': m.precio_unitario} for m in Medicamento.query.all()
    ]
    insumos_list = [
        {'id': i.id, 'nombre': i.nombre, 'precio': i.precio_unitario} for i in Insumo.query.all()
    ]
    honorarios_list = [
        {'id': h.id, 'nombre': h.servicio, 'precio': h.precio} for h in HonorarioMedico.query.all()
    ]
    servicios_list = [
        {'id': s.id, 'nombre': s.nombre, 'precio': s.precio} for s in ServicioClinico.query.all()
    ]
    return render_template(
        'administracion/nueva_factura.html',
        pacientes=pacientes_list,
        medicamentos=medicamentos_list,
        insumos=insumos_list,
        honorarios=honorarios_list,
        servicios=servicios_list
    )

# Rutas para Administración
@app.route('/administracion/facturacion')
@login_required
def facturacion():
    facturas = Factura.query.all()
    return render_template('administracion/facturacion.html', facturas=facturas)

@app.route('/administracion/cuentas_por_cobrar')
@login_required
def cuentas_por_cobrar():
    cuentas = CuentaPorCobrar.query.all()
    return render_template('administracion/cuentas_por_cobrar.html', cuentas=cuentas)

# === Rutas para Bioanalistas ===
@app.route('/bioanalistas')
@login_required
def bioanalistas():
    bioanalistas_list = Bioanalista.query.all()
    return render_template('bioanalistas.html', bioanalistas=bioanalistas_list)

@app.route('/bioanalistas/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_bioanalista():
    if request.method == 'POST':
        bioanalista = Bioanalista(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            email=request.form['email'],
            telefono=request.form['telefono']
        )
        db.session.add(bioanalista)
        db.session.commit()
        flash('Bioanalista creado exitosamente')
        return redirect(url_for('bioanalistas'))
    return render_template('bioanalistas_nuevo.html')

@app.route('/bioanalistas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_bioanalista(id):
    bioanalista = Bioanalista.query.get_or_404(id)
    if request.method == 'POST':
        bioanalista.nombre = request.form['nombre']
        bioanalista.apellido = request.form['apellido']
        bioanalista.email = request.form['email']
        bioanalista.telefono = request.form['telefono']
        db.session.commit()
        flash('Bioanalista actualizado exitosamente')
        return redirect(url_for('bioanalistas'))
    return render_template('bioanalistas_editar.html', bioanalista=bioanalista)


# Función para obtener accesos directos del usuario
def obtener_accesos_directos_usuario(usuario_id):
    return AccesoDirecto.query.filter_by(usuario_id=usuario_id).order_by(AccesoDirecto.orden).all()


# Registrar la función como filtro de Jinja2 para usar en plantillas
app.jinja_env.globals['obtener_accesos_directos_usuario'] = obtener_accesos_directos_usuario

# Ruta para chat general
@app.route('/chat')
@login_required
def chat():
    mensajes = MensajeChat.query.order_by(MensajeChat.fecha.asc()).all()
    return render_template('chat.html', username=current_user.username, mensajes=mensajes)

# SocketIO: evento para recibir y emitir mensajes
@socketio.on('send_message')
def handle_send_message(data):
    # Guardar mensaje en la base de datos usando los campos correctos
    remitente = data.get('remitente') or data.get('username')
    destinatario = data.get('destinatario')
    if not destinatario:
        destinatario = 'general'
    mensaje = data.get('message')
    nuevo_mensaje = MensajeChat(remitente=remitente, destinatario=destinatario, mensaje=mensaje)
    db.session.add(nuevo_mensaje)
    db.session.commit()
    emit('receive_message', {
        'remitente': remitente,
        'destinatario': destinatario,
        'message': mensaje
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])