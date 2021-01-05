#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
__author__ = "gisly"

SEPARATOR = '\t'
IGNORABLE_POS = ['PUNCT', 'SYM', 'X']
UNIMORPH_POS = {'ADJ':	'ADJ',
'ADP':	'ADP',
'ADV':	'ADV',
'AUX':	'AUX'	,
'CCONJ':	'CONJ',
'DET':	'DET'	,
'INTJ':	'INTJ'	,
'NOUN':	'N'	,
'NUM':	'NUM'	,
'PART':	'PART'	,
'PRON':	'PRO'	,
'PROPN':	'PROPN'	,
'SCONJ':	'CONJ',
'VERB' : 'V'}

def get_wordforms(corpus_filename):
    wordforms = []
    current_id_to_ignore_min = None
    current_id_to_ignore_max = None
    with open(corpus_filename, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if line == '':
                current_id_to_ignore_min = None
                current_id_to_ignore_max = None
            elif line[0].isnumeric():
                line_parts = line.split(SEPARATOR)
                id = line_parts[0]
                word = line_parts[1]
                lemma = line_parts[2]
                pos = line_parts[3]
                features = line_parts[5]
                #we are ignoring multiword expressions
                # because I am not sure which POS they should have
                if is_multiword(id):
                    id_parts = id.split('-')
                    current_id_to_ignore_min = int(id_parts[0])
                    current_id_to_ignore_max = int(id_parts[1])
                    continue
                if current_id_to_ignore_min and current_id_to_ignore_max \
                        and current_id_to_ignore_min <= int(id) <= current_id_to_ignore_max:
                    continue
                if is_to_ignore(pos):
                    continue
                if lemma.replace('.', '').isnumeric():
                    continue
                if is_typo(features):
                    continue
                wordforms.append({'word': word, 'lemma': lemma,
                                  'pos': pos, 'features': features})
    return wordforms


def read_features_from_filename(filename):
    features = dict()
    with open(filename, 'r', encoding='utf-8') as fin:
        for line in fin:
            features_parts = line.strip().split('\t')
            if len(features_parts) < 2:
                print(features_parts)
            features[features_parts[0]] = features_parts[1]
    return features



def is_to_ignore(pos):
    return pos in IGNORABLE_POS

def is_multiword(id):
    return '-' in id

def is_typo(features):
    return 'Typo=Yes' in features


def convert_wordforms(wordforms, features_dict):
    for wordform in wordforms:
        wordform['pos_unimorph'] = convert_pos(wordform)
        wordform['features_unimorph'] = set()
        features = wordform['features'].split('|')
        for feature in features:
            if feature == 'Mood=Cnd':
                if 'VerbForm=Conv' not in features:
                    print(wordform)

        for feature in features:
            if is_feature_bad_for_pos(wordform['pos'], feature):
                continue
            feature_unimorph = features_dict.get(feature)
            if feature_unimorph is None or feature_unimorph == '' or feature_unimorph == '_':
                #print(feature)
                continue
            elif feature_unimorph.startswith('POS='):
                wordform['pos_unimorph'] = feature_unimorph.split('POS=')[-1]
            elif feature_unimorph.startswith('CMD='):
                process_special_feature(wordform, feature)
            else:
                wordform['features_unimorph'].add(feature_unimorph)


def process_special_feature(wordform, feature):
    if feature == 'Poss=Yes':
        wordform['features_unimorph'] = process_possesive(wordform)
        print("!!!!", wordform)
    #TODO

def process_possesive(wordform):
    features = wordform['features'].split('|')
    feature_dict = {}
    for feature in features:
        feature_parts = feature.split('=')
        feature_dict[feature_parts[0]] = feature_parts[1]
    possessiveness_features = set()
    possessiveness = 'PSS' + feature_dict['Person']
    if feature_dict['Number'] == 'Sing':
        possessiveness += 'S'
    else:
        possessiveness += 'P'
    possessiveness_features.add(possessiveness)
    return possessiveness_features



def is_feature_bad_for_pos(pos, feature):
    if pos == 'ADP' and feature.startswith('Case='):
        return True
    if pos == 'AUX' and feature.startswith('Polarity='):
        return True
    return False

def convert_pos(wordform):
    return UNIMORPH_POS[wordform['pos']]

def get_unimorph_features(wordform):
    features = wordform['pos_unimorph']
    for feature_unimorph in wordform['features_unimorph']:
        features += ';' + feature_unimorph
    features = add_obligatory_markers(features)
    return features

def add_obligatory_markers(features):
    if features == 'N':
        return 'N;NOM'
    return features

def write_wordforms_to_file(wordforms, features, output_filename):
    convert_wordforms(wordforms, features)
    wordforms_already_written = set()
    sorted_wordforms = sorted(wordforms, key=lambda x:x['lemma'])
    with open(output_filename, 'w', encoding='utf-8', newline='') as fout:
        for sorted_wordform in sorted_wordforms:
            wordform_line = sorted_wordform['lemma'] + '\t' +\
                       sorted_wordform['word'] + '\t' +\
                       get_unimorph_features(sorted_wordform)
            if wordform_line in wordforms_already_written:
                continue
            wordforms_already_written.add(wordform_line)
            fout.write(wordform_line + '\n')

def convert_corpus(corpus_filename, features_filename, output_filename):
    wordforms = get_wordforms(corpus_filename)
    features = read_features_from_filename(features_filename)
    write_wordforms_to_file(wordforms, features, output_filename)


def main():
    if len(sys.argv) < 4:
        print("usage: ud_converter.py <filename_corpus> <filename_features> <filename_output>")
        return
    corpus_filename = sys.argv[1]
    features_filename = sys.argv[2]
    output_filename = sys.argv[3]
    convert_corpus(corpus_filename, features_filename, output_filename)
    print('success')


if __name__ == '__main__':
    main()