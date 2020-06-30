from statistics import mean
import nltk
import yaml

from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

from string import punctuation
from collections import defaultdict

import os


invalid_extensions = ('.py', '.yml', '.txt')
colleges = [c for c in os.listdir() if not c.endswith(invalid_extensions)]

word_count = {}
word_unique = {}
page_count = {}
yaml_info = defaultdict(list)

colleges_by_field = {
    'human': ['direitorp', 'fau', 'fflch'],
    'exact': ['eesc', 'ime', 'iqsc'],
    'bio': ['fmrp', 'fsp']
}

YAML_FILENAME = 'exemplo.yml'


def create_file_if_not_exists(filename, original, command):
    try:
        open(filename, 'r')
    except FileNotFoundError:
        os.system(f'{command} {original} {filename}')


projects_count = 0
for college in colleges:
    print(f'\n\n## {college} ##')
    projects = [p for p in os.listdir(college) if p[-4:] == '.pdf']

    word_count[college] = []
    word_unique[college] = []
    page_count[college] = []
    proj_count_by_college = 0
    for project_name in projects:
        projects_count += 1
        proj_count_by_college += 1
        project_file = college + '/' + project_name

        create_file_if_not_exists(f'{project_file}.yml', YAML_FILENAME, 'cp')
        create_file_if_not_exists(
            f'{project_file}.txt', project_file, 'pdftotext')

        with open(f'{project_file}.txt', 'r') as f:
            text = f.read()
            words = [word
                     for word in word_tokenize(text.lower())
                     if word not in list(punctuation)]

        def clean(text):
            if text is None:
                return ''
            return text.lower().strip()

        with open(f'{project_file}.yml', 'r') as f:
            info = yaml.load(f, Loader=yaml.FullLoader)

            yaml_info['ini'] += [clean(info['ini'])]
            yaml_info['end'] += [clean(info['end'])]
            yaml_info['ref'] += [clean(info['ref'])]
            yaml_info['sec'] += [clean(t) for t in info['secoes']]
            yaml_info['abs'] += [info['resumo_ab']]
            yaml_info['kws'] += [info['kw']]
            yaml_info['epi'] += [info['c_citacao']]
            yaml_info['ded'] += [info['dedictria']]
            yaml_info['agr'] += [info['agradecim']]
            yaml_info['scn'] += [len(info['secoes'])]

            again = defaultdict(bool)
            for sec in info['secoes']:
                sec = clean(sec)
                if 'método' in sec or 'materia' in sec or 'metodo' in sec and not again['met']:
                    yaml_info['met'] += [sec]
                    again['met'] = True
                if 'result' in sec or 'discuss' in sec and not again['res']:
                    yaml_info['res'] += [sec]
                    again['res'] = True
                if 'objetivo' in sec and not again['obj']:
                    yaml_info['obj'] += [sec]
                    again['obj'] = True

        print(f'{proj_count_by_college:2}----{project_name}----')

        pdfinfo_result = os.popen(
            f'pdfinfo {project_file} | grep Pages:').read()
        pages = int(pdfinfo_result.split(':')[1])

        page_count[college] += [pages]

        word_count[college] += [len(words)]
        word_unique[college] += [len(set(words))]
    print('########')


print('\n\nRESULTS')
print('count_mean\tunique_mean\tpages')
all_word_count = mean([count for counts in word_count.values()
                       for count in counts])
all_word_unique = mean([count for counts in word_unique.values()
                        for count in counts])
all_page_count = mean([count for counts in page_count.values()
                       for count in counts])

print('{:10.1f}\t{:11.1f}\t{:4}'.format(
    all_word_count, all_word_unique, int(all_page_count)))

print('\n\nRESULTS BY COLLEGE')
print('college     \tcount_mean\tunique_mean\tratio_unique\tpages')
for college in colleges:
    count = mean(word_count[college])
    unique = mean(word_unique[college])
    pages = mean(page_count[college])
    print('{:12}\t{:10.1f}\t{:11.1f}\t{:12.1f}%\t{:4}'.format(
        college, count, unique, unique/count*100, int(pages)
    ))


print('\n\nRESULTS BY FIELD')
print('field     \tcount_mean\tunique_mean\tratio_unique\tpages')
for field in colleges_by_field:
    f_word_count = []
    f_word_unique = []
    f_page_count = []

    for college in colleges_by_field[field]:
        f_word_count += [mean(word_count[college])]
        f_word_unique += [mean(word_unique[college])]
        f_page_count += [mean(page_count[college])]

    count = mean(f_word_count)
    unique = mean(f_word_unique)
    pages = mean(f_page_count)
    print('{:12}\t{:10.1f}\t{:11.1f}\t{:12.1f}%\t{:4}'.format(
        field, count, unique, unique/count*100, int(pages)))


def print_freq_dist_results(param, title, f=50):
    print('\n\n', title)
    param_freq = FreqDist(yaml_info[param])
    for word, freq in param_freq.most_common(f):
        print('{:5.2f}% {:4}\t{}'.format(freq/projects_count*100, freq, word))


print_freq_dist_results('ini', 'INTRO RESULTS')
print_freq_dist_results('end', 'ENDING RESULTS')
print_freq_dist_results('ref', 'REFERENCE RESULTS')
print_freq_dist_results('sec', 'MIDDLE SECTION RESULTS')
print_freq_dist_results('scn', 'MIDDLE SECTION NUMBER RESULTS')
print('MEAN:', mean(yaml_info['scn']))


print_freq_dist_results('obj', 'OBJECTIVE SECTION RESULTS')
print_freq_dist_results('met', 'METHODS SECTION RESULTS')
print_freq_dist_results('res', 'RESULTS AND DISCUSSION SECTION RESULTS')

print_freq_dist_results('abs', 'ABSTRACT RESULTS')
print_freq_dist_results('kws', 'ABSTRACT KEY-WORDS RESULTS')

print_freq_dist_results('epi', 'EPÍGRAFE RESULTS')
print_freq_dist_results('ded', 'DEDICATÓRIA RESULTS')
print_freq_dist_results('agr', 'AGRADECIMENTOS RESULTS')

print('\n\nPROJECTS COUNT', projects_count)
