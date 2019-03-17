#!/usr/bin/python
# -*- coding: utf-8 -*
#Created by https://github.com/flying-bear/practice
import os
from collections import OrderedDict
from sys import argv

totally_correct_wordforms = 0
all_wordforms = 0

def input_files(path_dict): # opens and reads input files
    files = {'standard':{},
             'test': {}}
    for key in path_dict:
        f_path = path_dict[key]
        f_name = os.path.splitext(os.path.basename(f_path))[0]
        with open(f_path, 'r', encoding='utf-8') as file: # os.path -- make the path universal
            f_text = file.read()
        files[key].update({'path':f_path, 'name':f_name, 'text':f_text})
    return files # returns a dictionary of files and corresponding paths, names, and texts


def initialize_evaluation(): # creates evaluation with zero values
    evaluation = {'Hits':0,
                  'Deletions':0,
                  'Insertions':0,
                  'CorrectMorphemes':0,
                  'CorrectTags':0}
    return evaluation


def list_boundaries_and_tags(line_list): # separates tags from morphemes in a given segmentation list
    morphemes = []
    line_data = {'boundaries':set(),
                 'tag_dict': {}}
    for el in line_list:
        segment = el.split('_')
        morphemes.append(segment[0])
        cursor = len(''.join(morphemes))
        line_data['boundaries'].add(cursor)
        if len(segment) == 2:
            tag = segment[1]
        else:
            tag = ''
        line_data['tag_dict'][segment[0]+'_'+str(cursor)] = tag
    return line_data


def compare_boundaries(f_bound, s_bound): # compares two given sets of boundaries
    loc_eval = {'Hits':0, 'Deletions':0, 'Insertions':0}
    loc_eval['Hits'] = len(s_bound.intersection(f_bound))
    loc_eval['Deletions'] = len(s_bound.difference(f_bound))
    loc_eval['Insertions'] = len(f_bound.difference(s_bound))
    return loc_eval


def check_morphs_and_tags(f_tag_dict, s_tag_dict): # compares morphemes and tags given two dicts
    global totally_correct_wordforms
    global all_wordforms

    all_wordforms += 1
    loc_eval = {'CorrectMorphemes':0, 'CorrectTags':0}
    is_all_correct = True
    for key in s_tag_dict: # there must be a morpheme tag
        if key in f_tag_dict: # there is a morpheme tag
            loc_eval['CorrectMorphemes'] += 1 # that must be a correctly split morpheme
            if s_tag_dict[key] == f_tag_dict[key]: # tags are equal
                loc_eval['CorrectTags'] += 1 # tag is correct
        else:
            is_all_correct = False
    if is_all_correct:
        totally_correct_wordforms += 1
    return loc_eval


def compare(f_line_list, s_line_list, evaluation): # compares to lines
    f_data = list_boundaries_and_tags(f_line_list)
    f_bound = f_data['boundaries']
    f_tags = f_data['tag_dict']
    s_data = list_boundaries_and_tags(s_line_list)
    s_bound = s_data['boundaries']
    s_tags = s_data['tag_dict']
    b_eval = compare_boundaries(f_bound, s_bound)
    loc_eval = check_morphs_and_tags(f_tags, s_tags)
    loc_eval.update(b_eval)
    for key in evaluation:
        evaluation[key] += loc_eval[key]
    return evaluation

def evaluate(file, standard, ev_dict): # evaluates two given texts
    file = file.strip()
    f_lines = file.split('\n')
    standard = standard.strip()
    s_lines = standard.split('\n')
    s_length = len(s_lines)
    if len(f_lines) != s_length: # check that the files have the same number of lines
        with open('log.txt', 'w', encoding='utf-8') as file:
            file.write('Error: wrong number of lines')
        return ev_dict
    else:
        file = open('log.txt', 'w', encoding='utf-8')
        for i in range(s_length):
            s_line = s_lines[i].strip()
            f_line = f_lines[i].strip()
            if not s_line: # check that either lines are both non-empty or both empty
                if not f_line:
                    continue
                else:
                    file.write(f'Error: bad line {i+1}\n')
            elif not f_line:
                file.write(f'Error: bad line {i+1}\n')
            else:
                s_list = s_line.split('\t') # list with the word as 0 element and taged morphemes as 1 element
                f_list = f_line.split('\t')
                if s_list[0] != f_list[0]:
                    file.write(f'Error: bad line {i+1}\n')
                else:
                    ev_dict.update(compare(f_list[1].split(), s_list[1].split(), ev_dict)) # compare segmentation lists (without words)
        file.close()
        return ev_dict

def write_results(evaluation):
    H = evaluation['Hits']
    D = evaluation['Deletions']
    I = evaluation['Insertions']
    print(f'H = {H}')
    print(f'D = {D}')
    print(f'I = {I}')
    print(f'CorrectTags = {evaluation["CorrectTags"]}')
    if H or (D and I):
        Precision = H/(H+I)
        Recall = H/(H+D)
        results = OrderedDict({'Precision': Precision,
                   'Recall': Recall,
                   'F-measure': (2*Precision*Recall)/(Precision+Recall),
                   'CorrectMorphemes':evaluation['CorrectMorphemes'],
                   'CorrectTags':evaluation['CorrectTags'],
                    'AllWordforms' : all_wordforms,
                    'TotallyCorrect' : totally_correct_wordforms,
                    'ShareCorrect' : float(totally_correct_wordforms) / all_wordforms})
    else:
        results = OrderedDict({'Precision': 0,
                   'Recall': 0,
                   'F-measure': 0,
                   'CorrectMorphemes': 0,
                   'CorrectTags': 0,
                    'AllWordforms': all_wordforms,
                    'TotallyCorrect': totally_correct_wordforms,
                    'ShareCorrect': 0           })
    
    with open('results.txt', 'w', encoding='utf-8') as file:
        for key in results:
            file.write(key+' = '+str(results[key])+'\n')

def main():
    try:
        paths = {'standard':argv[1], 'test':argv[2]}
    except IndexError:
        paths = {'standard': input('print standard file path: '),
                 'test': input('print test file path: ')}
    evaluation = initialize_evaluation()
    files = input_files(paths)
    write_results(evaluate(files['test']['text'], files['standard']['text'], evaluation))

if __name__ == '__main__':
    main()