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


# ─── Tests de getTarifa ────────────────────────────────────────────────────────

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
        """
        Peso negativo debería retornar 400, pero actualmente retorna 200.
        Este test FALLARÁ, evidenciando el BUG-01.
        """
        resp = client.get("/getTarifa?peso_kg=-5")
        # Comportamiento ESPERADO (correcto):
        assert resp.status_code == 400  # Fallará con el bug actual

    def test_tarifa_peso_cero(self):
        """
        Peso cero debería retornar 400, pero actualmente retorna 200.
        Este test FALLARÁ, evidenciando el BUG-01.
        """
        resp = client.get("/getTarifa?peso_kg=0")
        assert resp.status_code == 400  # Fallará con el bug actual


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


# ─── Tests de despachos ────────────────────────────────────────────────────────

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
        """
        Despacho con direccion_destino vacía debería retornar 400.
        Este test FALLARÁ, evidenciando el BUG-02.
        """
        resp = client.post("/despachos", json={
            "remitente": "Test",
            "destinatario": "Test",
            "direccion_origen": "Corrientes 100, Buenos Aires",
            "direccion_destino": "   ",  # Solo espacios
            "peso_kg": 2.0
        })
        assert resp.status_code == 400  # Fallará con el bug actual

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
        """Buscar un ID que no existe debe retornar 404."""
        resp = client.get("/despachos/id_falso_xyz")
        assert resp.status_code == 404
