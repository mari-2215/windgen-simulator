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

O script de planejamento foi adicionado em `scripts/bench_test_3.py`. A execução padrão apenas
imprime a trajetória prevista, sem enviar comando físico ao ESC.

```bash
python3 scripts/bench_test_3.py --max-throttle 0.60 --ramp 2 --hold 3
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

O teste de throttle máximo não ficou liberado como primeiro procedimento físico. A etapa física
permanece condicionada a proteção mecânica, ausência de hélice, corte de energia, alimentação
compatível e supervisão. O valor de throttle máximo deverá ser definido por etapa, começando por
um limite conservador e aumentando somente após cada execução validada.

## Evolução para aplicativo

O aplicativo de bancada foi definido como prioridade operacional após o Bench Test 2. A interface
prevista deverá concentrar:

- seleção da porta serial;
- escolha do perfil de teste;
- campo de throttle máximo;
- botões de iniciar, parar e emergência;
- gráfico de throttle em tempo real;
- leitura futura de RPM;
- exportação automática de logs e CSV;
- registro das mídias associadas a cada ensaio.
