#!/usr/bin/env python3
"""
Script de instalación rápida para Medisoft
Configura el entorno y la base de datos automáticamente
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Imprimir banner de bienvenida"""
    print("=" * 60)
    print("🏥 MEDISOFT - Sistema de Gestión Médica")
    print("=" * 60)
    print("Script de instalación automática")
    print("=" * 60)

def check_python_version():
    """Verificar versión de Python"""
    print("📋 Verificando requisitos...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Instalando dependencias...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        return False

def create_env_file():
    """Crear archivo .env si no existe"""
    print("\n🔧 Configurando variables de entorno...")
    
    if os.path.exists('.env'):
        print("✅ Archivo .env ya existe")
        return True
    
    # Leer el archivo de ejemplo
    if os.path.exists('env_example.txt'):
        with open('env_example.txt', 'r') as f:
            env_content = f.read()
        
        # Crear archivo .env
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado")
        print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de PostgreSQL")
        return True
    else:
        print("❌ No se encontró el archivo env_example.txt")
        return False

def check_postgresql():
    """Verificar si PostgreSQL está disponible"""
    print("\n🗄️  Verificando PostgreSQL...")
    
    try:
        # Intentar importar psycopg2
        import psycopg2
        print("✅ Driver PostgreSQL (psycopg2) - OK")
        return True
    except ImportError:
        print("❌ Error: psycopg2 no está instalado")
        print("   Ejecuta: pip install psycopg2-binary")
        return False

def setup_database():
    """Configurar la base de datos"""
    print("\n🗄️  Configurando base de datos...")
    
    try:
        # Importar y ejecutar el script de inicialización
        from init_db import main as init_db_main
        init_db_main()
        return True
    except Exception as e:
        print(f"❌ Error al configurar la base de datos: {str(e)}")
        print("   Asegúrate de que PostgreSQL esté instalado y corriendo")
        print("   Verifica las credenciales en el archivo .env")
        return False

def print_next_steps():
    """Imprimir próximos pasos"""
    print("\n" + "=" * 60)
    print("🎉 ¡Instalación completada!")
    print("=" * 60)
    print("\n📋 Próximos pasos:")
    print("1. Configura PostgreSQL:")
    print("   - Instala PostgreSQL si no lo tienes")
    print("   - Crea una base de datos: CREATE DATABASE medisoft_db;")
    print("   - Edita el archivo .env con tus credenciales")
    print("\n2. Inicializa la base de datos:")
    print("   python init_db.py")
    print("\n3. Ejecuta la aplicación:")
    print("   python app.py")
    print("\n4. Accede a la aplicación:")
    print("   http://localhost:5000")
    print("\n5. Credenciales de acceso:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n⚠️  IMPORTANTE: Cambia las credenciales después del primer acceso")
    print("=" * 60)

def main():
    """Función principal"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    # Crear archivo .env
    if not create_env_file():
        sys.exit(1)
    
    # Verificar PostgreSQL
    if not check_postgresql():
        print("\n💡 Para instalar PostgreSQL:")
        if platform.system() == "Windows":
            print("   - Descarga desde: https://www.postgresql.org/download/windows/")
        elif platform.system() == "Darwin":  # macOS
            print("   - brew install postgresql")
        else:  # Linux
            print("   - sudo apt-get install postgresql postgresql-contrib")
        sys.exit(1)
    
    # Configurar base de datos
    if not setup_database():
        print_next_steps()
        sys.exit(1)
    
    print_next_steps()

if __name__ == '__main__':
    main()
