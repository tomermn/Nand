"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter

ARITHMETIC_COMMANDS = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
ARITHMETIC_COMMAND = "C_ARITHMETIC"
MEMORY_ACCESS_COMMANDS = ["C_PUSH", "C_POP"]
LABEL_COMMANDS = ["C_LABEL", "C_GOTO", "C_IF"]
FUNCTION_COMMANDS = ["C_FUNCTION", "C_RETURN", "C_CALL"]
COMMAND_OPEN = "C_"
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"
MATHEMATICAL_OPERATION = ["add", "sub", "neg"]
COMPARE_OPERATION = ["eq", "gt", "lt"]
LOGICAL_OPERATION = ["and", "or", "not"]


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    # initialize objects
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    code_writer.set_file_name(input_filename)
    # translation
    parser.advance()
    while parser.has_more_commands():
        if parser.command_type() == ARITHMETIC_COMMAND:
            handle_arithmetic_command(code_writer, parser)
        # memory access commands (push/pop)
        else:
            handle_memory_access_command(code_writer, parser)
        parser.advance()
    last_instruction_type = parser.command_type()
    if last_instruction_type == ARITHMETIC_COMMAND:
        handle_arithmetic_command(code_writer, parser)
    # memory access commands (push/pop)
    else:
        handle_memory_access_command(code_writer, parser)



def handle_memory_access_command(code_writer: CodeWriter, parser: Parser) -> None:
    command = parser.command_type()
    segment = parser.arg1()
    index = parser.arg2()
    code_writer.write_push_pop(command, segment, index)


def handle_arithmetic_command(code_writer: CodeWriter, parser: Parser) -> None:
    command = parser.arg1()
    switch_command = {ADD: code_writer.add, SUB: code_writer.sub, NEG: code_writer.neg, EQ: code_writer.eq,
                      GT: code_writer.gt, LT: code_writer.lt, AND: code_writer.and_, OR: code_writer.or_,
                      NOT: code_writer.not_}
    command_to_execute = switch_command[command]
    command_to_execute()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
