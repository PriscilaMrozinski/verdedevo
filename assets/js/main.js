const botao = document.getElementById("btnConsulta");
const campo = document.getElementById("campoBusca");
const resultado = document.getElementById("resultado");

botao.addEventListener("click", async () => {

    const texto = campo.value.trim();

    if (texto === "") {
        resultado.innerHTML = "Digite uma planta.";
        return;
    }

    const resposta = await fetch(`/buscar?q=${texto}`);
    const dados = await resposta.json();

    if (dados.status === "ok") {

        resultado.innerHTML = `
        <div class="bg-white p-5 rounded-2xl shadow mt-4 text-left">
            <h3 class="text-2xl font-bold text-green-800">${dados.nome}</h3>
            <p><strong>Nome científico:</strong> ${dados.cientifico}</p>
            <p><strong>Benefícios:</strong> ${dados.beneficios}</p>
            <p><strong>Parte utilizada:</strong> ${dados.parte}</p>
            <p><strong>Preparo:</strong> ${dados.preparo}</p>
        </div>
        `;

    } else {
        resultado.innerHTML = `
        <p class="text-red-600 font-semibold mt-4">
            ${dados.mensagem}
        </p>
        `;
    }

});