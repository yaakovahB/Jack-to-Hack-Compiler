import sys
import pathlib
import CodeWriter
import Parser


# TODO: go through all the functions and look for and handle edge cases!!!
# TODO: combine some functions with similar functionality

# translate the vm file to asm code and write it to the output file


def translate_file(path, code_writer):

    if str(path).endswith('.vm'):
        parser = Parser.Parser(path)
        while parser.has_more_commands():
            # need to have this at beginning of loop so that the first time we run through the loop, there is a command
            parser.advance()

            code_writer.set_file_name(parser.input_file_name)

            if parser.command_type() == 'C_ARITHMETIC':
                code_writer.write_arithmetic(parser.current_command)
            elif parser.command_type() == 'C_PUSH':
                code_writer.write_push_pop('push', parser.arg1(), parser.arg2())
            elif parser.command_type() == 'C_POP':
                code_writer.write_push_pop('pop', parser.arg1(), parser.arg2())
            elif parser.command_type() == 'C_LABEL':
                code_writer.write_label(parser.arg1())
            elif parser.command_type() == 'C_GOTO':
                code_writer.write_goto(parser.arg1())
            elif parser.command_type() == 'C_IF':
                code_writer.write_if(parser.arg1())
            elif parser.command_type() == 'C_FUNCTION':
                code_writer.write_function(parser.arg1(), parser.arg2())
            elif parser.command_type() == 'C_RETURN':
                code_writer.write_return()
            elif parser.command_type() == 'C_CALL':
                code_writer.write_call(parser.arg1(), parser.arg2())


def main():

    directory_or_file = sys.argv[1]
    output_file = sys.argv[2]

    code_writer = CodeWriter.CodeWriter(pathlib.Path(output_file))

    directory_or_file_path = pathlib.Path(directory_or_file)

    if directory_or_file_path.is_file():
        code_writer.write_init()
        translate_file(directory_or_file_path, code_writer)
    elif directory_or_file_path.is_dir():
        code_writer.write_init()
        # for each .vm file in the directory, translate the vm code to asm code and write it to the output file
        for path in directory_or_file_path.iterdir():
            translate_file(path, code_writer)

    code_writer.close()


if __name__ == '__main__':
    main()
