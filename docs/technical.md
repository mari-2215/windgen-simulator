# Documentação técnica

## Modelo Weibull

Para forma `k` e escala `lambda`, a média é `lambda * Gamma(1 + 1/k)`. O projeto recebe a média
desejada e calcula a escala. Amostras Weibull são suavizadas por recorrência AR(1) e renormalizadas
para preservar a média. Isso produz uma série plausível para testes de software, não um espectro
de turbulência certificado.

## Rede neural

A MLP possui 2 entradas (`wind_mps`, `distance_m`), múltiplas camadas ocultas configuráveis e uma
saída sigmoide. A configuração padrão usa camadas `32 -> 24 -> 12`, ativação `tanh`, normalização
de entradas/saída, validação determinística e otimizador Adam. O alvo é throttle normalizado de
0 a 1.

O conjunto sintético aproxima uma planta não linear de vento/distância/throttle com ruído. Essa lei
é apenas uma planta didática. O modelo válido deve ser treinado com CSV de anemômetro contendo
`wind_mps,distance_m,throttle`, com separação treino/validação e registro da incerteza.

## Reprodutibilidade

- todas as simulações recebem semente;
- unidades internas são SI;
- CSV usa ponto decimal e cabeçalho explícito;
- testes cobrem unidades, limites, reprodução e aprendizado;
- versão do modelo e metadados de calibração devem integrar a Fase 2.

## Critérios de aceitação da Fase 1

- prompt válido produz série, CSV e gráfico sem hardware;
- média da série fica próxima do valor solicitado, respeitando teto de rajada;
- MLP reduz a perda em dados sintéticos;
- comando passa por limite de rampa e teto;
- backend físico não abre porta serial sem token explícito;
- todos os testes passam em Python 3.12.
