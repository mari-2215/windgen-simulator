# Neural Offshore Wind Lab

[English](README.md)

Projeto acadêmico - Fase 1 de um gerador de ventos inteligente para simular séries temporais
inspiradas em cenários offshore. O sistema interpreta um prompt em português, gera velocidades
com distribuição de Weibull e usa uma rede neural MLP profunda para estimar o comando de um motor.

> **Segurança:** o modo padrão é `mock`, mantendo a hélice removida no primeiro ensaio e prevendo
> anteparo, botão de emergência, limitação de corrente, fixação mecânica e supervisão presencial. A saída
> experimental MSP deve ser validada contra a versão de Betaflight instalada antes de energizar
> o ESC. Este software não é um sistema de segurança certificado.

## O que a Fase 1 entrega

- gerador Weibull reproduzível com rajadas e correlação temporal;
- MLP NumPy profunda e configurável como modelo inverso `(vento desejado, distância) -> throttle`;
- interpretação controlada de prompts, sem depender de serviço externo;
- CSV e gráfico PNG;
- dashboard Streamlit com simulação e app de bancada operacional;
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

O app possui duas abas: simulação Weibull/MLP e **Bench Tests**. A aba de bancada gera o perfil de
throttle, mostra o gráfico, monta o comando seguro para copiar, exporta registros em Markdown/CSV e
executa o Bench Test 3 no motor quando as confirmações de laboratório são marcadas.

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
continua responsável pelo sinal temporizado ao ESC. A integração foi detalhada em [docs/hardware.md](docs/hardware.md).

Para o primeiro teste com Raspberry Pi 2B, SpeedyBee F405 V4 e um motor, foi preparado o roteiro
[Bench Test 1 - teste de bancada e filmagem](docs/BENCH_TEST_1.pt-BR.md). O teste começa em `mock`, faz
uma consulta MSP somente-leitura e só libera um giro curto após confirmações explícitas.

## Resultados de bancada

O Bench Test 1 foi concluído com sucesso: o motor respeitou o throttle definido e o tempo de
execução configurado. Após o teste, o fluxo normal de parada foi atualizado para incluir rampa de
desaceleração até 0%, mantendo parada imediata apenas para interrupções e falhas.

O Bench Test 2 também foi concluído com sucesso, validando o perfil com mudança de gradiente. O
Bench Test 3 foi concluído com sucesso, registrando melhor comportamento com 61 amostras na rampa
de finalização. O Bench Test 4 mostrou o ensaio longo pelo terminal e abriu a necessidade de malha
fechada. O Bench Test 5 introduz feedback de velocidade atual do vento usando fonte simulada ou
anemômetro serial externo.

O aplicativo de bancada foi incorporado ao `app.py`, concentrando planejamento, visualização do
perfil, comando pronto, registro do ensaio e execução física guardada do Bench Test 3.

- [Resultados e observações](docs/RESULTS_AND_OBSERVATIONS.pt-BR.md)
- [Bench Test 2](docs/BENCH_TEST_2.pt-BR.md)
- [Bench Test 3](docs/BENCH_TEST_3.pt-BR.md)
- [Bench Test 4](docs/BENCH_TEST_4.pt-BR.md)
- [Bench Test 5](docs/BENCH_TEST_5.pt-BR.md)
- [Notas de RPM pela SpeedyBee](docs/RPM_SPEEDYBEE.pt-BR.md)
- [Vídeo do Bench Test 1](docs/media/bench-test-1-motor-run.mp4)
- [Vídeo do Bench Test 2](docs/media/bench-test-2-gradient-run.mp4)
- [Vídeo do Bench Test 5 - outrunner](docs/media/bench-test-5-outrunner-throttle-response.mp4)
- [Vídeo do Bench Test 5 - terminal 0.1 s](docs/media/bench-test-5-terminal-sampling-010.mp4)

![Dashboard do simulador](docs/media/dashboard-plot.png)

## Localização do controle neural do motor

O controle foi distribuído em camadas auditáveis:

- `src/labo_gerador_de_ventos/models/mlp.py`: definindo, treinando e executando a MLP profunda;
- `src/labo_gerador_de_ventos/prompt.py`: convertendo o prompt em vento e distância;
- `src/labo_gerador_de_ventos/control/neural_command.py`: transformando a previsão da MLP em
  throttle e aplicando o teto independente do Bench Test 1;
- `src/labo_gerador_de_ventos/control/actuator.py`: aplicando rampa, parada e quadro MSP;
- `scripts/bench_test_1.py`: reunindo as camadas nos modos `neural-mock` e `neural-motor`.
- `scripts/bench_test_2.py`: preparando o perfil de gradiente `0% -> 10% -> 60% -> 25% -> 0%`.
- `scripts/bench_test_3.py`: planejando rampa de 2 s, patamar de throttle máximo e descida de 2 s.
- `scripts/bench_test_4.py`: executando comando neural por prompt, exaustão e layout 1-4 motores.
- `scripts/bench_test_5.py`: executando comando neural com feedback de velocidade atual do vento.
- `src/labo_gerador_de_ventos/control/neural_array.py`: distribuindo throttle neural por posição.
- `src/labo_gerador_de_ventos/sensors/wind.py`: lendo vento simulado ou anemômetro serial.

O caminho implementado ficou definido como:

```text
prompt -> parser -> MLP -> throttle previsto -> limite de 10% -> rampa -> F405/ESC -> motor
```

Por ter sido treinada com dados sintéticos, a MLP permaneceu classificada como demonstração neural
de integração. A arquitetura foi ampliada com múltiplas camadas, Adam e validação, mas a precisão
física depende da coleta posterior com anemômetro e dados reais da bancada.

Python 3.12 é a versão-alvo do projeto. Em Raspberry Pi OS, a disponibilidade deverá ser confirmada
para a arquitetura/versão instalada; oferecendo a imagem oficial outra versão, ficou previsto o
uso de container ou compilação consciente do 3.12. No Pi 2, o retreinamento foi mantido fora do controle.

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

1. Executando e validando inicialmente em `mock`.
2. Treinando a MLP sintética apenas para integração de software.
3. Coletando com anemômetro: distância, throttle/RPM e vento medido.
4. Retreinando e validando em dados separados, sem adotar o sintético como calibração final.
5. Testando sem hélice, com alimentação limitada e parada de emergência.
6. Habilitando o backend físico somente após as verificações de `docs/hardware.md`.
7. Evoluindo para um aplicativo dedicado, reduzindo comandos manuais durante ensaios de bancada.

## Limitações científicas

Weibull representa estatística de velocidade, não CFD nem espectro completo de turbulência.
A MLP inicial aprende uma planta sintética e serve para validar o pipeline. Aplicações Petrobras
ou ensaios homologáveis exigem calibração rastreável, incerteza, sensores reais, análise de riscos
e validação segundo normas aplicáveis.
