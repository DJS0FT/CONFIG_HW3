import sys
import re
import argparse

class ParserError(Exception):
    pass

class EvaluatorError(Exception):
    pass

def remove_single_line_comments(text):
    lines = text.split('\n')
    new_lines = [line for line in lines if not (line.strip().startswith('*') or line.strip().startswith('#'))]
    return '\n'.join(new_lines)

def remove_multiline_comments(text):
    return re.sub(r'\{\{!--.*?--\}\}', '', text, flags=re.DOTALL)

def tokenize(text):
    token_pattern = r'''
       (q\(.*?\))            
     | (\.\{|\}\.|:=|=|\[|\]|,|\(|\)) 
     | ([0-9]+)              
     | (concat|len|\+|\-|\*) 
     | ([_a-zA-Z][_a-zA-Z0-9]*) 
    '''
    tokens_raw = re.findall(token_pattern, text, flags=re.VERBOSE | re.DOTALL)
    tokens = []
    for t in tokens_raw:
        for g in t:
            if g.strip():
                tokens.append(g.strip())
                break
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.constants = {}

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        if self.pos >= len(self.tokens):
            raise ParserError("Ожидался токен, но входной поток закончился.")
        t = self.tokens[self.pos]
        if expected is not None and t != expected:
            raise ParserError(f"Ожидался токен '{expected}', а встречено '{t}'")
        self.pos += 1
        return t

    def parse(self):
        while self.current_token() is not None:
            self.parse_statement()
        return self.constants

    def parse_statement(self):
        name_t = self.current_token()
        if not re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', name_t if name_t else ''):
            raise ParserError(f"Ожидалось имя переменной, а встречено '{name_t}'")
        self.consume()
        op = self.consume()
        if op != ':=':
            raise ParserError(f"Ожидался оператор ':=', а встречено '{op}'")
        value = self.parse_value()
        self.constants[name_t] = value

    def parse_value(self):
        t = self.current_token()
        if t is None:
            raise ParserError("Ожидалось значение, но поток токенов закончился.")
        if re.match(r'^[0-9]+$', t):
            val = int(self.consume())
            return val
        elif t.startswith('q(') and t.endswith(')'):
            val = t[2:-1]
            # Удаляем внешние кавычки, если они есть
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            self.consume()
            return val
        elif t == '[':
            return self.parse_array()
        elif t == '.{':
            return self.parse_computation()
        elif re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', t):
            name = self.consume()
            if name not in self.constants:
                raise ParserError(f"Неизвестная константа '{name}'")
            return self.constants[name]
        else:
            raise ParserError(f"Неверный токен для значения: '{t}'")

    def parse_array(self):
        self.consume('[')
        arr = []
        while True:
            if self.current_token() == ']':
                self.consume(']')
                return arr
            val = self.parse_value()
            arr.append(val)
            if self.current_token() == ',':
                self.consume(',')
                continue
            elif self.current_token() == ']':
                self.consume(']')
                return arr
            else:
                raise ParserError("Ожидался ',' или ']' при разборе массива.")

    def parse_computation(self):
        self.consume('.{')
        op = self.consume()
        args = []
        while self.current_token() not in ('}.', None):
            arg_val = self.parse_value()
            args.append(arg_val)
            if self.current_token() == ',':
                self.consume(',')  # Пропускаем запятую и продолжаем
        if self.current_token() != '}.':
            raise ParserError("Ожидалось '}.', при завершении вычисления")
        self.consume('}.')
        return self.evaluate_computation(op, args)

    def evaluate_computation(self, op, args):
        if op == '+':
            if len(args) < 2:
                raise EvaluatorError("Операция '+' требует минимум 2 аргумента.")
            result = args[0]
            for a in args[1:]:
                if not isinstance(a, int):
                    raise EvaluatorError("Операция '+' поддерживает только числа.")
                result += a
            return result
        elif op == '-':
            if len(args) < 2:
                raise EvaluatorError("Операция '-' требует минимум 2 аргумента.")
            result = args[0]
            for a in args[1:]:
                if not isinstance(a, int):
                    raise EvaluatorError("Операция '-' поддерживает только числа.")
                result -= a
            return result
        elif op == '*':
            if len(args) < 2:
                raise EvaluatorError("Операция '*' требует минимум 2 аргумента.")
            result = args[0]
            for a in args[1:]:
                if not isinstance(a, int):
                    raise EvaluatorError("Операция '*' поддерживает только числа.")
                result *= a
            return result
        elif op == 'concat':
            if any(not isinstance(a, str) for a in args):
                raise EvaluatorError("Операция 'concat' поддерживает только строки.")
            return "".join(args)
        elif op == 'len':
            if len(args) != 1:
                raise EvaluatorError("Операция 'len' требует ровно 1 аргумент.")
            val = args[0]
            if isinstance(val, str) or isinstance(val, list):
                return len(val)
            else:
                raise EvaluatorError("Операция 'len' поддерживает только строку или массив.")
        else:
            raise EvaluatorError(f"Неизвестная операция '{op}'")

def to_toml(constants):
    lines = []
    for k, v in constants.items():
        val_str = value_to_toml(v)
        lines.append(f"{k} = {val_str}")
    return "\n".join(lines)

def value_to_toml(val):
    if isinstance(val, int):
        return str(val)
    elif isinstance(val, str):
        escaped = val.replace('"', '\\"')
        return f"\"{escaped}\""
    elif isinstance(val, list):
        inner = ", ".join(value_to_toml(x) for x in val)
        return f"[{inner}]"
    else:
        raise EvaluatorError(f"Неподдерживаемый тип для TOML: {type(val)}")

def main():
    parser = argparse.ArgumentParser(description="Конвертер конфигураций в TOML.")
    parser.add_argument('-o', '--output', type=str, help='Имя выходного TOML файла')
    args = parser.parse_args()

    input_text = sys.stdin.read()
    input_text = remove_single_line_comments(input_text)
    input_text = remove_multiline_comments(input_text)
    tokens = tokenize(input_text)
    parser_obj = Parser(tokens)
    try:
        constants = parser_obj.parse()
    except (ParserError, EvaluatorError) as e:
        sys.stderr.write("Ошибка: " + str(e) + "\n")
        sys.exit(1)
    toml_output = to_toml(constants)
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(toml_output)
        except IOError as e:
            sys.stderr.write("Ошибка при записи в файл: " + str(e) + "\n")
            sys.exit(1)
    else:
        print(toml_output)

if __name__ == "__main__":
    main()
