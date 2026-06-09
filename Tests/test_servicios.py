"""
tests/test_servicios.py
Tests de ejemplo para orientar al equipo de testers.
Cubren los endpoints principales del sistema.

Ejecutar con: pytest tests/ -v
"""

import json
import os
import pytest
from fastapi.testclient import TestClient

# Ajuste de path para importar main desde la raíz del proyecto
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


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


# ─── Tests de getTarifa (BUG-01 corregido) ────────────────────────────────────

class TestGetTarifa:
    def test_tarifa_peso_bajo(self):
        """Peso menor a 1 kg debe devolver tarifa base de 350."""
        resp = client.get("/getTarifa?peso_kg=0.5")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 350.0

    def test_tarifa_peso_medio(self):
        """Peso entre 1 y 5 kg debe devolver tarifa de 700."""
        resp = client.get("/getTarifa?peso_kg=3.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 700.0

    def test_tarifa_peso_alto(self):
        """Peso mayor a 10 kg debe devolver tarifa de 2500."""
        resp = client.get("/getTarifa?peso_kg=15.0")
        assert resp.status_code == 200
        assert resp.json()["tarifa"] == 2500.0

    def test_tarifa_peso_negativo(self):
        """[BUG-01 corregido] Peso negativo debe retornar 400."""
        resp = client.get("/getTarifa?peso_kg=-5")
        assert resp.status_code == 400

    def test_tarifa_peso_cero(self):
        """[BUG-01 corregido] Peso cero debe retornar 400."""
        resp = client.get("/getTarifa?peso_kg=0")
        assert resp.status_code == 400


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
        """[BUG-02 corregido] Despacho con direccion_destino vacía debe retornar 400."""
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, Buenos Aires",
            "direccion_destino": "   ",  # Solo espacios
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
        """[BUG-03 corregido] Buscar un ID que no existe debe retornar 404."""
        resp = client.get("/despachos/id_falso_xyz")
        assert resp.status_code == 404


# ─── Tests de notificaciones (BUG-04 corregido) ───────────────────────────────

class TestNotificaciones:
    def test_notificacion_despacho_inexistente(self):
        """Notificar llegada de un ID que no existe debe retornar 404."""
        resp = client.post("/notificaciones/llegada/id_falso_xyz")
        assert resp.status_code == 404

    def test_notificacion_servicio_caido_no_crashea(self):
        """
        [BUG-04 corregido] Si el servicio externo de alertas falla, el servidor
        debe responder con un mensaje de error controlado sin cerrarse.
        """
        # El servicio externo (http://servicio-alertas.interno/notify) siempre
        # falla en entorno de tests porque no existe. Con el bug corregido,
        # el servidor captura la excepción y devuelve una respuesta controlada
        # en lugar de crashear.
        despachos = client.get("/despachos").json()
        assert len(despachos) > 0, "Se necesita al menos un despacho en despachos.json"

        despacho_id = despachos[0]["id"]
        resp = client.post(f"/notificaciones/llegada/{despacho_id}")

        # El servidor no debe caer: tiene que responder con algún código HTTP
        assert resp.status_code in (200, 503)
        data = resp.json()
        assert "mensaje" in data
        # El mensaje debe indicar que el servicio no está disponible
        assert "no disponible" in data["mensaje"].lower() or "no enviada" in data["mensaje"].lower()