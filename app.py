"""Formulario de alta para el inventario TIC del proyecto de IAW."""

import os

import mysql.connector
from flask import Flask, render_template, request


app = Flask(__name__)

TIPOS = ("Ordenador", "Monitor", "Impresora", "Periférico", "Otro")
ESTADOS = ("Disponible", "En uso", "En reparación", "Retirado")
LONGITUDES = {"tipo": 30, "marca": 60, "modelo": 80, "aula": 30, "estado": 30}


def formulario(error=None, valores=None):
    """Muestra el formulario y conserva sus valores si hay un error."""
    return render_template(
        "index.html",
        error=error,
        valores=valores or {},
        tipos=TIPOS,
        estados=ESTADOS,
    )


@app.route("/")
def inicio():
    return formulario()


@app.route("/equipos", methods=["POST"])
def registrar_equipo():
    datos = {
        campo: request.form.get(campo, "").strip()
        for campo in LONGITUDES
    }

    if not all(datos.values()):
        return formulario("Completa todos los campos antes de guardar.", datos), 400

    if datos["tipo"] not in TIPOS or datos["estado"] not in ESTADOS:
        return formulario("Selecciona un tipo y un estado válidos.", datos), 400

    if any(len(datos[campo]) > maximo for campo, maximo in LONGITUDES.items()):
        return formulario("Uno de los campos supera la longitud permitida.", datos), 400

    clave = os.environ.get("INVENTARIO_DB_PASSWORD")
    if not clave:
        app.logger.error("Falta configurar INVENTARIO_DB_PASSWORD")
        return formulario("La aplicación no está configurada para guardar equipos.", datos), 500

    conexion = None
    cursor = None

    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="inventario",
            password=clave,
            database="inventario",
        )
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO equipos (tipo, marca, modelo, aula, estado)
               VALUES (%s, %s, %s, %s, %s)""",
            (datos["tipo"], datos["marca"], datos["modelo"], datos["aula"], datos["estado"]),
        )
        conexion.commit()
        identificador = cursor.lastrowid
    except mysql.connector.Error:
        app.logger.exception("No se pudo guardar el equipo en MySQL")
        return formulario("No se ha podido guardar el equipo. Inténtalo de nuevo.", datos), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()

    return render_template(
        "confirmacion.html", equipo={"id": identificador, **datos}
    ), 201


if __name__ == "__main__":
    # Servidor de desarrollo para la práctica local. Apache recibe las visitas.
    app.run(host="127.0.0.1", port=5000, debug=False)
