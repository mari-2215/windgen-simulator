# Neural Offshore Wind Lab

[English](README.md)

Projeto acadêmico - Fase 1 de um gerador de ventos inteligente para simular séries temporais
inspiradas em cenários offshore. O sistema interpreta um prompt em português, gera velocidades
com distribuição de Weibull e usa uma rede neural MLP leve para estimar o comando de um motor.

> **Segurança:** o modo padrão é `mock`. Nunca monte hélice para o primeiro ensaio. Use anteparo,
> botão de emergência, limitação de corrente, fixação mecânica e supervisão presencial. A saída
> experimental MSP deve ser validada contra a versão de Betaflight instalada antes de energizar
> o ESC. Este software não é um sistema de segurança certificado.

## O que a Fase 1 entrega

- gerador Weibull reproduzível com rajadas e correlação temporal;
- MLP NumPy treinada como modelo inverso `(vento desejado, distância) -> throttle`;
- interpretação controlada de prompts, sem depender de serviço externo;
- CSV e gráfico PNG;
- dashboard Streamlit;
- CLI e testes unitários;
- atuador simulado e backend MSP/Betaflight experimental, bloqueado por padrão;
- documentação de arquitetura, hardware, implementação e roadmap.

## Início rápido

```bash
python -m venv .venv
# Linux/Raspberry Pi: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python scripts/train_model.py
neural-wind-lab simulate --prompt "vento offshore médio de 12 m/s, rajadas de 18 m/s por 60 s a 1,5 m"
streamlit run app.py
pytest
```

Os artefatos são gravados em `artifacts/`. A semente aleatória pode ser fixada por CLI ou no
dashboard para permitir repetição do experimento.

## Exemplos de prompt

```text
vento constante de 8 m/s por 30 s a 1 m
cenário offshore moderado, média 12 m/s, rajadas de 18 m/s, duração 2 min, distância 1500 mm
vento forte de 45 km/h durante 90 s a 2 m
```

O parser aceita `m/s`, `km/h`, segundos/minutos e distância em `m` ou `mm`. Termos vagos usam
presets documentados: leve 6 m/s, moderado 12 m/s e forte 18 m/s.

## Hardware disponível e decisão de integração

O material de referência original cita Raspberry Pi 5, Pixhawk e MAVLink. O protótipo disponível
usa Raspberry Pi 2B e SpeedyBee F405 V4, normalmente associada ao ecossistema Betaflight/MSP.
Por isso, esta versão não usa PyMAVLink. O Pi executa geração, inferência e supervisão; a F405
continua responsável pelo sinal temporizado ao ESC. Consulte [docs/hardware.md](docs/hardware.md).

Python 3.12 é a versão-alvo do projeto. Em Raspberry Pi OS, confirme a disponibilidade para a
arquitetura/versão instalada; quando a imagem oficial oferecer outra versão, use container ou
compile 3.12 conscientemente. O Pi 2 tem recursos limitados: evite retreinar durante o controle.

## Estrutura

```text
NEURAL_OFFSHORE_WIND_LAB/
├── app.py
├── config/default.json
├── docs/
├── scripts/train_model.py
├── src/labo_gerador_de_ventos/
│   ├── control/
│   ├── models/
│   └── *.py
├── tests/
└── artifacts/
```

## Fluxo operacional seguro

1. Execute e valide tudo em `mock`.
2. Treine a MLP com dados sintéticos apenas para integração de software.
3. Colete dados reais com anemômetro: distância, throttle/RPM e vento medido.
4. Retreine e valide em dados separados; não use o sintético como calibração final.
5. Teste sem hélice, com alimentação limitada e parada de emergência.
6. Só então habilite o backend físico conforme `docs/hardware.md`.

## Limitações científicas

Weibull representa estatística de velocidade, não CFD nem espectro completo de turbulência.
A MLP inicial aprende uma planta sintética e serve para validar o pipeline. Aplicações Petrobras
ou ensaios homologáveis exigem calibração rastreável, incerteza, sensores reais, análise de riscos
e validação segundo normas aplicáveis.
