import pytest
from unittest.mock import patch
from catalog_manager import CatalogManager

# --- ESCENARIO 1: TEST DE INTEGRACIÓN (Sin Mocks) ---
def test_get_products_integration():
    manager = CatalogManager()
    products = manager.get_products()
    assert isinstance(products, list)
    assert len(products) > 0

# --- ESCENARIO 2: TEST UNITARIO (Con Mocks) ---
@patch('catalog_manager.requests.get')
def test_get_products_happy_path(mock_get):
    # Definimos una respuesta falsa (Mock)
    mock_response = mock_get.return_value 
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "products": [
            {"id": 1, "name": "Remera A", "brand": "Polo"},
            {"id": 2, "name": "Remera B", "brand": "H&M"},
            {"id": 3, "name": "Remera C", "brand": "Polo"},
        ]
    }
    
    manager = CatalogManager()
    resultado = manager.get_products()
    
    assert len(resultado) == 3

@patch('catalog_manager.CatalogManager.get_products')
def test_filter_by_brand_logic(mock_get):
    # Definimos una respuesta falsa (Mock)
    mock_get.return_value.status_code = 200
    mock_get.return_value = [
        {"id": 1, "name": "Remera A", "brand": "Polo"},
        {"id": 2, "name": "Remera B", "brand": "H&M"},
        {"id": 3, "name": "Remera C", "brand": "Polo"},
    ]
    
    manager = CatalogManager()
    resultado = manager.filter_by_brand("Polo")
    
    # Validamos que la lógica de filtrado funcione
    assert len(resultado) == 2
    assert resultado[0]["name"] == "Remera A"
    assert resultado[1]["name"] == "Remera C"