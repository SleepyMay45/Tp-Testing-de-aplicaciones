"""
main.py - Backend de Gestión de Envíos
Materia: Testing de Aplicaciones (UADE)
Equipo 4 - Developer: Mayra Gutierrez

NOTA INTERNA PARA EL EQUIPO:
Se han dejado los siguientes bugs intencionales para que sean detectados en testing:
  [BUG-01] getTarifa acepta peso negativo o cero sin error (validación incompleta)
  [BUG-02] createDespacho permite direccion_destino vacía o en blanco sin rechazar el request
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ─── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="API Gestión de Envíos",
    description="Sistema de gestión de envíos - UADE Testing de Aplicaciones - Equipo 4",
    version="1.0.0"
)

# ─── Rutas a archivos JSON ─────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USUARIOS_FILE  = os.path.join(DATA_DIR, "usuarios.json")
DESPACHOS_FILE = os.path.join(DATA_DIR, "despachos.json")
TARIFAS_FILE   = os.path.join(DATA_DIR, "tarifas.json")
QUEJAS_FILE    = os.path.join(DATA_DIR, "quejas.json")

# ─── Helpers de persistencia ───────────────────────────────────────────────────

def leer_json(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def escribir_json(path: str, data: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Modelos Pydantic ──────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class RegistroRequest(BaseModel):
    nombre: str
    email: str
    password: str

class DespachoRequest(BaseModel):
    remitente: str
    destinatario: str
    direccion_origen: str
    direccion_destino: str
    peso_kg: float
    notas: Optional[str] = ""

class ActualizarEstadoRequest(BaseModel):
    estado: str  # pendiente | en_camino | entregado | cancelado

class QuejasRequest(BaseModel):
    despacho_id: str
    tipo: str           # "queja" | "devolucion"
    descripcion: str
    email_cliente: str

# ─── Endpoints de autenticación ────────────────────────────────────────────────

@app.post("/auth/login", tags=["Autenticación"])
def login(req: LoginRequest):
    """Login para usuarios comunes y administradores."""
    logger.info(f"Intento de login para: {req.email}")
    usuarios = leer_json(USUARIOS_FILE)

    for u in usuarios:
        if u["email"] == req.email and u["password"] == req.password:
            logger.info(f"Login exitoso: {req.email} (rol: {u['rol']})")
            return {
                "mensaje": "Login exitoso",
                "usuario_id": u["id"],
                "nombre": u["nombre"],
                "rol": u["rol"]
            }

    logger.warning(f"Login fallido para: {req.email}")
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")


@app.post("/auth/registro", tags=["Autenticación"])
def registro(req: RegistroRequest):
    """Registro de un nuevo usuario común."""
    logger.info(f"Intento de registro: {req.email}")
    usuarios = leer_json(USUARIOS_FILE)

    # Verificar que el email no exista
    for u in usuarios:
        if u["email"] == req.email:
            logger.warning(f"Registro rechazado, email duplicado: {req.email}")
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    if not req.nombre.strip() or not req.email.strip() or not req.password.strip():
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")

    nuevo = {
        "id": "u" + str(uuid.uuid4())[:6],
        "nombre": req.nombre,
        "email": req.email,
        "password": req.password,
        "rol": "usuario",
        "activo": True
    }
    usuarios.append(nuevo)
    escribir_json(USUARIOS_FILE, usuarios)
    logger.info(f"Usuario registrado exitosamente: {req.email}")
    return {"mensaje": "Usuario registrado correctamente", "usuario_id": nuevo["id"]}

# ─── Endpoints de despachos ────────────────────────────────────────────────────

@app.get("/despachos", tags=["Despachos"])
def listar_despachos():
    """Lista todos los despachos registrados."""
    logger.info("Listando todos los despachos")
    return leer_json(DESPACHOS_FILE)


@app.get("/despachos/{despacho_id}", tags=["Despachos"])
def obtener_despacho(despacho_id: str):
    """Obtiene un despacho por su ID."""
    logger.info(f"Buscando despacho: {despacho_id}")
    despachos = leer_json(DESPACHOS_FILE)
    for d in despachos:
        if d["id"] == despacho_id:
            return d
    raise HTTPException(status_code=404, detail="Despacho no encontrado")


@app.post("/despachos", tags=["Despachos"])
def crear_despacho(req: DespachoRequest):
    """
    Crea un nuevo despacho.

    [BUG-02] INTENCIONAL: no se valida si direccion_destino está vacía o es solo espacios.
    Debería rechazarse con un 400, pero actualmente el despacho se crea igual.
    """
    logger.info(f"Creando despacho de '{req.remitente}' hacia '{req.destinatario}'")

    # Validación de origen (correcta)
    if not req.direccion_origen.strip():
        raise HTTPException(status_code=400, detail="La dirección de origen es obligatoria")

    # BUG-02: falta validar direccion_destino — se omite intencionalmente
    # Línea correcta sería:
    # if not req.direccion_destino.strip():
    #     raise HTTPException(status_code=400, detail="La dirección de destino es obligatoria")

    if not req.remitente.strip() or not req.destinatario.strip():
        raise HTTPException(status_code=400, detail="Remitente y destinatario son obligatorios")

    # Calcular tarifa automáticamente
    tarifa = _calcular_tarifa(req.peso_kg)

    nuevo = {
        "id": "d" + str(uuid.uuid4())[:6],
        "remitente": req.remitente,
        "destinatario": req.destinatario,
        "direccion_origen": req.direccion_origen,
        "direccion_destino": req.direccion_destino,
        "peso_kg": req.peso_kg,
        "estado": "pendiente",
        "fecha_creacion": datetime.now().isoformat(),
        "tarifa": tarifa,
        "notas": req.notas
    }
    despachos = leer_json(DESPACHOS_FILE)
    despachos.append(nuevo)
    escribir_json(DESPACHOS_FILE, despachos)
    logger.info(f"Despacho creado: {nuevo['id']} | Tarifa calculada: ${tarifa}")
    return {"mensaje": "Despacho creado", "despacho": nuevo}


@app.patch("/despachos/{despacho_id}/estado", tags=["Despachos"])
def actualizar_estado(despacho_id: str, req: ActualizarEstadoRequest):
    """Actualiza el estado de un despacho (pendiente, en_camino, entregado, cancelado)."""
    estados_validos = ["pendiente", "en_camino", "entregado", "cancelado"]
    if req.estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones: {estados_validos}")

    despachos = leer_json(DESPACHOS_FILE)
    for d in despachos:
        if d["id"] == despacho_id:
            estado_anterior = d["estado"]
            d["estado"] = req.estado
            escribir_json(DESPACHOS_FILE, despachos)
            logger.info(f"Despacho {despacho_id}: estado cambiado de '{estado_anterior}' a '{req.estado}'")
            return {"mensaje": "Estado actualizado", "despacho_id": despacho_id, "nuevo_estado": req.estado}

    raise HTTPException(status_code=404, detail="Despacho no encontrado")

# ─── Endpoint nuevo 1: getTarifa ───────────────────────────────────────────────

@app.get("/getTarifa", tags=["Servicios"])
def get_tarifa(peso_kg: float = Query(..., description="Peso del paquete en kilogramos")):
    """
    Calcula y devuelve la tarifa correspondiente según el peso del paquete.

    [BUG-01] INTENCIONAL: se acepta peso_kg <= 0 sin lanzar error.
    El sistema debería rechazar valores negativos o cero, pero actualmente
    los procesa y devuelve un precio_base de la primera franja (350.0).
    """
    logger.info(f"Consulta de tarifa para peso: {peso_kg} kg")

    # BUG-01: falta esta validación — omitida intencionalmente
    # if peso_kg <= 0:
    #     raise HTTPException(status_code=400, detail="El peso debe ser mayor a 0")

    tarifa = _calcular_tarifa(peso_kg)
    logger.info(f"Tarifa calculada: ${tarifa} para {peso_kg} kg")
    return {
        "peso_kg": peso_kg,
        "tarifa": tarifa,
        "moneda": "ARS"
    }

# ─── Endpoint nuevo 2: validarDireccion ───────────────────────────────────────

@app.get("/validarDireccion", tags=["Servicios"])
def validar_direccion(direccion: str = Query(..., description="Dirección a validar")):
    """
    Valida si una dirección tiene el formato mínimo esperado (calle + número + ciudad).
    Simula una validación básica de geolocalización sin consumir APIs externas.
    """
    logger.info(f"Validando dirección: '{direccion}'")

    if not direccion.strip():
        logger.warning("Dirección vacía recibida en validarDireccion")
        raise HTTPException(status_code=400, detail="La dirección no puede estar vacía")

    partes = direccion.strip().split(",")
    if len(partes) < 2:
        logger.warning(f"Dirección con formato inválido: '{direccion}'")
        return {
            "direccion": direccion,
            "valida": False,
            "mensaje": "Formato inválido. Se esperaba: 'Calle Número, Ciudad'"
        }

    calle_numero = partes[0].strip()
    tiene_numero = any(char.isdigit() for char in calle_numero)

    if not tiene_numero:
        logger.warning(f"Dirección sin número: '{direccion}'")
        return {
            "direccion": direccion,
            "valida": False,
            "mensaje": "La calle debe incluir un número"
        }

    logger.info(f"Dirección válida: '{direccion}'")
    return {
        "direccion": direccion,
        "valida": True,
        "mensaje": "Dirección con formato válido"
    }

# ─── Endpoint: quejas y devoluciones ──────────────────────────────────────────

@app.post("/quejas", tags=["Atención al cliente"])
def registrar_queja(req: QuejasRequest):
    """Registra una queja o solicitud de devolución asociada a un despacho."""
    logger.info(f"Nueva {req.tipo} para despacho: {req.despacho_id}")

    tipos_validos = ["queja", "devolucion"]
    if req.tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Opciones: {tipos_validos}")

    # Verificar que el despacho exista
    despachos = leer_json(DESPACHOS_FILE)
    ids_existentes = [d["id"] for d in despachos]
    if req.despacho_id not in ids_existentes:
        raise HTTPException(status_code=404, detail="El despacho indicado no existe")

    nueva_queja = {
        "id": "q" + str(uuid.uuid4())[:6],
        "despacho_id": req.despacho_id,
        "tipo": req.tipo,
        "descripcion": req.descripcion,
        "email_cliente": req.email_cliente,
        "fecha": datetime.now().isoformat(),
        "estado": "abierta"
    }
    quejas = leer_json(QUEJAS_FILE)
    quejas.append(nueva_queja)
    escribir_json(QUEJAS_FILE, quejas)
    logger.info(f"Queja registrada: {nueva_queja['id']}")
    return {"mensaje": "Queja registrada correctamente", "queja_id": nueva_queja["id"]}


@app.get("/quejas", tags=["Atención al cliente"])
def listar_quejas():
    """Lista todas las quejas y devoluciones registradas."""
    logger.info("Listando todas las quejas")
    return leer_json(QUEJAS_FILE)

# ─── Helper privado de cálculo de tarifa ──────────────────────────────────────

def _calcular_tarifa(peso_kg: float) -> float:
    """Calcula la tarifa según el peso usando la tabla de tarifas.json."""
    tarifas = leer_json(TARIFAS_FILE)
    for t in tarifas:
        if t["peso_min_kg"] <= peso_kg <= t["peso_max_kg"]:
            return t["precio_base"]
    # Fallback: si el peso supera todos los rangos, aplica el máximo
    return tarifas[-1]["precio_base"]
