import sqlite3

# Cambia la ruta si tu base de datos no está en esta ubicación
DB_PATH = 'instance/medisoft.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Agregar columnas si no existen
try:
    cursor.execute("ALTER TABLE empresa ADD COLUMN correo_emisor VARCHAR(120);")
except Exception as e:
    print('correo_emisor:', e)
try:
    cursor.execute("ALTER TABLE empresa ADD COLUMN correo_password VARCHAR(120);")
except Exception as e:
    print('correo_password:', e)
try:
    cursor.execute("ALTER TABLE empresa ADD COLUMN smtp_server VARCHAR(120);")
except Exception as e:
    print('smtp_server:', e)
try:
    cursor.execute("ALTER TABLE empresa ADD COLUMN smtp_port VARCHAR(10);")
except Exception as e:
    print('smtp_port:', e)

conn.commit()
conn.close()
print('Migración completada.')
