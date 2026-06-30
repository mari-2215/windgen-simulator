# Resultados e observações

## Bench Test 1

O primeiro ensaio de bancada foi concluído com sucesso. O motor respeitou o limite de throttle
configurado e o tempo de execução definido. A execução também confirmou que o pipeline
`prompt -> rede neural -> limitador -> F405/ESC -> motor` ficou operacional para um motor em baixa
potência.

## Bench Test 2

O segundo ensaio de bancada foi concluído com sucesso. A execução registrou a evolução do controle
para um perfil com mudança de gradiente, avançando do giro curto em baixa potência para uma
sequência com patamares intermediários de throttle.

## Melhorias incorporadas

- A rampa de parada foi adicionada ao fluxo normal do `scripts/bench_test_1.py`.
- A parada imediata foi mantida para interrupções e falhas.
- O perfil do Bench Test 2 foi preparado com a sequência `rampa -> 10% -> 60% -> 25% -> rampa`.
- O Bench Test 2 foi registrado como concluído e passou a compor a trilha experimental do projeto.
- O Bench Test 3 foi estruturado como próxima etapa, com rampa de 2 s para subida e descida.
- A documentação passou a registrar a necessidade de uma aplicação dedicada para facilitar a
  operação em bancada.
- As mídias do dashboard e do ensaio passaram a ser referenciadas no repositório.

## Mídias

- [Vídeo do Bench Test 1](media/bench-test-1-motor-run.mp4)
- [Vídeo do Bench Test 2](media/bench-test-2-gradient-run.mp4)
- [Dashboard - entrada do cenário](media/dashboard-input.png)
- [Dashboard - gráfico de velocidade](media/dashboard-plot.png)
- [Dashboard - tabela exportável](media/dashboard-table.png)

![Entrada do cenário no dashboard](media/dashboard-input.png)

![Gráfico de velocidade do vento no dashboard](media/dashboard-plot.png)

![Tabela exportável no dashboard](media/dashboard-table.png)
