import re
import sys
import pathlib


class JackTokenizer:
    """
    removes comment and white space from input stream and breaks it into Jack tokens, as specified by the Jack grammar
    """

    keyword_ = r'(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|' \
               r'let|do|if|else|while|return)'
    symbol_ = r'(\{|\}|\[|\]|\(|\)|\.|,|;|\+|-|\*|/|&|\||<|>|=|~)'
    integer_constant = r'\d+'
    string_constant = '"[^"]*"'
    identifier_ = r'[A-Za-z_][A-Za-z0-9_]*'

    # Combine all patterns into a single regular expression.
    pattern = f'({string_constant})|({integer_constant})|({symbol_})|({identifier_})|({keyword_})'

    # opens the input file/stream and gets it ready to tokenize it
    def __init__(self, input_path):

        # remove any comments
        input_file_contents = self.remove_comments(input_path)

        # create list of tokens (and what type it is)
        self.tokens = self.tokenize(input_file_contents)

        self.current_token = ()  # (type, token)
        self.number_current_token = 0

    def tokenize(self, input_file_contents):
        """
        helper method for the constructor
        divides 'input_file_contents' into tokens and writes all of those tokens into a list. The list is a list of
        tuples. each tuple is (token type, token)
        :param input_file_contents: a string that needs to be divided into tokens
        :return:
        """
        # Find all matches using the pattern
        matches = re.findall(self.pattern, input_file_contents)

        # Flatten the matches and remove empty strings
        elements = [match[0] or match[1] or match[2] or match[3] or match[4] for match in matches if any(match)]

        tokens = []
        for element in elements:
            if re.match('^(' + self.keyword_ + ')$', element):
                tokens.append(('keyword', element))
            elif re.match('^(' + self.symbol_ + ')$', element):
                # (<,>, and &) are also used for XML markup, and thus they can't appear as data in XML files
                tokens.append(('symbol', element))
            elif re.match('^(' + self.integer_constant + ')$', element):
                tokens.append(('integerConstant', element))
            elif re.match('^(' + self.string_constant + ')$', element):
                tokens.append(('stringConstant', element[1:-1]))  # need the '[1:-1]' to get rid of quotes
            elif re.match('^(' + self.identifier_ + ')$', element):
                tokens.append(('identifier', element))
            else:
                raise Exception(f'{element} is not a legal token in the Jack Grammar')

        return tokens

    @staticmethod
    def remove_comments(path):
        """
        helper method for the constructor
        stores all the contents, without the comments, of 'path' in a string
        :param path:
        :return:
        """
        file_contents = path.read_text()

        # Remove /* ... */ comments
        file_contents = re.sub(r"/\*.*?\*/", "", file_contents, flags=re.DOTALL)

        # Remove /** ... */ API comments
        file_contents = re.sub(r"/\*\*.*?\*/", "", file_contents, flags=re.DOTALL)

        # Remove // comments
        file_contents = re.sub(r"//.*", "", file_contents)

        return file_contents

    def has_more_tokens(self):
        if self.number_current_token == len(self.tokens):
            return False
        else:
            return True

    def advance(self):
        """
        gets the next token from the input and makes it the current token. This method should only be called if the
        method has_more_tokens() is true. Initially there is no current token
        :return:
        """
        self.current_token = self.tokens[self.number_current_token]
        self.number_current_token = self.number_current_token + 1

    def token_type(self):
        """
        returns the type of the current token
        :return:
        """
        return self.current_token[0]

    def keyword(self):
        """
        returns the keyword which is the current token. Should be called only when token_type() is 'keyword''
        :return:
        """
        return self.current_token[1]

    def symbol(self):
        """
        returns the character which is the current token. Should be called only when token_type() is 'symbol'
        :return:
        """
        return self.current_token[1]

    def identifier(self):
        """
        returns the identifier which is the current token. Should be called only when token_type() is 'identifier'
        :return:
        """
        return self.current_token[1]

    def int_val(self):
        """
        returns the integer value which is the current token.
        Should be called only when token_type() is 'integerConstant'
        :return:
        """
        return int(self.current_token[1])

    def string_val(self):
        """
        returns the string value which is the current token, without the double quotes.
        this method Should be called only when token_type() is 'string_constant'
        :return:
        """
        return self.current_token[1]

    def next_token_type(self):
        """
        this method should only be called when syntactically, there needs to be more tokens, and so
        if there are no more tokens than an exception is raised
        :return:
        """
        if self.number_current_token == len(self.tokens):
            raise Exception('there is no \'next token\'')
        return self.tokens[self.number_current_token][0]

    def next_keyword(self):
        """
        this method should only be called when syntactically, there needs to be more tokens, and so
        if there are no more tokens than an exception is raised
        :return:
        """
        if self.number_current_token == len(self.tokens):
            raise Exception('there is no \'next keyword\'')
        return self.tokens[self.number_current_token][1]

    def next_symbol(self):
        """
        this method should only be called when syntactically, there needs to be more tokens, and so
        if there are no more tokens than an exception is raised
        :return:
        """
        if self.number_current_token == len(self.tokens):
            raise Exception('there is no \'next symbol\'')
        return self.tokens[self.number_current_token][1]
