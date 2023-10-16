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
                    header: `__PRIMARY_HEADER__`,
                    msg: `__PRIMARY_MSG__`,
                },
                secondary_rol: {
                    header: `__SECONDARY_HEADER__`,
                    msg: `__SECONDARY_MSG__`,
                }
            },
        """
        template_ = template
        if len(a.split('\n')) == 1:
            template_ = template_.replace("__PRIMARY_HEADER__", markdown_convertion(a[:10]) + ' ...')
            template_ = template_.replace("__PRIMARY_MSG__", markdown_convertion(a))
        else:
            template_ = template_.replace("__PRIMARY_HEADER__", markdown_convertion(a.split('\n')[0]))
            template_ = template_.replace("__PRIMARY_MSG__", markdown_convertion('\n'.join(a.split('\n')[1:])))

        if len(b.split('\n')) == 1:
            template_ = template_.replace("__SECONDARY_HEADER__", markdown_convertion(b[:10]) + ' ...')
            template_ = template_.replace("__SECONDARY_MSG__", markdown_convertion(b))
        else:
            template_ = template_.replace("__SECONDARY_HEADER__", markdown_convertion(b.split('\n')[0]))
            template_ = template_.replace("__SECONDARY_MSG__", markdown_convertion('\n'.join(b.split('\n')[1:])))
        self.html_string += template_

    def save_file(self, file_name):
        from toolbox import get_log_folder
        with open('crazy_functions/pdf_fns/report_template.html', 'r', encoding='utf8') as f:
            html_template = f.read()
        html_template = html_template.replace("__TF_ARR__", self.html_string)
        with open(os.path.join(get_log_folder(), file_name), 'w', encoding='utf8') as f:
            f.write(html_template.encode('utf-8', 'ignore').decode())
        return os.path.join(get_log_folder(), file_name)
