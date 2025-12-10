from lexer import Lexer, LexerError
from ast_nodes import Node

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.tokens = list(self.lexer.tokenize())
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF','',-1,-1)

    def next(self):
        t = self.peek()
        self.pos += 1
        return t

    def expect(self, kind, value=None):
        tok = self.peek()
        if value is None:
            if tok[0] != kind:
                raise ParseError(f"Expected {kind} but got {tok}")
        else:
            if tok[0] != kind or tok[1] != value:
                raise ParseError(f"Expected {kind} {value} but got {tok}")
        return self.next()

    # --------------------------
    # PROGRAMA
    # --------------------------
    def parse(self):
        program = Node("Program", [])
        while self.peek()[0] != 'EOF':
            decl = self.parse_external_decl()
            program.children.append(decl)
        return program

    # --------------------------
    # DECLARAÇÕES DE TOPO
    # --------------------------
    def parse_external_decl(self):
        tok = self.peek()
        if tok[0] in ('INT','FLOAT','VOID'):
            typ = self.next()[0]
            idt = self.peek()

            if idt[0] != 'ID':
                raise ParseError(f"Expected identifier after type, got {idt}")

            name = self.next()[1]

            # Função?
            if self.peek()[0] == 'LPAREN':
                self.next()
                params = []
                if self.peek()[0] != 'RPAREN':
                    params = self.parse_param_list()
                self.expect('RPAREN')
                body = self.parse_compound_stmt()
                return Node("Function", [
                    Node("Type", value=typ),
                    Node("Name", value=name),
                    Node("Params", children=params),
                    body
                ])

            # Variável global simples
            self.expect('SEMI')
            return Node("GlobalVar", [
                Node("Type", value=typ),
                Node("Name", value=name)
            ])

        else:
            raise ParseError(f"Unexpected token at top-level: {tok}")

    # --------------------------
    # PARÂMETROS
    # --------------------------
    def parse_param_list(self):
        params = []
        while True:
            if self.peek()[0] in ('INT','FLOAT','VOID'):
                typ = self.next()[0]
                name = None
                if self.peek()[0] == 'ID':
                    name = self.next()[1]
                params.append(Node("Param", value={'type': typ, 'name': name}))

            if self.peek()[0] == 'COMMA':
                self.next()
                continue
            break
        return params

    # --------------------------
    # BLOCO
    # --------------------------
    def parse_compound_stmt(self):
        self.expect('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Node("Block", children=stmts)

    # --------------------------
    # STATEMENTS
    # --------------------------
    def parse_statement(self):
        tok = self.peek()

        # declaração simples SEM inicialização
        if tok[0] in ('INT', 'FLOAT'):
            return self.parse_decl_stmt()

        if tok[0] == 'LBRACE':
            return self.parse_compound_stmt()

        if tok[0] == 'IF':
            return self.parse_if()

        if tok[0] == 'WHILE':
            return self.parse_while()

        if tok[0] == 'FOR':
            return self.parse_for()

        if tok[0] == 'RETURN':
            return self.parse_return()

        # expressão isolada (agora parse_assignment suporta '=')
        expr = self.parse_expression()
        self.expect('SEMI')
        return Node("ExprStmt", children=[expr])

    # --------------------------
    # DECLARAÇÃO SEM INICIALIZAÇÃO
    # --------------------------
    def parse_decl_stmt(self):
        typ = self.next()[0]

        name_tok = self.peek()
        if name_tok[0] != 'ID':
            raise ParseError(f"Expected identifier in declaration, got {name_tok}")

        name = self.next()[1]

        # *** REMOVER inicialização dentro da declaração ***
        self.expect('SEMI')

        return Node("Decl", children=[
            Node("Type", value=typ),
            Node("Name", value=name)
        ])

    # --------------------------
    # IF
    # --------------------------
    def parse_if(self):
        self.expect('IF')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        then = self.parse_statement()

        els = None
        if self.peek()[0] == 'ELSE':
            self.next()
            els = self.parse_statement()

        n = Node("If", children=[cond, then])
        if els:
            n.children.append(els)
        return n

    # --------------------------
    # WHILE
    # --------------------------
    def parse_while(self):
        self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_statement()
        return Node("While", children=[cond, body])

    # --------------------------
    # FOR
    # --------------------------
    def parse_for(self):
        self.expect('FOR')
        self.expect('LPAREN')

        init = None
        if self.peek()[0] != 'SEMI':
            init = self.parse_expression()
        self.expect('SEMI')

        cond = None
        if self.peek()[0] != 'SEMI':
            cond = self.parse_expression()
        self.expect('SEMI')

        post = None
        if self.peek()[0] != 'RPAREN':
            post = self.parse_expression()
        self.expect('RPAREN')

        body = self.parse_statement()
        return Node("For", children=[
            init if init else Node("None"),
            cond if cond else Node("None"),
            post if post else Node("None"),
            body
        ])

    # --------------------------
    # RETURN
    # --------------------------
    def parse_return(self):
        self.expect('RETURN')
        if self.peek()[0] == 'SEMI':
            self.next()
            return Node("Return", children=[])

        expr = self.parse_expression()
        self.expect('SEMI')
        return Node("Return", children=[expr])

    # --------------------------
    # EXPRESSÕES
    # --------------------------
    # agora parse_expression chama parse_assignment (para suportar '=')
    def parse_expression(self):
        return self.parse_assignment()

    # assignment (right-associative): a = b = c
    def parse_assignment(self):
        left = self.parse_logical_or()
        # se próximo token for '=' (OP, '='), trata como atribuição
        if self.peek()[0] == 'OP' and self.peek()[1] == '=':
            # somente variáveis (ou chamadas) podem ser atribuídas; permitir Var or Call as LHS
            self.next()  # consome '='
            right = self.parse_assignment()  # right-assoc
            return Node("Assign", children=[left, right], value='=')
        return left

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.peek()[0] == 'OP' and self.peek()[1] == '||':
            op = self.next()[1]
            right = self.parse_logical_and()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.peek()[0] == 'OP' and self.peek()[1] == '&&':
            op = self.next()[1]
            right = self.parse_equality()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('==','!='):
            op = self.next()[1]
            right = self.parse_relational()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('<','>','<=','>='):
            op = self.next()[1]
            right = self.parse_additive()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_additive(self):
        node = self.parse_term()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('+','-'):
            op = self.next()[1]
            right = self.parse_term()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('*','/','%'):
            op = self.next()[1]
            right = self.parse_factor()
            node = Node("BinaryOp", children=[node, right], value=op)
        return node

    def parse_factor(self):
        tok = self.peek()

        if tok[0] == 'LPAREN':
            self.next()
            n = self.parse_expression()
            self.expect('RPAREN')
            return n

        if tok[0] == 'ID':
            name = self.next()[1]
            # chamada de função
            if self.peek()[0] == 'LPAREN':
                self.next()
                args = []
                if self.peek()[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek()[0] == 'COMMA':
                        self.next()
                        args.append(self.parse_expression())
                self.expect('RPAREN')
                return Node("Call", children=args, value=name)

            # variável
            return Node("Var", value=name)

        if tok[0] in ('INT','FLOAT','STRING','CHAR'):
            val = self.next()[1]
            return Node("Literal", value=val)

        # unário
        if tok[0] == 'OP' and tok[1] in ('-','!','++','--'):
            op = self.next()[1]
            r = self.parse_factor()
            return Node("UnaryOp", children=[r], value=op)

        raise ParseError(f"Unexpected token in factor: {tok}")
