"""
tests/test_servicios.py
Tests de ejemplo para orientar al equipo de testers.
Cubren los endpoints principales del sistema.

Ejecutar con: pytest Tests/ -v

SPRINT 3 — Correcciones en tests:
  [FIX-04] Fixtures con backup/restore para que los tests no contaminen
            los archivos JSON reales entre ejecuciones.
  [FIX-05] Agregados tests de peso <= 0 en crear_despacho (cobertura faltante).
  [FIX-06] Agregados tests de valores límite exactos de tarifa (1.0, 5.0, 10.0 kg).
  [FIX-08] Agregados tests de formato de email en registro y quejas.
  [FIX-09] Agregado test que verifica que campos vacíos se validan antes
            que email duplicado.
  [FIX-10] Agregados tests de descripción vacía y email vacío en quejas.
"""

import json
import os
import shutil
import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app, USUARIOS_FILE, DESPACHOS_FILE, QUEJAS_FILE

client = TestClient(app)


# ─── Fixtures: backup/restore de archivos JSON ────────────────────────────────
#
# [FIX-04] Sin estos fixtures, cada test que escribe en los JSON (registro,
# crear_despacho, quejas) modifica el archivo real. En la segunda ejecución
# test_registro_exitoso falla porque el email ya existe. La solución es
# guardar una copia antes del test y restaurarla al finalizar.

@pytest.fixture(autouse=True)
def restaurar_json():
    """
    Antes de cada test copia los archivos JSON a .bak.
    Al terminar (pase o falle) los restaura desde .bak.
    """
    archivos = [USUARIOS_FILE, DESPACHOS_FILE, QUEJAS_FILE]
    backups = {}
    for path in archivos:
        bak = path + ".bak"
        shutil.copy(path, bak)
        backups[path] = bak

    yield  # el test corre aquí

    for path, bak in backups.items():
        shutil.copy(bak, path)
        os.remove(bak)


# ─── Tests de autenticación ────────────────────────────────────────────────────

