"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

import JackTokenizer
import SymbolTable
import VMWriter

keyword = "KEYWORD"
symbol = "SYMBOL"
identifier = "IDENTIFIER"
int_const = "INT_CONST"
string_const = "STRING_CONST"
none = ""
EMPTY = ""
TYPE = 0
KIND = 1
INDEX = 2
LABEL = "L"


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    label_counter = 0

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.symbol_table = SymbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(output_stream)
        self.output_file = output_stream
        self.class_name = EMPTY

        # -- subroutine_fields -- #
        self.curr_subroutine_name = EMPTY
        self.curr_subroutine_return_value = EMPTY
        self.curr_subroutine_type = EMPTY

        # -- vars fields -- #
        self.curr_var_names = []
        self.curr_var_kind = EMPTY
        self.curr_var_type = EMPTY
        self.negative_const = False
        self.current_array_name = EMPTY

        # -- general_fields -- #
        self.tab_num = 0
        self.array_counter = 0
        self.class_var_kinds = ["STATIC", "FIELD"]
        self.var_types = ["INT", "BOOLEAN", "CHAR"]
        self.func_types = ["METHOD", "FUNCTION", "CONSTRUCTOR"]
        self.statement_types = ["IF", "WHILE", "LET", "DO", "RETURN"]
        self.const_keywords = ["NULL", "TRUE", "FALSE", "THIS"]
        self.operators = ["+", "-", "*", "/", "&", "|", "<", ">", "=", ]
        self.terms_optional_symbols = ["(", "[", "."]
        self.unary_ops = ["-", "~", "^", "#"]  # ^ = leftshift, # = rightshift

    def is_token_valid(self, grammar_type, characters) -> bool:
        """
        checks if current token have the correct type.
        in case of keyword and symbol, checks if the current token is the correct symbol/keyword.
        """
        curr_token_type = self.tokenizer.token_type()
        if len(grammar_type) == 1 and identifier in grammar_type:
            return True
        if curr_token_type not in grammar_type:
            return False
        if curr_token_type == keyword:
            word_to_check = self.tokenizer.keyword()
            if word_to_check not in characters:
                return False
        elif curr_token_type == symbol:
            if self.tokenizer.symbol() not in characters:
                return False
        return True

    def generate_line(self, mandatory_type=False):
        curr_token_type = self.tokenizer.token_type()
        type_switch = {keyword: "keyword", symbol: "symbol", identifier: "identifier",
                       int_const: "integerConstant", string_const: "stringConstant"}
        compare_op_switch = {"<": "&lt", ">": "&gt", "&": "&amp"}
        type = type_switch[curr_token_type]
        token_to_write = self.tokenizer.switch_commands_types(curr_token_type)
        if mandatory_type:
            type = mandatory_type.lower()
        if curr_token_type == keyword:
            token_to_write = token_to_write.lower()
        elif curr_token_type == symbol:
            if token_to_write in [">", "<", "&"]:
                token_to_write = compare_op_switch[token_to_write] + ";"
        self.write("<" + type + "> " + token_to_write + " </" + type + ">")

    def process(self, grammar_types, character, is_subroutine=False, update_table=False) -> None:
        """
        helper function for each compilation method. write to output the token
        """

        if self.is_token_valid(grammar_types, character):
            if is_subroutine:
                self.curr_subroutine_type = self.tokenizer.keyword()
            elif update_table:
                self.update_symbol_table()
        else:
            self.write("syntax_error")
        self.tokenizer.advance()

    def update_symbol_table(self):
        if self.tokenizer.symbol() == ";" or self.tokenizer.symbol() == ")":
            if len(self.symbol_table.subroutine_symbol_table) == 0 \
                    and (self.curr_subroutine_type == "METHOD"):
                self.symbol_table.define("this", self.class_name, "ARG")
            for i in range(len(self.curr_var_names)):
                self.symbol_table.define(self.curr_var_names[i], self.curr_var_type, self.curr_var_kind)
            self.curr_var_names.clear()
        elif self.tokenizer.symbol() != ",":
            self.curr_var_names.append(self.tokenizer.identifier())

    def write(self, word: str) -> None:
        self.tab()
        self.output_file.write(word + "\n")

    def tab(self) -> None:
        self.output_file.write(self.tab_num * "  ")

    # -- helpers -- #
    def traverse_over_vars(self, kind):
        self.set_curr_var_kind(kind)
        self.set_curr_var_type()
        indicator = 1
        while indicator:
            self.process([identifier], none, update_table=True)
            if self.check_comma_separate() == False:
                indicator = 0
            self.process([symbol], [";", ","], update_table=True)

    def check_comma_separate(self):
        if self.tokenizer.token_type() == symbol:
            if self.tokenizer.symbol() == ",":
                return True
        return False

    # -- setters -- #

    def set_class_name(self):
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()

    def set_curr_var_kind(self, kind):
        if kind == "CLASS":
            self.curr_var_kind = self.tokenizer.keyword()
        else:
            self.curr_var_kind = kind
        self.tokenizer.advance()

    def set_curr_var_type(self):
        if self.tokenizer.token_type() == keyword:
            self.curr_var_type = self.tokenizer.keyword()
        else:
            self.curr_var_type = self.tokenizer.identifier()
        self.tokenizer.advance()

    def set_subroutine_name(self):
        self.curr_subroutine_name = self.class_name + "." + self.tokenizer.identifier()
        self.tokenizer.advance()

    def set_subroutine_return_value(self):
        self.curr_subroutine_return_value = self.tokenizer.keyword()
        self.tokenizer.advance()

    # -- ompilation_routines -- #

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.process([keyword], ["CLASS"])
        self.set_class_name()
        self.process([symbol], ["{"])
        self.compile_class_var_decs()
        self.compile_subroutine_decs()
        self.process([symbol], ["}"])

    def compile_class_var_decs(self):
        """
        compiles all vars decs in a class, calls to compile_class_var_dec
        """
        indicator = 1
        while indicator:
            curr_type = self.tokenizer.token_type()
            if curr_type != keyword:
                indicator = 0
            elif self.tokenizer.keyword() not in self.class_var_kinds:
                indicator = 0
            else:
                self.compile_class_var_dec()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""

        self.traverse_over_vars("CLASS")

    def compile_subroutine_decs(self):
        """
        compiles all subroutine decs in a class, calls to compile_subroutine
        """
        indicator = 1
        while indicator:
            curr_type = self.tokenizer.token_type()
            if curr_type != keyword:
                indicator = 0
            elif self.tokenizer.keyword() not in self.func_types:
                indicator = 0
            else:
                self.compile_subroutine()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()
        self.process([keyword], self.func_types, is_subroutine=True)
        self.set_subroutine_return_value()
        self.set_subroutine_name()
        self.process([symbol], ["("])
        self.compile_parameter_list()
        self.process([symbol], [")"])
        if self.curr_subroutine_type == "CONSTRUCTOR":
            self.vm_writer.write_push("constant", self.symbol_table.var_count("ARG"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif self.curr_subroutine_type == "METHOD":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        self.compile_subroutine_body()

    def compile_subroutine_body(self):
        """
        compiles the subroutine body
        """
        self.process([symbol], ["{"])
        self.compile_var_decs()
        self.vm_writer.write_function(self.curr_subroutine_name, self.symbol_table.var_count("VAR"))
        self.compile_statements()
        self.process([symbol], ["}"])

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        curr_type = self.tokenizer.token_type()
        if curr_type == keyword or curr_type == identifier:
            indicator = 1
            while indicator:
                self.curr_var_kind = "ARG"
                self.set_curr_var_type()
                self.process([identifier], none, update_table=True)
                if self.check_comma_separate() == False:
                    indicator = 0
                else:
                    self.process([symbol], [","], update_table=True)
            self.update_symbol_table()

    def compile_var_decs(self):
        indicator = 1
        is_declared = False
        while (indicator):
            if self.tokenizer.token_type() != "KEYWORD":
                indicator = 0
            elif self.tokenizer.keyword() != "VAR":
                indicator = 0
            else:
                self.compile_var_dec()
                is_declared = True
        if not is_declared:
            for i in range(len(self.curr_var_names)):
                self.symbol_table.define(self.curr_var_names[i], self.curr_var_type, self.curr_var_kind)
            self.curr_var_names.clear()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self.traverse_over_vars("VAR")

    # -- statements routines -- #
    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        statement_switch = {"LET": self.compile_let, "IF": self.compile_if, "WHILE": self.compile_while,
                            "DO": self.compile_do, "RETURN": self.compile_return}
        indicator = 1
        while indicator:
            curr_type = self.tokenizer.token_type()
            if curr_type != keyword:
                indicator = 0
            else:
                is_statement = self.tokenizer.keyword()
                if is_statement not in self.statement_types:
                    indicator = 0
                else:
                    statement_to_execute = statement_switch[is_statement]
                    statement_to_execute()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.process([keyword], ["DO"])
        object_name = self.tokenizer.identifier()
        self.process([identifier], none)
        self.process_subroutine_call(object_name)
        self.vm_writer.write_pop("temp", 0)  # clean the value from void method to temp 0
        self.process([symbol], [";"])

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.process([keyword], ["LET"])
        destination = self.tokenizer.identifier()
        dest_kind = self.symbol_table.kind_of(destination)
        if dest_kind == "FIELD" and self.curr_subroutine_type == "CONSTRUCTOR":
            dest_kind = "this"
        dest_index = self.symbol_table.index_of(destination)
        self.process([identifier], none)
        if self.tokenizer.symbol() == "[":
            self.process_destination_array(destination)
            self.process([symbol], ["="])
            self.compile_expression()
            self.process([symbol], [";"])
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.process([symbol], ["="])
            self.compile_expression()
            self.process([symbol], [";"])
            self.vm_writer.write_pop(dest_kind, dest_index)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.process([keyword], ["WHILE"])
        self.process([symbol], ["("])
        while_label = LABEL + str(self.label_counter)
        self.label_counter += 1
        end_label = LABEL + str(self.label_counter)
        self.label_counter += 1
        self.vm_writer.write_label(while_label)
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(end_label)
        self.process([symbol], [")"])
        self.process([symbol], ["{"])
        self.compile_statements()
        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(end_label)
        self.process([symbol], ["}"])

    def compile_return(self) -> None:
        """Compiles a return statement."""

        self.process([keyword], ["RETURN"])
        if self.tokenizer.token_type() != symbol:
            self.compile_expression()

        elif self.tokenizer.symbol() == '-':
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)
        self.process([symbol], [";"])
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.process([keyword], ["IF"])
        self.process([symbol], ["("])
        self.compile_expression()
        self.process([symbol], [")"])
        self.process([symbol], ["{"])
        self.vm_writer.write_arithmetic("NOT")
        true_label = LABEL + str(self.label_counter)
        self.label_counter += 1
        false_label = LABEL + str(self.label_counter)
        self.label_counter += 1
        self.vm_writer.write_if(false_label)
        self.compile_statements()
        self.vm_writer.write_goto(true_label)
        self.process([symbol], ["}"])
        self.vm_writer.write_label(false_label)
        if self.tokenizer.token_type() == keyword:
            if self.tokenizer.keyword() == "ELSE":
                self.process([keyword], ["ELSE"])
                self.process([symbol], ["{"])
                self.compile_statements()
                self.process([symbol], ["}"])
        self.vm_writer.write_label(true_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.token_type() == symbol:
            curr_symbol = self.tokenizer.symbol()
            if curr_symbol in self.operators:
                operator = curr_symbol
                self.process(symbol, self.operators)
                self.compile_term()
                if operator == "*":
                    self.vm_writer.write_call("Math.multiply", 2)

                elif operator == "/":
                    self.vm_writer.write_call("Math.divide", 2)
                else:
                    self.vm_writer.write_arithmetic(operator)
            elif curr_symbol == "[":
                self.process_array(self.current_array_name)
            else:
                break

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        name_to_write = EMPTY
        curr_type = self.tokenizer.token_type()
        if curr_type == int_const:
            self.vm_writer.write_push("constant", self.tokenizer.int_val())
            self.tokenizer.advance()
        elif curr_type == string_const:
            self.compile_string(self.tokenizer.string_val())
        elif curr_type == keyword:
            curr_keyword = self.tokenizer.keyword()
            if curr_keyword in self.const_keywords:
                self.compile_keyword(keyword)
        elif curr_type == identifier:
            name_to_write += self.tokenizer.identifier()
            self.process([identifier], none)
            curr_type = self.tokenizer.token_type()
            if curr_type == symbol:
                curr_symbol = self.tokenizer.symbol()
                if curr_symbol in self.terms_optional_symbols:
                    self.process_complex_term(name_to_write)
                else:
                    self.current_array_name = name_to_write
                    self.write_identifier(name_to_write)
        elif self.tokenizer.symbol() == "(":
            self.process([symbol], "(")
            self.compile_expression()
            self.process([symbol], ")")
        elif self.tokenizer.symbol() in self.unary_ops:
            curr_symbol = self.tokenizer.symbol()
            self.process([symbol], self.unary_ops)
            self.compile_term()
            if curr_symbol == "-":
                self.vm_writer.write_arithmetic("NEG")
            elif curr_symbol == "~":
                self.vm_writer.write_arithmetic("NOT")
            elif curr_symbol == "^" or curr_symbol == "#":
                self.vm_writer.write_arithmetic(curr_symbol)

    def process_complex_term(self, object_name):
        curr_token = self.tokenizer.symbol()
        if curr_token == "[":
            self.process_array(object_name)
        elif curr_token == ".":
            self.process_subroutine_call(object_name)
        elif curr_token == "(":
            self.process_function_call()

    def process_destination_array(self, array_name):
        self.vm_writer.write_push(self.symbol_table.kind_of(array_name), self.symbol_table.index_of(array_name))
        self.process([symbol], ["["])
        self.compile_expression()
        self.vm_writer.write_arithmetic("+")
        self.process([symbol], ["]"])

    def process_array(self, array_name):
        self.vm_writer.write_push(self.symbol_table.kind_of(array_name), self.symbol_table.index_of(array_name))
        self.process([symbol], ["["])
        self.compile_expression()
        self.vm_writer.write_arithmetic("+")
        self.process([symbol], ["]"])
        self.vm_writer.write_pop("pointer", 1)
        self.vm_writer.write_push("that", 0)

    def process_subroutine_call(self, object_name):
        function_name = object_name
        if self.tokenizer.symbol() == ".":
            self.process([symbol], ["."])
            function_name = object_name + "." + self.tokenizer.identifier()
            self.process([identifier], none)
        self.process([symbol], ["("])
        n_args = self.compile_expression_list()
        self.process([symbol], [")"])
        self.vm_writer.write_call(function_name, n_args)

    def process_function_call(self):
        self.process([symbol], ["("])
        self.compile_expression_list()
        self.process([symbol], [")"])

    def compile_expression_list(self):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        expression_counter = 0
        if self.tokenizer.token_type() != symbol:
            self.compile_expression()
            expression_counter += 1
        elif self.tokenizer.symbol() == "(" or self.tokenizer.symbol() in self.unary_ops:
            self.compile_expression()
            expression_counter += 1
        elif self.tokenizer.symbol() == "\"":
            self.compile_expression()
            expression_counter += 1
        while self.tokenizer.token_type() == symbol:
            if self.tokenizer.symbol() == ",":
                self.process([symbol], ",")
                self.compile_expression()
                expression_counter += 1
            else:
                break
        return expression_counter

    def compile_keyword(self, keyword):
        if keyword == "this":
            self.vm_writer.write_push("pointer", 0)
        elif self.tokenizer.keyword() == "TRUE":
            self.vm_writer.write_push("constant", 1)
            self.vm_writer.write_arithmetic("NEG")
        else:
            self.vm_writer.write_push("constant", 0)
        self.tokenizer.advance()

    def compile_string(self, string_val):
        self.vm_writer.write_push("constant", len(self.tokenizer.string_val()))
        self.vm_writer.write_call("String.new", 1)
        for char in string_val:
            self.vm_writer.write_push("constant", ord(char))
            self.vm_writer.write_call("String.appendChar", 2)
        self.tokenizer.advance()

    def write_identifier(self, name):
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)
        self.vm_writer.write_push(kind, index)
