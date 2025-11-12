from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from fastapi import Header
import sqlite3
import os

# ===============================
# CONFIGURACIÓN DE LA APLICACIÓN
# ===============================
app = FastAPI(title="API de Reservas Deportivas - Parcial UTN FRT (6 tablas)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # permite conexión desde el frontend local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# CONEXIÓN Y CREACIÓN DE BASE DE DATOS
# ===============================
DB_NAME = "reservas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    first_time = not os.path.exists(DB_NAME)
    conn = get_db_connection()
    cur = conn.cursor()

    # 1) Sucursales (sede donde están las canchas)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sucursales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT
        );
    """)

    # 2) Tipos de canchas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tipos_cancha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );
    """)

    # 3) Canchas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS canchas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            tipo_id INTEGER NOT NULL,
            sucursal_id INTEGER NOT NULL,
            capacidad INTEGER NOT NULL,
            FOREIGN KEY (tipo_id) REFERENCES tipos_cancha(id) ON DELETE RESTRICT,
            FOREIGN KEY (sucursal_id) REFERENCES sucursales(id) ON DELETE RESTRICT
        );
    """)

    # 4) Usuarios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefono TEXT
        );
    """)

    # 5) Métodos de pago
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metodo TEXT NOT NULL UNIQUE
        );
    """)

    # 6) Reservas (relacionada con canchas, usuarios y pagos)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            cancha_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            duracion INTEGER NOT NULL,
            jugadores INTEGER NOT NULL,
            pago_id INTEGER NOT NULL,
            fecha_creacion TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (cancha_id) REFERENCES canchas(id) ON DELETE CASCADE,
            FOREIGN KEY (pago_id) REFERENCES pagos(id) ON DELETE RESTRICT
        );
    """)

    conn.commit()

    # Seed inicial: sólo si la DB no existía antes (para evitar duplicados)
    if first_time:
        # Sucursales
        sucursales = [
            ("Sede Central", "Av. Principal 123"),
            ("Sede Norte", "Calle Norte 45"),
            ("Sede Sur", "Boulevard Sur 9"),
            ("Sede Este", "Ruta Este 1"),
            ("Sede Oeste", "Av. Oeste 77"),
            ("Sede Universitaria", "Campus UTN 10"),
            ("Sede Centro", "Calle Centro 50"),
            ("Sede Parque", "Parque Central 3"),
            ("Sede Barrio", "Barrio Verde 12"),
            ("Sede Villa", "Villa Azul 6"),
        ]
        cur.executemany("INSERT INTO sucursales (nombre, direccion) VALUES (?, ?);", sucursales)

        # Tipos de canchas
        tipos = [("Fútbol 5",), ("Fútbol 7",), ("Fútbol 11",), ("Césped Sintético",), ("Cemento",),
                 ("Polideportivo",), ("Cancha Techada",), ("Cancha Exterior",), ("Pista",), ("Multiuso",)]
        cur.executemany("INSERT INTO tipos_cancha (nombre) VALUES (?);", tipos)

        # Canchas (10)
        canchas = []
        for i in range(1, 11):
            nombre = f"Cancha {i}"
            tipo_id = (i % 5) + 1       # 1..5
            sucursal_id = ((i-1) % 10) + 1  # 1..10
            capacidad = 5 + (i % 4) * 3
            canchas.append((nombre, tipo_id, sucursal_id, capacidad))
        cur.executemany("INSERT INTO canchas (nombre, tipo_id, sucursal_id, capacidad) VALUES (?, ?, ?, ?);", canchas)

        # Usuarios (10)
        usuarios = [
            ("Juan Pérez", "juanp@example.com", "341-111-0001"),
            ("María Gómez", "mariag@example.com", "341-111-0002"),
            ("Carlos Ruiz", "carlosr@example.com", "341-111-0003"),
            ("Lucía Fernández", "luciaf@example.com", "341-111-0004"),
            ("Diego Martín", "diegom@example.com", "341-111-0005"),
            ("Ana Torres", "anat@example.com", "341-111-0006"),
            ("Pablo Díaz", "pablod@example.com", "341-111-0007"),
            ("Sofía López", "sofial@example.com", "341-111-0008"),
            ("Mateo Ruiz", "mateor@example.com", "341-111-0009"),
            ("Valentina Cruz", "valentic@example.com", "341-111-0010"),
        ]
        cur.executemany("INSERT INTO usuarios (nombre, email, telefono) VALUES (?, ?, ?);", usuarios)

        # Métodos de pago (pagos)
        pagos = [("Efectivo",), ("Transferencia",), ("Tarjeta",), ("MercadoPago",), ("QR",),
                 ("Cheque",), ("Contraentrega",), ("Otro",), ("CuentaCorriente",), ("Débito",)]
        cur.executemany("INSERT INTO pagos (metodo) VALUES (?);", pagos)

        # Reservas (10) - combinando usuarios, canchas y pagos
        reservas = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(1, 11):
            usuario_id = i
            cancha_id = i
            fecha = (datetime.now()).strftime("%Y-%m-%d")
            hora = f"{10 + (i % 8)}:00"
            duracion = 60 if i % 2 == 0 else 90
            jugadores = 6 + (i % 6)
            pago_id = (i % 5) + 1
            fecha_creacion = now
            reservas.append((usuario_id, cancha_id, fecha, hora, duracion, jugadores, pago_id, fecha_creacion))
        cur.executemany("""
            INSERT INTO reservas (usuario_id, cancha_id, fecha, hora, duracion, jugadores, pago_id, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, reservas)

        conn.commit()

    conn.close()

# Inicializo la DB (crea tablas y seeds si no existía)
init_db()

# ===============================
# MODELOS Pydantic
# ===============================
class CanchaCreate(BaseModel):
    nombre: str
    tipo_id: int
    sucursal_id: int
    capacidad: int

class CanchaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_id: Optional[int] = None
    sucursal_id: Optional[int] = None
    capacidad: Optional[int] = None

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

class ReservaCreate(BaseModel):
    nombre: str            # nombre del usuario — si no existe, lo creamos
    email: str
    cancha_id: int
    fecha: str
    hora: str
    duracion: int
    jugadores: int
    pago_id: int

class ReservaUpdate(BaseModel):
    fecha: Optional[str] = None
    hora: Optional[str] = None
    duracion: Optional[int] = None
    jugadores: Optional[int] = None
    pago_id: Optional[int] = None

# ===============================
# REDIRECCIÓN A DOCUMENTACIÓN
# ===============================
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# ===============================
# ENDPOINTS: TIPOS / SUCURSALES / PAGOS / CANCHAS / USUARIOS / RESERVAS
# (básicos: listar, crear, actualizar, eliminar donde corresponde)
# ===============================

# --- TIPOS DE CANCHA ---
@app.get("/tipos")
def listar_tipos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tipos_cancha")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return items

# --- SUCURSALES ---
@app.get("/sucursales")
def listar_sucursales():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sucursales")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return items

# --- PAGOS ---
@app.get("/pagos")
def listar_pagos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pagos")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return items

# --- CANCHAS ---
@app.post("/canchas", status_code=201)
def crear_cancha(cancha: CanchaCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO canchas (nombre, tipo_id, sucursal_id, capacidad) VALUES (?, ?, ?, ?)",
            (cancha.nombre, cancha.tipo_id, cancha.sucursal_id, cancha.capacidad)
        )
        conn.commit()
        cancha_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=409, detail="Ya existe una cancha con ese nombre o referencia inválida.")
    conn.close()
    return {"id": cancha_id, "mensaje": "Cancha creada correctamente"}

@app.get("/canchas")
def listar_canchas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.nombre, c.capacidad, c.tipo_id, t.nombre AS tipo_nombre,
               c.sucursal_id, s.nombre AS sucursal_nombre
        FROM canchas c
        LEFT JOIN tipos_cancha t ON c.tipo_id = t.id
        LEFT JOIN sucursales s ON c.sucursal_id = s.id
    """)
    canchas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return canchas

