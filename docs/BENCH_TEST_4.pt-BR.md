# Bench Test 4

O Bench Test 4 foi definido como a próxima evolução da bancada: ensaio de maior duração, comando
por prompt usando rede neural e preparação para um arranjo com até quatro motores. A meta deixou de
ser ditar manualmente uma porcentagem fixa e passou a ser:

```text
prompt -> MLP -> distribuição por layout -> motores -> registro de RPM/exaustão
```

## Objetivos

- realizar teste de exaustão com o motor ligado por aproximadamente 10 minutos;
- usar prompt como entrada principal de comando;
- permitir que a rede neural estime o throttle-base;
- distribuir o throttle para 1 a 4 motores;
- comparar layout em cruz (`cross`) e em X (`x`);
- preparar leitura/registro de RPM;
- manter log de estabilidade, ruído, aquecimento percebido e falhas.

## Execução simulada

```bash
python3 scripts/bench_test_4.py \
  --mode mock \
  --prompt "vento offshore de 12 m/s por 10 min a 1 m" \
  --layout cross \
  --motor-count 1 \
  --duration 600 \
  --ramp 2
```

## Execução física de bancada

```bash
python3 scripts/bench_test_4.py \
  --mode motor \
  --port /dev/ttyACM0 \
  --prompt "vento offshore de 12 m/s por 10 min a 1 m" \
  --layout cross \
  --motor-count 1 \
  --duration 600 \
  --ramp 2 \
  --confirm-secured \
  --confirm-supervision \
  --confirm-estop
```

O teste físico envia comandos reais por MSP para a F405/ESC. Para um motor, a saída `M1` é usada.
Para quatro motores, a distribuição segue:

| Layout | M1 | M2 | M3 | M4 |
| --- | --- | --- | --- | --- |
| `cross` | front | right | back | left |
| `x` | front-right | back-right | back-left | front-left |

## RPM

A leitura automática de RPM ainda depende da instrumentação disponível na bancada, como telemetria
do ESC, sensor óptico/hall ou outro canal confiável. O Bench Test 4 já reserva o registro de RPM no
fluxo experimental e no app, mas a aquisição automática deverá ser conectada após a escolha do
sensor ou protocolo.

## Critérios de observação

- duração total completada;
- ausência de movimento residual na parada;
- ruído/vibração;
- aquecimento do motor, ESC e alimentação;
- RPM médio/máximo quando houver leitura;
- mensagens de erro ou perda de comunicação.
