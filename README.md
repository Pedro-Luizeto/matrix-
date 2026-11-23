# MATRIX TERMINAL

Animação de chuva digital inspirada no visual de Matrix, feita em Python com Tkinter.

## Requisitos

- Windows 10 ou 11
- Python 3.10 ou superior
- Tkinter (normalmente incluído na instalação oficial do Python)

Não utiliza APIs, conexão com internet ou bibliotecas externas.

## Como executar

1. Extraia a pasta `matrix-terminal`.
2. Abra o terminal dentro dessa pasta.
3. Execute:

```bash
python main.py
```

Se o comando `python` não funcionar no Windows, tente:

```bash
py main.py
```

## Controles

- **Pausar / Continuar:** interrompe ou retoma a animação.
- **Reiniciar:** redistribui as colunas.
- **Tela cheia:** ativa ou desativa a tela cheia.
- **F11:** alterna tela cheia.
- **ESC:** sai da tela cheia.
- **Velocidade:** ajusta a velocidade da chuva.
- **Densidade:** ajusta o espaçamento entre as colunas.
- **Cor:** alterna entre três paletas.

## Responsabilidade dos arquivos

- `main.py`: inicia a aplicação e o loop principal do Tkinter.
- `animation.py`: controla as colunas, caracteres, velocidades, cores e FPS.
- `interface.py`: cria a janela, cabeçalho, controles e tela de inicialização.
- `config.py`: centraliza cores, fontes, FPS e paletas.

## Observações de desempenho

O Canvas mantém os itens de texto e atualiza suas posições e propriedades, em vez de apagar e recriar todos os caracteres em cada quadro. A atualização é agendada em intervalos de aproximadamente 16 ms (alvo de 60 FPS). O movimento usa delta time, então a velocidade permanece consistente mesmo quando um quadro demora mais. A taxa real depende do computador, da resolução e da quantidade de colunas.
