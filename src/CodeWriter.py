# reads in and translates vm commands into assembly commands and writes them to the output file


class CodeWriter:

    # constructor - opens output file and gives attributes values
    def __init__(self, path):

        file = path.open('w')

        self.output_file_name = path.stem
        self.output_file_path = file
        self.label_counter = 0
        self.current_input_file_name = ''
        self.function_call_number = 0

    # informs codeWriter that translation of new vm file is started
    def set_file_name(self, file_name):
        self.current_input_file_name = file_name

    # writes the arithmetic commands to the output file
    def write_arithmetic(self, command):

        asm_command = ''

        if command in ['add', 'sub', 'and', 'or']:
            asm_command += '//write_binary_command\n'
            asm_command += self.translate_binary_command(command)
        elif command in ['neg', 'not']:
            asm_command += '//write_unary_command\n'
            asm_command += self.translate_unary_command(command)
        elif command in ['gt', 'lt', 'eq']:
            asm_command += '//write_comparison_command\n'
            asm_command += self.translate_comparison_command(command)
            self.label_counter += 1

        self.output_file_path.write(asm_command)

    # writes all push and pop commands to the output file
    def write_push_pop(self, command, segment, index):

        asm_command = ''

        if command == 'push':
            asm_command += self.translate_push_command(segment, index, self.current_input_file_name)
        elif command == 'pop':
            asm_command += self.translate_pop_command(segment, index, self.current_input_file_name)

        self.output_file_path.write(asm_command)

    # writes the VM initialization (bootstrap code) .This code must be placed at the beginning of the output file
    def write_init(self):
        asm_command = self.translate_init(self)
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the label command
    def write_label(self, label):
        asm_command = f'({label}{self.label_counter})\n'
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the goto command
    def write_goto(self, label):
        asm_command = f'@{label}{self.label_counter}\n' \
                      '0;JMP\n'
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the if-goto command
    def write_if(self, label):
        asm_command = self.pop_to_d()
        asm_command += f'@{label}{self.label_counter}\n' \
                       'D;JNE\n'
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the call command
    # calls function, stating how manu arguments have been pushed onto the stack
    def write_call(self, function_name, num_args):

        asm_command = '//write_call\n'
        asm_command += self.translate_call(function_name, num_args)
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the return command and puts back previous stack
    def write_return(self):

        asm_command = '//write_return\n'

        # FRAME = LCL -> FRAME refers to subroutines local variables, arguments, etc. FRAME is a temp variable here
        asm_command += '@LCL\n' \
                       'D=M\n' \
                       '@FRAME\n' \
                       'M=D\n'
        # RET = *(FRAME-5) -> put return address in temp variable
        asm_command += 'D=M\n' \
                       '@5\n' \
                       'A=D-A\n' \
                       'D=M\n' \
                       '@RET\n' \
                       'M=D\n'
        # *ARG = pop() --> reposition return value for caller (to where ARG is)
        asm_command += self.pop_to_d()
        asm_command += '@ARG\n' \
                       'A=M\n' \
                       'M=D\n'
        # SP = ARG+1 --> restore SP of caller (restore the stack)
        asm_command += '@ARG\n' \
                       'D=M\n' \
                       '@SP\n' \
                       'M=D+1\n'
        # THAT = *(FRAME-1) -- > restore THAT of caller
        asm_command += '@FRAME\n' \
                       'D=M\n' \
                       '@1\n' \
                       'A=D-A\n' \
                       'D=M\n' \
                       '@THAT\n' \
                       'M=D\n'
        # THIS = *(FRAME-2) -- > restore THIS of caller
        asm_command += '@FRAME\n' \
                       'D=M\n' \
                       '@2\n' \
                       'A=D-A\n' \
                       'D=M\n' \
                       '@THIS\n' \
                       'M=D\n'
        # ARG = *(FRAME-3) -- > restore ARG of caller
        asm_command += '@FRAME\n' \
                       'D=M\n' \
                       '@3\n' \
                       'A=D-A\n' \
                       'D=M\n' \
                       '@ARG\n' \
                       'M=D\n'
        # LCL = *(FRAME-4) -- > restore LCL of caller
        asm_command += '@FRAME\n' \
                       'D=M\n' \
                       '@4\n' \
                       'A=D-A\n' \
                       'D=M\n' \
                       '@LCL\n' \
                       'M=D\n'
        # goto RET --> go to return address in caller's code
        asm_command += '@RET\n' \
                       'A=M\n' \
                       '0;JMP\n'
        self.output_file_path.write(asm_command)

    # writes the assembly code that effects the function command
    # this is the code the function itself, that has 'num_locals' local variables
    def write_function(self, function_name, num_locals):

        asm_command = '//write_function\n'

        # (function_name)
        asm_command += f'({function_name})\n'

        # push 0 'num_locals' times
        for x in range(int(num_locals)):
            asm_command += self.translate_push_constant(0)

        self.output_file_path.write(asm_command)

    # translating (helper) functions

    def translate_binary_command(self, vm_op):

        asm_op = self.translate_op(vm_op)

        asm_code = '//Translate binary command\n'

        # move first number in stack into D
        asm_code += '@SP\n' \
                    'A=M-1\n' \
                    'D=M\n'

        # pop first number (decrement sp)
        asm_code += '@SP\n' \
                    'M=M-1\n'

        # replace second number in stack with answer
        asm_code += 'A=M-1\n' \
                    f'M=M{asm_op}D\n'

        return asm_code

    def translate_unary_command(self, vm_op):
        asm_op = self.translate_op(vm_op)

        asm_code = '//Translate unary command\n'

        asm_code += '@SP' + '\n' \
                            'A=M-1' + '\n' \
                                      f'M={asm_op}M\n'

        return asm_code

    def translate_comparison_command(self, vm_op):

        dictionary = {'eq': 'JEQ',
                      'gt': 'JGT',
                      'lt': 'JLT'}

        asm_code = '//Translate comparison command\n'

        asm_code += self.translate_binary_command('sub')
        asm_code += self.pop_to_d()
        asm_code += f'@TRUE{self.label_counter}\n' \
                    'D;' + dictionary[vm_op] + '\n' \
                                               '@0\n' \
                                               'D=A\n' \
                                               f'@PUSH_RESULT{self.label_counter}\n' \
                                               '0;JMP\n' \
                                               f'(TRUE{self.label_counter})\n' \
                                               '@1\n' \
                                               'D=A\n' \
                                               f'(PUSH_RESULT{self.label_counter})\n'
        asm_code += self.push_d_to_stack()
        asm_code += self.translate_unary_command('neg')

        return asm_code

    def translate_push_command(self, segment, index, input_file_name):

        asm_code = '//Translate push command\n'

        if segment in ['constant']:
            asm_code += self.translate_push_constant(index)

        if segment in ['static']:
            asm_code += self.translate_push_static(index, input_file_name)

        if segment in ['argument', 'local', 'this', 'that']:
            asm_code += self.translate_push_argument_local_this_that(segment, index)

        if segment in ['pointer', 'temp']:
            asm_code += self.translate_push_pointer_temp(segment, index)

        return asm_code

    def translate_push_constant(self, index):
        asm_code = f'@{index}\n' \
                   'D=A' + '\n'
        asm_code += self.push_d_to_stack()
        return asm_code

    # remind myself why this works the way it does!!
    def translate_push_static(self, index, file_name):
        asm_code = f'@{file_name}.{index}\n' \
                   'D=M' + '\n'
        asm_code += self.push_d_to_stack()
        return asm_code

    def translate_push_pointer_temp(self, segment, index):

        vm_to_asm_segment_dictionary = {'pointer': '3',
                                        'temp': '5'}

        asm_code = f'@{index}\n' \
                   'D=A\n' \
                   f'@{vm_to_asm_segment_dictionary[segment]}\n' \
                   'A=D+A\n' \
                   'D=M\n'
        asm_code += self.push_d_to_stack()
        return asm_code

    def translate_push_argument_local_this_that(self, segment, index):

        vm_to_asm_segment_dictionary = {'argument': 'ARG',
                                        'local': 'LCL',
                                        'this': 'THIS',
                                        'that': 'THAT'}

        asm_code = f'@{index}\n' \
                   'D=A' + '\n' \
                           f'@{vm_to_asm_segment_dictionary[segment]}\n' \
                           'A=D+M\n' \
                           'D=M\n'
        asm_code += self.push_d_to_stack()
        return asm_code

    def translate_pop_command(self, segment, index, input_file_name):

        asm_code = '//Translate pop command\n'

        if segment in ['static']:
            asm_code += self.translate_pop_static(index, input_file_name)

        if segment in ['argument', 'local', 'this', 'that']:
            asm_code += self.translate_pop_argument_local_this_that(segment, index)

        if segment in ['pointer', 'temp']:
            asm_code += self.translate_pop_pointer_temp(segment, index)

        return asm_code

    def translate_pop_static(self, index, input_file_name):

        asm_code = self.pop_to_d()
        asm_code += f'@{input_file_name}.{index}\n' \
                    'M=D' + '\n'

        return asm_code

    def translate_pop_pointer_temp(self, segment, index):

        vm_to_asm_segment_dictionary = {'pointer': '3',
                                        'temp': '5'}

        # get the address that we need to pop into
        asm_code = f'@{vm_to_asm_segment_dictionary[segment]}\n' \
                   'D=A\n' \
                   f'@{index}\n' \
                   'D=D+A\n'
        # store the address in a general purpose register
        asm_code += '@R13\n' \
                    'M=D\n'

        # pop value from the stack that needs to be stored in address
        asm_code += self.pop_to_d()

        # store D in the address that is currently stored in R13
        asm_code += '@R13\n' \
                    'A=M\n' \
                    'M=D\n'

        return asm_code

    # only thing diff in this function and one above it is D=M instead of D=A. Make this into one function!
    def translate_pop_argument_local_this_that(self, segment, index):

        vm_to_asm_segment_dictionary = {'argument': 'ARG',
                                        'local': 'LCL',
                                        'this': 'THIS',
                                        'that': 'THAT'}

        # get the address that we need to pop into
        asm_code = f'@{vm_to_asm_segment_dictionary[segment]}\n' \
                   'D=M\n' \
                   f'@{index}\n' \
                   'D=D+A\n' \
            # store the address in a general purpose register
        asm_code += '@R13\n' \
                    'M=D\n'

        # pop value from the stack that needs to be stored in address
        asm_code += self.pop_to_d()

        # store D in the address that is currently stored in R13
        asm_code += '@R13\n' \
                    'A=M\n' \
                    'M=D\n'

        return asm_code

        # helper functions

    @staticmethod
    def translate_init(self):

        # bootstrap code (sp=256 call sys.init)
        asm_command = '@256\n' \
                      'D=A\n' \
                      '@SP\n' \
                      'M=D\n'

        asm_command += self.translate_call("Sys.init", '0')

        return asm_command

    def translate_call(self, function_name, num_args):
        # push return address
        return_address = f'FUNCTION{self.function_call_number}'
        asm_command = f'@{return_address}\n' \
                      'D=A\n'
        asm_command += self.push_d_to_stack()
        # push LCL
        asm_command += '@LCL\n' \
                       'D=M\n'
        asm_command += self.push_d_to_stack()
        # push ARG
        asm_command += '@ARG\n' \
                       'D=M\n'
        asm_command += self.push_d_to_stack()
        # push THIS
        asm_command += '@THIS\n' \
                       'D=M\n'
        asm_command += self.push_d_to_stack()
        # push THAT
        asm_command += '@THAT\n' \
                       'D=M\n'
        asm_command += self.push_d_to_stack()
        # ARG = SP - m - 5 (reposition ARG, m = number of arguments)
        asm_command += '@SP\n' \
                       'D=M\n' \
                       '@5\n' \
                       'D=D-A\n' \
                       f'@{num_args}\n' \
                       'D=D-A\n' \
                       '@ARG\n' \
                       'M=D\n'
        # LCL = SP
        asm_command += '@SP\n' \
                       'D=M\n' \
                       '@LCL\n' \
                       'M=D\n'
        # goto f
        asm_command += f'@{function_name}\n' \
                       '0;JMP\n'
        # (return address)
        asm_command += f'({return_address})\n'

        self.function_call_number += 1

        return asm_command

    @staticmethod
    def push_d_to_stack():
        # push D into stack
        asm_code = '@SP\n' \
                   'A=M\n' \
                   'M=D\n'

        # advance sp
        asm_code += '@SP\n' \
                    'M=M+1\n'

        return asm_code

    # do I need to take into consideration popping when nothing is in stack? (underflow)
    @staticmethod
    def pop_to_d():
        # pop from stack into D
        asm_code = '@SP\n' \
                   'M=M-1\n' \
                   'A=M\n' \
                   'D=M\n'

        return asm_code

    @staticmethod
    def translate_op(op):
        dictionary = {'add': '+',
                      'sub': '-',
                      'and': '&',
                      'or': '|',
                      'not': '!',
                      'neg': '-'}

        return dictionary[op]

    # closes the output file
    def close(self):
        self.output_file_path.close()
