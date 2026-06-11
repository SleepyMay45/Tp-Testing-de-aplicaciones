from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --------------------------------------------------
# BUG-01 / REQ-01
# Peso negativo debe devolver error 400
# --------------------------------------------------
def test_peso_negativo_rechazado():
    response = client.post(
        "/tarifa",
        json={"peso_kg": -5}
    )

    assert response.status_code == 400
    assert "peso" in response.json()["detail"].lower()


# --------------------------------------------------
# BUG-02 / REQ-02
# Dirección vacía no debe permitir despacho
# --------------------------------------------------
def test_direccion_vacia_rechazada():
    response = client.post(
        "/despachos",
        json={
            "direccion_destino": "",
            "peso_kg": 10
        }
    )

    assert response.status_code == 400
    assert "dirección" in response.json()["detail"].lower()


# --------------------------------------------------
# BUG-02 (variante)
# Dirección con espacios tampoco debe permitirse
# --------------------------------------------------
def test_direccion_con_espacios_rechazada():
    response = client.post(
        "/despachos",
        json={
            "direccion_destino": "     ",
            "peso_kg": 10
        }
    )

    assert response.status_code == 400
    assert "dirección" in response.json()["detail"].lower()


# --------------------------------------------------
# BUG-04 / REQ-04
# Falla del servicio de alertas no debe
# provocar caída de la aplicación
# --------------------------------------------------
def test_falla_notificaciones_no_crashea(monkeypatch):

    def mock_error(*args, **kwargs):
        raise Exception("Servicio caído")

    monkeypatch.setattr(
        "main.enviar_notificacion",
        mock_error
    )

    response = client.post(
        "/notificaciones",
        json={
            "cliente": "Juan",
            "mensaje": "Despacho entregado"
        }
    )

    assert response.status_code in [200, 503]

    if response.status_code == 503:
        assert "no disponible" in response.json()["detail"].lower()