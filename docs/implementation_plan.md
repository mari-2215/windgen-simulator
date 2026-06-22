# Plano de implementação em etapas

## Etapa 1 - Núcleo lógico (entregue)

- parser de prompts e unidades;
- série Weibull reproduzível;
- MLP leve e dataset sintético;
- CSV, gráfico, dashboard, CLI e testes;
- abstração de atuador, mock e bloqueios de segurança.

## Etapa 2 - Comissionamento eletrônico

- inventariar motor, KV, ESC, tensão e corrente;
- confirmar firmware/protocolo da F405 V4;
- implementar heartbeat/watchdog e parada física;
- ensaiar sem hélice e registrar telemetria.

## Etapa 3 - Calibração

- desenhar experimento distância x throttle x vento;
- coletar repetições com anemômetro calibrado;
- dividir treino/validação/teste por sessão;
- treinar, comparar baseline e publicar métricas/incerteza.

## Etapa 4 - Malha fechada

- incorporar vento medido;
- MLP fornece feed-forward e PID supervisor corrige erro;
- validar overshoot, tempo de acomodação e parada segura.

## Etapa 5 - Homologação acadêmica

- protocolo experimental, análise estatística e rastreabilidade;
- testes de longa duração, térmicos, vibração e falhas;
- relatório final e pacote reproduzível.

