"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from re import sub
KEYWORDS = {"CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"}

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
           '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}

MIN_INT_VALUE = 0
MAX_INT_VALUE = 32767

KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"
IDENTIFIER = "IDENTIFIER"
END_OF_LINE = "\n"
EMPTY = ""
TAB = "\t"
SPACE = " "
DOUBLE_QUOTE = "\""
SLASH = '/'
COMMENTS_FORMAT = "(//.*)|(/\*([\n]|[^*]|(\*+([^*/]|[\n])))*\*+/)"



class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements
    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.input_lines = input_stream.read()
        self.input_lines = sub(COMMENTS_FORMAT, "", self.input_lines)
        self.input_lines = self.input_lines.splitlines()
        self.current_line_index = 0
        self.current_char_index = 0
        self.current_token = EMPTY

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.current_line_index < len(self.input_lines) - 1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        self.extract_token()

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token:
            if self.current_token in SYMBOLS:
                return SYMBOL
            elif self.is_current_token_int():
                return INT_CONST
            elif self.is_current_token_string():
                return STRING_CONST
            elif self.current_token.upper() in KEYWORDS:
                return KEYWORD
            return IDENTIFIER
        self.current_token = "}"
        return SYMBOL

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> str:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return self.current_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        return self.current_token.replace(DOUBLE_QUOTE, EMPTY)

    def clean_token(self, token: str) -> str:
        token = token.replace("\t", "")
        token = token.replace(" ", "")
        token = token.replace("\n", "")
        return token

    def is_current_token_int(self) -> bool:
        """

        :return: True if the current token is an int
        """
        return '0' <= self.current_token[0] <= '9'

    def is_current_token_string(self) -> bool:
        """
        check if the first char is "
        :return: True if the current token is a string
        """
        return self.current_token[0] == DOUBLE_QUOTE

    def reset_token(self) -> None:
        """
        reset token to ""
        :return: None
        """
        self.current_token = EMPTY

    def is_symbol(self, char_to_check) -> bool:
        """

        :param char_to_check: the current char
        :return: True if the current char is a symbol
        """
        return char_to_check in SYMBOLS

    def is_int(self, char_to_check):
        return char_to_check == '-' and \
            '0' <= self.input_lines[self.current_line_index][self.current_char_index + 1] <= '9'

    def find_next_word(self) -> None:
        """

        :return: skip spaces and tabs and spotting the first char of the next word
        """
        self.skip_empty_lines()
        if self.has_more_tokens():
            current_line = self.input_lines[self.current_line_index]
            if current_line != EMPTY:
                while current_line[self.current_char_index] in {SPACE, TAB, SLASH}:
                    if self.current_char_index == len(current_line) - 1:
                        self.current_char_index = 0
                        self.current_line_index += 1
                    elif current_line[self.current_char_index] == SLASH:
                        break
                    else:
                        self.current_char_index += 1
                    self.skip_empty_lines()
                    if self.has_more_tokens():
                        current_line = self.input_lines[self.current_line_index]

    def is_comment(self, current_line):
        return current_line[self.current_char_index] == SLASH and \
               (current_line[self.current_char_index + 1] == SLASH or current_line[self.current_char_index + 1] == "*")

    def skip_empty_lines(self):
        current_line = self.clean_token(self.input_lines[self.current_line_index])
        while len(current_line) == 0 and self.has_more_tokens():
            self.current_line_index += 1
            current_line = self.clean_token(self.input_lines[self.current_line_index])

    def is_end_of_line(self) -> bool:
        """

        :return: True if the current char is end of line
        """
        return (len(self.input_lines[self.current_line_index]) == self.current_char_index) or \
               (not self.has_more_tokens())

    def handle_end_of_line(self) -> None:
        """
        skip to the next line and reset the char index
        :return: None
        """
        if self.is_end_of_line():
            self.current_line_index += 1
            self.current_char_index = 0

    def handle_comment_until_closing(self) -> None:
        """
        /*comment until closing */
        /** API comment until closing */
        :return: None
        """
        self.skip_empty_lines()
        current_line = self.input_lines[self.current_line_index]
        while not self.end_of_comment(current_line):
            if len(self.input_lines[self.current_line_index]) - 1 == self.current_char_index:
                self.current_line_index += 1
                self.current_char_index = 0
            else:
                self.current_char_index += 1
            self.skip_empty_lines()
            current_line = self.input_lines[self.current_line_index]
        self.current_line_index += 1
        self.current_char_index = 0

    def end_of_comment(self, current_line):
        return current_line[self.current_char_index] == '/' and current_line[self.current_char_index - 1] == '*'

    def handle_string(self):
        if self.current_token == "\"":
            while self.input_lines[self.current_line_index][self.current_char_index] != "\"":
                self.current_token += self.input_lines[self.current_line_index][self.current_char_index]
                self.current_char_index += 1
            self.current_char_index += 1
            return True
        return False

    def extract_token(self) -> None:
        """
        Manage the extraction of a token from the line
        :return: None
        """
        if self.has_more_tokens():
            self.find_next_word()
            self.reset_token()
            is_first_index_of_token = True
            is_token_extracted = self.is_end_of_line()
            current_line = self.input_lines[self.current_line_index]
            while not is_token_extracted and current_line[self.current_char_index] not in {SPACE, TAB}:
                # first round, if token is a symbol extract and stop loop else extract and continue
                if is_first_index_of_token:
                    self.current_token += current_line[self.current_char_index]
                    is_first_index_of_token = False
                    is_token_extracted = self.is_symbol(self.current_token)
                    self.current_char_index += 1
                    if self.handle_string():
                        is_token_extracted = True
                else:
                    # if reached to symbol stop extracting
                    if self.is_symbol(current_line[self.current_char_index]):
                        is_token_extracted = True
                    # else continue extracting characters
                    else:
                        self.current_token += current_line[self.current_char_index]
                        self.current_char_index += 1
                if self.is_end_of_line():
                    break
            self.handle_end_of_line()

    def switch_commands_types(self, type_):
        command = {"KEYWORD": self.keyword, "SYMBOL": self.symbol, "IDENTIFIER": self.identifier,
                   "INT_CONST": self.int_val, "STRING_CONST": self.string_val}
        command_to_activate = command[type_]
        return command_to_activate()

    def get_current_token(self):
        return self.current_token
