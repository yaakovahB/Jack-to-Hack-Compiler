

class SymbolTable:

    def __init__(self):
        """
        creates a new empty symbol table
        """
        self.class_table = {}
        self.subroutine_table = {}
        self.arg_counter = 0
        self.var_counter = 0
        self.static_counter = 0
        self.field_counter = 0
        self.if_counter = 0
        self.while_counter = 0

    def start_subroutine(self):
        """
        starts a new subroutine scope (i.e., resets/clears the subroutine's symbol table)
        :return: void
        """
        self.subroutine_table.clear()

        self.var_counter = 0
        self.arg_counter = 0
        self.if_counter = 0
        self.while_counter = 0

    def define(self, name, type_, kind):
        """
        defines a new identifier of a given name, type, and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope
        :param name: string
        :param type_: string
        :param kind: STATIC, FIELD, ARG, or VAR
        :return: void
        """
        if kind == 'static':  # class scope
            self.class_table[name] = (type_, 'static', self.static_counter)
            self.static_counter += 1
        elif kind == 'field':  # class scope
            self.class_table[name] = (type_, 'field', self.field_counter)
            self.field_counter += 1
        elif kind == 'arg':  # subroutine scope
            self.subroutine_table[name] = (type_, 'arg', self.arg_counter)
            self.arg_counter += 1
        elif kind == 'var':  # subroutine scope
            self.subroutine_table[name] = (type_, 'var', self.var_counter)
            self.var_counter += 1
        else:
            raise Exception(f'{kind} is not a legal kind in the Jack Grammar')

    def kind_of(self, name):
        """
        returns the 'kind' of the named identifier in the current scope. If the identifier is unknown in the current
        scope, returns NONE
        :param name: string
        :return: STATIC, FIELD, ARG, VAR, NONE
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][1]
        elif name in self.class_table:
            return self.class_table[name][1]
        else:
            return None

    def type_of(self, name):
        """
        returns the 'type' of the named identifier in the current scope
        :param name: string
        :return: string
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][0]
        elif name in self.class_table:
            return self.class_table[name][0]
        else:
            raise Exception(f'{name} is not a legal kind in the Jack Grammar')

    def index_of(self, name):
        """
        returns the 'index' assigned to the named identifier
        :param name: string
        :return: int
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][2]
        elif name in self.class_table:
            return self.class_table[name][2]
        else:
            raise Exception(f'{name} is not a legal kind in the Jack Grammar')

    def defined(self, name):
        if name in self.subroutine_table or name in self.class_table:
            return True
        else:
            return False
