import operator
import random
from deap import base, gp, creator, tools
import math

# 1. Criar o conjunto de primitivas
pset = gp.PrimitiveSetTyped("MAIN", [float, float, int], str)  # velocidade, distância, tipo -> ação
pset.renameArguments(ARG0="velocidade")
pset.renameArguments(ARG1="distancia")
pset.renameArguments(ARG2="tipo")

def if_then_else(condition, out1, out2):
    return out1 if condition else out2

def protected_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1.0

# Operadores lógicos
pset.addPrimitive(operator.lt, [float, float], bool)
pset.addPrimitive(operator.gt, [float, float], bool)
pset.addPrimitive(operator.eq, [float, float], bool)
pset.addPrimitive(operator.eq, [int, int], bool)
pset.addPrimitive(if_then_else, [bool, str, str], str)

# Operações numéricas
pset.addPrimitive(operator.add, [float, float], float)
pset.addPrimitive(operator.sub, [float, float], float)
pset.addPrimitive(operator.mul, [float, float], float)
pset.addPrimitive(protected_div, [float, float], float)

# Terminais
pset.addTerminal("jump", str)
pset.addTerminal("duck", str)
pset.addTerminal("nothing", str)
pset.addTerminal(1.0, float)
pset.addTerminal(0.0, float)
pset.addTerminal(0, int)
pset.addTerminal(1, int)
pset.addTerminal(2, int)
pset.addTerminal(3, int)
pset.addTerminal(4, int)
pset.addTerminal(5, int)

# Adicionar terminais booleanos obrigatórios
pset.addTerminal(True, bool)
pset.addTerminal(False, bool)

# 2. Definir tipos
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

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
