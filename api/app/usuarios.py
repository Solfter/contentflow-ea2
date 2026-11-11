from datetime import datetime
from flask import Blueprint, jsonify, request
from app.db import db
from app.errores import ErrorAPI, validar

bp = Blueprint("usuarios", __name__)

@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    filtro = {}
    pais = request.args.get("pais")
    if pais:
        filtro["pais"] = pais
    docs = list(db.usuarios.find(filtro).limit(50))
    return jsonify(docs), 200


@bp.route("/usuarios/<id>", methods=["GET"])
def obtener_usuario(id):
    doc = db.usuarios.find_one({"_id": id})
    if doc is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(doc), 200


@bp.route("/usuarios", methods=["POST"])
def crear_usuario():
    datos = request.get_json()
    errores = validar(datos, {
        "_id": str, "nombre": str, "correo": str,
        "pais": str, "genero": str, "dispositivo": str,
    })
    if not errores:
        if "@" not in datos["correo"]:
            errores.append("El correo no tiene un formato válido")
        if datos["genero"] not in ("Masculino", "Femenino", "Otro"):
            errores.append("genero debe ser Masculino, Femenino u Otro")
        if datos["dispositivo"] not in ("Desktop", "Tablet", "Móvil"):
            errores.append("dispositivo debe ser Desktop, Tablet o Móvil")
    if errores:
        raise ErrorAPI("Datos inválidos", 400, errores)

    nuevo = {
        "_id": datos["_id"],
        "nombre": datos["nombre"],
        "correo": datos["correo"],
        "pais": datos["pais"],
        "genero": datos["genero"],
        "fecha_registro": datetime.now(),
        "dispositivo": datos["dispositivo"],
    }
    db.usuarios.insert_one(nuevo)
    return jsonify(nuevo), 201