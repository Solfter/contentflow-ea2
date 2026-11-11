# ContentFlow: base de datos NoSQL en MongoDB Atlas y API REST

Evaluación Parcial N°2 (BDY0101, Bases de Datos No Relacionales, Forma A).

ContentFlow es una plataforma donde los usuarios crean publicaciones, reaccionan, comentan y participan en campañas. Este proyecto implementa su base de datos en **MongoDB Atlas (cluster M0)**, consultas y operaciones CRUD sobre los datos, y una **API REST en Python (Flask + pymongo)** que lee y escribe en la base con validaciones, control de errores y logs.

## Estructura del repositorio

```
contentflow/
├── api/                      API REST (Flask + pymongo)
│   ├── app/
│   │   ├── main.py           Aplicación, /health, manejadores de error y log de peticiones
│   │   ├── db.py             Conexión a Atlas (lee las variables de entorno)
│   │   ├── usuarios.py       Endpoints de usuarios
│   │   ├── publicaciones.py  Endpoints de publicaciones
│   │   ├── errores.py        Error propio (ErrorAPI) y validador de campos
│   │   └── logger.py         Configuración de logs (consola y archivo)
│   └── requirements.txt      Dependencias de Python
├── data/                     JSON del caso (una colección por archivo)
├── scripts/                  Scripts de MongoDB (extensión de VS Code), numerados en orden de ejecución
├── postman/                  Colección de Postman exportada
├── evidencias/               Capturas de configuración, consultas, CRUD y API
├── .env.example              Plantilla de variables de entorno (sin credenciales)
└── README.md
```

## Requisitos

- Cluster gratuito **M0** en MongoDB Atlas, con la base `ev-2-bd-nosql`.
- Un usuario de base de datos con rol **readWrite** sobre `ev-2-bd-nosql`.
- Acceso de red restringido en Atlas (Network Access): solo la IP pública del equipo de desarrollo (una única dirección `/32`), sin abrir el cluster a todo Internet. Quien clone este repositorio debe agregar su propia IP en Network Access para poder conectarse.
- Python 3.10 o superior.
- VS Code con la extensión **MongoDB for VS Code** (para ejecutar los scripts `.mongodb`), y opcionalmente MongoDB Compass.
- Postman (o un cliente HTTP equivalente) para probar la API.

## 1. Configuración de variables de entorno

El string de conexión **nunca va en el código**. Se lee desde un archivo `.env` que no se sube al repositorio.

1. Copia `.env.example` como `.env` **en la carpeta `contentflow/`** (al mismo nivel que este README).
2. Completa los valores:

```
MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=<cluster>
MONGODB_DB=ev-2-bd-nosql
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

Copia el string desde Atlas: **Connect, Drivers**. Si la contraseña tiene caracteres especiales (`@`, `:`, `/`, `#`, `?`), codifícalos en la URI (por ejemplo `@` pasa a `%40`).

## 2. Carga de datos

Importa cada archivo de `data/` en su colección (base `ev-2-bd-nosql`) con **MongoDB Compass** (Add Data, Import JSON) o con `mongoimport --jsonArray`:

| Archivo | Colección |
|---|---|
| `usuarios.json` | `usuarios` |
| `publicaciones.json` | `publicaciones` |
| `reacciones.json` | `reacciones` |
| `comentarios.json` | `comentarios` |
| `campanas.json` | `campanas` (sin ñ) |

Los `_id` son texto (`user_1`, `pub_1`, ...) y se mantienen así. Cada colección debe quedar con 500 documentos.

## 3. Scripts de MongoDB

Se ejecutan abriendo el archivo en VS Code, conectado al cluster, y usando **Run** (Playground). Van en este orden:

| Script | Propósito | ¿Re-ejecutable? |
|---|---|---|
| `1.verificar-conexion.mongodb` | Ping, listado de colecciones y escritura/lectura/borrado de un documento de prueba | Sí |
| `2.verificar-insercion.mongodb` | Cantidad de documentos por colección | Sí |
| `3.verificar-fechas.mongodb` | Cuenta campos de fecha como texto y como Date | Sí |
| `4.conversion-fechas.mongodb` | Convierte las fechas de texto a Date (`$toDate`) | Sí (solo toca las que siguen como texto) |
| `5.inconsistencias.mongodb` | Detecta referencias inválidas entre colecciones | Sí |
| `6.duplicados.mongodb` | Detecta reacciones duplicadas y fechas imposibles | Sí |
| `7.correcciones.mongodb` | Elimina la reacción duplicada respaldándola en `reacciones_respaldo` | **No: ejecutar una sola vez** |
| `8.etiquetado-fechas.mongodb` | Etiqueta con `inconsistencia` los documentos con fechas imposibles | Sí |
| `9.consultas.mongodb` | Consultas de lectura: filtros, proyecciones, ordenamientos y agregaciones | Sí |
| `10.explicacion-indices.mongodb` | `explain("executionStats")` antes y después de crear índices | **Una sola vez** (si se repite, el "antes" ya usa índice) |
| `11.crud.mongodb` | Ciclo CRUD completo con evidencias de estado antes y después | Sí (borra lo que crea) |
| `12.indices-concern.mongodb` | Índices adicionales y pruebas de write/read concern `majority` | Sí |

