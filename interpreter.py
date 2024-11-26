from parser import parse, Node
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import operator
from enum import Enum
import sys
import os

class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    DOUBLE = "double"
    ARRAY = "array"
    VOID = "void"
    STRUCT = "struct"

@dataclass
class Value:
    type: DataType
    value: Any

class Environment:
    def __init__(self, parent=None):
        self.values: Dict[str, Value] = {}
        self.parent = parent
        self.return_value = None
        self.functions = {}
        self.struct_types = {}
        
    def get(self, name: str) -> Optional[Value]:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not found")
    
    def set(self, name: str, value: Value):
        env = self
        while env.parent is not None:
            if name in env.values:
                env.values[name] = value
                return
            env = env.parent
        self.values[name] = value
        
    def define_function(self, name: str, func):
        self.functions[name] = func
        
    def get_function(self, name: str):
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        raise NameError(f"Function '{name}' not found")

    def define_struct(self, name: str, members: dict):
        self.struct_types[name] = members

    def get_struct(self, name: str):
        if name in self.struct_types:
            return self.struct_types[name]
        if self.parent:
            return self.parent.struct_types.get(name)
        return None

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.setup_builtins()
        
    def setup_builtins(self):
        def write_fn(args):
            print(self.convert_to_string(args[0]))
            return Value(DataType.VOID, None)
            
        def read_fn(args):
            prompt = self.convert_to_string(args[0])
            val = input(prompt)
            try:
                return Value(DataType.INT, int(val))
            except ValueError:
                return Value(DataType.STRING, val)
            
        def convert_fn(args):
            value, target_type = args
            if isinstance(target_type, Value):
                target_type = target_type.value
            if target_type == "int":
                try:
                    return Value(DataType.INT, int(float(value.value)))
                except (ValueError, TypeError):
                    return Value(DataType.INT, 0)
                
        # Fonctions de gestion de fichiers
        def internal_exists(args):
            path = self.convert_to_string(args[0]).strip('"')  # Enlever les guillemets
            return Value(DataType.BOOL, os.path.exists(path))
        
        def internal_write_file(args):
            try:
                path = self.convert_to_string(args[0]).strip('"')
                content = self.convert_to_string(args[1])
                with open(path, 'w') as f:
                    f.write(content)
                return Value(DataType.BOOL, True)
            except Exception as e:
                print(f"Error writing to file: {str(e)}")
                return Value(DataType.BOOL, False)

        def internal_read_file(args):
            try:
                path = self.convert_to_string(args[0]).strip('"')
                with open(path, 'r') as f:
                    content = f.read()
                return Value(DataType.STRING, content)
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                return Value(DataType.STRING, "")
        
        def internal_append_file(args):
            try:
                path = self.convert_to_string(args[0]).strip('"')
                content = self.convert_to_string(args[1])
                with open(path, 'a') as f:
                    f.write(content)
                return Value(DataType.BOOL, True)
            except Exception as e:
                print(f"Error appending to file: {str(e)}")
                return Value(DataType.BOOL, False)

        def internal_open(args):
            try:
                path = self.convert_to_string(args[0]).strip('"')
                mode = self.convert_to_string(args[1]).strip('"')
                # Ouvrir le fichier avec le bon mode
                file = open(path, mode)
                return Value(DataType.INT, file.fileno())
            except Exception as e:
                print(f"Error opening file: {str(e)}")
                return Value(DataType.INT, -1)

        def internal_create(args):
            path = self.convert_to_string(args[0]).strip('"')  # Enlever les guillemets
            try:
                with open(path, 'w') as f:
                    pass
                return Value(DataType.INT, os.open(path, os.O_RDWR))
            except Exception as e:
                print(f"Error creating file: {str(e)}")  # Debug
                return Value(DataType.INT, -1)

        def internal_write(args):
           try:
               fd = args[0].value
               data = self.convert_to_string(args[1])
               with os.fdopen(fd, 'w') as f:
                   f.write(data)
               return Value(DataType.BOOL, True)
           except Exception as e:
               print(f"Error writing to file: {str(e)}")
               return Value(DataType.BOOL, False)

        def internal_read_all(args):
            try:
                fd = args[0].value
                with os.fdopen(fd, 'r') as f:
                    content = f.read()
                return Value(DataType.STRING, content)
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                return Value(DataType.STRING, "")

        def internal_close(args):
            try:
                handle = args[0].value
                if isinstance(handle, int) and handle >= 0:
                    os.close(handle)
                    return Value(DataType.BOOL, True)
                return Value(DataType.BOOL, False)
            except Exception as e:
                print(f"Error closing file: {str(e)}")
                return Value(DataType.BOOL, False)

        def internal_delete(args):
            path = self.convert_to_string(args[0]).strip('"')  # Enlever les guillemets
            try:
                os.remove(path)
                return Value(DataType.BOOL, True)
            except Exception as e:
                print(f"Error deleting file: {str(e)}")  # Debug
                return Value(DataType.BOOL, False)

        def internal_size(args):
            path = self.convert_to_string(args[0]).strip('"')  # Enlever les guillemets
            try:
                size = os.path.getsize(path)
                return Value(DataType.INT, size)
            except Exception as e:
                print(f"Error getting file size: {str(e)}")  # Debug
                return Value(DataType.INT, -1)
            
        def size_fn(args):
            arg = args[0]
            if arg.type == DataType.ARRAY:
                return Value(DataType.INT, len(arg.value))
            elif arg.type == DataType.STRING:
                # Enlever les guillemets si présents
                val = arg.value
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                return Value(DataType.INT, len(val))
            else:
                raise TypeError("size() requires a string or array argument")


        # Enregistrement des fonctions
        self.global_env.define_function("size", size_fn)
        self.global_env.define_function("__internal_exists", internal_exists)
        self.global_env.define_function("__internal_open", internal_open)
        self.global_env.define_function("__internal_close", internal_close)
        self.global_env.define_function("__internal_write", internal_write)
        self.global_env.define_function("__internal_write_file", internal_write_file)
        self.global_env.define_function("__internal_read_file", internal_read_file)
        self.global_env.define_function("__internal_append_file", internal_append_file)
        self.global_env.define_function("__internal_read_all", internal_read_all)
        self.global_env.define_function("__internal_create", internal_create)
        self.global_env.define_function("__internal_delete", internal_delete)
        self.global_env.define_function("__internal_size", internal_size)
                    
        self.global_env.define_function("write", write_fn)
        self.global_env.define_function("read", read_fn)
        self.global_env.define_function("convert", convert_fn)

    def convert_to_string(self, value: Value) -> str:
        if value.type == DataType.STRING:
            # Enlever les guillemets si présents
            val = value.value
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            return val
        elif value.type == DataType.BOOL:
            return str(value.value).lower()
        return str(value.value)

    def visit(self, node):
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.visit_unknown)
        return visitor(node)
        
    def visit_unknown(self, node):
        raise Exception(f"Unknown node type: {node.type}")

    def visit_Program(self, node):
        return self.visit(node.children[0])

    def visit_Statements(self, node):
        result = None
        for child in node.children:
            result = self.visit(child)
            if self.current_env.return_value is not None:
                break
        return result

    def visit_MakeType(self, node):
        struct_name = node.leaf['name']
        members = {}
        
        for member_node in node.children[0].children:
            member_type = member_node.leaf['type']
            member_name = member_node.leaf['name']
            members[member_name] = member_type
            
        self.current_env.define_struct(struct_name, members)
        return Value(DataType.VOID, None)

    def visit_Import(self, node):
        filename = node.leaf['file']
        alias = node.leaf.get('alias', filename.split('.')[0])

        try:
            with open(filename, 'r') as file:
                content = file.read()

            # Créer un nouvel environnement pour le module
            module_env = Environment(self.current_env)
            ast = parse(content)

            # Sauvegarder l'environnement actuel
            prev_env = self.current_env
            self.current_env = module_env

            # Exécuter le module
            self.visit(ast)

            # Restaurer l'environnement précédent
            self.current_env = prev_env

            # Ajouter le module à l'environnement courant
            self.current_env.values[alias] = Value(DataType.VOID, module_env)

        except FileNotFoundError:
            raise ImportError(f"Module '{filename}' not found")
        
    def visit_MethodCall(self, node):
        obj_name = node.leaf['object']
        method_name = node.leaf['method']
        obj = self.current_env.get(obj_name)
        arguments = []

        # Récupérer les arguments
        if isinstance(node.leaf['arguments'], Node):
            arg_node = node.leaf['arguments']
            while arg_node.type == 'Arguments' and arg_node.children:
                arguments.insert(0, self.visit(arg_node.children[0]))
                if len(arg_node.children) > 1:
                    arg_node = arg_node.children[1]
                else:
                    break
                
        # Vérifier que l'objet est un module ou une structure
        if not isinstance(obj.value, (Environment, dict)):
            raise TypeError(f"Object '{obj_name}' is not a module or struct")

        # Si c'est un module, appeler la fonction du module
        if isinstance(obj.value, Environment):
            method = obj.value.get_function(method_name)
            return method(arguments)

        # Si c'est une structure, accéder au membre
        else:
            if method_name not in obj.value:
                raise AttributeError(f"'{obj_name}' has no attribute '{method_name}'")
            return obj.value[method_name]
        
    def visit_CompoundAssignment(self, node):
        name = node.leaf['id']
        current = self.current_env.get(name)
        value = self.visit(node.leaf['value'])

        ops = {
            '+=': operator.add,
            '-=': operator.sub,
            '*=': operator.mul,
            '/=': operator.truediv,
        }

        op = ops[node.leaf['operator']]

        # Effectuer l'opération
        if current.type in [DataType.INT, DataType.FLOAT, DataType.DOUBLE]:
            result_value = op(current.value, value.value)
            # Conserver le type de la variable originale
            result = Value(current.type, result_value)
            self.current_env.set(name, result)
            return result
        else:
            raise TypeError(f"Compound assignment not supported for type {current.type}")

    def visit_Declaration(self, node):
        name = node.leaf['id']
        declared_type = node.leaf['type']
        
        struct_type = self.current_env.get_struct(declared_type)
        if struct_type:
            if 'value' in node.leaf:
                value = self.visit(node.leaf['value'])
                self.current_env.set(name, value)
            else:
                instance = {}
                for member_name, member_type in struct_type.items():
                    instance[member_name] = self.get_default_value(member_type)
                self.current_env.set(name, Value(DataType.STRUCT, instance))
            return

        if 'value' in node.leaf:
            value = self.visit(node.leaf['value'])
            self.current_env.set(name, value)
        else:
            self.current_env.set(name, self.get_default_value(declared_type))

    def visit_Assignment(self, node):
        if isinstance(node.leaf, dict):
            name = node.leaf['id']
            value = self.visit(node.leaf['value'])
            self.current_env.set(name, value)
            return value
        else:
            target = self.visit(node.children[0])
            value = self.visit(node.children[1])
            return value

    def visit_MemberAccess(self, node):
        obj_name = node.leaf['object']
        member_name = node.leaf['member']
        
        obj = self.current_env.get(obj_name)
        if obj.type != DataType.STRUCT:
            raise TypeError(f"Cannot access member of non-struct value")
            
        if member_name not in obj.value:
            raise AttributeError(f"Struct has no member '{member_name}'")
            
        return obj.value[member_name]

    def visit_MemberAssignment(self, node):
        obj_name = node.leaf['object']
        member_name = node.leaf['member']
        value = self.visit(node.leaf['value'])
        
        obj = self.current_env.get(obj_name)
        if obj.type != DataType.STRUCT:
            raise TypeError(f"Cannot assign to member of non-struct value")
            
        if member_name not in obj.value:
            raise AttributeError(f"Struct has no member '{member_name}'")
            
        obj.value[member_name] = value
        return value

    def visit_CallOrInstantiation(self, node):
        id_name = node.leaf['id']
        arguments = []
        
        if isinstance(node.leaf['arguments'], Node):
            arg_node = node.leaf['arguments']
            while arg_node.type == 'Arguments' and arg_node.children:
                arguments.insert(0, self.visit(arg_node.children[0]))
                if len(arg_node.children) > 1:
                    arg_node = arg_node.children[1]
                else:
                    break
        
        struct_type = self.current_env.get_struct(id_name)
        if struct_type:
            if len(arguments) != len(struct_type):
                raise TypeError(f"Expected {len(struct_type)} arguments for struct '{id_name}', got {len(arguments)}")
                
            instance = {}
            for (member_name, member_type), value in zip(struct_type.items(), arguments):
                instance[member_name] = value
                
            return Value(DataType.STRUCT, instance)
        
        try:
            func = self.current_env.get_function(id_name)
            return func(arguments)
        except NameError:
            raise NameError(f"'{id_name}' is neither a struct type nor a function")

    def visit_BinaryOp(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])

        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '%': operator.mod,
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '>': operator.gt,
            '<=': operator.le,
            '>=': operator.ge,
            '&&': lambda x, y: x and y,
            '||': lambda x, y: x or y,
        }

        # Gestion spéciale pour la concaténation de chaînes
        if node.leaf['operator'] == '+' and (left.type == DataType.STRING or right.type == DataType.STRING):
            # Convertir les valeurs en chaînes
            left_str = self.convert_to_string(left)
            right_str = self.convert_to_string(right)

            # Si la chaîne est entre guillemets, les enlever
            if left_str.startswith('"') and left_str.endswith('"'):
                left_str = left_str[1:-1]
            if right_str.startswith('"') and right_str.endswith('"'):
                right_str = right_str[1:-1]

            return Value(DataType.STRING, f'"{left_str}{right_str}"')

        # Pour les autres opérations
        op = ops[node.leaf['operator']]
        result = op(left.value, right.value)

        # Déterminer le type du résultat
        if isinstance(result, bool):
            return Value(DataType.BOOL, result)
        elif isinstance(result, int):
            return Value(DataType.INT, result)
        elif isinstance(result, float):
            return Value(DataType.FLOAT, result)
        return Value(DataType.STRING, str(result))


    def visit_Function(self, node):
        func_name = node.leaf['function']
        arguments = []

        if isinstance(node.leaf['arguments'], Node):
            arg_node = node.leaf['arguments']
            while arg_node.type == 'Arguments' and arg_node.children:
                arguments.insert(0, self.visit(arg_node.children[0]))
                if len(arg_node.children) > 1:
                    arg_node = arg_node.children[1]
                else:
                    break

        func = self.current_env.get_function(func_name)
        return func(arguments)

    def visit_FunctionCall(self, node):
        func_name = node.leaf['function']
        arguments = []

        if isinstance(node.leaf['arguments'], Node):
            arg_node = node.leaf['arguments']
            while arg_node.type == 'Arguments' and arg_node.children:
                arguments.insert(0, self.visit(arg_node.children[0]))
                if len(arg_node.children) > 1:
                    arg_node = arg_node.children[1]
                else:
                    break

        func = self.current_env.get_function(func_name)
        return func(arguments)

    def visit_Arguments(self, node):
        result = []
        for child in node.children:
            result.append(self.visit(child))
        return result

    def visit_Comment(self, node):
        return Value(DataType.VOID, None)

    def visit_ArrayAccess(self, node):
        array = self.current_env.get(node.leaf['array'])
        index = self.visit(node.children[0])

        if array.type != DataType.ARRAY:
            raise TypeError("Cannot index non-array value")

        if not isinstance(index.value, int):
            raise TypeError("Array index must be an integer")

        if index.value < 0 or index.value >= len(array.value):
            raise IndexError("Array index out of bounds")

        return Value(array.type, array.value[index.value])

    def visit_ArrayElements(self, node):
        elements = []
        for child in node.children:
            elements.append(self.visit(child))
        return Value(DataType.ARRAY, elements)

    def visit_Empty(self, node):
        return Value(DataType.VOID, None)
    
    def visit_UnaryOp(self, node):
        operand = self.visit(node.children[0])
        
        if node.leaf['operator'] == '-':
            return Value(operand.type, -operand.value)
        elif node.leaf['operator'] == '!':
            return Value(DataType.BOOL, not operand.value)
            
        return operand

    def visit_If(self, node):
        condition = self.visit(node.children[0])
        
        if condition.value:
            return self.visit(node.children[1])
        elif len(node.children) > 2:
            return self.visit(node.children[2])

    def visit_RangeLoop(self, node):
        start = self.visit(node.children[0])
        end = self.visit(node.children[1])
        
        if 'iterator' in node.leaf:
            iterator_name = node.leaf['iterator']
            for i in range(int(start.value), int(end.value) + 1):
                self.current_env.set(iterator_name, Value(DataType.INT, i))
                self.visit(node.children[2])
        else:
            for i in range(int(start.value), int(end.value) + 1):
                self.visit(node.children[2])

    def visit_WhileLoop(self, node):
        while self.visit(node.children[0]).value:
            self.visit(node.children[1])

    def visit_ForEachLoop(self, node):
        iterator_name = node.leaf['iterator']
        iterable = self.current_env.get(node.leaf['iterable'])
        
        if iterable.type == DataType.ARRAY:
            for item in iterable.value:
                self.current_env.set(iterator_name, Value(DataType.INT, item))
                self.visit(node.children[0])

    def visit_Define(self, node):
        func_name = node.leaf['name']

        def function(args):
            new_env = Environment(self.current_env)

            # Traitement des paramètres
            param_node = node.children[0]
            if param_node.type == 'Parameters':
                for i, param in enumerate(param_node.children):
                    param_type = param.leaf['type']
                    param_name = param.leaf['id']

                    if i >= len(args):
                        if 'default' in param.leaf:
                            # Utiliser la valeur par défaut
                            value = self.visit(param.leaf['default'])
                        else:
                            raise TypeError(f"Missing argument for parameter {param_name}")
                    else:
                        value = args[i]

                    # Vérifier le type pour les structures
                    if param_type not in ['int', 'string', 'bool', 'float', 'double']:
                        struct_type = self.current_env.get_struct(param_type)
                        if struct_type is None:
                            raise TypeError(f"Unknown type: {param_type}")
                        if value.type != DataType.STRUCT:
                            raise TypeError(f"Parameter {param_name} must be of type {param_type}")

                    new_env.set(param_name, value)

            # Exécuter le corps de la fonction
            prev_env = self.current_env
            self.current_env = new_env
            result = self.visit(node.children[1])
            self.current_env = prev_env
            return result

        self.current_env.define_function(func_name, function)

    def visit_Output(self, node):
        value = self.visit(node.children[0])
        return value

    def visit_Write(self, node):
        value = self.visit(node.children[0])
        print(self.convert_to_string(value))
        return Value(DataType.VOID, None)

    def visit_Read(self, node):
        prompt = self.visit(node.children[0])
        return Value(DataType.STRING, input(self.convert_to_string(prompt)))

    def visit_ArrayLiteral(self, node):
        if not node.children:
            return Value(DataType.ARRAY, [])

        elements = []
        array_elements = node.children[0]

        # Parcourir tous les enfants du noeud ArrayElements
        for child in array_elements.children:
            element = self.visit(child)
            elements.append(element.value)  # Ajouter à la fin au lieu d'insérer au début

        return Value(DataType.ARRAY, elements)

    def visit_Identifier(self, node):
        return self.current_env.get(node.leaf)

    def visit_Literal(self, node):
        value = node.leaf
        if isinstance(value, str):
            if value.startswith('"') and value.endswith('"'):
                return Value(DataType.STRING, value)
            elif value.lower() == 'true':
                return Value(DataType.BOOL, True)
            elif value.lower() == 'false':
                return Value(DataType.BOOL, False)
            try:
                return Value(DataType.INT, int(value))
            except ValueError:
                try:
                    return Value(DataType.FLOAT, float(value))
                except ValueError:
                    return Value(DataType.STRING, value)
        elif isinstance(value, (int, float)):
            return Value(DataType.INT if isinstance(value, int) else DataType.FLOAT, value)
        return Value(DataType.STRING, str(value))

    def get_default_value(self, type_name):
        defaults = {
            'int': Value(DataType.INT, 0),
            'float': Value(DataType.FLOAT, 0.0),
            'string': Value(DataType.STRING, ""),
            'bool': Value(DataType.BOOL, False),
            'double': Value(DataType.DOUBLE, 0.0)
        }
        return defaults.get(type_name, Value(DataType.VOID, None))

def execute(ast):
    interpreter = Interpreter()
    return interpreter.visit(ast)

def run_ada_file(filename):
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
            
        ast = parse(source_code)
        if ast is None:
            print(f"Error: Failed to parse {filename}")
            return
            
        execute(ast)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error while running {filename}: {str(e)}")

if __name__ == "__main__":
    # Vérifie les arguments
    if len(sys.argv) != 2:
        print("Usage: python compilateur.py <filename.ada>")
        print("Example: python compilateur.py program.ada")
        sys.exit(1)
        
    filename = sys.argv[1]
    
    # Vérifie l'extension
    if not filename.endswith('.ada'):
        print("Error: File must have .ada extension")
        print("Usage: python compilateur.py <filename.ada>")
        sys.exit(1)
        
    run_ada_file(filename)