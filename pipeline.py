
import sys

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def run(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                self.execute(line.strip())

    def execute(self, line):
        if not line.strip():
            return
        if not line.endswith(";"):
            print(f"Error: Missing semicolon at the end of line: {line}")
            return

        if line.startswith("var"):
            parts = line.split("=")
            var_name = parts[0].replace("var", "").strip()  # Extract the variable name
            var = parts[0].strip()
            value = "=".join(parts[1:]).strip()
            if value.startswith("\"") and value.endswith("\";"):  # STRING
                self.variables[var_name] = value[1:-2]  # Use var_name as the variable name
            elif value[0:-1].isdigit() and value.endswith (";"): #DIGIT
                self.variables[var_name] = value[0:-1]  # Use var_name as the variable name
            else:
                print("Error: unrecognized value type")
        elif line.startswith("console"):
            value = line[len("console"):].strip()
            if value.startswith("(") and value.endswith(");"):
                expr = value[1:-2].strip()
                if expr.startswith("\"") and expr.endswith("\""):
                    print(expr[1:-1])  # Print the string without outer quotes
                else:
                    result = self.evaluate_expression(expr)
                    print(result)
            else:
                print(f"Invalid statement: {line.strip()}")

        elif '=' in line and not line.startswith("=="):
            parts = line.split("=")
            var = parts[0].strip()
            value = "=".join(parts[1:]).strip()
            self.variables[var] = self.evaluate_expression(value)
        elif 'def' in line:
            func_name, params = line[4:].split("(", 1)
            params = params.rstrip("):").split(",")
            self.functions[func_name.strip()] = (params, line)
        elif '(' in line and line.endswith(")"):
            func_name, args = line.split("(", 1)
            args = args.rstrip(")").split(",")
            params, func_def = self.functions.get(func_name.strip(), (None, None))
            if params:
                call_args = {}
                for param, arg in zip(params, args):
                    call_args[param.strip()] = self.evaluate_expression(arg.strip())
                self.execute(func_def.replace(func_name, ""))
            else:
                print("Function", func_name, "not defined.")

        else:
            print("Invalid statement:", line)

    def evaluate_expression(self, expr):
        operators = {'+': lambda x, y: x + y,
                    '-': lambda x, y: x - y,
                    '*': lambda x, y: x * y,
                    '/': lambda x, y: x / y}

        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        def precedence_compare(op1, op2):
            return precedence[op1] <= precedence[op2]

        def apply_operator(op, stack):
            if len(stack) < 2:
                return None  # Return None if there are not enough operands
            op2 = stack.pop()
            op1 = stack.pop()
            return operators[op](op1, op2)

        tokens = expr.split()
        stack = []
        output = []

        for token in tokens:
            if token in operators:
                while stack and precedence_compare(stack[-1], token):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Discard '('
            else:
                try:
                    if '.' in token:
                        output.append(float(token))  # Append as float if token contains a dot
                    else:
                        output.append(int(token))  # Append as integer otherwise
                except ValueError:
                    if token in self.variables:  # Check if token is a variable
                        value = self.variables[token]
                        try:
                            if '.' in value:
                                output.append(float(value))  # Append as float if variable contains a dot
                            else:
                                output.append(int(value))  # Append as integer otherwise
                        except ValueError:
                            output.append(value)  # If the variable is not numeric, treat it as a string

        while stack:
            output.append(stack.pop())

        for token in output:
            if token in operators:
                result = apply_operator(token, stack)
                if result is None:
                    return None  # Return None if there are not enough operands
                stack.append(result)
            else:
                stack.append(token)

        if len(stack) == 1:
            return stack[0]
        elif stack:
            return ''.join(str(x) for x in stack)
        else:
            return None

    def evaluate_condition(self, condition):
        comparison_operators = ['==', '!=', '>', '<', '>=', '<=']
        for op in comparison_operators:
            if op in condition:
                var1, var2 = condition.split(op)
                val1 = self.evaluate_expression(var1.strip())
                val2 = self.evaluate_expression(var2.strip())
                if op == '==':
                    return val1 == val2
                elif op == '!=':
                    return val1 != val2
                elif op == '>':
                    return val1 > val2
                elif op == '<':
                    return val1 < val2
                elif op == '>=':
                    return val1 >= val2
                elif op == '<=':
                    return val1 <= val2
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py filename.pipe")
        return
    
    filename = sys.argv[1]
    interpreter = Interpreter()
    interpreter.run(filename)

if __name__ == "__main__":
    main()