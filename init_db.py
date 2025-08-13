#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Crea las tablas y un usuario administrador inicial
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path para importar la aplicación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario, Paciente, Medico, Insumo, Medicamento, HonorarioMedico, ServicioClinico, Bioanalista

def create_tables():
    """Crear todas las tablas de la base de datos"""
    print("Creando tablas...")
    with app.app_context():
        db.create_all()
        print("[OK] Tablas creadas exitosamente")

def create_admin_user():
    """Crear usuario administrador inicial"""
    print("Creando usuario administrador...")
    with app.app_context():
        # Verificar si ya existe un usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            print("✓ Usuario administrador ya existe")
            return
        
        # Crear usuario administrador
        admin_user = Usuario(
            username='admin',
            email='admin@medisoft.com',
            password_hash=generate_password_hash('admin123'),
            rol='administrador'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print("✓ Usuario administrador creado")
        print("  Usuario: admin")
        print("  Contraseña: admin123")

def create_sample_data():
    """Crear datos de ejemplo"""
    print("Creando datos de ejemplo...")
    with app.app_context():
        # Crear médicos de ejemplo
        medicos_data = [
            {
                'dni': '12345678',
                'nombre': 'Dr. Juan',
                'apellido': 'Pérez',
                'especialidad': 'Cardiología',
                'telefono': '+54 9 11 1234-5678',
                'email': 'juan.perez@medisoft.com'
            },
            {
                'dni': '23456789',
                'nombre': 'Dra. María',
                'apellido': 'González',
                'especialidad': 'Pediatría',
                'telefono': '+54 9 11 2345-6789',
                'email': 'maria.gonzalez@medisoft.com'
            },
            {
                'dni': '34567890',
                'nombre': 'Dr. Carlos',
                'apellido': 'Rodríguez',
                'especialidad': 'Dermatología',
                'telefono': '+54 9 11 3456-7890',
                'email': 'carlos.rodriguez@medisoft.com'
            }
        ]
        
        for medico_data in medicos_data:
            medico = Medico.query.filter_by(dni=medico_data['dni']).first()
            if not medico:
                medico = Medico(**medico_data)
                db.session.add(medico)
        
        # Crear pacientes de ejemplo
        pacientes_data = [
            {
                'dni': '11111111',
                'nombre': 'Ana',
                'apellido': 'López',
                'fecha_nacimiento': datetime.strptime('1985-03-15', '%Y-%m-%d').date(),
                'genero': 'Femenino',
                'telefono': '+54 9 11 1111-1111',
                'email': 'ana.lopez@email.com',
                'direccion': 'Av. Corrientes 1234, CABA'
            },
            {
                'dni': '22222222',
                'nombre': 'Roberto',
                'apellido': 'Martínez',
                'fecha_nacimiento': datetime.strptime('1978-07-22', '%Y-%m-%d').date(),
                'genero': 'Masculino',
                'telefono': '+54 9 11 2222-2222',
                'email': 'roberto.martinez@email.com',
                'direccion': 'Belgrano 567, CABA'
            }
        ]
        
        for paciente_data in pacientes_data:
            paciente = Paciente.query.filter_by(dni=paciente_data['dni']).first()
            if not paciente:
                paciente = Paciente(**paciente_data)
                db.session.add(paciente)
        
        # Crear insumos de ejemplo
        insumos_data = [
            {
                'codigo': 'INS001',
                'nombre': 'Jeringas 10ml',
                'descripcion': 'Jeringas desechables de 10ml',
                'stock': 100,
                'stock_minimo': 20,
                'precio_unitario': 2.50
            },
            {
                'codigo': 'INS002',
                'nombre': 'Guantes Látex M',
                'descripcion': 'Guantes de látex talla M',
                'stock': 200,
                'stock_minimo': 50,
                'precio_unitario': 1.80
            },
            {
                'codigo': 'INS003',
                'nombre': 'Algodón Estéril',
                'descripcion': 'Algodón estéril 100g',
                'stock': 50,
                'stock_minimo': 10,
                'precio_unitario': 5.00
            }
        ]
        
        for insumo_data in insumos_data:
            insumo = Insumo.query.filter_by(codigo=insumo_data['codigo']).first()
            if not insumo:
                insumo = Insumo(**insumo_data)
                db.session.add(insumo)
        
        # Crear medicamentos de ejemplo
        medicamentos_data = [
            {
                'codigo': 'MED001',
                'nombre': 'Paracetamol 500mg',
                'descripcion': 'Analgésico y antipirético',
                'principio_activo': 'Paracetamol',
                'presentacion': 'Comprimidos',
                'stock': 150,
                'stock_minimo': 30,
                'precio_unitario': 0.50,
                'fecha_vencimiento': datetime.strptime('2025-12-31', '%Y-%m-%d').date()
            },
            {
                'codigo': 'MED002',
                'nombre': 'Ibuprofeno 400mg',
                'descripcion': 'Antiinflamatorio no esteroideo',
                'principio_activo': 'Ibuprofeno',
                'presentacion': 'Comprimidos',
                'stock': 120,
                'stock_minimo': 25,
                'precio_unitario': 0.75,
                'fecha_vencimiento': datetime.strptime('2025-10-31', '%Y-%m-%d').date()
            }
        ]
        
        for medicamento_data in medicamentos_data:
            medicamento = Medicamento.query.filter_by(codigo=medicamento_data['codigo']).first()
            if not medicamento:
                medicamento = Medicamento(**medicamento_data)
                db.session.add(medicamento)
        
        # Crear servicios clínicos de ejemplo
        servicios_data = [
            {
                'codigo': 'SER001',
                'nombre': 'Consulta General',
                'descripcion': 'Consulta médica general',
                'precio': 50.00,
                'categoria': 'Consultas'
            },
            {
                'codigo': 'SER002',
                'nombre': 'Electrocardiograma',
                'descripcion': 'Estudio cardíaco',
                'precio': 120.00,
                'categoria': 'Estudios'
            },
            {
                'codigo': 'SER003',
                'nombre': 'Análisis de Sangre',
                'descripcion': 'Análisis bioquímico completo',
                'precio': 80.00,
                'categoria': 'Laboratorio'
            }
        ]
        
        for servicio_data in servicios_data:
            servicio = ServicioClinico.query.filter_by(codigo=servicio_data['codigo']).first()
            if not servicio:
                servicio = ServicioClinico(**servicio_data)
                db.session.add(servicio)
        
        db.session.commit()
        print("✓ Datos de ejemplo creados exitosamente")

def main():
    """Función principal"""
    print("=== Inicialización de la Base de Datos Medisoft ===")
    print()
    
    try:
        create_tables()
        print()
        create_admin_user()
        print()
        create_sample_data()
        print()
        print("=== Inicialización completada exitosamente ===")
        print()
        print("Para iniciar la aplicación:")
        print("1. Asegúrate de tener PostgreSQL instalado y corriendo")
        print("2. Configura las variables de entorno en un archivo .env")
        print("3. Ejecuta: python app.py")
        print()
        print("Credenciales de acceso:")
        print("Usuario: admin")
        print("Contraseña: admin123")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        print("Asegúrate de que PostgreSQL esté instalado y corriendo")
        sys.exit(1)

if __name__ == '__main__':
    create_tables()
    create_admin_user()
