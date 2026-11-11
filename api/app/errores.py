class ErrorAPI(Exception):
    def __init__(self, mensaje, codigo=400, detalles=None):
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalles = detalles


def validar(datos, esquema):
    if not isinstance(datos, dict):
        return ["El cuerpo debe ser un objeto JSON"]
    errores = []
    for campo, tipo in esquema.items():
        if campo not in datos or datos[campo] in (None, ""):
            errores.append(f"Falta el campo obligatorio: {campo}")
        elif not isinstance(datos[campo], tipo):
            errores.append(f"El campo {campo} debe ser de tipo {tipo.__name__}")
    return errores