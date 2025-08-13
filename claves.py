import os
from flask import Flask
from werkzeug.security import generate_password_hash

# Configurar la ruta a la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'medisoft.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar DB
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Modelo de ejemplo (ajusta según tu modelo real)
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    rol = db.Column(db.String(20))
    nombre_completo = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.DateTime)

with app.app_context():
    # Generar hash y SQL
    password_hash = generate_password_hash('s1p2t3')
    
    print("Hash generado:")
    print(password_hash)
    
    # Crear usuario directamente en la DB
    try:
        nuevo_usuario = Usuario(
            username='soporte',
            email='soporte@example.com',
            password_hash='s1p2t3',
            rol='full',
            nombre_completo='Usuario de Soporte Técnico',
            activo=True
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        print("\nUsuario 'soporte' creado exitosamente en la base de datos!")
    except Exception as e:
        print(f"\nError al crear usuario: {str(e)}")