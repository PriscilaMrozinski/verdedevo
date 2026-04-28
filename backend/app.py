from flask import Flask, render_template, request, redirect, jsonify
import json

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../assets"
)

ARQUIVO_JSON = "backend/banco_plantas.json"


def carregar_dados():
    with open(ARQUIVO_JSON, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados):
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/admin")
def admin():

    plantas = carregar_dados()

    busca = request.args.get("busca", "").lower()

    if busca:
        plantas = [
            p for p in plantas
            if busca in p["nome_popular"].lower()
            or busca in p["nome_cientifico"].lower()
        ]

    # -------------------------
    # GRÁFICO 1 - PARTES
    # -------------------------

    partes = {}

    for planta in plantas:
        for parte in planta["parte_utilizada"]:

            parte = parte.lower()

            if "casca" in parte:
                parte = "Casca"

            elif "caule" in parte:
                parte = "Caule"

            elif "folha" in parte:
                parte = "Folhas"

            elif "flor" in parte:
                parte = "Flores"

            elif "raiz" in parte:
                parte = "Raiz"

            elif "fruto" in parte:
                parte = "Fruto"

            else:
                parte = parte.capitalize()

            partes[parte] = partes.get(parte, 0) + 1

    # -------------------------
    # GRÁFICO 2 - BENEFÍCIOS
    # -------------------------

    beneficios = {}

    for planta in plantas:
        for item in planta["beneficios"]:
            beneficios[item] = beneficios.get(item, 0) + 1

    beneficios = dict(
        sorted(
            beneficios.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
    )

    # -------------------------
    # GRÁFICO 3 - TOP
    # -------------------------

    top_plantas = {}

    for planta in plantas[:5]:
        top_plantas[planta["nome_popular"]] = planta["id"] + 2

    return render_template(
        "admin.html",
        plantas=plantas,
        busca=busca,

        partes_labels=list(partes.keys()),
        partes_valores=list(partes.values()),

        beneficios_labels=list(beneficios.keys()),
        beneficios_valores=list(beneficios.values()),

        top_labels=list(top_plantas.keys()),
        top_valores=list(top_plantas.values())
    )

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():

    if request.method == "POST":

        plantas = carregar_dados()

        nova = {
            "id": len(plantas) + 1,
            "nome_popular": request.form["nome_popular"],
            "nome_cientifico": request.form["nome_cientifico"],
            "sinonimos": [],
            "parte_utilizada": [request.form["parte_utilizada"]],
            "beneficios": [request.form["beneficios"]],
            "indicacoes": [request.form["indicacoes"]],
            "preparo": request.form["preparo"],
            "contraindicacoes": "",
            "foto": ""
        }

        plantas.append(nova)
        salvar_dados(plantas)

        return redirect("/admin")

    return render_template("adicionar.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    plantas = carregar_dados()

    for planta in plantas:

        if planta["id"] == id:

            if request.method == "POST":

                planta["nome_popular"] = request.form["nome_popular"]
                planta["nome_cientifico"] = request.form["nome_cientifico"]
                planta["parte_utilizada"] = [request.form["parte_utilizada"]]
                planta["beneficios"] = [request.form["beneficios"]]
                planta["indicacoes"] = [request.form["indicacoes"]]
                planta["preparo"] = request.form["preparo"]

                salvar_dados(plantas)

                return redirect("/admin")

            return render_template("editar.html", planta=planta)


@app.route("/excluir/<int:id>")
def excluir(id):

    plantas = carregar_dados()

    plantas = [p for p in plantas if p["id"] != id]

    salvar_dados(plantas)

    return redirect("/admin")

@app.route("/buscar")
def buscar():

    termo = request.args.get("q", "").lower().strip()

    plantas = carregar_dados()

    for planta in plantas:

        nome = planta["nome_popular"].lower().strip()
        cientifico = planta["nome_cientifico"].lower().strip()

        # busca por nome popular
        if termo in nome:

            return jsonify({
                "status": "ok",
                "nome": planta["nome_popular"],
                "cientifico": planta["nome_cientifico"],
                "beneficios": ", ".join(planta["beneficios"]),
                "parte": ", ".join(planta["parte_utilizada"]),
                "preparo": planta["preparo"]
            })

        # busca por nome científico
        if termo in cientifico:

            return jsonify({
                "status": "ok",
                "nome": planta["nome_popular"],
                "cientifico": planta["nome_cientifico"],
                "beneficios": ", ".join(planta["beneficios"]),
                "parte": ", ".join(planta["parte_utilizada"]),
                "preparo": planta["preparo"]
            })

        # busca por sinônimos
        for sinonimo in planta["sinonimos"]:
            if termo in sinonimo.lower():

                return jsonify({
                    "status": "ok",
                    "nome": planta["nome_popular"],
                    "cientifico": planta["nome_cientifico"],
                    "beneficios": ", ".join(planta["beneficios"]),
                    "parte": ", ".join(planta["parte_utilizada"]),
                    "preparo": planta["preparo"]
                })

    return jsonify({
        "status": "erro",
        "mensagem": "🌱 Planta não encontrada no banco."
    })

app.run(debug=True)