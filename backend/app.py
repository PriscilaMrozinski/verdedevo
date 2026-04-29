# NLTK: biblioteca Python de Processamento de Linguagem Natural (PLN)
# NLTK: oferece recursos como: tokenização de texto, stemming, lematização, 
# análise de palavras, corpora liguísticos, classificação de textos
from nltk.stem import RSLPStemmer

from flask import Flask, render_template, request, redirect, jsonify
import json

# Para normalizar acentos, ç e caracteres especiais
import unicodedata 

# Compara palavras parecidas para verificar erro de digitação
import difflib

# RSLPStemmer: algoritmo de stemming em português (reduz palavras ao radical)
# RSLP: remove sufixos, reduz ao racial, ex.: ansiosa -> ansios
stemmer = RSLPStemmer()



app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../assets"
)

ARQUIVO_JSON = "backend/banco_plantas.json"

#  ---------------------------------------------------

# para normalizar acentos, ç, etc
def normalizar_texto(texto):
    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto

#  ---------------------------------------------------

def radicalizar(texto):
    texto = normalizar_texto(texto)
    palavras = texto.split()

    radicais = []

    for palavra in palavras:
        radicais.append(stemmer.stem(palavra))

    return " ".join(radicais)


# -----------------------------------------------------

def palavras_parecidas(palavra, texto):

    palavras_texto = texto.split()

    parecidas = difflib.get_close_matches(
        palavra,
        palavras_texto,
        n=1,
        cutoff=0.75
    )

    return len(parecidas) > 0

#  ---------------------------------------------------

def carregar_dados():
    with open(ARQUIVO_JSON, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados):
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


# -----------------------------------
# IA simples: sinônimos de sintomas
SINONIMOS = {
    "dor de barriga": ["cólica", "má digestão", "gases"],
    "barriga": ["cólica", "má digestão"],
    "gripe": ["tosse", "garganta", "imunidade"],
    "resfriado": ["tosse", "garganta"],
    "nervoso": ["ansiedade", "estresse"],
    "stress": ["estresse"],
    "dor muscular": ["dor muscular", "inflamação"],
    "pedra no rim": ["cálculos renais"],
    "rim": ["cálculos renais"],
    "sono ruim": ["sono", "insônia"],
    "dormir": ["sono"],
    "azia": ["azia", "gastrite"],
    "estômago": ["azia", "gastrite", "má digestão"]
}


def calcular_relevancia(termo, planta):
    score = 0

    texto = (
        planta["nome_popular"] + " " +
        planta["nome_cientifico"] + " " +
        " ".join(planta["beneficios"]) + " " +
        " ".join(planta["indicacoes"]) + " " +
        " ".join(planta["sinonimos"])
    )

    # texto = normalizar_texto(texto)
    # frase = normalizar_texto(termo)
    
    # PLN com stemming (RSLP/NLTK): reduz palavras ao radical para melhorar a busca semântica
    # Ex: ansiosa -> ansios | ansiedade -> ansied
    texto = radicalizar(texto)
    frase = radicalizar(termo)


    palavras = frase.split()

    palavras_ignorar = [
    "estou", "com", "de", "do", "da",
    "muita", "muito", "tenho", "uma",
    "o", "a", "e", "para", "sem",
    "na", "no", "meu", "minha",
    "ultimamente", "hoje", "ontem",
    "sinto", "sentindo", "ando",
    "nao", "não", "consigo",
    "ficando", "mais", "menos",
    "depois", "antes"
    ]

    # Busca normal
    for palavra in palavras:
        if palavra in palavras_ignorar:
            continue
        if palavra in texto:
            score += 3
        elif palavras_parecidas(palavra, texto):
            score += 1

    # Busca por frase completa
    if " ".join(palavras) in texto:
        score += 5

    # NOVO: busca sinônimos
    for chave in SINONIMOS:
        if chave in frase:
            for sinonimo in SINONIMOS[chave]:
                sinonimo = normalizar_texto(sinonimo)
                if sinonimo in texto:
                    score += 4

    return score



# Com normalização de acento, ç, etc
# def calcular_relevancia(termo, planta):

#     score = 0

#     texto = (
#         planta["nome_popular"] + " " +
#         planta["nome_cientifico"] + " " +
#         " ".join(planta["beneficios"]) + " " +
#         " ".join(planta["indicacoes"]) + " " +
#         " ".join(planta["sinonimos"])
#     )

#     texto = normalizar_texto(texto)
#     palavras = normalizar_texto(termo).split()

#     for palavra in palavras:
#         if palavra in texto:
#             score += 2
#         # para verificar erro de digitação (difflib)
#         elif palavras_parecidas(palavra, texto):
#             score += 1

#     return score

# -- Etapa 2 - evoluindo busca
# def calcular_relevancia(termo, planta):
#     score = 0

#     texto = (
#         planta["nome_popular"] + " " +
#         planta["nome_cientifico"] + " " +
#         " ".join(planta["beneficios"]) + " " +
#         " ".join(planta["indicacoes"])
#     ).lower()

#     palavras = termo.lower().split()

#     for palavra in palavras:
#         if palavra in texto:
#             score += 1

#     return score

# Etapa 1 
# -- Função (PLN básico sem IA), para calcular score comparando com a lista de plantas
# NLP (Processamento de Linguagem Natural) - versão rule-based (sem machine learning)
# -- Avalia cada planta individualmente // usa regras (keyword matching + score)
# def calcular_relevancia(termo, planta):

