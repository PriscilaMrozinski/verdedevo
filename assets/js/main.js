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

    // --- Bloco de Resposta no front, retorna três plantas no resultado da busca

    if (dados.status === "ok") {

        let html = `<div class="mt-4 space-y-4">`;

        dados.resultados.forEach(item => {

            html += `
        <div class="bg-white p-5 rounded-2xl shadow text-left">
            <h3 class="text-2xl font-bold text-green-800">
                ${item.nome}
            </h3>

            <p><strong>Nome científico:</strong> ${item.cientifico}</p>
            <p><strong>Benefícios:</strong> ${item.beneficios}</p>
            <p><strong>Parte utilizada:</strong> ${item.parte}</p>
            <p><strong>Preparo:</strong> ${item.preparo}</p>

 
        </div>
        `;
        });

        html += `</div>`;

        resultado.innerHTML = html;

    } else {
        resultado.innerHTML = `
    <p class="text-red-600 font-semibold mt-4">
        ${dados.mensagem}
    </p>
    `;
    }

    // if (dados.status === "ok") {

    //     resultado.innerHTML = `
    //     <div class="bg-white p-5 rounded-2xl shadow mt-4 text-left">
    //         <h3 class="text-2xl font-bold text-green-800">${dados.nome}</h3>
    //         <p><strong>Nome científico:</strong> ${dados.cientifico}</p>
    //         <p><strong>Benefícios:</strong> ${dados.beneficios}</p>
    //         <p><strong>Parte utilizada:</strong> ${dados.parte}</p>
    //         <p><strong>Preparo:</strong> ${dados.preparo}</p>
    //     </div>
    //     `;

    // } else {
    //     resultado.innerHTML = `
    //     <p class="text-red-600 font-semibold mt-4">
    //         ${dados.mensagem}
    //     </p>
    //     `;
    // }

});