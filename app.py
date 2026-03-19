from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

ARCHIVO = "arribos_pasaporte_dni.xlsx"

# Cargar Excel una sola vez
df = pd.read_excel(ARCHIVO, dtype=str)
df.columns = [str(c).strip().lower() for c in df.columns]

# Limpiar datos
df["id_tramite"] = df["id_tramite"].astype(str).str.strip()
df["fecha_arribo"] = pd.to_datetime(
    df["fecha_arribo"], errors="coerce"
).dt.strftime("%d/%m/%Y")
df["item_id"] = df["item_id"].astype(str).str.strip()


@app.route("/", methods=["GET", "POST"])
def index():

    id_buscado = ""
    resultado = None
    coincidencias = []

    if request.method == "POST":

        id_buscado = request.form.get("id_tramite", "").strip()

        if not id_buscado:
            resultado = "vacio"
        else:
            resultados = df[df["id_tramite"] == id_buscado]

            if not resultados.empty:
                resultado = "encontrado"
                coincidencias = resultados[
                    ["id_tramite", "fecha_arribo", "item_id"]
                ].to_dict(orient="records")
            else:
                resultado = "no_encontrado"

    return render_template(
        "index.html",
        coincidencias=coincidencias,
        id_buscado=id_buscado,
        resultado=resultado
    )


if __name__ == "__main__":
    app.run(debug=True)