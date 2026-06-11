## Pasos para ejecutar

1- Instalar python

2- Ejecutar `python -m venv .venv` o `python3 -m venv .venv`

3- Ejecutar `source .venv/bin/activate` o `venv\Scripts\activate.bat`

4- Instalar las dependencias `pip install requests pytest`

5- Ejecutar con `pytest`

### Coverage

`pip install pytest-cov`

y luego ejecutar: 
`pytest --cov=catalog_manager`


## Ejercicios

### 1 - Testeamos la api - a modo de script

### Ejercicio 1: Verificación de Marcas (GET)

Endpoint: https://automationexercise.com/api/brandsList

Crear un test que verifique que la respuesta sea 200 y que al menos una de las marcas de la lista se llame "Polo" o "H&M".

### Ejercicio 2: Búsqueda de Producto (POST)

Endpoint: https://automationexercise.com/api/searchProduct

1. Enviar un parámetro llamado search_product con el valor "tshirt".
2. Validar que el código de respuesta sea 200.
3. Validar que en la lista de resultados aparezcan productos que contengan la palabra "Shirt" en su nombre.

### Ejercicio 3: Intento de Creación Fallido (Método no permitido)

Endpoint: https://automationexercise.com/api/productsList

Intentar hacer un requests.post() a esa URL (que solo acepta GET).

Validación: El API de esta web suele devolver un mensaje específico en el JSON: {"responseCode": 405, "message": "This request method is not supported."}. Validar que ese mensaje este presente.

### Ejercicio 4: Verificación de Cuenta de Usuario (POST)

Endpoint: https://automationexercise.com/api/verifyLogin

1. Enviar un email y password inexistentes.
2. Validar que el responseCode dentro del JSON sea 404.
3. Validar que el mensaje sea "User not found!".

---

### 2 - Testeamos el servicio con test unitarios

### Ejercicio 5: Test de filtrado con Mock

Mockear get_products para que devuelva 3 productos (2 "Adidas" y 1 "Nike").

Validar: Que filter_by_brand("Adidas") devuelva exactamente 2 elementos.

### Ejercicio 6: Test de Error de Red

Mockear la respuesta para que el status_code sea 500.

Validar: Que get_products() devuelva una lista vacía [] y no rompa la aplicación.

### Ejercicio 7: Coverage
Una vez terminados los tests, ejecuta el siguiente comando en la terminal:

`pytest --cov=catalog_manager --cov-report=term-missing`

Observa la columna "Missing". Esas son las líneas de código de catalog_manager.py que tus tests no están tocando.
Crea los tests necesarios para que la cobertura llegue al 100%.