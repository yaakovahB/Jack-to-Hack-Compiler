
# reads input file (via a path) and gives access to each line without white spaces or comments


class Parser:

    # constructor - opens file at a given path and gives values to the class attributes
    def __init__(self, path):

        self.input_file_name = path.stem
        self.current_command = ""
        self.commands = []
        self.number_current_command = 0

        # fill self.commands with all the commands in the current file
        for line in path.read_text().splitlines():

            # get rid of comments and then strip the line of white spaces
            temp_line = line.partition("//")[0].strip()

            self.current_command = temp_line
            if self.command_type() is not None:
                self.commands.append(temp_line)

        self.current_command = ""

    # returns True or False, according to if there are more commands in the input file
    def has_more_commands(self):
        if self.number_current_command == len(self.commands):
            return False
        else:
            return True

    # increases self.number_current_command by 1, and self.current_command accordingly
    def advance(self):
        if not self.has_more_commands():
            return
        self.current_command = self.commands[self.number_current_command]
        self.number_current_command = self.number_current_command + 1

    # returns what kind of command it is
    def command_type(self):

        command = self.current_command

        if command == "":
            return None
        all_words_in_command = command.split()
        first_word = all_words_in_command[0]

        if first_word in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        elif first_word == 'push':
            return 'C_PUSH'
        elif first_word == 'pop':
            return 'C_POP'
        elif first_word == 'label':
            return 'C_LABEL'
        elif first_word == 'goto':
            return 'C_GOTO'
        elif first_word == 'if-goto':
            return 'C_IF'
        elif first_word == 'function':
            return 'C_FUNCTION'
        elif first_word == 'return':
            return 'C_RETURN'
        elif first_word == 'call':
            return 'C_CALL'
        else:
            return None

    # returns what kind of command it is if it is an arithmetic command, and otherwise returns which segment is used
    # this is not called if it is an arithmetic command, just covering edge cases
    def arg1(self):

        if self.command_type() == 'C_RETURN':
            return
        else:
            command = self.current_command
            all_words_in_command = command.split()

            # if there is only one word, it is an arithmetic command
            if len(all_words_in_command) == 1:
                return all_words_in_command[0]
            else:
                return all_words_in_command[1]

    # returns what kind of command it is if it is an arithmetic command, and otherwise returns the index
    # this is not called if it is an arithmetic command, just covering edge cases
    def arg2(self):
        if self.command_type() == 'C_RETURN':
            return
        else:
            command = self.current_command
            all_words_in_command = command.split()

            # if there is only one word, it is an arithmetic command
            if len(all_words_in_command) == 1:
                return all_words_in_command[0]
            else:
                return all_words_in_command[2]
