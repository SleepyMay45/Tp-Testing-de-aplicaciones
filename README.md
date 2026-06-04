## Cosas que instalar para que corra el programa

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## Levantar el servidor

```bash
uvicorn main:app --reload
```

El servidor queda disponible en: `http://127.0.0.1:8000`  
Documentación automática (Swagger UI): `http://127.0.0.1:8000/docs`  
Documentación alternativa (ReDoc): `http://127.0.0.1:8000/redoc`
## (Los links de arriba deberian de seguir funcionando)
## Siempre usar el segundo link que es el que abre la página web
## Cada vez que cierran y abren el programa tienen que poner uvicorn main:app --reload en la terminal para que funcione la página

---

## Ejecutar tests

```bash
pytest tests/ -v
```

---

## Estructura del proyecto

```
proyecto/
├── main.py                  # Backend FastAPI con todos los endpoints
├── requirements.txt         # Dependencias del proyecto
├── app.log                  # Log de operaciones (se genera al correr)
├── data/
│   ├── usuarios.json        # Usuarios precargados (admin + operadores)
│   ├── despachos.json       # Despachos registrados
│   ├── tarifas.json         # Tabla de tarifas por peso
│   └── quejas.json          # Registro de quejas y devoluciones
└── tests/
    └── test_servicios.py    # Tests unitarios y de integración
```


## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login de usuario o administrador |
| POST | `/auth/registro` | Registro de nuevo usuario común |
| GET | `/despachos` | Lista todos los despachos |
| GET | `/despachos/{id}` | Obtiene un despacho por ID |
| POST | `/despachos` | Crea un nuevo despacho |
| PATCH | `/despachos/{id}/estado` | Actualiza estado del despacho |
| GET | `/getTarifa?peso_kg=X` |  Calcula tarifa según peso (endpoint nuevo) |
| GET | `/validarDireccion?direccion=X` |  Valida formato de dirección (endpoint nuevo) |
| POST | `/quejas` | Registra queja o devolución |
| GET | `/quejas` | Lista todas las quejas |


## Usuarios precargados

| Email | Password | Rol |
|-------|----------|-----|
| admin@envios.com | admin123 | administrador |
| operador1@envios.com | oper123 | operador |
| operador2@envios.com | oper456 | operador |

## Bugs intencionales (para el equipo de testing)

Estos bugs fueron dejados a propósito para ser detectados durante el Sprint 2. Cada uno tiene su caso de prueba asociado en el informe de QA.

| ID | Caso de Prueba | Endpoint | Descripción del defecto |
|----|---------------|----------|-------------------------|
| BUG-01 | CP-01 | `GET /getTarifa` | Acepta `peso_kg` negativo o cero y devuelve una tarifa en lugar de error 400 |
| BUG-02 | CP-02 | `POST /despachos` | Permite crear un despacho con `direccion_destino` vacía o con solo espacios |
| BUG-03 | CP-03 | `GET /despachos/{id}` | Si el ID no existe, el servidor entra en bucle infinito y no responde (falta el 404) |
| BUG-04 | CP-04 | `POST /notificaciones/llegada/{id}` | Si el servicio de alertas falla, la excepción no controlada cierra el servidor Uvicorn |


## Logs

Las operaciones relevantes quedan registradas en `app.log` con timestamp y nivel.  
También se imprimen en consola mientras el servidor está corriendo.

---

## Explicando lo que hace el código

Esta sección explica qué significa cada parte de la página web (`http://127.0.0.1:8000/docs`) para que cualquier integrante del equipo pueda entender qué está viendo y cómo usarla.

---

### ¿Qué es Swagger UI?

Es la página que se abre cuando entrás a `/docs`. La genera FastAPI automáticamente a partir del código. Muestra todos los endpoints del sistema organizados por categoría (Autenticación, Despachos, Servicios, Atención al cliente) y permite probarlos sin necesidad de ninguna herramienta externa.

---

### Categorías (Tags)

Los endpoints están agrupados en bloques con nombre. Cada bloque se puede expandir o contraer haciendo click.

- **Autenticación** → login y registro de usuarios
- **Despachos** → crear, listar y actualizar envíos
- **Servicios** → calcular tarifa y validar dirección
- **Atención al cliente** → registrar y listar quejas

---

### Cómo probar un endpoint

1. Hacé click sobre el endpoint que querés probar (por ejemplo `POST /auth/login`)
2. Hacé click en el botón **"Try it out"** que aparece arriba a la derecha del bloque
3. Editá los valores en el campo de texto que se habilita
4. Hacé click en **"Execute"**
5. Abajo aparece la respuesta del servidor

---

### Example Value / Schema

Cuando abrís un endpoint que recibe datos (los que dicen POST o PATCH), aparece una sección llamada **"Request body"** con dos pestañas: **Example Value** y **Schema**.

**Example Value** muestra un ejemplo de cómo tiene que verse el JSON que se manda. Por ejemplo en `POST /auth/login`:

```json
{
  "email": "operador1@envios.com",
  "password": "oper123"
}
```

Esto significa: el endpoint espera recibir un email y una contraseña. El texto que aparece ahí es un ejemplo precargado para facilitar la prueba — se puede editar libremente antes de ejecutar.

**Schema** muestra la estructura técnica del modelo: qué campos existen, de qué tipo son (string, number, etc.) y cuáles son obligatorios. Es más técnico y no hace falta tocarlo para probar.

---

### Media Type

Aparece justo arriba del Example Value y dice `application/json`. Significa que los datos se envían en formato JSON. No hace falta cambiarlo, siempre tiene que quedar en `application/json`.

---

### Responses

Es la sección que aparece debajo del botón Execute. Muestra qué puede responder el servidor según lo que pasó:

- **200** → todo salió bien, la operación fue exitosa
- **400** → los datos enviados tienen algún error (campo vacío, formato incorrecto, etc.)
- **401** → credenciales incorrectas (solo aparece en login)
- **404** → no se encontró lo que se buscaba (por ejemplo un despacho con un ID que no existe)
- **422** → el formato del JSON está mal, falta un campo obligatorio o el tipo de dato es incorrecto

Después de ejecutar, aparece también la respuesta real del servidor con el código HTTP obtenido, el tiempo que tardó y el cuerpo de la respuesta en JSON.

---

### Ejemplo completo: probar el login

1. Abrís `POST /auth/login`
2. Hacés click en "Try it out"
3. El campo ya tiene cargado:
```json
{
  "email": "operador1@envios.com",
  "password": "oper123"
}
```
4. Hacés click en "Execute"
5. Abajo en Responses aparece código **200** y el servidor devuelve:
```json
{
  "mensaje": "Login exitoso",
  "usuario_id": "u002",
  "nombre": "Operador Uno",
  "rol": "operador"
}
```
Si en cambio ponés una contraseña incorrecta, el servidor devuelve código **401** con el mensaje `"Credenciales incorrectas"`.

---

### Ejemplo completo: probar un bug

Para ver el **BUG-01** en acción:

1. Abrís `GET /getTarifa`
2. Hacés click en "Try it out"
3. En el campo `peso_kg` escribís `-5`
4. Hacés click en "Execute"
5. El servidor responde **200** y calcula una tarifa — cuando lo correcto sería responder **400** rechazando el valor negativo

Eso es evidencia de un defecto: el sistema aceptó un dato inválido sin reportar error.