@app.put("/canchas/{id}")
def actualizar_cancha(id: int, cancha: CanchaUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM canchas WHERE id=?", (id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    if cancha.nombre:
        cur.execute("UPDATE canchas SET nombre=? WHERE id=?", (cancha.nombre, id))
    if cancha.tipo_id:
        cur.execute("UPDATE canchas SET tipo_id=? WHERE id=?", (cancha.tipo_id, id))
    if cancha.sucursal_id:
        cur.execute("UPDATE canchas SET sucursal_id=? WHERE id=?", (cancha.sucursal_id, id))
    if cancha.capacidad:
        cur.execute("UPDATE canchas SET capacidad=? WHERE id=?", (cancha.capacidad, id))
    conn.commit()
    conn.close()
    return {"mensaje": "Cancha actualizada correctamente"}

# Clave secreta de administrador
ADMIN_KEY = "RubenNieva2025"

@app.delete("/reservas/{id}")
def eliminar_reserva(id: int, x_admin_key: str = Header(None)):
            if x_admin_key != ADMIN_KEY:
                raise HTTPException(status_code=403, detail="Acceso denegado. Clave de administrador inválida.")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM reservas WHERE id=?", (id,))
            if cur.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail="Reserva no encontrada")
            conn.commit()
            conn.close()
            return {"mensaje": f"Reserva {id} eliminada correctamente"}

# --- USUARIOS ---
@app.post("/usuarios", status_code=201)
def crear_usuario(u: UsuarioCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios (nombre, email, telefono) VALUES (?, ?, ?)",
                    (u.nombre, u.email, u.telefono))
        conn.commit()
        uid = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="El email ya está registrado.")
    conn.close()
    return {"id": uid, "mensaje": "Usuario creado"}

