import os

def extract_chinese_characters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        chinese_characters = [] 
        sentence = {'file':file_path, 'begin':-1, 'end':-1, 'word': ""} 
        for index, char in enumerate(content):
            if 0x4e00 <= ord(char) <= 0x9fff:
                sentence['word'] += char
                if sentence['begin'] == -1: sentence['begin'] = index
                sentence['end'] = index
            else:
                if len(sentence['word'])>0:
                    chinese_characters.append(sentence)
                    sentence = {'file':file_path, 'begin':-1, 'end':-1, 'word': ""} 
        return chinese_characters

def extract_chinese_characters_from_directory(directory_path):
    chinese_characters = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                chinese_characters.extend(extract_chinese_characters(file_path))
    return chinese_characters

directory_path = './'
chinese_characters = extract_chinese_characters_from_directory(directory_path)
word_to_translate = {}
for d in chinese_characters:
    word_to_translate[d['word']] = "Translation"

print('All Chinese characters:', chinese_characters)