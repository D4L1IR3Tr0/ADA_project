import ply.yacc as yacc
from lexer import tokens, lexer

def clean_input(data):
    """Remove leading/trailing whitespace and normalize indentation."""
    lines = []
    for line in data.split('\n'):
        stripped = line.strip()
        if stripped:  # Only keep non-empty lines
            lines.append(stripped)
    return '\n'.join(lines)

class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = children if children is not None else []
        self.leaf = leaf
        self.parent = None
        # Set parent for all children
        for child in self.children:
            if isinstance(child, Node):
                child.parent = self
        
    def __str__(self, level=0):
        ret = "  " * level + f"Type: {self.type}"
        if self.leaf is not None:
            ret += f" | Leaf: {self.leaf}"
        ret += "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

# Precedence rules
precedence = (
    ('nonassoc', 'LOWER_THAN_ELSE'),
    ('nonassoc', 'ELSE'),
    ('right', 'ASSIGN', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMEEQUAL', 'DIVIDEEQUAL'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQUALS', 'NOTEQ', 'LT', 'GT', 'LEQ', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'NOT'),
    ('left', 'DOT'),
    ('left', 'LBRACK', 'RBRACK'),
    ('left', 'LPAREN', 'RPAREN')
)

# Grammar rules
def p_program(p):
    '''program : statement_sequence'''
    p[0] = Node('Program', [p[1]])

def p_statement_sequence(p):
    '''statement_sequence : statement statement_sequence
                        | statement'''
    if len(p) == 3:
        if p[2] is None:
            p[0] = Node('Statements', [p[1]])
        else:
            p[0] = Node('Statements', [p[1], p[2]])
    else:
        p[0] = Node('Statements', [p[1]])

def p_statement(p):
    '''statement : simple_statement
                | compound_statement
                | comment_statement'''
    p[0] = p[1]

def p_simple_statement(p):
    '''simple_statement : import_statement
                       | declaration
                       | assignment
                       | function_call_statement
                       | write_statement
                       | read_statement
                       | output_statement'''
    p[0] = p[1]

def p_function_call_statement(p):
    '''function_call_statement : function_call
                              | method_call'''
    p[0] = p[1]

def p_compound_statement(p):
    '''compound_statement : make_statement
                        | define_statement
                        | if_statement
                        | loop_statement'''
    p[0] = p[1]

def p_comment_statement(p):
    '''comment_statement : COMMENT
                       | BLOCK_COMMENT'''
    p[0] = Node('Comment', [], p[1])

def p_import_statement(p):
    '''import_statement : IMPORT LT FILE GT AS ID
                       | IMPORT LT FILE GT'''
    if len(p) == 7:
        p[0] = Node('Import', [], {'file': p[3], 'alias': p[6]})
    else:
        p[0] = Node('Import', [], {'file': p[3]})

def p_make_statement(p):
    '''make_statement : MAKE ID COLON struct_body END'''
    p[0] = Node('MakeType', [p[4]], {'name': p[2]})

def p_struct_body(p):
    '''struct_body : struct_members'''
    p[0] = p[1]

def p_struct_members(p):
    '''struct_members : struct_member struct_members
                     | struct_member'''
    if len(p) == 3:
        if isinstance(p[2], Node):
            p[2].children.insert(0, p[1])
            p[0] = p[2]
        else:
            p[0] = Node('StructMembers', [p[1], p[2]])
    else:
        p[0] = Node('StructMembers', [p[1]])

def p_struct_member(p):
    '''struct_member : TYPE ID'''
    p[0] = Node('StructMember', [], {'type': p[1], 'name': p[2]})

def p_declaration(p):
    '''declaration : TYPE ID ASSIGN expression
                  | TYPE ID
                  | ID ID ASSIGN expression
                  | ID ID'''
    if len(p) == 5:
        p[0] = Node('Declaration', [], {'type': p[1], 'id': p[2], 'value': p[4]})
    elif len(p) == 3:
        p[0] = Node('Declaration', [], {'type': p[1], 'id': p[2]})

def p_define_statement(p):
    '''define_statement : DEFINE ID LPAREN param_list RPAREN COLON statement_sequence END'''
    p[0] = Node('Define', [p[4], p[7]], {'name': p[2]})

def p_param_list(p):
    '''param_list : param_sequence
                 | empty'''
    p[0] = p[1]

def p_param_sequence(p):
    '''param_sequence : param COMMA param_sequence
                     | param'''
    if len(p) == 4:
        if isinstance(p[3], Node) and p[3].type == 'Parameters':
            p[3].children.insert(0, p[1])
            p[0] = p[3]
        else:
            p[0] = Node('Parameters', [p[1], p[3]])
    else:
        p[0] = Node('Parameters', [p[1]])

