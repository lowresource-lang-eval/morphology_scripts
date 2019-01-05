#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"
import os

import language_utils
import eaf_utils

EVENKI_LANGUAGE_CODE = "ev"

CONLL_DELIMITER = '\t'
CONLL_NEW_LINE = '\n'
CONLL_UNAVAILABLE = '_'

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


POS_CONVERSION = {u'сущ':'N', u'гл':'V', u'кол.числ':'Card', u'прил':'Adj', u'нареч':'Adv',
                  u'част':u'Part'}

"""
applies conll format conversion to all eaf files in a folder
"""
def convert_folder_conll(folder_name, output_filename, filenames_filter=None):
    file_num = 0
    bad_files = []
    with open(output_filename, 'w', encoding='utf-8') as fout:
        for filename in os.listdir(folder_name):
            print("=========" + filename + "==============")
            if eaf_utils.is_eaf(filename) and((not filenames_filter) or (filename in filenames_filter)):
                try:
                    convert_file_conll(os.path.join(folder_name, filename), fout)
                    file_num += 1
                except Exception as e:
                    print(e)
                    bad_files.append((filename, e))
    print("%s files converted" % file_num)
    return bad_files

"""
converts eaf files from the http://siberian-lang.srcc.msu.ru project
to the format specified at <TODO>
"""
def convert_file_conll(filename, fout):
    text_data = eaf_utils.get_text_data(filename, EVENKI_LANGUAGE_CODE)
    if not text_data:
        raise Exception("Empty filename: %s" % filename)
    for sentence_num, text_data_sentence in enumerate(text_data):
        if sentence_num > 0:
            fout.write(CONLL_NEW_LINE)
        write_comment_data(text_data_sentence, fout)
        write_all_tokens_data(text_data_sentence, fout, filename)

"""
creates metadata comment lines
"""
def write_comment_data(text_data_sentence, fout):
    #TODO
    pass

"""
creates the token table for CONLL
"""
def write_all_tokens_data(text_data_sentence, fout, filename):
    morph_data = text_data_sentence['morphology']
    if not morph_data:
        raise Exception("Empty morphology: %s" % filename)
    for token_id, morph_data_token in enumerate(morph_data):
        write_token_data(token_id, morph_data_token, filename, fout)


def write_token_data(token_id, morph_data_token, filename, fout):
    #ID
    output_line = str(token_id + 1)
    output_line += CONLL_DELIMITER
    #FORM
    output_line += morph_data_token['token']
    output_line += CONLL_DELIMITER
    #LEMMA
    output_line += get_lemma(morph_data_token)
    output_line += CONLL_DELIMITER
    #UPOS
    output_line += processPOS(morph_data_token['pos'], morph_data_token['analysis'], filename)
    output_line += CONLL_DELIMITER
    #XPOS
    output_line += CONLL_UNAVAILABLE
    output_line += CONLL_DELIMITER
    #FEATS
    output_line += generate_features(morph_data_token)
    output_line += CONLL_DELIMITER
    #HEAD
    output_line += CONLL_UNAVAILABLE
    output_line += CONLL_DELIMITER
    #DEPREL
    output_line += CONLL_UNAVAILABLE
    output_line += CONLL_DELIMITER
    #DEPS
    output_line += CONLL_UNAVAILABLE
    output_line += CONLL_DELIMITER
    #MISC
    output_line += CONLL_UNAVAILABLE
    output_line += CONLL_DELIMITER

    fout.write(output_line + CONLL_NEW_LINE)


def get_lemma(morph_data_token):
    return morph_data_token['analysis'][0]['fon']


def generate_features(morph_data_token):
    #TODO
    return ""


def processPOS(pos, analysis, filename):
    if pos:
        return encodePOS(pos)
    return guessPOS(analysis, filename)

def guessPOS(analysis, filename):
    pos = None
    first_gloss = normalize_gloss(analysis[0]['gloss'])
    if first_gloss.strip() == '':
        return CONLL_OTHER

    possible_pos_set = language_utils.get_russian_pos_set(first_gloss)
    if language_utils.is_proper_noun_translation(first_gloss):
        return CONLL_PROPER
    if language_utils.is_c_conjunction_translation(first_gloss):
        return CONLL_CCONJ
    if language_utils.is_s_conjunction_translation(first_gloss):
        return CONLL_SCONJ
    if language_utils.is_numeric_translation(first_gloss):
        return CONLL_NUM
    if language_utils.is_adverb_translation(first_gloss, possible_pos_set):
        return CONLL_ADV
    if language_utils.is_determiner_translation(first_gloss, analysis):
        return CONLL_DET
    if language_utils.is_pronoun_translation(first_gloss):
        return CONLL_PRON
    if language_utils.is_adjective_translation(possible_pos_set):
        return CONLL_ADJ


    for analysis_part in analysis:
        gloss = normalize_gloss(analysis_part['gloss'])
        if language_utils.is_slip(gloss):
            return CONLL_OTHER
        if language_utils.is_verb_gloss(gloss):
            return CONLL_VERB
        if language_utils.is_adjective_gloss(gloss):
            return CONLL_ADJ
        if language_utils.is_adverb_gloss(gloss):
            return CONLL_ADV
        if language_utils.is_noun_gloss(gloss):
            return CONLL_NOUN
    if pos is None:
        with open('D:/Projects/morphology_scripts/data/log.txt', 'a', encoding='utf-8') as fout:
            fout.write("FILENAME %s ATTENTION %s " % (filename, analysis) + '\r\n')
        return CONLL_NOUN
    return pos


def encodePOS(inner_POS):
    if inner_POS in POS_CONVERSION:
        return POS_CONVERSION[inner_POS]
    raise Exception("no such pos:" + inner_POS)

def normalize_gloss(gloss):
    return gloss.strip('-').split('{')[0].split('[')[0]


bad_files = convert_folder_conll("D:/ForElan/ForSIL_CORPUS/evenki_texts_corpus_05112018",
                   "D:/Projects/morphology_scripts/data/test.txt",
                    ['2007_Ekonda_Pankagir_LAv_transliterated.eaf_new.eaf']
                     )

for filename, e in bad_files:
    print("%s:%s" % (filename, e))