@app.get("/usuarios")
def listar_usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return items

@app.get("/usuarios/{id}")
def obtener_usuario(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(row)

# --- RESERVAS ---
@app.get("/reservas")
def listar_reservas(
    fecha: Optional[str] = Query(None),
    cancha_id: Optional[int] = Query(None),
    pago_id: Optional[int] = Query(None)
):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT r.*, u.nombre AS usuario_nombre, u.email AS usuario_email,
               c.nombre AS cancha_nombre, p.metodo AS metodo_pago
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN canchas c ON r.cancha_id = c.id
        JOIN pagos p ON r.pago_id = p.id
        WHERE 1=1
    """
    params = []
    if fecha:
        query += " AND r.fecha = ?"
        params.append(fecha)
    if cancha_id:
        query += " AND r.cancha_id = ?"
        params.append(cancha_id)
    if pago_id:
        query += " AND r.pago_id = ?"
        params.append(pago_id)

    cur.execute(query, params)
    reservas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return reservas

@app.post("/reservas", status_code=201)
def crear_reserva(r: ReservaCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1) Verifico cancha existe
    cur.execute("SELECT * FROM canchas WHERE id=?", (r.cancha_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="La cancha seleccionada no existe.")

    # 2) Verifico metodo de pago existe
    cur.execute("SELECT * FROM pagos WHERE id=?", (r.pago_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Método de pago inválido.")
    
    # 3) Verifico si ya hay una reserva en esa cancha, fecha y hora
    cur.execute("""
                SELECT id FROM reservas
                WHERE cancha_id=? AND fecha=? AND hora=?
                """, (r.cancha_id, r.fecha, r.hora))
    existente = cur.fetchone()
    if existente:
        conn.close()
        raise HTTPException(status_code=409, detail="Ya existe una reserva para esa cancha en la fecha y hora seleccionadas.")

    # 4) Me fijo si el usuario ya existe por email; si no, lo creo
    cur.execute("SELECT * FROM usuarios WHERE email=?", (r.email,))
    user = cur.fetchone()
    if user:
        usuario_id = user["id"]
    else:
        cur.execute("INSERT INTO usuarios (nombre, email) VALUES (?, ?)", (r.nombre, r.email))
        usuario_id = cur.lastrowid

    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  

    cur.execute("""
        INSERT INTO reservas (usuario_id, cancha_id, fecha, hora, duracion, jugadores, pago_id, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (usuario_id, r.cancha_id, r.fecha, r.hora, r.duracion, r.jugadores, r.pago_id, fecha_creacion))

    conn.commit()
    reserva_id = cur.lastrowid
    cur.execute("""
        SELECT r.*, u.nombre AS usuario_nombre, u.email AS usuario_email,
               c.nombre AS cancha_nombre, p.metodo AS metodo_pago
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN canchas c ON r.cancha_id = c.id
        JOIN pagos p ON r.pago_id = p.id
        WHERE r.id = ?
    """, (reserva_id,))
    nueva = cur.fetchone()
    conn.close()
    return dict(nueva)

@app.put("/reservas/{id}")
def actualizar_reserva(id: int, datos: ReservaUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reservas WHERE id=?", (id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if datos.fecha:
        cur.execute("UPDATE reservas SET fecha=? WHERE id=?", (datos.fecha, id))
    if datos.hora:
        cur.execute("UPDATE reservas SET hora=? WHERE id=?", (datos.hora, id))
    if datos.duracion:
        cur.execute("UPDATE reservas SET duracion=? WHERE id=?", (datos.duracion, id))
    if datos.jugadores:
        cur.execute("UPDATE reservas SET jugadores=? WHERE id=?", (datos.jugadores, id))
    if datos.pago_id:
        # verificar pago_id valida
        cur.execute("SELECT * FROM pagos WHERE id=?", (datos.pago_id,))
        if not cur.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Método de pago inválido.")
        cur.execute("UPDATE reservas SET pago_id=? WHERE id=?", (datos.pago_id, id))

    conn.commit()
    conn.close()
    return {"mensaje": "Reserva actualizada correctamente"}

@app.delete("/reservas/{id}")
def eliminar_reserva(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reservas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"mensaje": f"Reserva {id} eliminada correctamente"}

# ===============================
# ENDPOINT RESUMEN
# ===============================
@app.get("/resumen")
def resumen_general():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM canchas")
    total_canchas = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reservas")
    total_reservas = cur.fetchone()[0]

    cur.execute("""
        SELECT c.nombre, COUNT(r.id) as cantidad
        FROM canchas c LEFT JOIN reservas r ON c.id = r.cancha_id
        GROUP BY c.nombre ORDER BY cantidad DESC LIMIT 1
    """)
    mas_reservada = cur.fetchone()

    conn.close()
    return {
        "total_canchas": total_canchas,
        "total_reservas": total_reservas,
        "cancha_mas_reservada": dict(mas_reservada) if mas_reservada else None
    }