def p_param(p):
    '''param : ID
            | ID ASSIGN expression'''
    if len(p) == 4:
        p[0] = Node('Parameter', [], {'id': p[1], 'default': p[3]})
    else:
        p[0] = Node('Parameter', [], {'id': p[1]})

def p_empty(p):
    '''empty :'''
    p[0] = Node('Empty')

def p_assignment(p):
    '''assignment : ID ASSIGN expression
                 | ID compound_assignment expression
                 | array_access ASSIGN expression
                 | ID DOT ID ASSIGN expression'''
    if len(p) == 6:  # ID DOT ID ASSIGN expression
        p[0] = Node('MemberAssignment', [], {
            'object': p[1],
            'member': p[3],
            'value': p[5]
        })
    elif isinstance(p[1], Node):  # array access
        p[0] = Node('ArrayAssignment', [p[1], p[3]])
    elif p[2] == '<-':
        p[0] = Node('Assignment', [], {'id': p[1], 'value': p[3]})
    else:
        p[0] = Node('CompoundAssignment', [], {'id': p[1], 'operator': p[2], 'value': p[3]})

def p_compound_assignment(p):
    '''compound_assignment : PLUSEQUAL
                         | MINUSEQUAL
                         | TIMEEQUAL
                         | DIVIDEEQUAL'''
    p[0] = p[1]

def p_expression(p):
    '''expression : or_expr'''
    p[0] = p[1]

def p_or_expr(p):
    '''or_expr : or_expr OR and_expr
               | and_expr'''
    if len(p) == 4:
        p[0] = Node('BinaryOp', [p[1], p[3]], {'operator': p[2]})
    else:
        p[0] = p[1]

def p_and_expr(p):
    '''and_expr : and_expr AND comparison_expr
                | comparison_expr'''
    if len(p) == 4:
        p[0] = Node('BinaryOp', [p[1], p[3]], {'operator': p[2]})
    else:
        p[0] = p[1]

def p_comparison_expr(p):
    '''comparison_expr : additive_expr comparison_op additive_expr
                      | additive_expr'''
    if len(p) == 4:
        p[0] = Node('BinaryOp', [p[1], p[3]], {'operator': p[2]})
    else:
        p[0] = p[1]

def p_comparison_op(p):
    '''comparison_op : EQUALS
                    | NOTEQ
                    | LT
                    | GT
                    | LEQ
                    | GEQ'''
    p[0] = p[1]

def p_additive_expr(p):
    '''additive_expr : additive_expr PLUS multiplicative_expr
                    | additive_expr MINUS multiplicative_expr
                    | multiplicative_expr'''
    if len(p) == 4:
        p[0] = Node('BinaryOp', [p[1], p[3]], {'operator': p[2]})
    else:
        p[0] = p[1]

def p_multiplicative_expr(p):
    '''multiplicative_expr : multiplicative_expr TIMES unary_expr
                         | multiplicative_expr DIVIDE unary_expr
                         | multiplicative_expr MODULO unary_expr
                         | unary_expr'''
    if len(p) == 4:
        p[0] = Node('BinaryOp', [p[1], p[3]], {'operator': p[2]})
    else:
        p[0] = p[1]

def p_unary_expr(p):
    '''unary_expr : MINUS primary %prec UMINUS
                  | NOT primary
                  | primary'''
    if len(p) == 3:
        p[0] = Node('UnaryOp', [p[2]], {'operator': p[1]})
    else:
        p[0] = p[1]

