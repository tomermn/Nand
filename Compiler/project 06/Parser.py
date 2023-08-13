"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
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

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_file.read().splitlines()
        for i in range(len(self.input_lines)):
            self.input_lines[i] = self.delete_comment(self.input_lines[i])
        self.current_line = Parser.INITIAL_INDEX
        self.current_command = Parser.INITIAL_INDEX
        self.num_of_labels = 0

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
        return line


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
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.current_line = self.next_available_line()
            self.current_command += 1


    def next_available_line(self) -> int:
        """returns the index of the next available line, else -1"""
        if (self.current_line == len(self.input_lines)):
            current_line = (self.input_lines[self.current_line]).replace(" ", "")
            if current_line != Parser.EMPTY_LINE and not (self.is_description(current_line)):
                return self.current_line
        for i in range(self.current_line + 1 , len(self.input_lines)):#זה גורם שלא קוראים את השורה האחרונה בקובץ
            # clean line from spaces

            current_line = (self.input_lines[i]).replace(" ", "")
            if current_line != Parser.EMPTY_LINE and not(self.is_description(current_line)):
                return i
        return Parser.END_OF_FILE


    def is_description(self, line) -> bool:
        """"return true if the current line is a description"""
        # clean line from spaces
        if line[0] == Parser.COMMENT_CHAR and line[1] == Parser.COMMENT_CHAR:
            return True
        return False


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # clean line from spaces
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        if current_command[Parser.SYMBOL_INDEX] == Parser.A_COMMAND_SYMBOL:
            return "A_COMMAND"
        elif current_command[Parser.SYMBOL_INDEX] == Parser.L_COMMAND_SYMBOL:
            return "L_COMMAND"
        else:
            return "C_COMMAND"


    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or
            "L_COMMAND".
        """
        symbol_type = self.command_type()
        if symbol_type == "A_COMMAND":
            return self.a_command_symbol()
        return self.l_command_symbol()


    def l_command_symbol(self) -> str:
        """returns L command symbol"""
        # clean line from spaces
        current_symbol = (self.input_lines[self.current_line]).replace(" ", "")
        symbol_length = len(current_symbol)
        return current_symbol[Parser.COMMAND_BEGIN_INDEX:(symbol_length - 1)]


    def a_command_symbol(self) -> str:
        """returns A command symbol"""
        # clean line from spaces
        current_symbol = (self.input_lines[self.current_line]).replace(" ", "")
        symbol_length = len(current_symbol)
        return current_symbol[Parser.COMMAND_BEGIN_INDEX:symbol_length]


    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        dest_str = ""
        # clean line from spaces
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        for char in current_command:
            if char == Parser.END_OF_DEST:
                return dest_str
            dest_str += char

        return Parser.NULL


    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        if self.dest() != Parser.NULL:
            comp_index = self.find_comp_index()
            return self.extract_comp(comp_index)
        else:
            return self.extract_comp(0)


    def find_comp_index(self) -> int:
        """returns the first index of comp in the command"""
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        command_length = len(current_command)
        for i in range(0, command_length):
            if current_command[i] == Parser.END_OF_DEST:
                return i + 1
        return command_length


    def extract_comp(self, first_index: int) -> str:
        """returns the comp out of the command"""
        comp_str = ""
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        command_length = len(current_command)
        for i in range(first_index, command_length):
            if current_command[i] == Parser.END_OF_COMP:
                return comp_str
            comp_str += current_command[i]
        return comp_str


    def is_shift(self):
        """
        Checks if a C command is a shift.
        return:
        "101" - if the command is a shift.
        "111" - otherwise.
        """
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        command_length = len(current_command)
        for i in range(0, command_length):
            if current_command[i] == "<" or current_command[i] == ">":
                return Parser.SHIFT_INITIAL
        return Parser.C_INITIAL


    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        jump_str = ""
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        start_index = self.jump_str_start_index()
        if start_index != Parser.NO_JUMP:
            for i in range(start_index, start_index + Parser.JUMP_COMMAND_LENGTH):
                jump_str += current_command[i]
            return jump_str
        return Parser.NULL

    def jump_str_start_index(self) -> int:
        """returns the first index of jump in the command"""
        current_command = (self.input_lines[self.current_line]).replace(" ", "")
        command_length = len(current_command)
        for i in range(0, command_length):
            if current_command[i] == Parser.END_OF_COMP:
                return i + 1
        return Parser.NO_JUMP
