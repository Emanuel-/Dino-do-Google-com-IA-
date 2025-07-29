# Dino-do-Google-com-IA-
Projeto pessoal que pretende criar uma IA que aprenda a jogar o jogo do Dino do google


O projeto encontra-se pronto e funcional

Basta rodar o arquivo ia_ciclo_completo

O ciclo que acontece:

São testados 1000 modelos por epoch, depois de cada epoch há o cruzamento "genético" aonde os melhores modelos influenciam mais nas futuras gerações.

Uma vez que 10% dos modelos conseguem gabaritar as situações(que são modifcadas a cada epoch tal qual seria se as imagens fossem renderizadas), 4 das 10% melhores são pinçadas e carregam o comportamento dos 4 dinos que aparecerão jogando, isso se repete até a velocidade 60, no caso a cada geração é adicionado mais 300 exemplos devidamente equilibrados entre as ações.

Desse modo conseguimos ver a evolução do algoritmo em computadores com um processamento normal(como é o meu caso).
