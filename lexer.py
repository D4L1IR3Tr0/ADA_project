import ply.lex as lex

# TOKENS
tokens = (
    'IMPORT', 'DOT', 'AS', 'TYPE', 'ID', 'COLON', 'ASSIGN', 
    'INTEGER', 'FLOAT', 'STRING', 'BOOL',
    'LPAREN', 'RPAREN', 'COMMA', 'PLUS', 'PLUSEQUAL', 'MINUS', 'MINUSEQUAL',
    'TIMES', 'TIMEEQUAL', 'DIVIDE', 'DIVIDEEQUAL', 'MODULO',
    'EQUALS', 'NOTEQ', 'LT', 'GT', 'LEQ', 'GEQ', 'AND', 'OR', 'NOT',
    'WRITE', 'IN', 'READ', 'IF', 'ELSE', 'LOOP', 'LBRACK', 'RBRACK',
    'DEFINE', 'OUTPUT', 'COMMENT', 'BLOCK_COMMENT', 'END',
    'RANGE', 'FILE', 'MAKE'
)

# RESERVED
reserved = {
    'int': 'TYPE',
    'float': 'TYPE',
    'bool': 'TYPE',
    'string': 'TYPE',
    'double': 'TYPE',
    'as': 'AS',
    'in': 'IN',
    'if': 'IF',
    'else': 'ELSE',
    'loop': 'LOOP',
    'define': 'DEFINE',
    'out': 'OUTPUT',
    'make': 'MAKE'
}

# DEFINITIONS
t_IMPORT = r'@import'
t_MAKE = r'make'
t_DOT = r'\.'
t_COLON = r':'
t_ASSIGN = r'<-'
t_STRING = r'"([^"\\]|\\.)*"'
t_INTEGER = r'\d+'
t_FLOAT = r'\d*\.\d+'
t_BOOL = r'(?i)(true|false)'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_PLUS = r'\+'
t_MINUS = r'-'
t_PLUSEQUAL = r'\+='
t_MINUSEQUAL = r'-='
t_MODULO = r'%'
t_TIMES = r'\*'
t_TIMEEQUAL = r'\*='
t_DIVIDE = r'/'
t_DIVIDEEQUAL = r'/='
t_EQUALS = r'=='
t_NOTEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_WRITE = r'write'
t_READ = r'read'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_END = r'\/\.'

# RULES
def t_RANGE(t):
    r'\.\.(?!\.)'
    return t

def t_FILE(t):
    r'[a-zA-Z0-9_]+\.(ada|txt|log|csv|json|xml|md|py)'
    return t

# Rule for identifiers
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') 
    return t

# Comments
def t_COMMENT(t):
    r'--[^\n]*'
    pass 

def t_BLOCK_COMMENT(t):
    r'-\*(.|\n)*?\*-'
    t.lexer.lineno += t.value.count('\n') 
    pass 


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Lexing error at line {t.lineno}, position {t.lexpos}: illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# BUILD
lexer = lex.lex()


def test_lexer():
    data = """
    -- Gestion des importation avec gestiob des erruers exemple Erreur : Le module <math.ada> est introuvable.--
    @import <math.ada> as math

    x <- math.square(4)  -- Appelle la fonction square du module math.ada


    -- Déclaration de variables --
    int x <- 1
    string y <- "abc"
    bool b <- true
    double d <- 3.16

    int tab <- [1, 2, 3, 4, 5]

    -- Définition d'un type simple --
    type newStructure:
        int arg1
        int arg2
        int arg3
        define myfun():
            write("")
    /.

    -- Les operateur --
    -- logiques && || == ! != --
    -- mathematiques + - * / % < > <= >=--
    -- la concatenation + --

    -- Conversion simple --
    int x <- convert(y, int)  -- Convertit "abc" en int (ou retourne une valeur par défaut) --
    write(x)

    -- Lecture de l'entrée de l'utilisateur --
    z <- read("Entrez Z :")

    -- Affectations et opérations --
    a <- 2
    b <- 3

    a <- b
    a += 1

    write(a)  -- Affiche la valeur de a --
    write(a + x)  -- Affiche a + x --

    -- Définition de fonctions simples --

    define add(a, b):
        out(a + b)
    /.

    define add(a, b<-5):
        out(a + b)
    /.


    write(add(10, 12))

    -- Structure conditionnelle simple --
    if (a == 1 && b < 10):
        write("OK")
    else:
        write("not OK")
    /.

    -- Boucles simples --
    loop [0..10]:
        write("hello")
    /.

    loop c in [0..10]:
        write(c)
    /.

    loop c in tab:
        write(c)
    /.

    loop (b < 5):
        write(b)
        b += 1
    /.

    -- Commentaires --
    -- Ceci est un commentaire --
    -* Ceci est un commentaire
        sur plusueurs lignes *-
        """

    lexer.input(data)
    for tok in lexer:
        print(tok)
        
        
    test_lexer()