# Bench Test 3

O Bench Test 3 foi definido como a próxima etapa de bancada após a validação do perfil de gradiente
do Bench Test 2. A proposta passou a concentrar a transição do projeto para um controle mais
instrumentado, preparando coleta de RPM, testes por rede neural e uma operação menos dependente de
linha de comando.

## Objetivo técnico

O perfil base passa a usar rampa fixa de 2 s na subida e na descida:

```text
0% -> rampa de 2 s -> throttle máximo -> rampa de 2 s -> 0%
```

O script foi adicionado em `scripts/bench_test_3.py`. A execução padrão roda em `mock`, imprimindo
a trajetória prevista sem enviar comando físico ao ESC. O modo `motor` envia comandos reais para a
F405/ESC quando a bancada está confirmada.

```bash
python3 scripts/bench_test_3.py --mode mock --max-throttle 0.60 --ramp 2 --hold 3
```

Execução física de bancada:

```bash
python3 scripts/bench_test_3.py \
  --mode motor \
  --port /dev/ttyACM0 \
  --motor 1 \
  --max-throttle 1.00 \
  --ramp 2 \
  --hold 3 \
  --allow-full-throttle
```

## Escopo previsto

- validar a rampa de 2 s para subida e descida;
- testar o throttle máximo definido para a bancada;
- evoluir a operação para um aplicativo dedicado;
- estudar comunicação sem fio entre interface, Raspberry Pi e controlador;
- adicionar leitura de RPM para registrar resposta do motor;
- testar comandos gerados por redes neurais;
- iniciar teste de exaustão, mantendo logs de duração, temperatura percebida, estabilidade e falhas.

## Diretrizes de segurança

O teste de throttle máximo ficou disponível para bancada supervisionada. A etapa física permanece
condicionada a proteção mecânica, motor fixado, corte de energia, alimentação compatível e
supervisão. Acima de 60%, o script exige liberação explícita de full throttle.

## Evolução para aplicativo

O aplicativo de bancada foi incorporado ao `app.py`. A interface planeja o ensaio, visualiza o
perfil, gera o comando para execução controlada, exporta registros e executa o Bench Test 3 no
motor após confirmações explícitas. A interface passou a concentrar:

- seleção da porta serial;
- escolha do perfil de teste;
- campo de throttle máximo;
- botão de execução física guardada para o Bench Test 3;
- gráfico de throttle em tempo real;
- leitura futura de RPM;
- exportação automática de logs e CSV;
- registro das mídias associadas a cada ensaio.

Execução:

```bash
streamlit run app.py
```
