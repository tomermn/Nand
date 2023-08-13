"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

TYPE = 0
KIND = 1
INDEX = 2


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_symbol_table = {}
        self.subroutine_symbol_table = {}
        self.kind_counter_switch = {"STATIC": 0, "FIELD": 0,
                                    "ARG": 0, "VAR": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's
        symbol table).
        """
        self.subroutine_symbol_table.clear()
        self.kind_counter_switch["ARG"] = 0
        self.kind_counter_switch["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns
        it a running index. "STATIC" and "FIELD" identifiers have a class scope,
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        counter = self.kind_counter_switch[kind]
        if kind in ["STATIC", "FIELD"]:
            self.class_symbol_table[name] = [type, kind, counter]
            self.kind_counter_switch[kind] += 1
        else:
            self.subroutine_symbol_table[name] = [type, kind, counter]
            self.kind_counter_switch[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in
            the current scope.
        """
        return_val = self.kind_counter_switch[kind]
        return return_val

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """

        if name in self.subroutine_symbol_table:
            return_value = self.subroutine_symbol_table[name][KIND]
            if return_value == "VAR":
                return "local"
            elif return_value == "ARG":
                return "argument"
            else:
                return return_value.lower()
        elif name in self.class_symbol_table:
            return self.class_symbol_table[name][KIND]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][TYPE]
        return self.subroutine_symbol_table[name][TYPE]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][INDEX]
        return self.subroutine_symbol_table[name][INDEX]
