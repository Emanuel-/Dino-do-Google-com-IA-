from gp_config import toolbox
import random
import os
from deap import tools


POP_SIZE = 200
INDIVIDUOS_POR_TESTE = 4
CAMINHO_SALVAMENTO = "melhores_arvores"

populacao = toolbox.population(n=POP_SIZE)
indice_atual = 0
resultados = [0] * POP_SIZE
geracao_atual = 0

# Garante a existência da pasta de salvamento
os.makedirs(CAMINHO_SALVAMENTO, exist_ok=True)


def get_proxima_quadra():
    """
    Retorna a próxima sequência de 4 árvores compiladas.
    Se atingir o fim da população, retorna None para sinalizar fim de geração.
    """
    global indice_atual

    if indice_atual >= len(populacao):
        return None

    quadra = populacao[indice_atual:indice_atual + INDIVIDUOS_POR_TESTE]
    indice_atual += INDIVIDUOS_POR_TESTE
    return [toolbox.compile(expr=ind) for ind in quadra]


def registrar_resultados(pontuacoes, velocidades):
    """
    Registra os resultados (pontuações) da quadra atual.
    Se a velocidade for 60, salva a árvore correspondente.
    """
    global resultados, indice_atual, geracao_atual

    inicio = indice_atual - INDIVIDUOS_POR_TESTE
    for i in range(len(pontuacoes)):
        idx = inicio + i
        resultados[idx] = pontuacoes[i]

        if velocidades[i] >= 60:
            nome_arquivo = f"arvore_vel60_gen{geracao_atual}_ind{idx}.txt"
            caminho = os.path.join(CAMINHO_SALVAMENTO, nome_arquivo)
            with open(caminho, "w") as f:
                f.write(str(populacao[idx]))


def evoluir_populacao():
    global populacao, resultados, indice_atual, geracao_atual

    # Atribui o fitness (pontuação) de cada indivíduo
    for ind, score in zip(populacao, resultados):
        ind.fitness.values = (score,)

    melhores = tools.selBest(populacao, 100)  # os 100 melhores
    nova_pop = []

    # Preenche a nova população com cruzamentos entre os melhores
    while len(nova_pop) < POP_SIZE:
        pai1, pai2 = random.sample(melhores, 2)
        filho1, filho2 = toolbox.clone(pai1), toolbox.clone(pai2)

        if random.random() < 0.5:
            toolbox.mate(filho1, filho2)
            del filho1.fitness.values
            del filho2.fitness.values

        nova_pop.extend([filho1, filho2])

    # Corta o excesso se passar do tamanho
    populacao = nova_pop[:POP_SIZE]

    # Garante que todos os novos indivíduos estejam sem fitness atribuído
    for ind in populacao:
        if hasattr(ind.fitness, "values"):
            del ind.fitness.values
    
    # Calcula e imprime a média da geração
    media = sum(resultados) / len(resultados)
    print(f"[Geração {geracao_atual}] Média de pontuação: {media:.2f}")


    resultados = [0] * POP_SIZE
    indice_atual = 0
    geracao_atual += 1

    # Salva o melhor da geração
    melhor_da_geracao = tools.selBest(populacao, 1)[0]
    nome_arquivo = f"melhor_geracao.txt"
    caminho = os.path.join(CAMINHO_SALVAMENTO, nome_arquivo)
    with open(caminho, "w") as f:
        f.write(str(melhor_da_geracao))

