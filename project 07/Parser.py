"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """
    INITIAL_INDEX = -1
    NO_JUMP = -1
    END_OF_COMP = ";"
    END_OF_DEST = "="
    COMMAND_BEGIN_INDEX = 1
    A_COMMAND_SYMBOL = '@'
    L_COMMAND_SYMBOL = '('
    NEXT_LINE = 1
    END_OF_FILE = -1
    EMPTY_LINE = ""
    SYMBOL_INDEX = 0
    JUMP_COMMAND_LENGTH = 3
    COMMENT_CHAR = "/"
    NULL = "null"
    SHIFT_INITIAL = "101"
    C_INITIAL = "111"
    ARITHMETIC_COMMANDS = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
    ARITHMETIC_COMMAND = "C_ARITHMETIC"
    MEMORY_ACCESS_COMMANDS = ["C_PUSH", "C_POP", "push", "pop"]
    LABEL_COMMANDS = ["C_LABEL", "C_GOTO", "C_IF"]
    FUNCTION_COMMANDS = ["C_FUNCTION", "C_RETURN", "C_CALL"]
    ANOTHER_COMMAND = ""
    COMMAND_OPEN = "C_"

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        for i in range(len(self.input_lines)):
            self.input_lines[i] = self.delete_comment(self.input_lines[i])
        self.current_line = Parser.INITIAL_INDEX
        self.current_command = Parser.INITIAL_INDEX
        self.num_of_labels = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.current_line < len(self.input_lines):
            if self.next_available_line() != Parser.END_OF_FILE:
                return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.current_line = self.next_available_line()
            self.current_command += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command_type_str = self.extract_command()
        memory_access_command = self.is_memory_access_command(command_type_str)
        label_commands = self.is_label_command(command_type_str)
        function_commands = self.is_function_command(command_type_str)
        if memory_access_command != self.ANOTHER_COMMAND:
            return self.COMMAND_OPEN + memory_access_command
        elif label_commands != self.ANOTHER_COMMAND:
            return self.COMMAND_OPEN + label_commands
        elif function_commands != self.ANOTHER_COMMAND:
            return self.COMMAND_OPEN + function_commands
        return self.ARITHMETIC_COMMAND

    def extract_command(self) -> str:
        current_command = self.input_lines[self.current_line]
        command_type_first_index = self.first_index_ignore_spaces(current_command)
        command_type_last_index = self.find_command_last_index(command_type_first_index)
        return current_command[command_type_first_index: command_type_last_index]

    def find_command_last_index(self, command_type_first_index: int) -> int:
        current_command = self.input_lines[self.current_line]
        last_index = command_type_first_index
        for i in range(command_type_first_index, len(current_command)):
            if current_command[i] == ' ':
                break
            last_index += 1

        return last_index #+ 1

    def first_index_ignore_spaces(self, line) -> int:
        index = 0
        while line[index] == ' ':
            index += 1
        return index

    def is_arithmetic_command(self, current_command: str) -> str:
        if current_command in self.ARITHMETIC_COMMANDS:
            return current_command.upper()
        return self.ANOTHER_COMMAND

    def is_memory_access_command(self, current_command: str) -> str:
        if current_command in self.MEMORY_ACCESS_COMMANDS:
            return current_command.upper()
        return self.ANOTHER_COMMAND

    def is_label_command(self, current_command: str) -> str:
        if current_command in self.LABEL_COMMANDS:
            return current_command.upper()
        return self.ANOTHER_COMMAND

    def is_function_command(self, current_command: str) -> str:
        if current_command in self.FUNCTION_COMMANDS:
            return current_command.upper()
        return self.ANOTHER_COMMAND

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == self.ARITHMETIC_COMMAND:
            return self.extract_command()
        arg1_first_index = self.get_arg1_first_index()
        arg1_last_index = self.get_arg1_last_index(arg1_first_index)
        return (self.input_lines[self.current_line])[arg1_first_index: arg1_last_index]

    def get_arg1_first_index(self) -> int:
        current_line = self.input_lines[self.current_line]
        first_word_first_index = self.first_index_ignore_spaces(current_line)
        first_word_last_index = self.find_command_last_index(first_word_first_index)
        current_line_ignore_command = current_line[first_word_last_index:]
        arg1_first_index = self.first_index_ignore_spaces(current_line_ignore_command)
        return arg1_first_index + first_word_last_index

    def get_arg1_last_index(self, arg1_first_index) -> int:
        return self.find_command_last_index(arg1_first_index)

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        constant_str = self.get_constant_str(current_command)
        return int(constant_str)

    def get_constant_str(self, current_command: str) -> str:
        str_of_constant = ""
        constant_index = self.find_constant_first_index_at_str(current_command)
        for i in range(constant_index,(len(current_command))):
            if self.is_number(current_command[i]):
                str_of_constant += current_command[i]

            #if current_command[constant_index]
        return str_of_constant

    def is_number(self, char_to_check) -> bool:
        return '0' <= char_to_check <= '9'

    def find_constant_first_index_at_str(self, current_command: str) -> int:
        constant_first_index = 0
        while not (self.is_number(current_command[constant_first_index])):
            constant_first_index += 1
        return constant_first_index

    def find_comment(self, line):
        """*/
        Finds the index of the "/" char in a command, which represents a comment.
        */"""
        counter = 0
        for i in range(len(line)):
            if line[i] == Parser.COMMENT_CHAR:
                return counter
            counter += 1
        return counter

    def delete_comment(self, line):
        """*/
        Returns a command (line) without comments.
        */"""
        comment_index = self.find_comment(line)
        if len(line) != comment_index:
            line = line[0:comment_index]
        line = line.replace("\t", "")
        return line

    def is_description(self, line) -> bool:
        """"return true if the current line is a description"""
        # clean line from spaces
        if line[0] == Parser.COMMENT_CHAR and line[1] == Parser.COMMENT_CHAR:
            return True
        return False

    def next_available_line(self) -> int:
        """returns the index of the next available line, else -1"""
        if (self.current_line == len(self.input_lines)):
            current_line = (self.input_lines[self.current_line]).replace(" ", "")
            if current_line != Parser.EMPTY_LINE and not (self.is_description(current_line)):
                return self.current_line
        for i in range(self.current_line + 1, len(self.input_lines)):  # זה גורם שלא קוראים את השורה האחרונה בקובץ
            # clean line from spaces
            current_line = (self.input_lines[i]).replace(" ", "")
            if current_line != Parser.EMPTY_LINE and not (self.is_description(current_line)):
                return i
        return Parser.END_OF_FILE
