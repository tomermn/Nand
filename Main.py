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
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

C_COMMAND_INITIAL = "111"

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    first_pass(parser, symbol_table)
    parser.current_line = Parser.INITIAL_INDEX
    second_pass(parser, symbol_table, output_file)


def first_pass(parser: Parser, symbol_table: SymbolTable) -> None:
    parser.advance()
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            parser.num_of_labels += 1
            current_instruction = parser.symbol()
            parser.advance()
            address = parser.current_command - parser.num_of_labels
            symbol_table.add_entry(current_instruction, address)
        else:
            parser.advance()


def second_pass(parser: Parser, symbol_table: SymbolTable, output_file: typing.TextIO) -> None:
    parser.advance()
    while parser.has_more_commands():
        instruction_type = parser.command_type()
        if instruction_type == "A_COMMAND":
            command_binary_code = handle_a_command(parser, symbol_table)
            output_file.write(command_binary_code+"\n")
        elif instruction_type == "C_COMMAND":
            command_binary_code = handle_c_command(parser)
            output_file.write(command_binary_code+"\n")
        parser.advance()
    last_instruction_type = parser.command_type()

    if last_instruction_type == "A_COMMAND":
        command_binary_code = handle_a_command(parser, symbol_table)
        output_file.write(command_binary_code + "\n")
    elif last_instruction_type == "C_COMMAND":
        command_binary_code = handle_c_command(parser)
        output_file.write(command_binary_code+"\n")


def handle_a_command(parser: Parser, symbol_table: SymbolTable) -> str:
    a_symbol = parser.symbol()
    if a_symbol.isnumeric():
        int_address = int(a_symbol)

    elif symbol_table.contains(a_symbol):
        int_address = symbol_table.get_address(a_symbol)

    else:
        int_address = symbol_table.next_index
        symbol_table.next_index += 1
        symbol_table.add_entry(a_symbol, int_address)

    get_binary = lambda x, n: format(x, 'b').zfill(n)
    bin_address = get_binary(int_address, 16)
    return bin_address


def handle_c_command(parser: Parser) -> str:
    binary_initial = parser.is_shift()
    binary_dest = Code.dest(parser.dest())
    binary_comp = Code.comp(parser.comp())
    binary_jump = Code.jump(parser.jump())
    return binary_initial + binary_comp + binary_dest + binary_jump


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
