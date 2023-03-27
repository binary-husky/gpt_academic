from .crazy_functions.func_template import func_template

from .crazy_functions.parse_source_code import (
    parse_project,
    parse_c_header,
    parse_python_project,
)


from .crazy_functions.read_abstract import read_artical_write_abstract


def get_crazy_functionals():
    from .crazy_functions.generate_func_comment import (
        generate_comment_for_function_for_batch,
    )

    return {
        "[Experiment] Please parse and deconstruct this project itself": {
            "Function": parse_project
        },
        "[Experiment] Parse the entire py project (input the project root path)": {
            "Color": "stop",  # button color
            "Function": parse_python_project,
        },
        "[Experiment] Parse the entire C++ project (input the project root path)": {
            "Color": "stop",  # button color
            "Function": parse_c_header,
        },
        "[Experiment] Read tex paper and write abstract (input the project root path)": {
            "Color": "stop",
            "Function": read_artical_write_abstract,
        },  # button color
        "[Experiment] Batch generate function comments (input the project root path)": {
            "Color": "stop",
            "Function": generate_comment_for_function_for_batch,
        },  # button color
        "[Experiment] Experimental functional template": {
            "Color": "stop",
            "Function": func_template,
        },  # button color
    }