def p_primary(p):
    '''primary : atom
               | LPAREN expression RPAREN'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_atom(p):
    '''atom : INTEGER
           | FLOAT
           | STRING
           | BOOL
           | ID
           | ID DOT ID
           | array_access
           | function_call_or_instantiation
           | method_call
           | array_literal'''
    if isinstance(p[1], Node):
        p[0] = p[1]
    elif isinstance(p[1], str) and len(p) == 4:  # ID DOT ID
        p[0] = Node('MemberAccess', [], {'object': p[1], 'member': p[3]})
    elif isinstance(p[1], str):
        if p[1].startswith('"') or p[1].isdigit() or p[1].lower() in ['true', 'false']:
            p[0] = Node('Literal', [], p[1])
        else:
            p[0] = Node('Identifier', [], p[1])
    else:
        p[0] = Node('Literal', [], p[1])

def p_function_call_or_instantiation(p):
    '''function_call_or_instantiation : ID LPAREN argument_list RPAREN'''
    # Si l'ID correspond à un type défini, c'est une instantiation
    # Sinon c'est un appel de fonction
    # Cette logique sera gérée dans l'interpréteur
    p[0] = Node('CallOrInstantiation', [], {
        'id': p[1],
        'arguments': p[3]
    })

def p_array_literal(p):
    '''array_literal : LBRACK array_elements RBRACK
                    | LBRACK RBRACK'''
    if len(p) == 4:
        p[0] = Node('ArrayLiteral', [p[2]])
    else:
        p[0] = Node('ArrayLiteral', [])

def p_array_elements(p):
    '''array_elements : expression COMMA array_elements
                     | expression'''
    if len(p) == 4:
        p[0] = Node('ArrayElements', [p[1], p[3]])
    else:
        p[0] = Node('ArrayElements', [p[1]])

def p_array_access(p):
    '''array_access : ID LBRACK expression RBRACK'''
    p[0] = Node('ArrayAccess', [p[3]], {'array': p[1]})

def p_function_call(p):
    '''function_call : ID LPAREN argument_list RPAREN'''
    p[0] = Node('FunctionCall', [], {'function': p[1], 'arguments': p[3]})

def p_method_call(p):
    '''method_call : ID DOT ID LPAREN argument_list RPAREN'''
    p[0] = Node('MethodCall', [], {'object': p[1], 'method': p[3], 'arguments': p[5]})

def p_argument_list(p):
    '''argument_list : argument_sequence
                    | empty'''
    p[0] = p[1]

def p_argument_sequence(p):
    '''argument_sequence : expression COMMA argument_sequence
                       | expression'''
    if len(p) == 4:
        p[0] = Node('Arguments', [p[1], p[3]])
    else:
        p[0] = Node('Arguments', [p[1]])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN COLON statement_sequence END %prec LOWER_THAN_ELSE
                   | IF LPAREN expression RPAREN COLON statement_sequence ELSE COLON statement_sequence END'''
    if len(p) == 8:
        p[0] = Node('If', [p[3], p[6]])
    else:
        p[0] = Node('If', [p[3], p[6], p[9]])

def p_loop_statement(p):
    '''loop_statement : LOOP LBRACK expression RANGE expression RBRACK COLON statement_sequence END
                     | LOOP ID IN LBRACK expression RANGE expression RBRACK COLON statement_sequence END
                     | LOOP ID IN ID COLON statement_sequence END
                     | LOOP LPAREN expression RPAREN COLON statement_sequence END'''
    if len(p) == 10:
        p[0] = Node('RangeLoop', [p[3], p[5], p[8]])
    elif len(p) == 12:
        p[0] = Node('RangeLoop', [p[5], p[7], p[10]], {'iterator': p[2]})
    elif len(p) == 8:
        if p[1] == 'loop' and p[3] == 'in':
            p[0] = Node('ForEachLoop', [p[6]], {'iterator': p[2], 'iterable': p[4]})
        else:
            p[0] = Node('WhileLoop', [p[3], p[6]])

def p_write_statement(p):
    '''write_statement : WRITE LPAREN expression RPAREN'''
    p[0] = Node('Write', [p[3]])

def p_read_statement(p):
    '''read_statement : READ LPAREN expression RPAREN'''
    p[0] = Node('Read', [p[3]])

def p_output_statement(p):
    '''output_statement : OUTPUT LPAREN expression RPAREN'''
    p[0] = Node('Output', [p[3]])

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} (value: {p.value}) on line {p.lineno}, position {p.lexpos}")
        if hasattr(p.lexer, 'lexdata'):
            lines = p.lexer.lexdata.splitlines()
            if p.lineno <= len(lines):
                print(f"Line content: {lines[p.lineno-1]}")
                print("Token stream:")
                lexer.input(lines[p.lineno-1])
                for tok in lexer:
                    print(f"  {tok}")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc(debug=True)

#def parse(data):
#    """Parse the input after cleaning it."""
#    try:
#        cleaned_data = clean_input(data)
#        return parser.parse(cleaned_data, lexer=lexer)
#    except Exception as e:
#        print(f"Parsing error: {str(e)}")
#        return None
#


def parse(data):
    """Parse the input after cleaning it."""
    cleaned_data = clean_input(data)
    return parser.parse(cleaned_data, lexer=lexer)

# Test code
if __name__ == "__main__":
    test_input = """
    make person:
        int age
        string name
    /.
    
    person p <- person(25, "Alice")
    write(p.name)
    write(p.age)
    
    person p2
    p2.age <- read("Enter age: ")
    p2.name <- read("Enter name: ")
    write(p2.name)
    write(p2.age)
    """
    print("\nParser output:")
    result = parse(test_input)
    print(result)