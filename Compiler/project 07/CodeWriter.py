"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
TRUE = 0
FALSE = -1
PUSH = "C_PUSH"
POP = "C_POP"
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"
SHIFT_LEFT = "shiftleft"
SHIFT_RIGHT = "shiftright"
CONSTANT = "constant"
LOCAL = "local"
ARGUMENT = "argument"
THIS = "this"
THAT = "that"
POINTER = "pointer"
STATIC = "static"
TEMP = "temp"
TEMP_REGISTER = "R5"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_file = output_stream
        self.filename = ""
        self.comp_num = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = filename

    def decrement_stack(self):
        """
        sp--
        """
        self.output_file.write("@SP\nM=M-1\n")


    def increment_stack(self):
        """
        sp++
        """
        self.output_file.write("@SP\nM=M+1\n")


    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """

        switch = {ADD: self.add, SUB: self.sub, NEG: self.neg,
                EQ: self.eq, GT: self.gt, LT: self.lt,
                  AND: self.and_, OR: self.or_, NOT: self.not_}

        activate_command = switch.get(command)
        activate_command()


    def pop_from_stack(self):
        """
        Writes in Assembly the commands to get the last variable from the stack.
        """
        self.output_file.write("//pop from stack:\n")
        self.decrement_stack()
        self.output_file.write("@SP\nA=M\nD=M\n")


    def push_to_stack(self):
        """
        Writes in Assembly the commands to push and arithmetic result to the abstract stack.
        """
        self.output_file.write("//push to stack:\n")
        self.output_file.write("@SP\nA=M\nM=D\n")
        self.increment_stack()


    def add(self):
        """
        Writes in Assembly the addition commands.
        """
        self.pop_from_stack()
        self.decrement_stack()
        self.output_file.write("//add:\n"
                               "@SP\nA=M\nD=D+M\n")
        self.push_to_stack()

    def sub(self):
        """
        Writes in Assembly the subtraction commands.
        """
        self.pop_from_stack()
        self.decrement_stack()
        self.output_file.write("//sub:\n"
                               "@SP\nA=M\nD=M-D\n")
        self.push_to_stack()

    def neg(self):
        """
        Writes in Assembly the neg commands, multiply the arg bu (-1)
        """
        self.pop_from_stack()
        self.output_file.write("//neg:\n"
                               "D=-D\n")
        self.push_to_stack()

    def eq(self):
        """
        Writes in Assembly the equal func, checks if x==y.
        """
        self.pop_from_stack()
        self.decrement_stack()
        self.output_file.write("//equal value:\n"
                               "@SP\nA=M\nD=M-D\n")
        self.output_file.write("//check if equal:\n"
                               "@COMPARE{}".format(self.comp_num)+"\nD;JEQ\nD=0\n@END_COMPARE{}".format(self.comp_num)+
                               "\n0;JMP\n")
        self.output_file.write("//equal labels:\n"
                               "(COMPARE{})".format(self.comp_num)+
                               "\nD=-1\n"+"(END_COMPARE{})".format(self.comp_num)+"\n")
        self.comp_num += 1
        self.push_to_stack()

    def gt(self):
        """
        Writes in Assembly the GT func, checks if x>y (the stack holds x before y).
        """
        self.pop_from_stack()
        self.output_file.write("//gt process - put y in R14:\n"
                               "@R14\nM=D\n")
        self.pop_from_stack()
        self.output_file.write("//put x in R15:\n"
                               "@R15\nM=D")
        self.output_file.write("//check if X > 0 or X < 0\n"
                               "@R15\nD=M\n"+"@X_IS_POSITIVE{}".format(self.comp_num)+
                               "\nD;JGT\n"+"@X_IS_NEGATIVE{}".format(self.comp_num)+"\nD;JLT\n")

        self.output_file.write("(X_IS_POSITIVE{})".format(self.comp_num)+
                               "\n@R14\nD=M\n"+"@TRUE_CASE{}".format(self.comp_num)+
                               "\nD;JLT\n"+"@SUBTRACTION{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("(X_IS_NEGATIVE{})".format(self.comp_num)+
                               "\n@R14\nD=M\n"+"@FALSE_CASE{}".format(self.comp_num)+
                               "\nD;JGT\n"+"@SUBTRACTION{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("(TRUE_CASE{})".format(self.comp_num)+"\nD=-1\n"+"@END{}".format(self.comp_num)+
                               "\n0;JMP\n")
        self.output_file.write("(FALSE_CASE{})".format(self.comp_num)+"\nD=0\n"+"@END{}".format(self.comp_num)+
                               "\n0;JMP\n")
        self.output_file.write("//subtraction x-y:\n"+"(SUBTRACTION{})".format(self.comp_num)+"\n"
                               "@R15\nD=M\n@R14\nD=D-M\n"+"@TRUE_CASE{}".format(self.comp_num)+
                               "\nD;JGT\n"+"@FALSE_CASE{}".format(self.comp_num)+
                               "\n0;JMP\n"+"(END{})".format(self.comp_num)+"\n")
        self.comp_num += 1
        self.push_to_stack()

    def lt(self):
        """
        Writes in Assembly the GL func, checks if x<y (the stack holds x before y).
        """
        self.pop_from_stack()
        self.output_file.write("//lt process: put y in R14:\n"
                               "@R14\nM=D\n")

        self.pop_from_stack()
        self.output_file.write("//put x in R15:\n"
                               "@R15\nM=D\n")
        self.output_file.write("//check if X < 0 or X > 0:\n"
                               "@R15\nD=M\n"+"@X_IS_POSITIVE{}".format(self.comp_num)+
                               "\nD;JGT\n"+"@X_IS_NEGATIVE{}".format(self.comp_num)+"\nD;JLT\n")
        self.output_file.write("(X_IS_POSITIVE{})".format(self.comp_num)+
                               "\n@R14\nD=M\n"+"@FALSE_CASE{}".format(self.comp_num)+
                               "\nD;JLT\n"+"@SUBTRACTION{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("(X_IS_NEGATIVE{})".format(self.comp_num)+
                               "\n@R14\nD=M\n"+"@TRUE_CASE{}".format(self.comp_num)+
                               "\nD;JGT\n"+"@SUBTRACTION{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("(TRUE_CASE{})".format(self.comp_num)+
                               "\nD=-1\n"+"@END{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("(FALSE_CASE{})".format(self.comp_num)+"\nD=0\n"+
                               "@END{}".format(self.comp_num)+"\n0;JMP\n")
        self.output_file.write("//subtraction x-y:\n"+"(SUBTRACTION{})".format(self.comp_num)+"\n"
                               "@R15\nD=M\n@R14\nD=D-M\n"+"@TRUE_CASE{}".format(self.comp_num)+
                               "\nD;JLT\n"+"@FALSE_CASE{}".format(self.comp_num)+
                               "\n0;JMP\n"+"(END{})".format(self.comp_num)+"\n")
        self.comp_num += 1
        self.push_to_stack()

    def and_(self):
        """
        Writes in Assembly the and func, Writes False if x==0 or y==0 (or both), TRUE otherwise.
        """
        self.pop_from_stack()
        self.decrement_stack()
        self.output_file.write("//and:\n"
                               "@SP\nA=M\nD=D&M\n")
        self.push_to_stack()


    def or_(self):
        """
        Writes in Assembly the or func, Writes False if x==0 and y==0, TRUE otherwise.
        """
        self.pop_from_stack()
        self.decrement_stack()
        self.output_file.write("//or:\n"
                               "@SP\nA=M\nD=D|M\n")
        self.push_to_stack()


    def not_(self):
        """
        Writes in Assembly the not func, Writes (!var).
        """
        self.pop_from_stack()
        self.output_file.write("//not:\n"
                               "D=!D\n")
        self.push_to_stack()

    def shift_left(self):
        """
        Writes in Assembly the shift_left func.
        """
        self.pop_from_stack()
        self.output_file.write("//shift left:\n"
                               "D=D<<\n")
        self.push_to_stack()

    def shift_right(self):
        """
        Writes in Assembly the shift_right func.
        """
        self.pop_from_stack()
        self.output_file.write("//shift right:\n"
                               "D=D>>\n")
        self.push_to_stack()





    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        switch_segment = {LOCAL: "LCL", ARGUMENT: "ARG", THIS: "THIS",
                  THAT: "THAT", TEMP: TEMP_REGISTER}
        switch_command = {PUSH: self.push_command, POP: self.pop_command}
        command_to_execute = switch_command[command]
        if segment == CONSTANT:
            self.push_constant(index)
        elif segment == STATIC:
            if command == PUSH:
                self.push_static(index, self.filename)
            else:
                self.pop_static(index, self.filename)
        elif segment == POINTER:
            if index == 0:
                self.change_this(command)
            else:
                self.change_that(command)
        else:
            chosen_segment = switch_segment[segment]
            command_to_execute(chosen_segment, index)


    def change_this(self, command):
        """
        Push to SP the address that is stored in THIS cell, or pop from SP a new value for THIS cell.
        """
        if command == PUSH:
            self.output_file.write("//get THIS address:\n"
                                   "@R3\nD=M\n")
            self.push_to_stack()
        else:
            self.pop_from_stack()
            self.output_file.write("@R3\nM=D\n")

    def change_that(self, command):
        """
        Push to SP the address that is stored in THAT cell, or pop from SP a new value for THAT cell.
        """
        if command == PUSH:
            self.output_file.write("//get THAT address:\n"
                                   "@R4\nD=M\n")
            self.push_to_stack()
        else:
            self.pop_from_stack()
            self.output_file.write("@R4\nM=D\n")



    def store_addr_in_R13(self, segment: str, index: int):
        """
        Helper function of "pop_command" and "push_command" function.
         stores an address in R13 cell.
        """
        self.output_file.write("//find the exact address in segment:\n"
                               "@" + segment + "\nD=M\n@" + str(index) + "\nA=D+A\n")
        self.output_file.write("//store the address in R13:\n"
                               "D=A\n@R13\nM=D")

    def push_constant(self, index: int):
        #*sp = index
        self.output_file.write("@"+str(index)+"\nD=A\n@SP\nA=M\nM=D\n")

        #sp++
        self.increment_stack()

    def pop_static(self, index: int, filename: str):
        self.pop_from_stack()  # D contains the poped value.
        self.output_file.write("//write to static memory:\n"
                               "@" + filename + "." + str(index) + "\nM=D")

    def push_static(self, index: int, filename: str):
        self.output_file.write("//write to stack from static memory:\n"
                               "@" + filename + "." + str(index) + "\nD=M")
        self.push_to_stack()

    def push_command(self, segment, index):
        if segment == TEMP_REGISTER:
            self.output_file.write("//get temp address:\n"
                                   "@R" + str(5 + index) + "\nD=M\n")
        else:
            self.store_addr_in_R13(segment, index)
            self.output_file.write("//get value from address:\n"
                               "@R13\nA=M\nD=M\n")
        self.push_to_stack()

    def pop_command(self, segment, index):
        if segment == TEMP_REGISTER:
            self.output_file.write("//get temp address:\n"
                                   "@R" + str(5 + index) + "\n")
            self.output_file.write("//store the address in R13:\n"
                                   "D=A\n@R13\nM=D")

        else:
            self.store_addr_in_R13(segment, index)

        self.pop_from_stack()
        self.output_file.write("//write to segment:\n"
                               "@R13\nA=M\nM=D\n")


    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
