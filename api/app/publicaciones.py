from datetime import datetime
from flask import Blueprint, jsonify, request
from app.db import db
from app.errores import ErrorAPI, validar

bp = Blueprint("publicaciones", __name__)


@bp.route("/publicaciones", methods=["GET"])
def listar_publicaciones():
    filtro = {}
    categoria = request.args.get("categoria")
    usuario_id = request.args.get("usuario_id")
    if categoria:
        filtro["categoria"] = categoria
    if usuario_id:
        filtro["usuario_id"] = usuario_id
    docs = list(db.publicaciones.find(filtro).sort("fecha_publicacion", -1).limit(50))
    return jsonify(docs), 200


@bp.route("/publicaciones", methods=["POST"])
def crear_publicacion():
    datos = request.get_json()
    errores = validar(datos, {
        "_id": str, "usuario_id": str, "contenido": str,
        "categoria": str, "hashtags": list, "tipo": str,
    })
    if not errores:
        if datos["tipo"] not in ("Video", "Texto", "Imagen"):
            errores.append("tipo debe ser Video, Texto o Imagen")
        if datos["categoria"] not in ("Deportes", "Cultura", "Entretenimiento", "Tecnología", "Educación"):
            errores.append("categoria no es válida")
    if errores:
        raise ErrorAPI("Datos inválidos", 400, errores)

    if db.usuarios.count_documents({"_id": datos["usuario_id"]}, limit=1) == 0:
        raise ErrorAPI("Referencia inválida", 422, [f"El usuario {datos['usuario_id']} no existe"])

    nueva = {
        "_id": datos["_id"],
        "usuario_id": datos["usuario_id"],
        "contenido": datos["contenido"],
        "fecha_publicacion": datetime.now(),
        "categoria": datos["categoria"],
        "hashtags": datos["hashtags"],
        "tipo": datos["tipo"],
    }
    db.publicaciones.insert_one(nueva)
    return jsonify(nueva), 201


@bp.route("/publicaciones/<id>", methods=["PUT"])
def editar_publicacion(id):
    datos = request.get_json()
    if not isinstance(datos, dict):
        raise ErrorAPI("El cuerpo debe ser un objeto JSON", 400)
    cambios = {}
    for campo in ("contenido", "categoria", "hashtags", "tipo"):
        if campo in datos:
            cambios[campo] = datos[campo]
    if not cambios:
        raise ErrorAPI("No se envió ningún campo editable", 400,
                        ["Campos permitidos: contenido, categoria, hashtags, tipo"])
    resultado = db.publicaciones.update_one({"_id": id}, {"$set": cambios})
    if resultado.matched_count == 0:
        return jsonify({"error": "Publicación no encontrada"}), 404
    return jsonify(db.publicaciones.find_one({"_id": id})), 200


@bp.route("/publicaciones/<id>", methods=["DELETE"])
def eliminar_publicacion(id):
    resultado = db.publicaciones.delete_one({"_id": id})
    if resultado.deleted_count == 0:
        return jsonify({"error": "Publicación no encontrada"}), 404
    return jsonify({"mensaje": "Publicación eliminada", "_id": id}), 200