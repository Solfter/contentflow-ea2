from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError, PyMongoError

from app.db import cliente
from app.logger import logger
from app.errores import ErrorAPI
from app import usuarios, publicaciones

app = Flask(__name__)
app.register_blueprint(usuarios.bp)
app.register_blueprint(publicaciones.bp)


@app.after_request
def registrar_peticion(respuesta):
    logger.info("%s %s -> %s", request.method, request.path, respuesta.status_code)
    return respuesta


@app.route("/health")
def health():
    try:
        cliente.admin.command("ping")
        return jsonify({"estado": "ok", "base_de_datos": "conectada"}), 200
    except Exception:
        logger.error("Health check: sin conexión con la base de datos")
        return jsonify({"estado": "error", "base_de_datos": "sin conexión"}), 503


@app.errorhandler(ErrorAPI)
def manejar_error_api(e):
    logger.warning("Validación fallida: %s %s", e.mensaje, e.detalles)
    return jsonify({"error": e.mensaje, "detalles": e.detalles}), e.codigo


@app.errorhandler(DuplicateKeyError)
def manejar_duplicado(e):
    logger.warning("Clave duplicada: %s", e)
    return jsonify({"error": "Ya existe un registro con ese identificador o correo"}), 409


@app.errorhandler(ServerSelectionTimeoutError)
def manejar_sin_conexion(e):
    logger.error("Sin conexión con MongoDB: %s", e)
    return jsonify({"error": "No hay conexión con la base de datos"}), 503


@app.errorhandler(PyMongoError)
def manejar_error_bd(e):
    logger.error("Error de base de datos: %s", e)
    return jsonify({"error": "Error en la base de datos"}), 500


@app.errorhandler(HTTPException)
def manejar_http(e):
    return jsonify({"error": e.description}), e.code


@app.errorhandler(Exception)
def manejar_inesperado(e):
    logger.exception("Error inesperado")
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)