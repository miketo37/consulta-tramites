from flask import Flask, render_template, request
import pandas as pd
from unidecode import unidecode

app = Flask(__name__)

ARCHIVO_PASAPORTE = "arribos_pasaporte.xlsx"
ARCHIVO_DNI = "arribos_dni.xlsx"


def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    texto = " ".join(texto.split())
    texto = unidecode(texto.lower())
    return texto


def normalizar_id(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    texto = " ".join(texto.split())
    return texto


def cargar_pasaportes():
    df = pd.read_excel(ARCHIVO_PASAPORTE, dtype=str)
    df.columns = [str(c).strip().lower() for c in df.columns]

    df["fecha_arribo"] = df["fecha_arribo"].astype(str).str.strip()

    df["nombre_normalizado"] = df["nombre_completo"].apply(normalizar_texto)
    df["id_tramite"] = df["id_tramite"].apply(normalizar_id)

    df["identificador"] = df["id_tramite"]

    return df


def cargar_dni():
    df = pd.read_excel(ARCHIVO_DNI, dtype=str)
    df.columns = [str(c).strip().lower() for c in df.columns]

    df["fecha_arribo"] = df["fecha_arribo"].astype(str).str.strip()

    df["nombre_normalizado"] = df["nombre_completo"].apply(normalizar_texto)
    df["numero_dni"] = df["numero_dni"].apply(normalizar_id)

    df["identificador"] = df["numero_dni"]

    return df


df_pasaporte = cargar_pasaportes()
df_dni = cargar_dni()

df_total = pd.concat([df_pasaporte, df_dni], ignore_index=True)


@app.route("/", methods=["GET", "POST"])
def index():

    nombre_buscado = ""
    id_tramite_buscado = ""
    numero_dni_buscado = ""

    coincidencias = []
    resultado = None
    tipo_busqueda = ""

    if request.method == "POST":

        nombre_buscado = request.form.get("nombre", "").strip()
        id_tramite_buscado = request.form.get("id_tramite", "").strip()
        numero_dni_buscado = request.form.get("numero_dni", "").strip()

        try:

            if id_tramite_buscado:

                tipo_busqueda = "id_tramite"
                id_normalizado = normalizar_id(id_tramite_buscado)

                resultado_base = df_pasaporte[
                    df_pasaporte["id_tramite"] == id_normalizado
                ]

                if not resultado_base.empty:

                    nombre_encontrado = resultado_base.iloc[0]["nombre_completo"]
                    nombre_normalizado = normalizar_texto(nombre_encontrado)

                    resultados = df_total[
                        df_total["nombre_normalizado"] == nombre_normalizado
                    ]

                else:
                    resultados = pd.DataFrame()

            elif numero_dni_buscado:

                tipo_busqueda = "numero_dni"
                dni_normalizado = normalizar_id(numero_dni_buscado)

                resultado_base = df_dni[
                    df_dni["numero_dni"] == dni_normalizado
                ]

                if not resultado_base.empty:

                    nombre_encontrado = resultado_base.iloc[0]["nombre_completo"]
                    nombre_normalizado = normalizar_texto(nombre_encontrado)

                    resultados = df_total[
                        df_total["nombre_normalizado"] == nombre_normalizado
                    ]

                else:
                    resultados = pd.DataFrame()

            elif nombre_buscado:

                tipo_busqueda = "nombre"

                nombre_normalizado = normalizar_texto(nombre_buscado)

                resultados = df_total[
                    df_total["nombre_normalizado"].str.contains(
                        nombre_normalizado, na=False
                    )
                ]

            else:

                resultados = pd.DataFrame()
                resultado = "vacio"

            if resultado != "vacio":

                if not resultados.empty:

                    resultado = "encontrado"

                    coincidencias = resultados[
                        ["item_id", "identificador", "nombre_completo", "fecha_arribo"]
                    ].drop_duplicates().to_dict(orient="records")

                else:

                    resultado = "no_encontrado"

        except Exception as e:

            resultado = f"error: {str(e)}"

    return render_template(
        "index.html",
        coincidencias=coincidencias,
        nombre_buscado=nombre_buscado,
        id_tramite_buscado=id_tramite_buscado,
        numero_dni_buscado=numero_dni_buscado,
        resultado=resultado,
        tipo_busqueda=tipo_busqueda,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)