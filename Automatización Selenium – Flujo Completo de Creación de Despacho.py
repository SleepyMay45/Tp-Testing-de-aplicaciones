from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_crear_despacho_completo():

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("http://localhost:8000")

        # Dirección
        direccion = wait.until(
            EC.presence_of_element_located(
                (By.ID, "direccion_destino")
            )
        )

        direccion.send_keys("Av. Corrientes 1234")

        # Peso
        peso = driver.find_element(By.ID, "peso_kg")
        peso.send_keys("5")

        # Calcular tarifa
        driver.find_element(
            By.ID,
            "btn-calcular"
        ).click()

        tarifa = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "tarifa")
            )
        )

        assert tarifa.text != ""

        # Confirmar despacho
        driver.find_element(
            By.ID,
            "btn-despachar"
        ).click()

        mensaje = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "mensaje_exito")
            )
        )

        assert "despacho creado" in mensaje.text.lower()

    finally:
        driver.quit()