#     score = 0
#     termo = termo.lower()

#     # nome
#     if termo in planta["nome_popular"].lower():
#         score += 5

#     # sintomas / indicações
#     for item in planta["indicacoes"]:
#         if termo in item.lower():
#             score += 3

#     # benefícios
#     for item in planta["beneficios"]:
#         if termo in item.lower():
#             score += 2

#     return score

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


# Etapa 3 - Retornar Três plantas, após busca
# Lembrando que deve atualizar o "Bloco de Resposta no front (main.js)"
#  A função Score pode ser mantida a mesma
@app.route("/buscar")
def buscar():

    termo = normalizar_texto(request.args.get("q", ""))
    plantas = carregar_dados()

    resultados = []

    for planta in plantas:
        score = calcular_relevancia(termo, planta)

        if score > 0:
            resultados.append({
                "planta": planta,
                "score": score
            })

    # ordenar por relevância
    resultados.sort(key=lambda x: x["score"], reverse=True)

    # pegar TOP 3
    top = resultados[:3]

    if top:

        resposta = []

        for item in top:
            p = item["planta"]

            resposta.append({
                "nome": p["nome_popular"],
                "cientifico": p["nome_cientifico"],
                "beneficios": ", ".join(p["beneficios"]),
                "parte": ", ".join(p["parte_utilizada"]),
                "preparo": p["preparo"],
                "score": item["score"]
            })

        return jsonify({
            "status": "ok",
            "resultados": resposta
        })

    return jsonify({
        "status": "erro",
        "mensagem": "Planta não encontrada."
    })


# -- Etapa 2 - evoluindo busca
# --- Retorna apenas UMA planta na busca
# @app.route("/buscar")
# def buscar():

#     termo = request.args.get("q", "").lower()
#     plantas = carregar_dados()

#     resultados = []

#     for planta in plantas:
#         score = calcular_relevancia(termo, planta)

#         if score > 0:
#             resultados.append({
#                 "planta": planta,
#                 "score": score
#             })

#     resultados.sort(key=lambda x: x["score"], reverse=True)

#     if resultados:
#         melhor = resultados[0]["planta"]

#         return jsonify({
#             "status": "ok",
#             "nome": melhor["nome_popular"],
#             "cientifico": melhor["nome_cientifico"],
#             "beneficios": ", ".join(melhor["beneficios"]),
#             "parte": ", ".join(melhor["parte_utilizada"]),
#             "preparo": melhor["preparo"]
#         })

#     return jsonify({
#         "status": "erro",
#         "mensagem": "Planta não encontrada."
#     })

# -------------------------------------------- 

# -- Etapa 1
# -- PNL básico
# @app.route("/buscar")
# def buscar():

#     termo = request.args.get("q", "").lower().strip()

#     plantas = carregar_dados()

#     resultados = []

#     for planta in plantas:

#         score = calcular_relevancia(termo, planta)

#         # guardar as plantas relevantes
#         if score > 0:
#             resultados.append({
#                 "planta": planta,
#                 "score": score
#             })

#     # ordenar a planta por maior relevância, baseado no score da função
#     resultados.sort(key=lambda x: x["score"], reverse=True)

#     if resultados:

#         melhor = resultados[0]["planta"]

#         return jsonify({
#             "status": "ok",
#             "nome": melhor["nome_popular"],
#             "cientifico": melhor["nome_cientifico"],
#             "beneficios": ", ".join(melhor["beneficios"]),
#             "parte": ", ".join(melhor["parte_utilizada"]),
#             "preparo": melhor["preparo"]
#         })

#     return jsonify({
#         "status": "erro",
#         "mensagem": "🌱 Nenhuma planta relacionada encontrada."
#     })

# --------- Rota buscar sem PNL ------
# ----- lembrando que na substituição da rota buscar acima, foi adicionado a função calcular relevância -----
# @app.route("/buscar")
# def buscar():

#     termo = request.args.get("q", "").lower().strip()

#     plantas = carregar_dados()

#     for planta in plantas:

#         nome = planta["nome_popular"].lower().strip()
#         cientifico = planta["nome_cientifico"].lower().strip()

#         # busca por nome popular
#         if termo in nome:

#             return jsonify({
#                 "status": "ok",
#                 "nome": planta["nome_popular"],
#                 "cientifico": planta["nome_cientifico"],
#                 "beneficios": ", ".join(planta["beneficios"]),
#                 "parte": ", ".join(planta["parte_utilizada"]),
#                 "preparo": planta["preparo"]
#             })

#         # busca por nome científico
#         if termo in cientifico:

#             return jsonify({
#                 "status": "ok",
#                 "nome": planta["nome_popular"],
#                 "cientifico": planta["nome_cientifico"],
#                 "beneficios": ", ".join(planta["beneficios"]),
#                 "parte": ", ".join(planta["parte_utilizada"]),
#                 "preparo": planta["preparo"]
#             })

#         # busca por sinônimos
#         for sinonimo in planta["sinonimos"]:
#             if termo in sinonimo.lower():

#                 return jsonify({
#                     "status": "ok",
#                     "nome": planta["nome_popular"],
#                     "cientifico": planta["nome_cientifico"],
#                     "beneficios": ", ".join(planta["beneficios"]),
#                     "parte": ", ".join(planta["parte_utilizada"]),
#                     "preparo": planta["preparo"]
#                 })

#     return jsonify({
#         "status": "erro",
#         "mensagem": "🌱 Planta não encontrada no banco."
#     })

app.run(debug=True)