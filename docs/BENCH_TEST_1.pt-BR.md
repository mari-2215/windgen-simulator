# Bench Test 1 - plano de teste de bancada e filmagem

O protocolo foi estruturado considerando o material disponível: Raspberry Pi 2B, stack SpeedyBee
F405 V4 e um motor brushless outrunner. A confirmação elétrica do motor, do ESC e da alimentação
permaneceu estabelecida como condição de liberação do ensaio físico.

## Mantendo os recursos necessários

- fonte ou bateria compatível com a tensão do motor e do ESC, com corrente adequada;
- cabo USB de dados entre Raspberry Pi e F405;
- motor firmemente fixado;
- proteção física e meio de cortar a alimentação imediatamente;
- **nenhuma hélice no primeiro teste**.

Foi registrada a disponibilidade de uma bateria nominal de 12 V. Antes da conexão, ficaram
previstos os seguintes registros:

- química da bateria (por exemplo, chumbo-ácido, Li-ion ou LiPo);
- tensão totalmente carregada - uma bateria chamada “12 V” pode ultrapassar 12 V;
- capacidade em Ah/mAh e corrente máxima ou classificação `C`;
- faixa de entrada impressa no ESC (em volts ou quantidade de células `S`);
- faixa de tensão/células e KV do motor.

O uso da bateria ficou condicionado à permanência da tensão **máxima carregada** dentro das faixas
do ESC e do motor. Considerando a elevada corrente de falha possível em baterias de 12 V, foram
previstos fusível adequado, conectores especificados e corte de energia acessível, sem ligações
diretas improvisadas.

Na ausência dos dados de KV/tensão do motor ou de tensão/corrente da alimentação, o plano ficou
restrito aos modos `mock`, `neural-mock` e `serial-check`, mantendo a potência do ESC desligada.

## 1. Preparando o Raspberry Pi

Na pasta do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pyserial
export PYTHONPATH="$PWD/src"
```

## 2. Executando o teste sem hardware

```bash
python3 scripts/bench_test_1.py --mode mock
```

O resultado esperado foi definido como `MOCK PASS`, ficando registrada na tela a rampa de 0% a
10% e o retorno a 0%.

## 3. Demonstrando a rede neural sem acionar o motor

```bash
python3 scripts/bench_test_1.py \
  --mode neural-mock \
  --prompt "vento offshore de 6 m/s por 3 s a 1 m" \
  --max-throttle 0.08
```

Durante essa etapa, o prompt foi convertido em velocidade e distância, a MLP calculou o throttle
bruto e o limitador independente restringiu a saída a 8%. Nenhum comando físico foi transmitido.

## 4. Detectando a F405 por USB

Nessa etapa, foi prevista apenas a conexão USB da F405, mantendo a alimentação de potência do ESC
desconectada:

```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
python3 scripts/bench_test_1.py --mode serial-check --port /dev/ttyACM0
```

O nome da porta poderá variar. O resultado esperado foi definido como `SERIAL PASS`, acompanhado
da versão da API MSP. Ocorrendo timeout, o plano foi interrompido nessa etapa, seguindo-se a
verificação do cabo de dados, porta, permissões e configuração do firmware.

## 5. Preparando o giro neural curto e sem hélice

1. Mantendo todos os equipamentos desligados durante a montagem.
2. Conectando o motor à saída M1 do ESC conforme o manual do stack.
3. Fixando mecanicamente o motor e mantendo a hélice removida.
4. Conectando F405 e ESC pelo chicote original do stack.
5. Preparando o corte físico de energia antes da energização.
6. Energizando o ESC somente após a compatibilidade da fonte/bateria ter sido comprovada.

```bash
python3 scripts/bench_test_1.py \
  --mode neural-motor \
  --port /dev/ttyACM0 \
  --motor 1 \
  --max-throttle 0.08 \
  --duration 3 \
  --prompt "vento offshore de 6 m/s por 3 s a 1 m"
```

O programa exigirá três confirmações digitadas. O prompt será processado pela MLP, o resultado será
limitado ao teto informado e encaminhado ao controle seguro. A rampa de partida foi limitada pelo
controlador e a parada normal passou a usar desaceleração gradual até 0%. Em caso de `Ctrl+C` ou
erro, a parada de emergência continuou sendo enviada imediatamente. O corte físico permaneceu
acessível durante todo o ensaio.

## Resultado registrado

O Bench Test 1 foi registrado como **bem-sucedido**. O motor respeitou o throttle configurado e o
tempo de execução definido no comando. A observação principal após o ensaio foi a necessidade de
formalizar uma rampa de parada além da rampa inicial, melhoria incorporada ao script
`scripts/bench_test_1.py`.

Materiais registrados:

- [vídeo do giro do Bench Test 1](media/bench-test-1-motor-run.mp4);
- [dashboard - entrada do cenário](media/dashboard-input.png);
- [dashboard - gráfico de velocidade](media/dashboard-plot.png);
- [dashboard - tabela exportável](media/dashboard-table.png).

![Dashboard com entrada do cenário](media/dashboard-input.png)

![Dashboard com gráfico de velocidade do vento](media/dashboard-plot.png)

## Registrando o vídeo

1. Registrando os componentes desligados e a hélice removida.
2. Registrando a fixação do motor e identificando Raspberry Pi, F405 e ESC.
3. Executando `mock` e registrando `MOCK PASS`.
4. Executando `neural-mock` e registrando o throttle bruto e o throttle limitado.
5. Executando `serial-check` e registrando `SERIAL PASS`.
6. Estando a alimentação confirmada, registrando o giro neural de três segundos e a parada.
7. Registrando `STOP SENT` e desligando a potência antes de qualquer aproximação física.

## Mantendo os dados para a próxima atualização

- modelo e KV do motor;
- modelo exato do ESC/stack;
- tensão e limite de corrente da alimentação;
- versão do Betaflight e protocolo do ESC;
- porta serial utilizada;
- resultado de cada etapa e qualquer mensagem de erro.
