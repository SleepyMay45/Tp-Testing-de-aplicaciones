
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
(Los links de arriba deberian de seguir funcionando)
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

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login de usuario o administrador |
| POST | `/auth/registro` | Registro de nuevo usuario común |
| GET | `/despachos` | Lista todos los despachos |
| GET | `/despachos/{id}` | Obtiene un despacho por ID |
| POST | `/despachos` | Crea un nuevo despacho |
| PATCH | `/despachos/{id}/estado` | Actualiza estado del despacho |
| GET | `/getTarifa?peso_kg=X` | ⭐ Calcula tarifa según peso (endpoint nuevo) |
| GET | `/validarDireccion?direccion=X` | ⭐ Valida formato de dirección (endpoint nuevo) |
| POST | `/quejas` | Registra queja o devolución |
| GET | `/quejas` | Lista todas las quejas |

---

## Usuarios precargados

| Email | Password | Rol |
|-------|----------|-----|
| admin@envios.com | admin123 | administrador |
| operador1@envios.com | oper123 | operador |
| operador2@envios.com | oper456 | operador |

---

## Bugs intencionales (para el equipo de testing)

| ID | Endpoint | Descripción |
|----|----------|-------------|
| BUG-01 | `GET /getTarifa` | Acepta `peso_kg` negativo o cero sin retornar error |
| BUG-02 | `POST /despachos` | Permite `direccion_destino` vacía o con solo espacios |

---

## Logs

Las operaciones relevantes quedan registradas en `app.log` con timestamp y nivel.  
También se imprimen en consola mientras el servidor está corriendo.
