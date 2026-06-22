# Teste de bancada e filmagem - Fase 1

Este roteiro foi feito para o material disponível: Raspberry Pi 2B, SpeedyBee F405 V4 stack e um
motor brushless outrunner. Ele não substitui a confirmação elétrica do motor, ESC e fonte.

## O que ainda é necessário

- fonte ou bateria compatível com a tensão do motor e do ESC, com corrente adequada;
- cabo USB de dados entre Raspberry Pi e F405;
- motor firmemente fixado;
- proteção física e meio de cortar a alimentação imediatamente;
- **nenhuma hélice no primeiro teste**.

Você informou que possui uma bateria de 12 V. Antes de conectá-la, registre:

- química da bateria (por exemplo, chumbo-ácido, Li-ion ou LiPo);
- tensão totalmente carregada - uma bateria chamada “12 V” pode ultrapassar 12 V;
- capacidade em Ah/mAh e corrente máxima ou classificação `C`;
- faixa de entrada impressa no ESC (em volts ou quantidade de células `S`);
- faixa de tensão/células e KV do motor.

Use a bateria somente se a tensão **máxima carregada** estiver dentro das faixas do ESC e do motor.
Baterias de 12 V podem fornecer corrente suficiente para causar incêndio ou derreter cabos; use
fusível adequado, conectores corretos e um corte de energia acessível. Não improvise ligação direta.

Se você não souber o KV/tensão do motor ou a tensão/corrente da fonte, faça apenas `mock` e
`serial-check`. Não ligue a potência do ESC por tentativa.

## 1. Preparar o Raspberry Pi

Na pasta do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyserial
export PYTHONPATH="$PWD/src"
```

## 2. Teste sem hardware

```bash
python3 scripts/bench_test.py --mode mock
```

Resultado esperado: `MOCK PASS`. Grave a tela mostrando a rampa de 0% a 10% e a parada.

## 3. Detectar a F405 por USB

Conecte somente o USB da F405, sem alimentação de potência no ESC:

```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
python3 scripts/bench_test.py --mode serial-check --port /dev/ttyACM0
```

O nome pode ser diferente. Resultado esperado: `SERIAL PASS` e a versão da API MSP. Se houver
timeout, pare aqui e verifique cabo de dados, porta, permissões e configuração do firmware.

## 4. Giro curto sem hélice - somente após confirmar alimentação

1. Desligue tudo.
2. Solde/conecte o motor à saída M1 do ESC conforme o manual do stack.
3. Fixe o motor mecanicamente e mantenha a hélice removida.
4. Conecte F405 e ESC pelo chicote original do stack.
5. Prepare o corte físico de energia.
6. Energize o ESC somente com fonte/bateria comprovadamente compatível.

```bash
python3 scripts/bench_test.py \
  --mode motor \
  --port /dev/ttyACM0 \
  --motor 1 \
  --max-throttle 0.08 \
  --duration 3
```

O programa exigirá três confirmações digitadas. Ele limita o comando a 10%, limita a rampa e envia
parada no bloco `finally`, inclusive após `Ctrl+C`. Ainda assim, mantenha a mão no corte físico.

## Roteiro simples para o vídeo

1. Mostre os componentes desligados e a hélice removida.
2. Mostre a fixação do motor e identifique Raspberry Pi, F405 e ESC.
3. Rode `mock` e mostre `MOCK PASS`.
4. Rode `serial-check` e mostre `SERIAL PASS`.
5. Se a alimentação estiver confirmada, filme o giro de três segundos e a parada automática.
6. Mostre o terminal com `STOP SENT` e desligue a potência antes de tocar no sistema.

## Dados a anotar para a próxima atualização

- modelo e KV do motor;
- modelo exato do ESC/stack;
- tensão e limite de corrente da alimentação;
- versão do Betaflight e protocolo do ESC;
- porta serial utilizada;
- resultado de cada etapa e qualquer mensagem de erro.
