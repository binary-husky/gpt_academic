from toolbox import update_ui, get_conf, trimmed_format_exc, get_log_folder
import os




class construct_html():
    def __init__(self) -> None:
        self.html_string = ""

    def add_row(self, a, b):
        from toolbox import markdown_convertion
        template = """
            {
                primary_col: {
                    header: String.raw`__PRIMARY_HEADER__`,
                    msg: String.raw`__PRIMARY_MSG__`,
                },
                secondary_rol: {
                    header: String.raw`__SECONDARY_HEADER__`,
                    msg: String.raw`__SECONDARY_MSG__`,
                }
            },
        """
        def std(str):
            str = str.replace(r'`',r'\`')
            str += ' '
            return str

        template_ = template
        a_lines = a.split('\n')
        b_lines = b.split('\n')

        if len(a_lines) == 1 or len(a_lines[0]) > 50:
            template_ = template_.replace("__PRIMARY_HEADER__", std(a[:20]))
            template_ = template_.replace("__PRIMARY_MSG__", std(markdown_convertion(a)))
        else:
            template_ = template_.replace("__PRIMARY_HEADER__", std(a_lines[0]))
            template_ = template_.replace("__PRIMARY_MSG__", std(markdown_convertion('\n'.join(a_lines[1:]))))

        if len(b_lines) == 1 or len(b_lines[0]) > 50:
            template_ = template_.replace("__SECONDARY_HEADER__", std(b[:20]))
            template_ = template_.replace("__SECONDARY_MSG__", std(markdown_convertion(b)))
        else:
            template_ = template_.replace("__SECONDARY_HEADER__", std(b_lines[0]))
            template_ = template_.replace("__SECONDARY_MSG__", std(markdown_convertion('\n'.join(b_lines[1:]))))
        self.html_string += template_

    def save_file(self, file_name):
        from toolbox import get_log_folder
        with open('crazy_functions/pdf_fns/report_template.html', 'r', encoding='utf8') as f:
            html_template = f.read()
        html_template = html_template.replace("__TF_ARR__", self.html_string)
        with open(os.path.join(get_log_folder(), file_name), 'w', encoding='utf8') as f:
            f.write(html_template.encode('utf-8', 'ignore').decode())
        return os.path.join(get_log_folder(), file_name)
