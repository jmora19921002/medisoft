# Medisoft - Sistema de Gestión Médica

Un sistema web completo para la gestión de clínicas médicas desarrollado con Flask y PostgreSQL.

## 🏥 Características

- **Gestión de Pacientes**: Registro, búsqueda y seguimiento de pacientes
- **Gestión de Médicos**: Administración de médicos y especialidades
- **Control de Insumos**: Inventario y control de stock de insumos médicos
- **Gestión de Medicamentos**: Control de medicamentos con fechas de vencimiento
- **Honorarios Médicos**: Administración de honorarios por médico y servicio
- **Servicios Clínicos**: Catálogo de servicios médicos con precios
- **Dashboard**: Panel de control con estadísticas y accesos rápidos
- **Sistema de Usuarios**: Autenticación y control de acceso

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticación**: Flask-Login
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Iconos**: Font Awesome

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd medisoft
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

1. Instalar PostgreSQL en tu sistema
2. Crear una base de datos:
```sql
CREATE DATABASE medisoft_db;
CREATE USER medisoft_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE medisoft_db TO medisoft_user;
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=development

# Configuración de PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=medisoft_user
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=medisoft_db

# URL de la base de datos
DATABASE_URL=postgresql://medisoft_user:tu_password@localhost:5432/medisoft_db
```

### 6. Inicializar la base de datos

```bash
python init_db.py
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 👤 Credenciales de Acceso

- **Usuario**: admin
- **Contraseña**: admin123

**⚠️ Importante**: Cambia estas credenciales después del primer inicio de sesión.

## 📁 Estructura del Proyecto

```
medisoft/
├── app.py                 # Aplicación principal Flask
├── config.py              # Configuración de la aplicación
├── init_db.py             # Script de inicialización de BD
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── .env                  # Variables de entorno (crear)
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── login.html        # Página de login
│   ├── index.html        # Dashboard
│   ├── pacientes/        # Gestión de pacientes
│   ├── medicos/          # Gestión de médicos
│   ├── insumos/          # Gestión de insumos
│   ├── medicamentos/     # Gestión de medicamentos
│   ├── honorarios/       # Gestión de honorarios
│   └── servicios/        # Gestión de servicios
└── static/               # Archivos estáticos
    ├── css/              # Hojas de estilo
    └── js/               # JavaScript
```

## 🗄️ Modelos de Base de Datos

### Usuario
- Gestión de usuarios del sistema
- Roles y permisos

### Paciente
- Información personal y médica
- Historial médico

### Médico
- Datos profesionales
- Especialidades
- Información de contacto

### Insumo
- Control de inventario
- Stock mínimo y actual
- Precios unitarios

### Medicamento
- Control de medicamentos
- Fechas de vencimiento
- Principios activos

### Honorario Médico
- Honorarios por médico
- Servicios específicos
- Precios

### Servicio Clínico
- Catálogo de servicios
- Categorías
- Precios

### Historial Médico
- Consultas médicas
- Diagnósticos
- Tratamientos

## 🔧 Funcionalidades Principales

### Dashboard
- Estadísticas generales
- Accesos rápidos
- Actividad reciente

### Gestión de Pacientes
- Registro de nuevos pacientes
- Búsqueda y filtros
- Historial médico
- Información de contacto

### Gestión de Médicos
- Registro de médicos
- Especialidades
- Honorarios
- Información profesional

### Control de Inventario
- Insumos médicos
- Medicamentos
- Alertas de stock bajo
- Fechas de vencimiento

### Servicios y Honorarios
- Catálogo de servicios
- Honorarios por médico
- Precios y categorías

## 🚀 Despliegue en Producción

### Usando Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Usando Docker (opcional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔒 Seguridad

- Autenticación de usuarios
- Contraseñas hasheadas
- Protección CSRF
- Validación de formularios
- Control de acceso por roles

## 📊 Reportes y Estadísticas

- Dashboard con métricas
- Estadísticas de pacientes
- Control de inventario
- Reportes de servicios

## 🛠️ Mantenimiento

### Backup de Base de Datos

```bash
pg_dump medisoft_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Base de Datos

```bash
psql medisoft_db < backup_file.sql
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

## 🔄 Actualizaciones

Para actualizar el sistema:

1. Hacer backup de la base de datos
2. Actualizar el código
3. Ejecutar migraciones si es necesario
4. Reiniciar la aplicación

---

**Desarrollado con ❤️ para la comunidad médica**
