# Roadmap de evolução

| Horizonte | Evolução | Resultado esperado |
|---|---|---|
| Fase 1 | Simulação, MLP sintética, UI e segurança básica | Pipeline demonstrável |
| Fase 1.1 | Bench Test 1 com um motor | Giro curto validado com rampa de partida e parada |
| Fase 1.2 | Bench Test 2 com gradiente | Perfil `10% -> 60% -> 25%` validado com logs |
| Fase 1.3 | Bench Test 3 com rampa de 2 s | Throttle máximo, RPM, comandos neurais e exaustão planejados |
| Fase 1.4 | Aplicativo de bancada | Operação com botões, porta serial, logs e parada evidente |
| Fase 2 | Anemômetro, LiDAR opcional e dataset real | Modelo calibrado |
| Fase 3 | Controle feed-forward + PID e watchdog MCU | Malha fechada |
| Fase 4 | Duto, colmeia de fluxo e instrumentação | Perfil espacial mais uniforme |
| Fase 5 | Múltiplos motores e controle multivariável | Campo de vento programável |
| Fase 6 | Espectros Kaimal/JONSWAP acoplados, LSTM/TCN | Cenários offshore mais ricos |
| Fase 7 | Digital twin, incerteza e detecção de anomalias | Operação auditável |
| Fase 8 | Ensaios normativos e revisão independente | Caminho para uso industrial |

Prioridades técnicas: segurança independente de software, qualidade dos dados, baseline físico
comparável à MLP, inferência otimizada no Pi e rastreabilidade de cada ensaio.
