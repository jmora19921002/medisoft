from database_config import db_manager
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox

class Medico:
    def __init__(self, id=None, nombre="", apellido="", edad=None, especialidad="", telefono="", email=""):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.especialidad = especialidad
        self.telefono = telefono
        self.email = email
    
    def guardar(self):
        query = """
        INSERT INTO medicos (nombre, apellido, edad, especialidad, telefono, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.nombre, self.apellido, self.edad, self.especialidad, self.telefono, self.email)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE medicos SET nombre=%s, apellido=%s, edad=%s, especialidad=%s, telefono=%s, email=%s
        WHERE id=%s
        """
        params = (self.nombre, self.apellido, self.edad, self.especialidad, self.telefono, self.email, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM medicos WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM medicos ORDER BY apellido, nombre"
        return db_manager.execute_query(query)
    
    @staticmethod
    def obtener_por_id(id):
        query = "SELECT * FROM medicos WHERE id=%s"
        result = db_manager.execute_query(query, (id,))
        if result:
            return result[0]
        return None

class Enfermera:
    def __init__(self, id=None, nombre="", apellido="", edad=None, especialidad="", telefono="", email=""):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.especialidad = especialidad
        self.telefono = telefono
        self.email = email
    
    def guardar(self):
        query = """
        INSERT INTO enfermeras (nombre, apellido, edad, especialidad, telefono, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.nombre, self.apellido, self.edad, self.especialidad, self.telefono, self.email)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE enfermeras SET nombre=%s, apellido=%s, edad=%s, especialidad=%s, telefono=%s, email=%s
        WHERE id=%s
        """
        params = (self.nombre, self.apellido, self.edad, self.especialidad, self.telefono, self.email, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM enfermeras WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM enfermeras ORDER BY apellido, nombre"
        return db_manager.execute_query(query)
    
    @staticmethod
    def obtener_por_id(id):
        query = "SELECT * FROM enfermeras WHERE id=%s"
        result = db_manager.execute_query(query, (id,))
        if result:
            return result[0]
        return None

class Paciente:
    def __init__(self, id=None, nombre="", apellido="", fecha_nacimiento=None, edad=None, 
                 genero="", telefono="", email="", direccion="", grupo_sanguineo="", 
                 alergias="", antecedentes=""):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.genero = genero
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.grupo_sanguineo = grupo_sanguineo
        self.alergias = alergias
        self.antecedentes = antecedentes
    
    def guardar(self):
        query = """
        INSERT INTO pacientes (nombre, apellido, fecha_nacimiento, edad, genero, telefono, 
                              email, direccion, grupo_sanguineo, alergias, antecedentes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.nombre, self.apellido, self.fecha_nacimiento, self.edad, self.genero,
                 self.telefono, self.email, self.direccion, self.grupo_sanguineo, 
                 self.alergias, self.antecedentes)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE pacientes SET nombre=%s, apellido=%s, fecha_nacimiento=%s, edad=%s, genero=%s,
                            telefono=%s, email=%s, direccion=%s, grupo_sanguineo=%s, 
                            alergias=%s, antecedentes=%s WHERE id=%s
        """
        params = (self.nombre, self.apellido, self.fecha_nacimiento, self.edad, self.genero,
                 self.telefono, self.email, self.direccion, self.grupo_sanguineo, 
                 self.alergias, self.antecedentes, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM pacientes WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM pacientes ORDER BY apellido, nombre"
        return db_manager.execute_query(query)
    
    @staticmethod
    def obtener_por_id(id):
        query = "SELECT * FROM pacientes WHERE id=%s"
        result = db_manager.execute_query(query, (id,))
        if result:
            return result[0]
        return None
    
    @staticmethod
    def buscar_por_nombre(nombre, apellido=""):
        query = """
        SELECT * FROM pacientes 
        WHERE nombre LIKE %s OR apellido LIKE %s 
        ORDER BY apellido, nombre
        """
        params = (f"%{nombre}%", f"%{apellido}%")
        return db_manager.execute_query(query, params)

class HistoriaMedica:
    def __init__(self, id=None, paciente_id=None, medico_id=None, fecha_consulta=None,
                 motivo_consulta="", sintomas="", diagnostico="", tratamiento="", 
                 plan_medico="", observaciones=""):
        self.id = id
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha_consulta = fecha_consulta or datetime.now()
        self.motivo_consulta = motivo_consulta
        self.sintomas = sintomas
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.plan_medico = plan_medico
        self.observaciones = observaciones
    
    def guardar(self):
        query = """
        INSERT INTO historias_medicas (paciente_id, medico_id, fecha_consulta, motivo_consulta,
                                      sintomas, diagnostico, tratamiento, plan_medico, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.paciente_id, self.medico_id, self.fecha_consulta, self.motivo_consulta,
                 self.sintomas, self.diagnostico, self.tratamiento, self.plan_medico, 
                 self.observaciones)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE historias_medicas SET paciente_id=%s, medico_id=%s, fecha_consulta=%s,
                                    motivo_consulta=%s, sintomas=%s, diagnostico=%s,
                                    tratamiento=%s, plan_medico=%s, observaciones=%s
        WHERE id=%s
        """
        params = (self.paciente_id, self.medico_id, self.fecha_consulta, self.motivo_consulta,
                 self.sintomas, self.diagnostico, self.tratamiento, self.plan_medico, 
                 self.observaciones, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM historias_medicas WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_por_paciente(paciente_id):
        query = """
        SELECT hm.*, m.nombre as medico_nombre, m.apellido as medico_apellido
        FROM historias_medicas hm
        LEFT JOIN medicos m ON hm.medico_id = m.id
        WHERE hm.paciente_id = %s
        ORDER BY hm.fecha_consulta DESC
        """
        return db_manager.execute_query(query, (paciente_id,))
    
    @staticmethod
    def obtener_por_id(id):
        query = """
        SELECT hm.*, m.nombre as medico_nombre, m.apellido as medico_apellido,
               p.nombre as paciente_nombre, p.apellido as paciente_apellido
        FROM historias_medicas hm
        LEFT JOIN medicos m ON hm.medico_id = m.id
        LEFT JOIN pacientes p ON hm.paciente_id = p.id
        WHERE hm.id = %s
        """
        result = db_manager.execute_query(query, (id,))
        if result:
            return result[0]
        return None

class Examen:
    def __init__(self, id=None, historia_id=None, tipo_examen="", descripcion="", 
                 resultado="", fecha_examen=None, fecha_resultado=None, estado="Pendiente"):
        self.id = id
        self.historia_id = historia_id
        self.tipo_examen = tipo_examen
        self.descripcion = descripcion
        self.resultado = resultado
        self.fecha_examen = fecha_examen
        self.fecha_resultado = fecha_resultado
        self.estado = estado
    
    def guardar(self):
        query = """
        INSERT INTO examenes (historia_id, tipo_examen, descripcion, resultado, 
                             fecha_examen, fecha_resultado, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.historia_id, self.tipo_examen, self.descripcion, self.resultado,
                 self.fecha_examen, self.fecha_resultado, self.estado)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE examenes SET historia_id=%s, tipo_examen=%s, descripcion=%s, resultado=%s,
                           fecha_examen=%s, fecha_resultado=%s, estado=%s
        WHERE id=%s
        """
        params = (self.historia_id, self.tipo_examen, self.descripcion, self.resultado,
                 self.fecha_examen, self.fecha_resultado, self.estado, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM examenes WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_por_historia(historia_id):
        query = "SELECT * FROM examenes WHERE historia_id=%s ORDER BY fecha_examen DESC"
        return db_manager.execute_query(query, (historia_id,))

class Tratamiento:
    def __init__(self, id=None, historia_id=None, nombre_tratamiento="", descripcion="",
                 medicamentos="", dosis="", duracion="", fecha_inicio=None, fecha_fin=None, 
                 estado="Activo"):
        self.id = id
        self.historia_id = historia_id
        self.nombre_tratamiento = nombre_tratamiento
        self.descripcion = descripcion
        self.medicamentos = medicamentos
        self.dosis = dosis
        self.duracion = duracion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
    
    def guardar(self):
        query = """
        INSERT INTO tratamientos (historia_id, nombre_tratamiento, descripcion, medicamentos,
                                 dosis, duracion, fecha_inicio, fecha_fin, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.historia_id, self.nombre_tratamiento, self.descripcion, 
                 self.medicamentos, self.dosis, self.duracion, self.fecha_inicio, 
                 self.fecha_fin, self.estado)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE tratamientos SET historia_id=%s, nombre_tratamiento=%s, descripcion=%s,
                               medicamentos=%s, dosis=%s, duracion=%s, fecha_inicio=%s,
                               fecha_fin=%s, estado=%s
        WHERE id=%s
        """
        params = (self.historia_id, self.nombre_tratamiento, self.descripcion, 
                 self.medicamentos, self.dosis, self.duracion, self.fecha_inicio, 
                 self.fecha_fin, self.estado, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM tratamientos WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_por_historia(historia_id):
        query = "SELECT * FROM tratamientos WHERE historia_id=%s ORDER BY fecha_inicio DESC"
        return db_manager.execute_query(query, (historia_id,))

class Cita:
    def __init__(self, id=None, paciente_id=None, medico_id=None, fecha_cita=None,
                 motivo="", estado="Programada", notas=""):
        self.id = id
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha_cita = fecha_cita
        self.motivo = motivo
        self.estado = estado
        self.notas = notas
    
    def guardar(self):
        query = """
        INSERT INTO citas (paciente_id, medico_id, fecha_cita, motivo, estado, notas)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.paciente_id, self.medico_id, self.fecha_cita, self.motivo, 
                 self.estado, self.notas)
        return db_manager.execute_query(query, params)
    
    def actualizar(self):
        query = """
        UPDATE citas SET paciente_id=%s, medico_id=%s, fecha_cita=%s, motivo=%s, estado=%s, notas=%s
        WHERE id=%s
        """
        params = (self.paciente_id, self.medico_id, self.fecha_cita, self.motivo, 
                 self.estado, self.notas, self.id)
        return db_manager.execute_query(query, params)
    
    def eliminar(self):
        query = "DELETE FROM citas WHERE id=%s"
        return db_manager.execute_query(query, (self.id,))
    
    @staticmethod
    def obtener_todas():
        query = """
        SELECT c.*, p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               m.nombre as medico_nombre, m.apellido as medico_apellido
        FROM citas c
        LEFT JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN medicos m ON c.medico_id = m.id
        ORDER BY c.fecha_cita DESC
        """
        return db_manager.execute_query(query)
    
    @staticmethod
    def obtener_por_fecha(fecha):
        query = """
        SELECT c.*, p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               m.nombre as medico_nombre, m.apellido as medico_apellido
        FROM citas c
        LEFT JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN medicos m ON c.medico_id = m.id
        WHERE DATE(c.fecha_cita) = %s
        ORDER BY c.fecha_cita
        """
        return db_manager.execute_query(query, (fecha,)) 