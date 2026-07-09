# RPM pela stack SpeedyBee

A leitura de RPM pela stack foi avaliada como caminho possível, mas ainda não ficou confiável na
bancada atual.

## Observações registradas

- A stack/firmware pode expor informação relacionada a RPM quando o ESC e o firmware suportam
  telemetria adequada ou Bidirectional DShot.
- O motor usado nesta fase é inrunner e não apresentou leitura confiável para este objetivo.
- Ao habilitar Bidirectional DShot, o motor passou a se movimentar em “trotes”, sem rotação
  contínua estável.
- Por esse motivo, RPM não foi adotado como variável de controle no Bench Test 5.

## Decisão de engenharia

O Bench Test 5 mantém:

- comando neural por prompt;
- execução pelo terminal e pelo app;
- feedback de vento preparado em modo simulado/serial;
- RPM documentado como instrumentação em avaliação.

Para RPM confiável, as opções continuam sendo:

- ESC/motor compatível com telemetria estável;
- sensor óptico;
- sensor Hall;
- tacômetro externo para validação de bancada.

RPM não substitui anemômetro. Para controle de vento, a variável de feedback física deverá ser
velocidade de vento medida.
