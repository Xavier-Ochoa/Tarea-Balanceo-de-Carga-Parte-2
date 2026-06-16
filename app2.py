from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

DB_HOST    = os.environ.get("DB_HOST", "mysql_master")
NODO_NAME  = os.environ.get("NODO_NAME", "Nodo ?")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user="root",
        password="root",
        database="cine"
    )

@app.route("/")
def index():
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM peliculas ORDER BY id DESC")
        peliculas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("index.html", peliculas=peliculas, nodo=NODO_NAME, db=DB_HOST)
    except Error as e:
        return f"Error de conexión en {NODO_NAME}: {e}", 500

@app.route("/agregar", methods=["POST"])
def agregar():
    titulo   = request.form["titulo"]
    director = request.form["director"]
    anio     = request.form["anio"]
    genero   = request.form["genero"]
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO peliculas (titulo, director, anio, genero) VALUES (%s, %s, %s, %s)",
            (titulo, director, anio, genero)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
    except Error as e:
        return f"Error al insertar: {e}", 500
    return redirect("/")

@app.route("/api/peliculas")
def api_peliculas():
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM peliculas ORDER BY id DESC")
        peliculas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify({"nodo": NODO_NAME, "db": DB_HOST, "data": peliculas})
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/agregar", methods=["POST"])
def api_agregar():
    data     = request.get_json()
    titulo   = data.get("titulo")
    director = data.get("director")
    anio     = data.get("anio")
    genero   = data.get("genero")
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO peliculas (titulo, director, anio, genero) VALUES (%s, %s, %s, %s)",
            (titulo, director, int(anio), genero)
        )
        conexion.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return jsonify({"success": True, "id": new_id, "nodo": NODO_NAME, "db": DB_HOST})
    except Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
