from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_crear_despacho_completo():
    print("Levantando el navegador Chrome...")
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # 1. Navegar a la página
        driver.get("http://localhost:8000")
        print("Página cargada. Ingresando datos...")

        # 2. Dirección
        direccion = wait.until(
            EC.presence_of_element_located((By.ID, "direccion_destino"))
        )
        direccion.send_keys("Av. Corrientes 1234")

        # 3. Peso
        peso = driver.find_element(By.ID, "peso_kg")
        peso.send_keys("5")

        # 4. Calcular tarifa
        driver.find_element(By.ID, "btn-calcular").click()

        tarifa = wait.until(
            EC.visibility_of_element_located((By.ID, "tarifa"))
        )
        assert tarifa.text != "", "Error: La tarifa está vacía"
        print(f"Éxito: Tarifa calculada correctamente ({tarifa.text}).")

        # 5. Confirmar despacho
        driver.find_element(By.ID, "btn-despachar").click()

        mensaje = wait.until(
            EC.visibility_of_element_located((By.ID, "mensaje_exito"))
        )
        assert "despacho creado" in mensaje.text.lower(), "Error: No apareció el mensaje"
        print("Éxito: ¡El mensaje de confirmación apareció en pantalla!")

    except Exception as e:
        print(f"El test falló: {e}")
        
    finally:
        print("Cerrando el navegador...")
        driver.quit()

# ESTO ES LO QUE FALTABA PARA QUE EL SCRIPT SE EJECUTE SOLO
if __name__ == "__main__":
    print("=== INICIANDO AUTOMATIZACIÓN E2E CON SELENIUM ===")
    test_crear_despacho_completo()