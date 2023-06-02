from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder
import glob

def 编译Latex(main_tex, work_folder):
    import os
    current_dir = os.getcwd()
    os.chdir(work_folder);
    main_file = os.path.basename(main_tex)
    assert main_file.endswith('.tex')
    main_file = main_file[:-4]
    os.system(f'pdflatex {main_file}.tex')
    os.system(f'bibtex {main_file}.aux')
    os.system(f'pdflatex {main_file}.tex')
    os.system(f'pdflatex {main_file}.tex')
    os.chdir(current_dir)
    pdf_output = os.path.join(work_folder, f'{main_file}.pdf')

    assert os.path.exists(pdf_output)
    return pdf_output

def Latex预处理(tar_file):
    from toolbox import extract_archive
    import shutil
    work_folder = 'private_upload/latex_workshop_temp'
    try:
        shutil.rmtree(work_folder)
    except:
        pass
    res = extract_archive(tar_file, dest_dir=work_folder)
    for texf in glob.glob('private_upload/latex_workshop_temp/*.tex'):
        with open(texf, 'r', encoding='utf8') as f:
            file_content = f.read()
        if r'\documentclass' in file_content:
            return texf, work_folder
        else:
            continue
    raise RuntimeError('无法找到一个主Tex文件（包含documentclass关键字）')



