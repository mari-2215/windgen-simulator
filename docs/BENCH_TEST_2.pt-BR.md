# Bench Test 2

O Bench Test 2 foi definido como evolução direta do primeiro ensaio físico. A meta técnica passou a
ser a validação de uma sequência com variação de gradiente:

```text
rampa -> 10% -> 60% -> 25% -> rampa de parada
```

O perfil foi implementado em `scripts/bench_test_2.py` e modelado em
`src/labo_gerador_de_ventos/control/profiles.py`.

## Perfil previsto

| Tempo | Throttle alvo | Finalidade |
| ---: | ---: | --- |
| 0 s a 3 s | 0% -> 10% | rampa inicial controlada |
| 3 s a 6 s | 10% | patamar baixo para estabilização |
| 6 s a 10 s | 10% -> 60% | subida de gradiente |
| 10 s a 13 s | 60% | patamar alto supervisionado |
| 13 s a 16 s | 60% -> 25% | redução intermediária |
| 16 s a 19 s | 25% | patamar médio |
| 19 s a 22 s | 25% -> 0% | rampa de parada |

## Execução simulada

```bash
python3 scripts/bench_test_2.py --mode mock
```

A execução em `mock` imprime os alvos e valores aplicados sem enviar comando físico ao ESC.

## Resultado registrado

O Bench Test 2 foi registrado como **bem-sucedido**. A sequência de gradiente foi executada como
continuidade do Bench Test 1, validando a transição entre patamares de throttle e mantendo a lógica
de rampa controlada.

Mídia registrada:

- [vídeo do Bench Test 2](media/bench-test-2-gradient-run.mp4).

## Execução física, mantida bloqueada por padrão

Como o perfil alcança 60% de throttle, a execução física ficou condicionada a liberação explícita,
sem hélice, com fixação mecânica, proteção, limitação de alimentação e corte físico de emergência.

```bash
python3 scripts/bench_test_2.py \
  --mode motor \
  --port /dev/ttyACM0 \
  --motor 1 \
  --allow-high-throttle
```

O script exige as confirmações:

- `PROPELLER_REMOVED`
- `MOTOR_SECURED`
- `ESTOP_READY`
- `BENCH_TEST_2_APPROVED`

## Observação sobre aplicativo

A operação por linha de comando foi suficiente para validação técnica, porém a manipulação em
bancada tende a ficar mais segura e simples com uma aplicação dedicada. O roadmap passou a incluir
um modo aplicativo com:

- seleção de porta serial;
- botão de teste `mock`;
- botão de teste neural;
- visualização do throttle em tempo real;
- execução de perfis salvos;
- botão de parada evidente;
- exportação automática de log, CSV e mídia do ensaio.
