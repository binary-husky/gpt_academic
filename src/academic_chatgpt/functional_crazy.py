from crazy_functions.read_abstract import read_article_write_abstract
from crazy_functions.parse_project_source_code import parse_project_itself
from crazy_functions.parse_project_source_code import parse_a_python_project
from crazy_functions.parse_project_source_code import parse_a_c_project_header_file
from crazy_functions.higher_order_functional_template import (
    higher_order_functional_template,
)


def get_crazy_functionals():
    from crazy_functions.generate_func_comment import (
        generate_comment_for_function_for_batch,
    )

    return {
        "[Experiment] Please parse and deconstruct this project itself": {
            "Function": parse_project_itself
        },
        "[Experiment] Parse the entire py project (input the project root path)": {
            "Color": "stop",  # button color
            "Function": parse_a_python_project,
        },
        "[Experiment] Parse the entire C++ project (input the project root path)": {
            "Color": "stop",  # button color
            "Function": parse_a_c_project_header_file,
        },
        "[Experiment] Read tex paper and write abstract (input the project root path)": {
            "Color": "stop",
            "Function": read_article_write_abstract,
        },  # button color
        "[Experiment] Batch generate function comments (input the project root path)": {
            "Color": "stop",
            "Function": generate_comment_for_function_for_batch,
        },  # button color
        "[Experiment] Experimental functional template": {
            "Color": "stop",
            "Function": higher_order_functional_template,
        },  # button color
    }
