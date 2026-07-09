# Bench Test 5

O Bench Test 5 introduz feedback de velocidade atual do vento. A meta passou a ser sair do comando
puramente feed-forward por prompt e iniciar uma correção em malha fechada:

```text
prompt -> MLP -> throttle base -> leitura de vento atual -> correção -> motores
```

## Sensor externo

Para medir velocidade atual de vento de verdade, é necessário um sensor externo de vento, como
anemômetro serial, sensor diferencial calibrado ou outro medidor validado. A stack/controladora e o
ESC podem ajudar com telemetria de motor/RPM, mas RPM não é medição direta de vento.

O terminal mantém duas fontes para desenvolvimento:

- `simulated`: feedback simulado, usado para teste de software sem sensor;
- `serial`: anemômetro externo enviando uma velocidade em `m/s` por linha serial.

No aplicativo, o Bench Test 5 foi simplificado: o comando principal é o prompt neural, e o
anemômetro real fica como instrumentação externa de bancada, não como requisito visual do app nesta
etapa.

## Execução simulada

```bash
python3 scripts/bench_test_5.py \
  --mode mock \
  --prompt "vento offshore de 12 m/s por 60 s a 1 m" \
  --wind-source simulated \
  --duration 60 \
  --ramp 2
```

## Execução física com anemômetro serial

```bash
python3 scripts/bench_test_5.py \
  --mode motor \
  --port /dev/ttyACM0 \
  --prompt "vento offshore de 12 m/s por 60 s a 1 m" \
  --layout cross \
  --motor-count 1 \
  --wind-source serial \
  --wind-port /dev/ttyUSB0 \
  --duration 60 \
  --ramp 2 \
  --confirm-secured \
  --confirm-supervision \
  --confirm-estop
```

## Controle

O comando neural continua definindo o throttle-base. A leitura de vento mede o erro em relação ao
vento alvo e aplica uma correção proporcional:

```text
throttle_corrigido = throttle_base + kp * (vento_alvo - vento_medido)
```

O valor final continua limitado por `--max-throttle`.

## Resultado parcial com motor outrunner

Após testes com motor outrunner, a resposta aos comandos de throttle melhorou em relação ao motor
inrunner usado anteriormente. O motor registrado para esta etapa foi o **HYPERION ZS3025B-10**.
A velocidade máxima suportada na bancada para esse conjunto foi registrada como **19 m/s**.

A taxa de amostragem de `0.1 s` apresentou melhor comportamento na execução pelo terminal,
reduzindo os engasgos percebidos durante a rampa. O app permaneceu em revisão separada porque o
vídeo registrado não correspondeu a uma execução feita pela interface.

Mídias registradas:

- [resposta de throttle com motor outrunner](media/bench-test-5-outrunner-throttle-response.mp4);
- [execução pelo terminal com amostragem 0.1 s](media/bench-test-5-terminal-sampling-010.mp4).

## RPM

A leitura de RPM permanece uma instrumentação separada. Foi identificado que a stack SpeedyBee pode
fornecer caminho para RPM via telemetria/recursos do ecossistema Betaflight/ESC, mas o motor
inrunner usado nesta etapa não forneceu leitura confiável. Além disso, ao habilitar Bidirectional
DShot, o motor passou a apresentar movimento aos “trotes”, em vez de rotação contínua.

Mesmo com o motor outrunner, a leitura de RPM pelo SpeedyBee ainda não foi obtida de forma confiável
durante esta atualização. A integração por API Betaflight envolvendo posição/tempo foi registrada
como tentativa não concluída e ficou fora do caminho crítico do Bench Test 5.

RPM pode ser útil para diagnosticar ESC, motor e carga, mas não substitui anemômetro para feedback
de vento. O caminho previsto ficou:

1. estabelecer feedback de vento com anemômetro;
2. adicionar RPM por telemetria ESC, sensor óptico ou Hall;
3. registrar vento, throttle, RPM e observações no mesmo log.

## Observação do app

No Bench Test 5 não foi mantido o conceito de “throttle máximo permitido” como comando principal.
O app passou a tratar o prompt como entrada de comando, deixando a rede neural calcular o throttle
necessário. O teto interno segue existindo apenas como proteção operacional do script.
