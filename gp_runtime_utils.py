# gp_runtime_utils.py

import operator
import math

# Proteções
def protected_div(x, y):
    try:
        return x / y if y != 0 else 1.0
    except:
        return 1.0

# Operadores disponíveis
primitive_set = {
    "add": operator.add,
    "sub": operator.sub,
    "mul": operator.mul,
    "protected_div": protected_div,
    "lt": operator.lt,
    "gt": operator.gt,
    "eq": operator.eq,
    "if_then_else": lambda cond, out1, out2: out1 if cond else out2,
    "True": True,
    "False": False,
}

def converter_em_funcao(texto):
    """Retorna uma função Python executável a partir do texto da árvore"""
    # Função com 3 variáveis de entrada: velocidade, distancia, tipo
    def func(velocidade, distancia, tipo, altura=300.0):
        local_vars = {
            "velocidade": velocidade,
            "distancia": distancia,
            "tipo": tipo,
            "altura": altura,
        }
        return eval(texto, primitive_set, local_vars)
    
    return func
