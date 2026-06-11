import requests

BASE_URL = "https://automationexercise.com/api"

"""Prueba que el endpoint de productos devuelva una lista válida."""
def test_get_products_list():
    # 1. Definir el endpoint
    url = BASE_URL + "/productsList"
    
    # 2. Ejecutar la acción
    response = requests.get(url)
    data = response.json()
    
    # 3. Validaciones (Assertions)
    assert response.status_code == 200
    assert "products" in data
    assert len(data["products"]) > 0
    
    # Validación de lógica: El primer producto debe tener nombre y precio
    primer_producto = data["products"][0]
    assert "name" in primer_producto
    assert "price" in primer_producto
