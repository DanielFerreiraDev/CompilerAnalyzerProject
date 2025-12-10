import re
from typing import Tuple

Token = Tuple[str, str, int, int]  # (type, value, line, col)

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text
        self.line = 1
        self.col = 1

    token_specification = [
        ('COMMENT',   r'//.*|/\*[\s\S]*?\*/'),
        ('STRING',    r'"([^"\\]|\\.)*"'),
        ('CHAR',      r"\'([^'\\]|\\.)*\'"),
        ('FLOAT',     r'\d+\.\d+'),
        ('INT',       r'\d+'),
        ('ID',        r'[A-Za-z_][A-Za-z0-9_]*'),
        ('OP',        r'==|!=|<=|>=|\+\+|--|\+|-|\*|/|%|<|>|=|&&|\|\||!'),
        ('SEMI',      r';'),
        ('COMMA',     r','),
        ('LPAREN',    r'\('),
        ('RPAREN',    r'\)'),
        ('LBRACE',    r'\{'),
        ('RBRACE',    r'\}'),
        ('WS',        r'[ \t\r\n]+'),
        ('MISMATCH',  r'.'),
    ]

    tok_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_specification), re.MULTILINE)

    keywords = {
        'int','float','for','if','else','while','return','void'
    }

    def tokenize(self):
        for mo in self.tok_regex.finditer(self.text):
            kind = mo.lastgroup
            value = mo.group(kind)

            # --- whitespace (corrigido) ---
            if kind == 'WS':
                if '\n' in value:
                    qnt = value.count('\n')
                    self.line += qnt

                    # coluna deve ser resetada apenas para o trecho DEPOIS do último '\n'
                    last_nl = value.rfind('\n')

                    # tamanho da parte depois do último '\n'
                    after = value[last_nl+1:]
                    self.col = len(after) + 1  
                else:
                    self.col += len(value)
                continue

            # --- comentários (corrigido igual ao WS) ---
            elif kind == 'COMMENT':
                if '\n' in value:
                    qnt = value.count('\n')
                    self.line += qnt

                    last_nl = value.rfind('\n')
                    after = value[last_nl+1:]
                    self.col = len(after) + 1  
                else:
                    self.col += len(value)
                continue

            elif kind == 'ID' and value in self.keywords:
                kind = value.upper()

            elif kind == 'MISMATCH':
                raise LexerError(f'Unexpected token {value!r} at line {self.line} col {self.col}')

            # gerar token
            tok = (kind, value, self.line, self.col)

            self.col += len(value)
            yield tok
