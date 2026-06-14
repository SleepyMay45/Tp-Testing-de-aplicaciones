import pytest
from unittest.mock import patch
from catalog_manager import CatalogManager

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def navegador():
    # Inicialización del WebDriver
    driver = webdriver.Chrome()
    # Entregamos el driver a la prueba
    yield driver
    # Cierre automático al finalizar
    driver.quit()

def test_crear_despacho_completo(navegador):
    wait = WebDriverWait(navegador, 10)
    navegador.get("http://localhost:8000")

    # Ingreso de Dirección
    direccion = wait.until(
        EC.presence_of_element_located((By.ID, "direccion_destino"))
    )
    direccion.send_keys("Av. Corrientes 1234")

    # Ingreso de Peso
    peso = navegador.find_element(By.ID, "peso_kg")
    peso.send_keys("5")

    # Acción: Calcular tarifa
    navegador.find_element(By.ID, "btn-calcular").click()

    # Validación de cálculo
    tarifa = wait.until(
        EC.visibility_of_element_located((By.ID, "tarifa"))
    )
    assert tarifa.text != "", "La tarifa no se calculó correctamente en la UI"

    # Acción: Confirmar despacho
    navegador.find_element(By.ID, "btn-despachar").click()

    # Validación final del flujo
    mensaje = wait.until(
        EC.visibility_of_element_located((By.ID, "mensaje_exito"))
    )
    assert "despacho creado" in mensaje.text.lower(), "El mensaje de éxito no apareció"


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