### Inconsistencias detectadas en los datos

| Hallazgo | Cantidad | Tratamiento |
|---|---|---|
| Referencias inválidas entre colecciones | 0 | Ninguno necesario |
| Reacción duplicada (mismo usuario y publicación) | 1 | Se eliminó la más antigua (`react_140`) y se respaldó en `reacciones_respaldo` |
| Reacciones con fecha anterior a su publicación | 244 | Campo `inconsistencia` (no se borran) |
| Comentarios con fecha anterior a su publicación | 251 | Campo `inconsistencia` (no se borran) |
| Publicaciones anteriores al registro de su autor | 48 | Campo `inconsistencia` (no se borran) |

Criterio: se elimina únicamente lo repetido; los datos cuyo valor correcto se desconoce se etiquetan para conservar trazabilidad y poder excluirlos en las consultas.

## 4. API REST

### Instalación y ejecución

Desde la carpeta `api/`, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

El servidor queda en `http://127.0.0.1:5000`. Comprueba la conexión con Atlas en `http://127.0.0.1:5000/health`.

Si PowerShell bloquea la activación del entorno virtual, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### Endpoints

| Método | Ruta | Descripción | Códigos |
|---|---|---|---|
| GET | `/health` | Prueba de conectividad con Atlas | 200, 503 |
| GET | `/usuarios` | Lista usuarios (máx. 50). Filtro opcional `?pais=` | 200 |
| GET | `/usuarios/<id>` | Obtiene un usuario | 200, 404 |
| POST | `/usuarios` | Crea un usuario | 201, 400, 409 |
| GET | `/publicaciones` | Lista publicaciones (máx. 50, más recientes primero). Filtros `?categoria=` y `?usuario_id=` | 200 |
| POST | `/publicaciones` | Crea una publicación | 201, 400, 409, 422 |
| PUT | `/publicaciones/<id>` | Edita `contenido`, `categoria`, `hashtags` o `tipo` | 200, 400, 404 |
| DELETE | `/publicaciones/<id>` | Elimina una publicación | 200, 404 |

### Ejemplo de creación de usuario

`POST /usuarios` con `Content-Type: application/json`:

```json
{
  "_id": "user_api_1",
  "nombre": "Usuario API",
  "correo": "api1@contentflow.com",
  "pais": "Chile",
  "genero": "Otro",
  "dispositivo": "Móvil"
}
```

La fecha de registro la asigna el servidor.

### Validaciones y control de errores

- **Campos obligatorios y tipos** en los `POST`; `genero` (Masculino, Femenino, Otro), `dispositivo` (Desktop, Tablet, Móvil), `tipo` (Video, Texto, Imagen) y `categoria` (Deportes, Cultura, Entretenimiento, Tecnología, Educación) con valores permitidos.
- **Referencia existente:** una publicación solo se crea si su `usuario_id` existe (422 si no).
- **Respuestas de error en JSON**, nunca páginas HTML ni datos internos:

| Código | Situación |
|---|---|
| 400 | Datos faltantes o inválidos, JSON mal formado |
| 404 | Recurso o ruta inexistente |
| 409 | Clave duplicada (`_id` o correo repetido) |
| 422 | Referencia a un usuario que no existe |
| 503 | Sin conexión con la base de datos |
| 500 | Error inesperado o de base de datos |

### Logs

Cada petición queda registrada (método, ruta y código de respuesta), junto con las validaciones fallidas, claves duplicadas y errores de conexión. Se escribe en consola y en el archivo definido por `LOG_FILE` (por defecto `logs/api.log`, excluido del repositorio).

### Pruebas con Postman

Importa `postman/ev-2.postman_collection.json` en Postman. Incluye el ciclo de lectura y escritura sobre usuarios y publicaciones y los casos de validación. Con la API en ejecución, los cambios hechos desde Postman pueden verificarse en Atlas (Data Explorer) o en Compass.

## Seguridad

- `.env` está en `.gitignore`; el repositorio solo contiene `.env.example` sin credenciales.
- La API usa un usuario de base de datos con rol **readWrite** limitado a la base `ev-2-bd-nosql`, no un usuario administrador.
- Consistencia: las escrituras de prueba usan write concern `majority` y las lecturas, read concern `majority` (valor por defecto de Atlas para escrituras).

## Límites del tier M0 (resumen)

Almacenamiento de 512 MB, 500 conexiones simultáneas y rendimiento compartido (el tier limita las operaciones por segundo). No admite sharding, por lo que la optimización se basa en **índices**. El volumen de este proyecto (5 colecciones de 500 documentos) queda muy por debajo de esos límites.
