# Integração de hardware e segurança

## Topologia recomendada

- Raspberry Pi 2B: prompt, simulação, inferência, logs e supervisão.
- SpeedyBee F405 V4: temporização de motor/ESC sob firmware Betaflight compatível.
- ESC do stack + motor outrunner: estágio de potência.
- Fonte de bancada dimensionada: corrente limitada e aterramento conforme projeto elétrico.
- Anemômetro: obrigatório para calibração física da MLP.

Não alimente motor pelo Raspberry Pi. Não una alimentação de potência sem revisar terra comum,
níveis lógicos e documentação das placas. Remova hélice em testes de comunicação.

## Por que não MAVLink

O PDF original propõe Pixhawk/PyMAVLink. A F405 V4 com Betaflight usa outro ecossistema; o backend
incluído envia um quadro MSP v1 compatível com o comando de motor usado historicamente pelo
Betaflight, mas firmware, modo, mapeamento e permissões podem variar. Valide com a documentação e
o configurador correspondentes à versão instalada. Não havendo confirmação, o modo `mock` deverá
ser mantido.

## Liberação experimental

O código só abre serial quando a variável abaixo corresponde exatamente ao token:

```bash
export LABO_HARDWARE_ENABLE=EU_CONFIRMO_BANCADA_SEGURA
```

Ainda são obrigatórios: anteparo, fixação, operador presente, limite de corrente, fusível, botão
de emergência físico normalmente fechado, timeout independente e teto inicial de 10% sem hélice.
O teto padrão de software é 30%, mas não substitui proteção elétrica/mecânica.

## Sequência de comissionamento

1. Inspecionar motor, ESC, fonte, cabos e fixação; registrar modelo/KV/corrente.
2. Confirmar firmware e protocolo do ESC no configurador SpeedyBee/Betaflight.
3. Validar UART/USB e quadros MSP com ESC desenergizado.
4. Validar parada por perda de comunicação.
5. Energizar com corrente mínima, sem hélice, e testar rampa.
6. Instalar anteparo e anemômetro; só então realizar coleta de baixa energia.
