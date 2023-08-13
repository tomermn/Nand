"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

import JackTokenizer

keyword = "KEYWORD"
symbol = "SYMBOL"
identifier = "IDENTIFIER"
int_const = "INT_CONST"
string_const = "STRING_CONST"
none = ""


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
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
        self.output_file = output_stream
        self.tab_num = 0
        self.class_var_types = ["STATIC", "FIELD"]
        self.var_types = ["INT", "BOOLEAN", "CHAR"]
        self.func_types = ["METHOD", "FUNCTION", "CONSTRUCTOR"]
        self.statement_types = ["IF", "WHILE", "LET", "DO", "RETURN"]
        self.operators = ["+", "-", "*", "/", "&", "|", "<", ">", "=", ]
        self.terms_optional_symbols = ["(", "[", "."]
        self.unary_ops = ["-", "~", "^", "#"] # ^ = leftshift, # = rightshift

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

    def process(self, grammar_types, character) -> None:
        """
        helper function for each compilation method. write to output the token
        """
        if self.is_token_valid(grammar_types, character):
            if len(grammar_types) == 1:
                self.generate_line(grammar_types[0])
            else:
                self.generate_line()
        else:
            self.write("syntax_error")

        self.tokenizer.advance()

    def write(self, word: str) -> None:
        self.tab()
        self.output_file.write(word + "\n")

    def tab(self) -> None:
        self.output_file.write(self.tab_num * "  ")

    # -- helpers -- #
    def traverse_over_vars(self, vars_category):
        self.process([keyword], vars_category)
        self.process([keyword, identifier], self.var_types)  # check type
        indicator = 1
        while indicator:
            self.process([identifier], none)
            if self.check_comma_separate() == False:
                indicator = 0
            self.process([symbol], [";", ","])

    def check_comma_separate(self):
        if self.tokenizer.token_type() == symbol:
            if self.tokenizer.symbol() == ",":
                return True
        return False

    # -- compilation routines -- #

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write("<class>")
        self.tab_num += 1
        self.process([keyword], ["CLASS"])
        self.process([identifier], none)
        self.process([symbol], ["{"])
        self.compile_class_var_decs()
        self.compile_subroutine_decs()
        self.process([symbol], ["}"])
        self.tab_num -= 1
        self.write("</class>")

    def compile_class_var_decs(self):
        """
        compiles all vars decs in a class, calls to compile_class_var_dec
        """
        indicator = 1
        while indicator:
            curr_type = self.tokenizer.token_type()
            if curr_type != keyword:
                indicator = 0
            elif self.tokenizer.keyword() not in self.class_var_types:
                indicator = 0
            else:
                self.compile_class_var_dec()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write("<classVarDec>")
        self.tab_num += 1
        self.traverse_over_vars(self.class_var_types)
        self.tab_num -= 1
        self.write("</classVarDec>")

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
        self.write("<subroutineDec>")
        self.tab_num += 1
        self.process([keyword], self.func_types)
        self.process([keyword, identifier], self.var_types + ["VOID"])  # return value
        self.process([identifier], none)  # function_name
        self.process([symbol], ["("])
        self.compile_parameter_list()
        self.process([symbol], [")"])
        self.compile_subroutine_body()
        self.tab_num -= 1
        self.write("</subroutineDec>")

    def compile_subroutine_body(self):
        """
        compiles the subroutine body
        """
        self.write("<subroutineBody>")
        self.tab_num += 1
        self.process([symbol], ["{"])
        indicator = 1
        while (indicator):
            if self.tokenizer.token_type() != "KEYWORD":
                indicator = 0
            elif self.tokenizer.keyword() != "VAR":
                indicator = 0
            else:
                self.compile_var_dec()
        self.compile_statements()
        self.process([symbol], ["}"])
        self.tab_num -= 1
        self.write("</subroutineBody>")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.write("<parameterList>")
        self.tab_num += 1
        curr_type = self.tokenizer.token_type()
        if curr_type == keyword or curr_type == identifier:
            indicator = 1
            while indicator:
                self.process([keyword, identifier], self.var_types)
                self.process([identifier], none)
                if self.check_comma_separate() == False:
                    indicator = 0
                else:
                    self.process([symbol], [","])

        self.tab_num -= 1
        self.write("</parameterList>")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write("<varDec>")
        self.tab_num += 1
        self.traverse_over_vars(["VAR"])
        self.tab_num -= 1
        self.write("</varDec>")

    # -- statements routines -- #
    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        statement_switch = {"LET": self.compile_let, "IF": self.compile_if, "WHILE": self.compile_while,
                            "DO": self.compile_do, "RETURN": self.compile_return}
        self.write("<statements>")
        self.tab_num += 1
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
        self.tab_num -= 1
        self.write("</statements>")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write("<doStatement>")
        self.tab_num += 1
        self.process([keyword], ["DO"])
        self.process([identifier], none)
        self.process_subroutine_call()
        self.process([symbol], [";"])
        self.tab_num -= 1
        self.write("</doStatement>")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write("<letStatement>")
        self.tab_num += 1
        self.process([keyword], ["LET"])
        self.process([identifier], none)
        if self.tokenizer.symbol() == "[":
            self.process_array()
        self.process([symbol], ["="])
        self.compile_expression()
        self.process([symbol], [";"])
        self.tab_num -= 1
        self.write("</letStatement>")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write("<whileStatement>")
        self.tab_num += 1
        self.process([keyword], ["WHILE"])
        self.process([symbol], ["("])
        self.compile_expression()
        self.process([symbol], [")"])
        self.process([symbol], ["{"])
        self.compile_statements()
        self.process([symbol], ["}"])
        self.tab_num -= 1
        self.write("</whileStatement>")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write("<returnStatement>")
        self.tab_num += 1
        self.process([keyword], ["RETURN"])

        if self.tokenizer.token_type() != symbol:
            self.compile_expression()
        elif self.tokenizer.symbol() == '-':
            self.compile_expression()
        self.process([symbol], [";"])
        self.tab_num -= 1
        self.write("</returnStatement>")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.write("<ifStatement>")
        self.tab_num += 1
        self.process([keyword], ["IF"])
        self.process([symbol], ["("])
        self.compile_expression()
        self.process([symbol], [")"])
        self.process([symbol], ["{"])
        self.compile_statements()
        self.process([symbol], ["}"])
        if self.tokenizer.token_type() == keyword:
            if self.tokenizer.keyword() == "ELSE":
                self.process([keyword], ["ELSE"])
                self.process([symbol], ["{"])
                self.compile_statements()
                self.process([symbol], ["}"])
        self.tab_num -= 1
        self.write("</ifStatement>")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write("<expression>")
        self.tab_num += 1
        self.compile_term()
        while self.tokenizer.token_type() == symbol:
            curr_symbol = self.tokenizer.symbol()
            if curr_symbol in self.operators:
                self.process([symbol], curr_symbol)
                self.compile_term()
            else:
                break
        self.tab_num -= 1
        self.write("</expression>")

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
        self.write("<term>")
        self.tab_num += 1
        curr_type = self.tokenizer.token_type()
        if curr_type == int_const or curr_type == string_const or curr_type == keyword:
            self.process([int_const, string_const, keyword], JackTokenizer.KEYWORDS)
        elif curr_type == identifier:
            self.process([identifier], none)
            curr_type = self.tokenizer.token_type()
            if curr_type == symbol:
                curr_symbol = self.tokenizer.symbol()
                if curr_symbol in self.terms_optional_symbols:
                    self.process_complex_term()
        elif self.tokenizer.symbol() == "(":
            self.process([symbol], "(")
            self.compile_expression()
            self.process([symbol], ")")

        elif self.tokenizer.symbol() in self.unary_ops:
            self.process([symbol], self.unary_ops)
            self.compile_term()
        self.tab_num -= 1
        self.write("</term>")

    def process_complex_term(self):
        curr_token = self.tokenizer.symbol()
        if curr_token == "[":
            self.process_array()
        elif curr_token == ".":
            self.process_subroutine_call()
        elif curr_token == "(":
            self.process_function_call()

    def process_array(self):
        self.process([symbol], ["["])
        self.compile_expression()
        self.process([symbol], ["]"])

    def process_subroutine_call(self):
        if self.tokenizer.symbol() == ".":
            self.process([symbol], ["."])
            self.process([identifier], none)
        self.process([symbol], ["("])
        self.compile_expression_list()
        self.process([symbol], [")"])

    def process_function_call(self):
        self.process([symbol], ["("])
        self.compile_expression_list()
        self.process([symbol], [")"])

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write("<expressionList>")
        self.tab_num += 1

        if self.tokenizer.token_type() != symbol:
            self.compile_expression()
        elif self.tokenizer.symbol() == "(" or self.tokenizer.symbol() in self.unary_ops:
            self.compile_expression()
        while self.tokenizer.token_type() == symbol:
            if self.tokenizer.symbol() == ",":
                self.process([symbol], ",")
                self.compile_expression()
            else:
                break
        self.tab_num -= 1
        self.write("</expressionList>")
