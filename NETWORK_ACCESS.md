# 🌐 Acceso a Medisoft desde la Red Local

## 📋 Requisitos Previos

1. **Python instalado** en tu máquina
2. **Dependencias instaladas** (`pip install -r requirements.txt`)
3. **Firewall configurado** para permitir conexiones al puerto 5000

## 🚀 Formas de Ejecutar la Aplicación

### Opción 1: Script Python (Recomendado)
```bash
# Solo localhost (más seguro)
python run.py local

# Accesible desde la red local
python run.py network

# Configuración personalizada
python run.py custom

# Ver ayuda
python run.py help
```

### Opción 2: Archivo Batch (Windows)
```cmd
# Doble clic en el archivo
run_network.bat
```

### Opción 3: Comando Directo
```bash
# Accesible desde la red
python app.py

# Solo localhost
set HOST=127.0.0.1 && python app.py
```

## 🌍 Acceso desde Otras Máquinas

### 1. Obtener tu IP de Red
```cmd
# En Windows
ipconfig

# En Linux/Mac
ifconfig
# o
ip addr
```

Busca la línea que contenga tu IP local (generalmente 192.168.x.x o 10.x.x.x)

### 2. URL de Acceso
```
http://TU_IP_LOCAL:5000

Ejemplo:
http://192.168.1.100:5000
```

### 3. Verificar Conexión
- Desde tu máquina: `http://localhost:5000`
- Desde otra máquina: `http://TU_IP:5000`

## 🔒 Configuración de Seguridad

### Firewall de Windows
1. Abrir "Firewall de Windows Defender"
2. "Configuración avanzada"
3. "Reglas de entrada"
4. "Nueva regla" → "Puerto"
5. TCP, puerto específico: 5000
6. "Permitir la conexión"
7. Aplicar a todos los perfiles
8. Nombre: "Medisoft Puerto 5000"

### Firewall de Router
- Verificar que el puerto 5000 esté abierto
- Configurar redirección de puertos si es necesario

## ⚠️ Consideraciones Importantes

### Desarrollo vs Producción
- **Desarrollo**: `host='0.0.0.0'` (accesible desde red)
- **Producción**: `host='127.0.0.1'` (solo localhost) + proxy reverso

### Seguridad
- La aplicación está en modo debug (NO usar en producción)
- Cualquier persona en tu red puede acceder
- Considerar autenticación adicional si es necesario

### Rendimiento
- El modo debug puede ser más lento
- Para mejor rendimiento, usar modo producción

## 🐛 Solución de Problemas

### Error: "Address already in use"
```bash
# Encontrar proceso usando el puerto 5000
netstat -ano | findstr :5000

# Terminar proceso (reemplazar PID con el número real)
taskkill /PID PID /F
```

### No se puede acceder desde otras máquinas
1. Verificar firewall
2. Verificar que esté ejecutándose en `0.0.0.0:5000`
3. Verificar que las máquinas estén en la misma red
4. Probar con `ping` entre máquinas

### Error de conexión
1. Verificar que la aplicación esté ejecutándose
2. Verificar puerto correcto
3. Verificar IP correcta
4. Verificar firewall

## 📱 Acceso desde Dispositivos Móviles

### Misma Red WiFi
- Conectar dispositivo móvil a la misma red WiFi
- Usar la IP de tu máquina + puerto 5000
- Ejemplo: `http://192.168.1.100:5000`

### Red Diferente
- Configurar redirección de puertos en router
- Usar IP pública de tu router
- Considerar VPN para mayor seguridad

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Configurar host y puerto
set HOST=0.0.0.0
set PORT=5000
set DEBUG=True

# Ejecutar
python app.py
```

### Archivo .env
```env
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

## 📞 Soporte

Si tienes problemas:
1. Verificar que Python esté instalado correctamente
2. Verificar dependencias instaladas
3. Verificar configuración de firewall
4. Verificar que esté ejecutándose en el puerto correcto
5. Revisar logs de la aplicación

---

**Nota**: Este documento asume que estás ejecutando la aplicación en Windows. Para otros sistemas operativos, los comandos pueden variar ligeramente.
