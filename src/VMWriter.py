import pathlib


class VMWriter:
    """
    output module for generating VM code.
    Emits VM commands into a file, using the VM command syntax
    """
    def __init__(self, path_):
        """
        creates a new file and prepares it for writing
        :param output_file:
        """
        self.output_file = path_

    def write_push(self, segment, index):
        """
        writes a VM push command
        :param segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        :param index: int
        :return: void
        """
        self.output_file.write(f'push {segment} {index}\n')

    def write_pop(self, segment, index):
        """
        writes a VM pop command
        :param segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        :param index: int
        :return: void
        """
        self.output_file.write(f'pop {segment} {index}\n')

    def write_arithmetic(self, command):
        """
        writes a VM arithmetic command
        :param command:
        :return: void
        """
        dict_ = {
            '+': 'add',
            '-': 'sub',
            # '': 'neg',
            '=': 'eq',
            '>': 'gt',
            '<': 'lt',
            '&': 'and',
            '|': 'or',
            '~': 'not',
            '*': 'call Math.multiply 2',
            '/': 'call Math.divide 2'
        }
        if command in dict_:
            command = dict_[command]
        self.output_file.write(f'{command}\n')

    def write_label(self, label):
        """
        writes a VM label command
        :param label: string
        :return: void
        """
        self.output_file.write(f'label {label}\n')

    def write_goto(self, label):
        """
        writes a VM goto command
        :param label: string
        :return: void
        """
        self.output_file.write(f'goto {label}\n')

    def write_if(self, label):
        """
        writes a VM if-goto command
        :param label: string
        :return: void
        """
        self.output_file.write(f'if-goto {label}\n')

    def write_call(self, name, n_args):
        """
        writes a VM call command
        :param name: string
        :param n_args: int
        :return: void
        """
        self.output_file.write(f'call {name} {n_args}\n')

    def write_function(self, name, n_locals):
        """
        writes a VM function command
        :param name: string
        :param n_locals: int
        :return: void
        """
        self.output_file.write(f'function {name} {n_locals}\n')

    def write_return(self):
        """
        writes a VM return command
        :return: void
        """
        self.output_file.write('return\n')

    def close(self):
        """
        closes the output file
        :return:
        """
        self.output_file.close()
