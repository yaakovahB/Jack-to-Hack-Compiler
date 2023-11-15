import JackTokenizer
import CompilationEngine
import sys
import pathlib


def compile_file(input_path):
    if str(input_path).endswith('.jack'):

        jack_tokenizer = JackTokenizer.JackTokenizer(input_path)

        # create output file and prepare it for writing
        output_string = str(input_path.absolute()).replace(".jack", ".vm")
        path = pathlib.Path(output_string)
        output_file_path = path.open('w')

        # use the CompilationEngine to compile the input jackTokenizer into the output file
        compile_engine = CompilationEngine.CompilationEngine(jack_tokenizer, output_file_path)
        compile_engine.compile_class()

        output_file_path.close()

def main():
    directory_or_file = sys.argv[1]
    directory_or_file_path = pathlib.Path(directory_or_file)

    if directory_or_file_path.is_file():
        compile_file(directory_or_file_path)
    elif directory_or_file_path.is_dir():
        # for each .jack file in the directory, translate the jack code to vm code and write it to an output file
        for path in directory_or_file_path.iterdir():
            compile_file(path)
    else:
        raise Exception


if __name__ == '__main__':
    main()



