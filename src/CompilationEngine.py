import symbolTable
import VMWriter


class CompilationEngine:
    """
    recursive top-down compilation engine. Reads its input from a jackTokenizer and writes its output into a vm writer.
    If xxx is a part of an expression and thus has a value, the emitted code should compute this value and leave it at
    the top of the VM stack
    """

    def __init__(self, tokenizer_, path_):
        """
        returns a new compilation engine with the given input and output. Next routine called must be compile_class()
        :param tokenizer_: tokenizer with a list of all the tokens needed to compile a file
        :param path_: the path to the output file that should be written to
        """
        self.tokenizer = tokenizer_
        self.symbol_table = symbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(path_)
        self.class_name = ""

    def compile_class(self):

        self.advance_tokenizer(Exception('file empty'))

        # 'class'
        if self.tokenizer.keyword() != 'class':
            raise ValueError('Jack specification mandates that the code in each file must be contained in a class')
        self.advance_tokenizer(ValueError('According to the syntax of the Jack language, \'className\' is expected'))

        self.class_name = self.tokenizer.identifier()

        # className
        self.compile_identifier()

        # '{'
        self.compile_symbol('{')

        # classVarDec
        while self.tokenizer.keyword() == 'static' or self.tokenizer.keyword() == 'field':
            self.compile_class_var_dec()

        # 'subroutineDec'
        while self.tokenizer.keyword() == 'constructor' or self.tokenizer.keyword() == 'function' or \
                self.tokenizer.keyword() == 'method':
            self.compile_subroutine()

        # '}'
        # not calling compile_symbol('}') bc it advances the tokenizer at the end of the method & we don't want it now
        if self.tokenizer.symbol() != '}':
            raise ValueError('According to the syntax of the Jack language, \'}\' is expected')

        if self.tokenizer.has_more_tokens():
            raise Exception('According to the syntax of Jack language, there should be no code after class definition')

    def compile_class_var_dec(self):
        """
        compiles a static declaration or a field declaration
        :return:
        """
        kind = self.tokenizer.keyword()

        # ('static'|'field')
        if not (self.tokenizer.keyword() == 'static' or self.tokenizer.keyword() == 'field'):
            raise ValueError('According to the syntax of the Jack language, \'static\' or \'field\' is expected ')
        self.advance_tokenizer(ValueError('According to the syntax of the Jack language, \'type\' is expected'))

        type_ = self.tokenizer.keyword()

        # type
        self.compile_type()

        name = self.tokenizer.identifier()
        # varName
        self.compile_identifier()

        self.symbol_table.define(name, type_, kind)

        # (,varName)*
        while self.tokenizer.symbol() == ',':
            self.advance_tokenizer(ValueError('According to the syntax of the Jack language, \'varName\' is expected'))
            name = self.tokenizer.identifier()
            self.compile_identifier()
            self.symbol_table.define(name, type_, kind)

        # ;
        self.compile_symbol(';')

    def compile_subroutine(self):
        """
        compiles a complete method, function, or constructor
        :return:
        """

        function_type = self.tokenizer.keyword()
        # 'constructor'|'function'|'method'
        if self.tokenizer.keyword() != 'constructor' and self.tokenizer.keyword() != 'function' and \
                self.tokenizer.keyword() != 'method':
            raise ValueError('\'constructor\', \'function\', or \'method\' is expected ')
        self.advance_tokenizer(ValueError('\'void\' or \'type\' is expected'))

        # 'void'|type
        if self.tokenizer.keyword() == 'void':
            self.advance_tokenizer(ValueError('\'subroutineName\' is expected'))
        else:
            self.compile_type()

        name = self.tokenizer.identifier()
        # subroutineName
        self.compile_identifier()

        subroutine_name = f'{self.class_name}.{name}'

        self.symbol_table.start_subroutine()

        # '('
        self.compile_symbol('(')

        if function_type == 'method':
            self.symbol_table.define('this', 'self', 'arg')

        # parameterList
        self.compile_parameter_list()

        # ')'
        self.compile_symbol(')')

        # subroutineBody
        self.compile_subroutine_body(subroutine_name, function_type)

    def compile_subroutine_body(self, subroutine_name, function_type):

        # '{'
        self.compile_symbol('{')

        # (varDec)*
        while self.tokenizer.keyword() == 'var':
            self.compile_var_dec()

        self.vm_writer.write_function(subroutine_name, self.symbol_table.var_counter)
        if function_type == 'method':
            # push self and pop it to pointer 0 - this.
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
        elif function_type == 'constructor':
            self.vm_writer.write_push('constant', self.symbol_table.field_counter)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)

        # statements
        self.compile_statements(subroutine_name)

        # '}'
        self.compile_symbol('}')

    def compile_parameter_list(self):
        """
        compiles a (possibly empty) parameter list, not including the enclosing "()"
        :return:
        """

        # ((type varName) (',' type varName)*)?

        if self.tokenizer.symbol() == ')':
            return

        while True:
            type_for_symbol_table = self.tokenizer.keyword()
            # type
            self.compile_type()
            name_for_symbol_table = self.tokenizer.identifier()
            # varName
            self.compile_identifier()

            self.symbol_table.define(name_for_symbol_table, type_for_symbol_table, 'arg')

            if self.tokenizer.symbol() == ')':
                break

            # (',' type varName)*
            self.compile_symbol(',')

    def compile_var_dec(self):
        """
        compiles a var declaration
        :return:
        """
        # 'var'
        if self.tokenizer.keyword() != 'var':
            raise ValueError('According to the syntax of the Jack language, \'var\' is expected ')
        self.advance_tokenizer(ValueError('According to the syntax of the Jack language, \'type\' is expected'))

        type_for_symbol_table = self.tokenizer.keyword()
        # type
        self.compile_type()
        name_for_symbol_table = self.tokenizer.identifier()
        # varName
        self.compile_identifier()

        self.symbol_table.define(name_for_symbol_table, type_for_symbol_table, 'var')

        # (,varName)*
        while self.tokenizer.symbol() == ',':
            self.advance_tokenizer(ValueError('According to the syntax of the Jack language, \'varName\' is expected'))
            name_for_symbol_table = self.tokenizer.identifier()
            self.compile_identifier()

            self.symbol_table.define(name_for_symbol_table, type_for_symbol_table, 'var')

        # ;
        self.compile_symbol(';')

    def compile_identifier(self):
        if self.tokenizer.token_type() != 'identifier':
            raise ValueError('According to the syntax of the Jack language, \'identifier\' is expected')
        self.advance_tokenizer(ValueError('\'another tokens\' is expected'))

    def compile_symbol(self, symbol):
        """
        this method was passed a specific symbol for debugging purposes
        :param symbol:
        :return:
        """
        if self.tokenizer.symbol() != symbol:
            raise ValueError(f'According to the syntax of the Jack language, \'{symbol}\' is expected')
        self.advance_tokenizer(ValueError('\'another tokens\' is expected'))

    def compile_type(self):
        """
        type: 'int'|'char'|'boolean'|className
        :return:
        """
        if not (self.tokenizer.token_type() == 'identifier' or self.tokenizer.keyword() == 'int' or \
                self.tokenizer.keyword() == 'char' or self.tokenizer.keyword() == 'boolean'):
            raise ValueError('\'int\', \'char\', \'boolean\' or \'className\' is expected ')
        self.advance_tokenizer(ValueError('\'another tokens\' is expected'))

    def compile_statements(self, subroutine_name):
        """
        compiles a sequence of statements, not including the "{}"
        :return:
        """
        if self.tokenizer.keyword() != 'let' and self.tokenizer.keyword() != 'do' and \
                self.tokenizer.keyword() != 'while' and self.tokenizer.keyword() != 'if' and \
                self.tokenizer.keyword() != 'return':
            return
        while self.tokenizer.keyword() == 'let' or self.tokenizer.keyword() == 'do' or \
                self.tokenizer.keyword() == 'while' or self.tokenizer.keyword() == 'if' or \
                self.tokenizer.keyword() == 'return':
            if self.tokenizer.keyword() == 'let':
                self.compile_let()
            elif self.tokenizer.keyword() == 'if':
                self.compile_if(subroutine_name)
            elif self.tokenizer.keyword() == 'while':
                self.compile_while(subroutine_name)
            elif self.tokenizer.keyword() == 'do':
                self.compile_do()
            elif self.tokenizer.keyword() == 'return':
                self.compile_return()

    def compile_do(self):
        """
        compiles a do statement
        :return:
        """
        # do
        if self.tokenizer.keyword() != 'do':
            raise ValueError('\'do\' keyword is expected ')
        self.advance_tokenizer(ValueError('\'subroutineCall\' is expected'))

        # subroutineCall
        self.compile_subroutine_call()

        # pop off the return value bc we don't need it
        self.vm_writer.write_pop('temp', 0)

        # ;
        self.compile_symbol(';')

    def compile_let(self):
        """
        compiles a let statement
        :return:
        """
        # let
        if self.tokenizer.keyword() != 'let':
            raise ValueError('\'let\' keyword is expected ')
        self.advance_tokenizer(ValueError('\'varName\' is expected'))

        name = self.tokenizer.identifier()
        # varName
        self.compile_identifier()

        # ('[' expression ']' ) ?
        if self.tokenizer.symbol() == '[':

            # '['
            self.compile_symbol('[')

            # expression
            self.compile_expression()

            # ']'
            self.compile_symbol(']')

            # push address of array onto the stack
            if self.symbol_table.kind_of(name) == 'var':
                self.vm_writer.write_push('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'static':
                self.vm_writer.write_push('static', self.symbol_table.index_of(name))
            else:  # field
                self.vm_writer.write_push('this', self.symbol_table.index_of(name))

            #  arr + index
            self.vm_writer.write_arithmetic('add')

            # '='
            self.compile_symbol('=')

            # expression
            self.compile_expression()

            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:

            # get value to put into variable

            # '='
            self.compile_symbol('=')

            # expression
            self.compile_expression()

            # put value into variable
            if self.symbol_table.kind_of(name) == 'var':
                self.vm_writer.write_pop('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.vm_writer.write_pop('argument', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'static':
                self.vm_writer.write_pop('static', self.symbol_table.index_of(name))
            else:  # field
                self.vm_writer.write_pop('this', self.symbol_table.index_of(name))
        # ';'
        self.compile_symbol(';')

    def compile_while(self, subroutine_name):
        """
        compiles a while statement
        :return:
        """
        # while
        if self.tokenizer.keyword() != 'while':
            raise ValueError('\'while\' keyword is expected ')
        self.advance_tokenizer(ValueError('\'(\' is expected'))

        # '('
        self.compile_symbol('(')

        self.vm_writer.write_label(f'WHILE_LOOP{self.symbol_table.while_counter}')
        temp = self.symbol_table.while_counter
        self.symbol_table.while_counter += 1

        # expression
        self.compile_expression()

        # negate the expression
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(f'FINISH_WHILE{temp}')

        # ')'
        self.compile_symbol(')')

        # '{'
        self.compile_symbol('{')

        # statements
        self.compile_statements(subroutine_name)

        self.vm_writer.write_goto(f'WHILE_LOOP{temp}')

        # '}'
        self.compile_symbol('}')

        self.vm_writer.write_label(f'FINISH_WHILE{temp}')

    def compile_return(self):
        """
        compiles a return statement
        :return:
        """

        # return
        if self.tokenizer.keyword() != 'return':
            raise ValueError('\'return\' keyword is expected ')
        self.advance_tokenizer(ValueError('\';\' is expected'))

        # expression?
        if self.tokenizer.symbol() != ';':
            self.compile_expression()
        else:
            self.vm_writer.write_push('constant', 0)

        self.vm_writer.write_return()

        # ;
        self.compile_symbol(';')

    def compile_if(self, subroutine_name):
        """
        compiles an if statement, possibly with a trailing else clause
        :return:
        """
        temp = self.symbol_table.if_counter
        # if
        if self.tokenizer.keyword() != 'if':
            raise ValueError('\'if\' keyword is expected ')
        self.advance_tokenizer(ValueError('\'(\' is expected'))

        self.symbol_table.if_counter += 1

        # '('
        self.compile_symbol('(')

        # expression
        self.compile_expression()

        # ')'
        self.compile_symbol(')')

        self.vm_writer.write_arithmetic("not")

        self.vm_writer.write_if(f'ELSE{temp}')

        # '{'
        self.compile_symbol('{')

        # statements
        self.compile_statements(subroutine_name)

        # '}'
        self.compile_symbol('}')

        # GOTO END
        self.vm_writer.write_goto(f'END{temp}')
        self.vm_writer.write_label(f'ELSE{temp}')

        # ('else' '{' statements '}')?
        if self.tokenizer.token_type() == 'keyword' and self.tokenizer.keyword() == 'else':

            # else
            self.advance_tokenizer(ValueError('\'{\' is expected'))

            # '{'
            self.compile_symbol('{')

            # statements
            self.compile_statements(subroutine_name)

            # '}'
            self.compile_symbol('}')

        self.vm_writer.write_label(f'END{temp}')

    def compile_expression(self):
        """
        compiles an expression
        :return:
        """
        # term
        self.compile_term()

        while self.tokenizer.token_type() == 'symbol' \
                and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:

            op = self.tokenizer.symbol()

            self.compile_symbol(self.tokenizer.symbol())

            self.compile_term()

            self.vm_writer.write_arithmetic(op)

            # (op term)*

    def compile_term(self):
        """
        compiles a term. A single look-ahead token is used to distinguish between a variable, an array entry,
        and a subroutine call.
        :return:
        """

        # integerConstant | stringConstant | keywordConstant | varName |
        # varName'['expression']' | subroutineCall |'('expression')' | unaryOp term

        # unaryOp term
        if self.tokenizer.token_type() == 'symbol' and (
                self.tokenizer.symbol() == '-' or self.tokenizer.symbol() == '~'):
            dict_ = {'-': 'neg', '~': 'not'}
            op = self.tokenizer.symbol()
            self.compile_symbol(self.tokenizer.symbol())
            self.compile_term()
            self.vm_writer.write_arithmetic(dict_[op])
        # '('expression')'
        elif self.tokenizer.token_type() == 'symbol' and self.tokenizer.symbol() == '(':
            self.compile_symbol('(')
            self.compile_expression()
            self.compile_symbol(')')
        # integerConstant
        elif self.tokenizer.token_type() == 'integerConstant':
            num = self.tokenizer.int_val()
            self.advance_tokenizer(ValueError('\'another tokens\' is expected'))
            self.vm_writer.write_push('constant', num)
        # stringConstant
        elif self.tokenizer.token_type() == 'stringConstant':
            str_ = self.tokenizer.string_val()
            self.advance_tokenizer(ValueError('\'another tokens\' is expected'))
            self.vm_writer.write_push('constant', len(str_))
            self.vm_writer.write_call("String.new", 1)
            for letter in str_:
                self.vm_writer.write_push('constant', ord(letter))
                self.vm_writer.write_call("String.appendChar", 2)
        # keywordConstant
        elif self.tokenizer.token_type() == 'keyword':
            keyword = self.tokenizer.keyword()
            self.advance_tokenizer(ValueError('\'another tokens\' is expected'))
            if keyword == "this":
                self.vm_writer.write_push('pointer', 0)
            elif keyword == "true":
                self.vm_writer.write_push('constant', 1)
                self.vm_writer.write_arithmetic('neg')
            else:  # false/null
                self.vm_writer.write_push('constant', 0)
        # subroutineCall
        elif self.tokenizer.token_type() == 'identifier' and self.tokenizer.next_token_type() == 'symbol' \
                and (self.tokenizer.next_symbol() == '(' or self.tokenizer.next_symbol() == '.'):
            self.compile_subroutine_call()
        # varName
        elif self.tokenizer.token_type() == 'identifier':
            name = self.tokenizer.identifier()

            # varName'['expression']'
            if self.tokenizer.next_token_type() == 'symbol' and self.tokenizer.next_symbol() == '[':
                self.tokenizer.advance()
                # '['
                self.compile_symbol('[')

                # expression
                self.compile_expression()

                # ']'
                self.compile_symbol(']')

                if self.symbol_table.kind_of(name) == 'var':
                    self.vm_writer.write_push('local', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'arg':
                    self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'static':
                    self.vm_writer.write_push('static', self.symbol_table.index_of(name))
                else:
                    self.vm_writer.write_push('this', self.symbol_table.index_of(name))

                # arr + index
                self.vm_writer.write_arithmetic('add')

                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)

            else:
                self.advance_tokenizer(ValueError('\'another tokens\' is expected'))
                if self.symbol_table.kind_of(name) == 'var':
                    self.vm_writer.write_push('local', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'arg':
                    self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'static':
                    self.vm_writer.write_push('static', self.symbol_table.index_of(name))
                else:
                    self.vm_writer.write_push('this', self.symbol_table.index_of(name))

    def compile_expression_list(self) -> int:
        """
        compiles a (possibly empty) comma-separated list of expressions
        :return:
        """
        counter = 0
        # (expression(','expression)*)?
        if self.tokenizer.symbol() == ')':
            return 0

        # expression(','expression)*
        while True:
            # expression
            self.compile_expression()

            counter += 1  # maybe take this out?

            if self.tokenizer.symbol() == ')':
                break

            # ','
            self.compile_symbol(',')

        return counter

    def compile_subroutine_call(self):

        # subroutineName'('expressionList')' | (className|varName)'.'subroutineName'('expressionList')'
        if self.tokenizer.next_token_type() == 'symbol' and self.tokenizer.next_symbol() == '.':
            num_arguments = 0

            name = self.tokenizer.identifier()
            # (className|varName)
            self.compile_identifier()
            # '.'
            self.compile_symbol('.')
            function_name = self.tokenizer.identifier()

            self.compile_identifier()

            # '('
            self.compile_symbol('(')

            # if the method is being called on an object and not a class,the object will be a var in the symbol table
            if self.symbol_table.defined(name):
                num_arguments += 1  # need to pass the object that is calling the method (this)
                # push the object calling the method to the stack
                if self.symbol_table.kind_of(name) == 'var':
                    self.vm_writer.write_push('local', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'arg':
                    self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'static':
                    self.vm_writer.write_push('static', self.symbol_table.index_of(name))
                else:  # field
                    self.vm_writer.write_push('this', self.symbol_table.index_of(name))

            # expressionList
            num_arguments += self.compile_expression_list()

            # ')'
            self.compile_symbol(')')

            # if the method is being called on an object and not a class,the object will be a var in the symbol table
            if self.symbol_table.defined(name):
                name = self.symbol_table.type_of(name)

            self.vm_writer.write_call(f'{name}.{function_name}', num_arguments)

        else:
            function_name = self.tokenizer.identifier()
            # subroutineName
            self.compile_identifier()

            # push this
            self.vm_writer.write_push('pointer', 0)

            # '('
            self.compile_symbol('(')

            # expressionList
            num_arguments = self.compile_expression_list() + 1

            # ')'
            self.compile_symbol(')')

            self.vm_writer.write_call(f'{self.class_name}.{function_name}', num_arguments)

    def advance_tokenizer(self, exception):
        """
        advances the tokenizer if there are more tokens and raises and Exception if there are not and syntactically
        there needed to be
        :param exception: the exception that needs to be raised
        :return: nothing
        """
        if not self.tokenizer.has_more_tokens():
            raise exception
        self.tokenizer.advance()
