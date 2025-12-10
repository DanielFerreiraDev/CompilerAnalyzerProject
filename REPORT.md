# Trabalho AP3 - Construção de Compiladores

**Autor:** Daniel Ferreira do Nascimento

**Resumo:** Implementação de um analisador léxico e sintático (subconjunto de C), com geração de AST e detecção de erros.

## 1. Introdução
Este projeto implementa as primeiras fases de um compilador para um subconjunto simplificado da linguagem C. Ele inclui:

Analisador Léxico (Lexer)

Analisador Sintático (Parser) — Recursive Descent

Geração de AST (Abstract Syntax Tree)

Mensagens de erro sintático detalhadas

Testes com 10 programas (5 válidos / 5 inválidos)

O objetivo é demonstrar, de forma prática, como funcionam as etapas iniciais de um compilador real.

## 2. Metodologia
A implementação foi dividida em três componentes principais: o analisador léxico (lexer ), o analisador sintático (parser ) e o gerador de AST.


O *analisador léxico* tem como função transformar o texto do código-fonte em uma lista
de tokens. Ele utiliza expressões regulares para identificar palavras-chave, operadores,
delimitadores, números, identificadores e literais.
Dentre os aspectos importantes do lexer está o cálculo correto de linha e coluna para
gerar mensagens de erro precisas. O lexer também ignora comentários // e /* */.

O *parser* foi implementado como um recursive descent parser, interpretando a sequência
de tokens e garantindo que ela siga a gramática definida.
Para este trabalho, foi implementado suporte às seguintes estruturas:
- declarações de variáveis;
- funções com parâmetros;
- comandos condicionais (if/else);
- laços de repetição (while e for);
- atribuições (=);
- expressões aritméticas e lógicas.


Cada construção sintática resulta em um nó da AST, em formato hierárquico. A AST é
exportada como JSON para visualização estruturada.

## 3. Testes e Resultados
Foram testados dez programas em C simplificado, sendo cinco válidos e cinco inválidos.

Todos foram processados pelo script run_examples.py, que gera arquivos JSON contendo AST ou mensagens de erro.

SAIDA (run_examples.py):

Parsed error1.c -> ERROR: Expected SEMI but got ('ID', 'a', 3, 5)

Parsed error2.c -> ERROR: Unexpected token in factor: ('RBRACE', '}', 6, 1)

Parsed error3.c -> ERROR: Expected RPAREN but got ('LBRACE', '{', 1, 11)

Parsed error4.c -> ERROR: Unexpected token in factor: ('SEMI', ';', 3, 9)

Parsed error5.c -> ERROR: Expected identifier after type, got ('INT', '123', 1, 5)

Parsed valid1.c -> OK

Parsed valid2.c -> OK

Parsed valid3.c -> OK

Parsed valid4.c -> OK

Parsed valid5.c -> OK

## 4. Discussão
A implementação do compilador simplificado permitiu observar, na prática, diversos de-
safios típicos das fases iniciais de construção de um compilador. Essa etapa é crucial para
entender como a análise léxica e sintática se complementam, e como decisões na gramática
influenciam diretamente a robustez e a clareza do parser.


Desafios Encontrados

Durante o desenvolvimento, alguns desafios se destacaram:

- Cálculo correto de linha e coluna no lexer. Pequenos desvios no controle da posição do token causaram erros inconsistentes no parser. Foi necessário reestruturar o tratamento de quebras de linha para garantir sincronização entre lexer e parser.

- Reconhecimento preciso de tokens complexos. Operadores compostos como ==, !=, <=, >=, && e || exigiram atenção especial na ordem das expressões regulares, pois operadores de um caractere poderiam capturar incorretamente os compostos.

- Ambiguidade entre declaração e expressão. Um dos maiores desafios foi diferenciar corretamente declarações do tipo:
int a ;
de expressões como:
a = 3;
O parser inicial confundia os dois contextos e tratava atribuições como parte de declarações. A solução foi separar rigidamente as regras da gramática e evitar permitir inicializações dentro de declarações.

- Tratamento da atribuição na expressão. A implementação da regra de atribuição (ID = Expr) exigiu cuidado com associatividade e precedência. A utilização de recursão à direita foi necessária para comportar corretamente expressões como:
a = b = 3;
8
mesmo que a linguagem simplificada não utilize esse padrão.

- Erros sintáticos claros e consistentes. Para facilitar depuração e avaliação, foi preciso padronizar mensagens de erro com o formato: “Expected X but got Y (linha,
coluna)”, possibilitando rastreabilidade e correção rápida.


Limitações e desafios

- Maior esforço de implementação. É necessário escrever e depurar cada regra
individualmente.
- Dificuldade em suportar gramáticas mais complexas. Recursos completos da
linguagem C (como ponteiros, arrays, structs, operadores unários múltiplos) seriam
muito trabalhosos de implementar manualmente.
- Maior suscetibilidade a erros sutis. Um detalhe incorreto na precedência ou
associatividade pode comprometer toda a análise sintática.

## 5. Conclusão
O projeto implementado demonstra de forma prática as etapas iniciais de um compilador:
análise léxica, análise sintática e geração de uma árvore sintática abstrata. Todos os
componentes foram implementados manualmente, o que evidencia a compreensão dos
princípios fundamentais da disciplina.

## Apêndice
- Para rodar o analisador nos exemplos rode:

```
python3 ./run_examples.py
```
