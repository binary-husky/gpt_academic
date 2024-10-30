import token
import tokenize
import copy
import io


def remove_python_comments(input_source: str) -> str:
    source_flag = copy.copy(input_source)
    source = io.StringIO(input_source)
    ls = input_source.split('\n')
    prev_toktype = token.INDENT
    readline = source.readline

    def get_char_index(lineno, col):
        # find the index of the char in the source code
        if lineno == 1:
            return len('\n'.join(ls[:(lineno-1)])) + col
        else:
            return len('\n'.join(ls[:(lineno-1)])) + col + 1

    def replace_char_between(start_lineno, start_col, end_lineno, end_col, source, replace_char, ls):
        # replace char between start_lineno, start_col and end_lineno, end_col with replace_char, but keep '\n' and ' '
        b = get_char_index(start_lineno, start_col)
        e = get_char_index(end_lineno, end_col)
        for i in range(b, e):
            if source[i] == '\n':
                source = source[:i] + '\n' + source[i+1:]
            elif source[i] == ' ':
                source = source[:i] + ' ' + source[i+1:]
            else:
                source = source[:i] + replace_char + source[i+1:]
        return source

    tokgen = tokenize.generate_tokens(readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if toktype == token.STRING and (prev_toktype == token.INDENT):
            source_flag = replace_char_between(slineno, scol, elineno, ecol, source_flag, ' ', ls)
        elif toktype == token.STRING and (prev_toktype == token.NEWLINE):
            source_flag = replace_char_between(slineno, scol, elineno, ecol, source_flag, ' ', ls)
        elif toktype == tokenize.COMMENT:
            source_flag = replace_char_between(slineno, scol, elineno, ecol, source_flag, ' ', ls)
        prev_toktype = toktype
    return source_flag


# 示例使用
if __name__ == "__main__":
    with open("source.py", "r", encoding="utf-8") as f:
        source_code = f.read()

    cleaned_code = remove_python_comments(source_code)

    with open("cleaned_source.py", "w", encoding="utf-8") as f:
        f.write(cleaned_code)