class TestLogin:
    def test_login_exitoso_operador(self):
        """Login con credenciales válidas de operador debe retornar 200."""
        resp = client.post("/auth/login", json={
            "email": "operador1@envios.com",
            "password": "oper123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "operador"
        assert "usuario_id" in data

    def test_login_exitoso_admin(self):
        """Login con credenciales de administrador debe retornar 200 y rol admin."""
        resp = client.post("/auth/login", json={
            "email": "admin@envios.com",
            "password": "admin123"
        })
        assert resp.status_code == 200
        assert resp.json()["rol"] == "administrador"

    def test_login_password_incorrecta(self):
        """Login con password incorrecta debe retornar 401."""
        resp = client.post("/auth/login", json={
            "email": "operador1@envios.com",
            "password": "wrongpassword"
        })
        assert resp.status_code == 401

    def test_login_email_inexistente(self):
        """Login con email que no existe debe retornar 401."""
        resp = client.post("/auth/login", json={
            "email": "noexiste@envios.com",
            "password": "cualquiera"
        })
        assert resp.status_code == 401


class TestRegistro:
    def test_registro_exitoso(self):
        """Registro con datos válidos debe retornar 200."""
        resp = client.post("/auth/registro", json={
            "nombre": "Usuario Test",
            "email": "test_nuevo@envios.com",
            "password": "pass123"
        })
        assert resp.status_code == 200
        assert "usuario_id" in resp.json()

    def test_registro_email_duplicado(self):
        """Registro con email ya existente debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "Duplicado",
            "email": "admin@envios.com",
            "password": "algo"
        })
        assert resp.status_code == 400

    def test_registro_nombre_vacio(self):
        """Registro con nombre vacío debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "   ",
            "email": "nuevo@envios.com",
            "password": "pass123"
        })
        assert resp.status_code == 400

    def test_registro_email_vacio(self):
        """Registro con email vacío debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "Alguien",
            "email": "   ",
            "password": "pass123"
        })
        assert resp.status_code == 400

    def test_registro_password_vacia(self):
        """Registro con password vacía debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "Alguien",
            "email": "nuevo@envios.com",
            "password": "   "
        })
        assert resp.status_code == 400

    # [FIX-08] Validación de formato de email
    def test_registro_email_sin_arroba(self):
        """[FIX-08] Email sin @ debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "Test",
            "email": "noesunmail.com",
            "password": "pass123"
        })
        assert resp.status_code == 400

    def test_registro_email_sin_dominio(self):
        """[FIX-08] Email sin dominio válido debe retornar 400."""
        resp = client.post("/auth/registro", json={
            "nombre": "Test",
            "email": "usuario@",
            "password": "pass123"
        })
        assert resp.status_code == 400

    # [FIX-09] Validación de orden: campos vacíos se detectan antes que duplicado
    def test_registro_campos_vacios_tienen_prioridad_sobre_duplicado(self):
        """
        [FIX-09] Si el email es duplicado Y el nombre está vacío,
        el error debe ser 'campos obligatorios', no 'email duplicado'.
        Antes el orden estaba invertido.
        """
        resp = client.post("/auth/registro", json={
            "nombre": "   ",
            "email": "admin@envios.com",  # email duplicado
            "password": "pass123"
        })
        assert resp.status_code == 400
        assert "obligatorio" in resp.json()["detail"].lower()


# ─── Tests de getTarifa (BUG-01 corregido) ────────────────────────────────────

class TestGetTarifa:
    def test_tarifa_peso_bajo(self):
        """Peso de 0.5 kg (rango 0-1) debe devolver tarifa de 350."""
        resp = client.get("/getTarifa?peso_kg=0.5")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 350.0

    def test_tarifa_peso_medio(self):
        """Peso de 3.0 kg (rango 1-5) debe devolver tarifa de 700."""
        resp = client.get("/getTarifa?peso_kg=3.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 700.0

    def test_tarifa_peso_alto(self):
        """Peso de 15.0 kg (rango >10) debe devolver tarifa de 2500."""
        resp = client.get("/getTarifa?peso_kg=15.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 2500.0

    def test_tarifa_peso_negativo(self):
        """[BUG-01] Peso negativo debe retornar 400."""
        resp = client.get("/getTarifa?peso_kg=-5")
        assert resp.status_code == 400

    def test_tarifa_peso_cero(self):
        """[BUG-01] Peso cero debe retornar 400."""
        resp = client.get("/getTarifa?peso_kg=0")
        assert resp.status_code == 400

    # [FIX-06] Valores límite exactos — antes devolvían la tarifa del rango anterior
    def test_tarifa_limite_exacto_1kg(self):
        """[FIX-06] Peso exacto de 1.0 kg debe caer en rango 1-5 (tarifa 700), no en 0-1 (350)."""
        resp = client.get("/getTarifa?peso_kg=1.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 700.0

    def test_tarifa_limite_exacto_5kg(self):
        """[FIX-06] Peso exacto de 5.0 kg debe caer en rango 5-10 (tarifa 1400), no en 1-5 (700)."""
        resp = client.get("/getTarifa?peso_kg=5.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 1400.0

    def test_tarifa_limite_exacto_10kg(self):
        """[FIX-06] Peso exacto de 10.0 kg debe caer en rango >10 (tarifa 2500), no en 5-10 (1400)."""
        resp = client.get("/getTarifa?peso_kg=10.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 2500.0


# ─── Tests de validarDireccion ─────────────────────────────────────────────────

class TestValidarDireccion:
    def test_direccion_valida(self):
        """Dirección con calle, número y ciudad debe ser válida."""
        resp = client.get("/validarDireccion?direccion=Av. Corrientes 1234, Buenos Aires")
        assert resp.status_code == 200
        assert resp.json()["valida"] is True

    def test_direccion_sin_numero(self):
        """Dirección sin número debe ser inválida."""
        resp = client.get("/validarDireccion?direccion=Corrientes, Buenos Aires")
        assert resp.status_code == 200
        assert resp.json()["valida"] is False

    def test_direccion_vacia(self):
        """Dirección vacía debe retornar 400."""
        resp = client.get("/validarDireccion?direccion= ")
        assert resp.status_code == 400

    def test_direccion_sin_coma(self):
        """Dirección sin coma separadora debe ser inválida."""
        resp = client.get("/validarDireccion?direccion=Belgrano 789")
        assert resp.status_code == 200
        assert resp.json()["valida"] is False


# ─── Tests de despachos (BUG-02 y BUG-03 corregidos) ─────────────────────────

class TestDespachos:
    def test_listar_despachos(self):
        """Listar despachos debe retornar una lista."""
        resp = client.get("/despachos")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_crear_despacho_valido(self):
        """Crear despacho con todos los campos válidos debe retornar 200."""
        resp = client.post("/despachos", json={
            "remitente": "Test Remitente",
            "destinatario": "Test Destinatario",
            "direccion_origen": "Corrientes 100, Buenos Aires",
            "direccion_destino": "San Martin 200, Cordoba",
            "peso_kg": 3.0,
            "notas": "Prueba"
        })
        assert resp.status_code == 200
        assert "despacho" in resp.json()

    def test_crear_despacho_destino_vacio(self):
        """[BUG-02] Despacho con direccion_destino vacía debe retornar 400."""
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, Buenos Aires",
            "direccion_destino": "   ",
            "peso_kg": 2.0
        })
        assert resp.status_code == 400

    def test_crear_despacho_sin_remitente(self):
        """Despacho sin remitente debe retornar 400."""
        resp = client.post("/despachos", json={
            "remitente": "",
            "destinatario": "Alguien",
            "direccion_origen": "Corrientes 100, CABA",
            "direccion_destino": "Mitre 50, Rosario",
            "peso_kg": 1.0
        })
        assert resp.status_code == 400

    def test_obtener_despacho_inexistente(self):
        """[BUG-03] Buscar un ID que no existe debe retornar 404."""
        resp = client.get("/despachos/id_falso_xyz")
        assert resp.status_code == 404

    # [FIX-05] Cobertura faltante: peso inválido en crear_despacho
    def test_crear_despacho_peso_negativo(self):
        """[FIX-05] Crear despacho con peso negativo debe retornar 400."""
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, CABA",
            "direccion_destino": "Mitre 50, Rosario",
            "peso_kg": -3.0
        })
        assert resp.status_code == 400

    def test_crear_despacho_peso_cero(self):
        """[FIX-05] Crear despacho con peso cero debe retornar 400."""
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, CABA",
            "direccion_destino": "Mitre 50, Rosario",
            "peso_kg": 0.0
        })
        assert resp.status_code == 400

    def test_tarifa_calculada_correctamente_al_crear(self):
        """La tarifa en el despacho creado debe coincidir con la tabla de tarifas."""
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, CABA",
            "direccion_destino": "Mitre 50, Rosario",
            "peso_kg": 3.0  # rango 1-5 kg → 700 ARS
        })
        assert resp.status_code == 200
        assert resp.json()["despacho"]["tarifa"] == 700.0


# ─── Tests de notificaciones (BUG-04 corregido) ───────────────────────────────

class TestNotificaciones:
    def test_notificacion_despacho_inexistente(self):
        """Notificar llegada de un ID que no existe debe retornar 404."""
        resp = client.post("/notificaciones/llegada/id_falso_xyz")
        assert resp.status_code == 404

    def test_notificacion_servicio_caido_no_crashea(self):
        """
        [BUG-04] Si el servicio externo de alertas falla, el servidor
        debe responder con un mensaje de error controlado sin cerrarse.
        """
        despachos = client.get("/despachos").json()
        assert len(despachos) > 0, "Se necesita al menos un despacho en despachos.json"

        despacho_id = despachos[0]["id"]
        resp = client.post(f"/notificaciones/llegada/{despacho_id}")

        assert resp.status_code in (200, 503)
        data = resp.json()
        assert "mensaje" in data
        assert "no disponible" in data["mensaje"].lower() or "no enviada" in data["mensaje"].lower()


# ─── Tests de quejas ───────────────────────────────────────────────────────────

class TestQuejas:
    def test_registrar_queja_valida(self):
        """Queja con todos los campos válidos debe retornar 200."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "queja",
            "descripcion": "El paquete llegó dañado",
            "email_cliente": "cliente@test.com"
        })
        assert resp.status_code == 200
        assert "queja_id" in resp.json()

    def test_registrar_devolucion_valida(self):
        """Devolución con todos los campos válidos debe retornar 200."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "devolucion",
            "descripcion": "No corresponde al pedido",
            "email_cliente": "cliente@test.com"
        })
        assert resp.status_code == 200

    def test_queja_tipo_invalido(self):
        """Tipo distinto de 'queja' o 'devolucion' debe retornar 400."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "reclamo",
            "descripcion": "Algo",
            "email_cliente": "cliente@test.com"
        })
        assert resp.status_code == 400

    def test_queja_despacho_inexistente(self):
        """Queja sobre un despacho que no existe debe retornar 404."""
        resp = client.post("/quejas", json={
            "despacho_id": "id_falso",
            "tipo": "queja",
            "descripcion": "Algo",
            "email_cliente": "cliente@test.com"
        })
        assert resp.status_code == 404

    # [FIX-10] Validaciones de campos vacíos en quejas
    def test_queja_descripcion_vacia(self):
        """[FIX-10] Queja con descripción vacía debe retornar 400."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "queja",
            "descripcion": "   ",
            "email_cliente": "cliente@test.com"
        })
        assert resp.status_code == 400

    def test_queja_email_vacio(self):
        """[FIX-10] Queja con email vacío debe retornar 400."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "queja",
            "descripcion": "El paquete llegó dañado",
            "email_cliente": "   "
        })
        assert resp.status_code == 400

    # [FIX-08] Validación de formato de email en quejas
    def test_queja_email_formato_invalido(self):
        """[FIX-08] Queja con email sin formato válido debe retornar 400."""
        resp = client.post("/quejas", json={
            "despacho_id": "d001",
            "tipo": "queja",
            "descripcion": "El paquete llegó dañado",
            "email_cliente": "noesunmail"
        })
        assert resp.status_code == 400

    def test_listar_quejas(self):
        """Listar quejas debe retornar una lista."""
        resp = client.get("/quejas")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
