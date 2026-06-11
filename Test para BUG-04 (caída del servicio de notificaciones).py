def test_falla_notificacion_no_crashea(monkeypatch):

    def mock_error(*args, **kwargs):
        raise Exception("Servicio caído")

    monkeypatch.setattr(
        "main.enviar_notificacion",
        mock_error
    )

    response = client.post(
        "/notificar",
        json={
            "mensaje": "Pedido entregado"
        }
    )

    assert response.status_code in [200, 503]