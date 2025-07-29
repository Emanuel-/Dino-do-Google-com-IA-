import random
from deap import base, creator, tools, gp
import operator
import math
from gerador_dados import gerar_base_simples

# ----- Configuração do GP (Programação Genética) -----
pset = gp.PrimitiveSetTyped("MAIN", [float, float, int], str)  # distancia, altura, tipo -> acao
pset.renameArguments(ARG0="distancia")
pset.renameArguments(ARG1="altura")
pset.renameArguments(ARG2="tipo")

# Funções auxiliares
def if_then_else(cond, out1, out2):
    return out1 if cond else out2

def protected_div(a, b):
    return a / b if b != 0 else 1

# Primitivas
pset.addPrimitive(operator.lt, [float, float], bool)
pset.addPrimitive(operator.gt, [float, float], bool)
pset.addPrimitive(operator.eq, [int, int], bool)
pset.addPrimitive(if_then_else, [bool, str, str], str)

pset.addPrimitive(operator.add, [float, float], float)
pset.addPrimitive(operator.sub, [float, float], float)
pset.addPrimitive(operator.mul, [float, float], float)
pset.addPrimitive(protected_div, [float, float], float)

# Terminais
for valor in ["jump", "duck", "nothing"]:
    pset.addTerminal(valor, str)

for i in range(6):
    pset.addTerminal(i, int)

for val in [0.0, 1.0, 5.0, 10.0, 50.0, 100.0, 300.0]:
    pset.addTerminal(val, float)

pset.addTerminal(True, bool)
pset.addTerminal(False, bool)

# Tipos do indivíduo
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

# Toolbox
toolbox = base.Toolbox()
toolbox.register("expr", gp.genFull, pset=pset, min_=2, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr, pset=pset)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.decorate("mate", gp.staticLimit(key=len, max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=17))

# ----- Avalia uma árvore em todos os exemplos -----
def avaliar_arvore(func, base):
    acertos = 0
    for exemplo in base:
        pred = func(exemplo["distancia"], exemplo["altura"], exemplo["tipo"])
        if pred == exemplo["saida"]:
            acertos += 1
    return acertos

# ----- Loop de evolução -----
def executar_evolucao():
    pop = toolbox.population(n=1000)
    geracao = 0

    while True:
        base_treinamento = gerar_base_simples()

        for ind in pop:
            func = toolbox.compile(expr=ind)
            score = avaliar_arvore(func, base_treinamento)
            ind.fitness.values = (score,)

        # Estatísticas
        pop.sort(key=lambda ind: ind.fitness.values[0], reverse=True)
        melhores = pop[:10]
        melhor_score = melhores[0].fitness.values[0]
        percent_100 = sum(1 for ind in pop if ind.fitness.values[0] == 900) / len(pop)

        print(f"Geração {geracao}: Melhor = {melhor_score} | 100% = {percent_100*100:.1f}%")

        if percent_100 >= 0.10:
            print("\n🎉 10% ou mais dos indivíduos gabaritaram!")
            for i, ind in enumerate(melhores):
                with open(f"melhor_arvore_{i}.txt", "w") as f:
                    f.write(str(ind))
            break

        # Evolui
        descendentes = []
        while len(descendentes) < len(pop):
            pais = toolbox.select(pop, 2)
            filhos = list(map(toolbox.clone, pais))

            if random.random() < 0.5:
                toolbox.mate(filhos[0], filhos[1])
                del filhos[0].fitness.values
                del filhos[1].fitness.values

            for filho in filhos:
                if random.random() < 0.2:
                    toolbox.mutate(filho)
                    del filho.fitness.values

            descendentes.extend(filhos)

        pop = descendentes[:len(pop)]
        geracao += 1

if __name__ == "__main__":
    executar_evolucao()
