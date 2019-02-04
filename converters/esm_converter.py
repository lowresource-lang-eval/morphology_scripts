#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"
from converters import esm_utils
from converters.evenki_lals_converter import write_single_token_data


import os
import sys

import traceback
import random

RANDOM_THRESHOLD = 0

CONLL_DELIMITER = '\t'
CONLL_NEW_LINE = '\n'
CONLL_NO_VALUE = '_'

CONLL_ADP = "ADP"
CONLL_NOUN = "NOUN"
CONLL_PROPER = "PROPN"
CONLL_CCONJ = "CCONJ"
CONLL_SCONJ = "SCONJ"
CONLL_ADJ = "ADJ"
CONLL_VERB = "VERB"
CONLL_INTJ = "INTJ"
CONLL_PRON = "PRON"
CONLL_NUM = "NUM"
CONLL_ADV = "ADV"
CONLL_DET = "DET"
CONLL_OTHER = "X"
CONLL_PARTICLE = "PART"

POS_CONVERSION = {'%%' : CONLL_OTHER,
                  'UNKN' : CONLL_OTHER,
                  'adj' : CONLL_ADJ,
                  'adv' : CONLL_ADV,
                  'clit' : CONLL_PARTICLE,
                  #TODO:?
                  'conj' : CONLL_CCONJ,
                  'dem' : CONLL_DET,
                  'emph' : CONLL_PRON,
                  'emphpers' : CONLL_PRON,
                  #TODO:?
                  'expl' : CONLL_INTJ,
                  'interj' : CONLL_INTJ,
                  #TODO:?
                  'interrog' : CONLL_PRON,
                    'n' : CONLL_NOUN,
                  #TODO
                     'np:G' : CONLL_NOUN,
                     'nprop' : CONLL_PROPER,
                     'num' : CONLL_NUM,
                     'pers' : CONLL_PRON,
                     'pp' : CONLL_ADP,
                  #TODO
                     'preverb' : CONLL_ADV,
                     'pro' : CONLL_PRON,
                     'ptcl' : CONLL_PARTICLE,
                     'ptcp' : CONLL_VERB,
                     'quant': CONLL_DET,
                     'qv' : CONLL_VERB,
                     'v' : CONLL_VERB
                  }
DERIVATIVE_GLOSSES = ['TODO']

POSES = set()


def convert_folder_conll(folder_name, output_filename_train, output_filename_test,
                         filenames_restriction,
                         filenames_filter=None):
    file_num = 0
    bad_files = []
    num_tokens = 0
    num_sentences = 0
    with open(output_filename_train, 'w', encoding='utf-8', newline='') as fout_train:
        with open(output_filename_test, 'w', encoding='utf-8', newline='') as fout_test:
            for root, dirs, files in os.walk(folder_name):
                for base_filename in files:
                    filename = os.path.join(root, base_filename)
                    if esm_utils.is_esm(filename) and \
                        (len(filenames_restriction) == 0 or filename in filenames_restriction):
                        try:
                            print("=======", filename, "==============")

                            file_num_tokens, file_num_sentences = \
                                convert_file_conll(os.path.join(folder_name, filename),
                                                   filenames_filter,
                                                   fout_train, fout_test)
                            file_num += 1
                            num_tokens += file_num_tokens
                            num_sentences += file_num_sentences
                        except Exception as e:
                            print(e)
                            traceback.print_exc()
                            bad_files.append((filename, e))
                            return
    print("%s files converted" % file_num)
    return bad_files, num_tokens, num_sentences

"""
converts eaf files from exmaralda format
to the format specified at https://lowresource-lang-eval.github.io
"""
def convert_file_conll(filename, filenames_filter,
                       fout_train, fout_test):
    total_num_sentences = 0
    num_tokens = 0
    text_data = esm_utils.get_text_data(filename)
    if not text_data:
        raise Exception("Empty filename: %s" % filename)


    for sentence_num, text_data_sentence in enumerate(text_data):
        base_filename = os.path.basename(filename)
        if base_filename in filenames_filter and sentence_num in filenames_filter[base_filename]:
            continue

        if random.random() > RANDOM_THRESHOLD:
            fout = fout_train
        else:
            fout = fout_test
        """if base_filename in filenames_filter and sentence_num in filenames_filter[base_filename]:
            fout = fout_train
        else:
            fout = fout_test"""
        fout.write(CONLL_NEW_LINE)
        total_num_sentences += 1
        write_comment_data(filename, sentence_num, text_data_sentence, fout)
        num_sentence_tokens = write_all_tokens_data(text_data_sentence, fout, filename)
        num_tokens += num_sentence_tokens
    return num_tokens, total_num_sentences

"""
creates metadata comment lines
"""
def write_comment_data(filename, sentence_num, text_data_sentence, fout):
    fout.write("#%s:%s\n" % (os.path.basename(filename), sentence_num))
    sentence_text = text_data_sentence['sentence'].replace("\n", "#")
    sentence_translation = text_data_sentence['translation'].replace("\n", "\n#")
    fout.write("#%s;%s\n" % (sentence_text,
                             sentence_translation))

"""
creates the token table for CONLL
"""
def write_all_tokens_data(text_data_sentence, fout, filename):
    morph_data = text_data_sentence['morphology']
    token_id = 0
    for morph_data_token in morph_data:
        token_id = write_token_data(token_id, morph_data_token, filename, fout)
    return len(morph_data)


def write_token_data(token_id, morph_data_token, filename, fout):
    token_data = normalize_token(morph_data_token)
    write_single_token_data(str(token_id), token_data,
                                filename, fout)
    token_id += 1
    return token_id




def normalize_token(morph_data_token):
    normalized_token = normalize_wordform(morph_data_token['token'])
    normalized_morphemes = normalize_morphemes(morph_data_token['token'])
    normalized_glosses = normalize_glosses(morph_data_token['analysis'])
    normalized_lemma = get_lemma(normalized_morphemes, normalized_glosses)
    normalized_pos = normalize_pos(morph_data_token['pos'])
    normalized_features = normalize_features(get_features(morph_data_token))

    return {'normalized_token': normalized_token,
                            'normalized_glosses': normalized_glosses,
                            'normalized_morphemes': normalized_morphemes,
                            'normalized_lemma': normalized_lemma,
                            'normalized_pos': normalized_pos,
                            'normalized_features': normalized_features,
                            }


def normalize_wordform(token):
    return token.replace('-', '')


def get_lemma(morphemes, glosses):
    lemma = morphemes[0]
    for i in range(1, len(morphemes)):
        morpheme = morphemes[i]
        gloss = glosses[i]
        if is_derivative(gloss):
            lemma += morpheme
    return lemma


def normalize_morphemes(morphemes):
    return morphemes.split('-')

def normalize_glosses(glosses):
    gloss_parts = glosses.split('-')
    for gloss_part in gloss_parts:
        if '.' in gloss_part:
            print(gloss_part)
    return gloss_parts


def normalize_pos(pos):
    POSES.add(pos)
    return POS_CONVERSION[pos]


def get_features(morph_data_token):
    return []


def normalize_features(param):
    return 'TODO'


def is_derivative(gloss):
    return gloss in DERIVATIVE_GLOSSES


def main():
    if len(sys.argv) < 4:
        print("usage: esm_converter.py <folder> <train_file> <test_file>")
        return
    bad_files, num_tokens, num_sentences = convert_folder_conll(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        [],
        dict()
    )

    for filename, e in bad_files:
        print("%s:%s" % (filename, e))
    print("Total tokens: %s. Total sentences: %s" % (num_tokens, num_sentences))



if __name__ == '__main__':
    main()
