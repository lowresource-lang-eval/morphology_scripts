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


POS_CONVERSION = {'n': CONLL_NOUN,
                  'adj' : CONLL_ADJ,
                  'v' : CONLL_VERB,
                  'adv' : CONLL_ADV,
                  'cardnum': CONLL_NUM,
                  'pro' : CONLL_PRON,
                  'pers' : CONLL_PRON,
                  'pro-adj': CONLL_DET,
                  'SLIP' : CONLL_OTHER,
                  'interj' : CONLL_INTJ,
                  'advlizer' : CONLL_VERB,
                  'conn' : CONLL_SCONJ,
                  '[нрзб]' : CONLL_OTHER,
                  '???' : CONLL_OTHER,
                  'prt' : CONLL_OTHER}


FON_SET = set()
GLOSSES = dict()

"""
applies conll format conversion to all eaf files in a folder
"""
def convert_folder_conll(folder_name, output_filename, filenames_filter=None):
    with open('D:/Projects/morphology_scripts/data/log.txt', 'w', encoding='utf-8') as fout:
        fout.write('')
    file_num = 0
    bad_files = []
    num_tokens = 0
    num_sentences = 0
    with open(output_filename, 'w', encoding='utf-8') as fout:
        for filename in os.listdir(folder_name):
            print("=========" + filename + "==============")
            if eaf_utils.is_eaf(filename) and((not filenames_filter) or (filename in filenames_filter)):
                try:
                    file_num_tokens, file_num_sentences  = convert_file_conll(os.path.join(folder_name, filename), fout)
                    file_num += 1
                    num_tokens += file_num_tokens
                    num_sentences += file_num_sentences
                except Exception as e:
                    print(e)
                    bad_files.append((filename, e))
    print("%s files converted" % file_num)
    return bad_files, num_tokens, num_sentences

"""
converts eaf files from the http://siberian-lang.srcc.msu.ru project
to the format specified at <TODO>
"""
def convert_file_conll(filename, fout):
    total_num_sentences = 0
    num_tokens = 0
    text_data = eaf_utils.get_text_data(filename, EVENKI_LANGUAGE_CODE)
    if not text_data:
        raise Exception("Empty filename: %s" % filename)
    for sentence_num, text_data_sentence in enumerate(text_data):
        if not text_data_sentence['morphology'] or \
                has_cyrillic(text_data_sentence['morphology']):
            continue
        if sentence_num > 0:
            fout.write(CONLL_NEW_LINE)
        total_num_sentences += 1
        write_comment_data(text_data_sentence, fout)
        num_sentence_tokens = write_all_tokens_data(text_data_sentence, fout, filename)
        num_tokens += num_sentence_tokens
    return num_tokens, total_num_sentences

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

    for token_id, morph_data_token in enumerate(morph_data):
        write_token_data(token_id, morph_data_token, filename, fout)
    return len(morph_data)


def write_token_data(token_id, morph_data_token, filename, fout):
    token = language_utils.normalize_token(morph_data_token['token'])
    normalized_glosses = language_utils.normalize_glosses(morph_data_token['analysis'])

    if len(normalized_glosses) > 1:
        base_filename = os.path.basename(filename)
        for normalized_gloss in normalized_glosses[1:]:
            if normalized_gloss in GLOSSES:
                GLOSSES[normalized_gloss].add(base_filename)
            else:
                GLOSSES[normalized_gloss] = {base_filename}

    if token == '':
        return
    #ID
    output_line = str(token_id + 1)
    output_line += CONLL_DELIMITER
    #FORM
    output_line += token
    output_line += CONLL_DELIMITER

    for symbol in token:
        FON_SET.add(symbol)

    #LEMMA
    output_line += get_lemma(morph_data_token, normalized_glosses)
    output_line += CONLL_DELIMITER
    #UPOS
    output_line += processPOS(morph_data_token['pos'], morph_data_token['analysis'],
                              normalized_glosses, filename)
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


def get_lemma(morph_data_token, normalized_glosses):
    lemma = morph_data_token['analysis'][0]['fon']
    for i in range(1, len(normalized_glosses)):
        analysis = morph_data_token['analysis'][i]
        gloss_normalized = normalized_glosses[i]
        if language_utils.is_derivative(gloss_normalized):
            lemma += analysis['fon'].strip('-')
        else:
            pass
            #break

    return language_utils.normalize_token(lemma)


def generate_features(morph_data_token):
    #TODO
    return ""


def processPOS(pos, analysis, normalized_glosses, filename):
    if pos:
        return encodePOS(pos)
    return guessPOS(analysis, normalized_glosses, filename)

def guessPOS(analysis, normalized_glosses, filename):
    pos = None
    first_gloss = normalize_gloss(normalized_glosses[0])
    first_fon = analysis[0]['fon']
    if first_gloss.strip() == '':
        return CONLL_OTHER
    if language_utils.is_slip_unknown(first_gloss):
        return CONLL_OTHER
    if language_utils.is_noun_negation(first_fon, first_gloss):
        return CONLL_NOUN

    possible_pos_set = language_utils.get_russian_pos_set(first_gloss)
    if language_utils.is_interjection_translation(first_gloss):
        return CONLL_INTJ
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
    if language_utils.is_pronoun_translation(first_fon, first_gloss):
        return CONLL_PRON
    if language_utils.is_adjective_translation(possible_pos_set):
        return CONLL_ADJ

    if len(analysis) > 1:
        for i in range(1, len(analysis)):
            analysis_part = analysis[i]
            gloss = normalized_glosses[i]
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
        """with open('D:/Projects/morphology_scripts/data/log.txt', 'a', encoding='utf-8') as fout:
            fout.write("FILENAME %s ATTENTION %s " % (filename, analysis) + '\r\n')"""
        return CONLL_NOUN
    return pos


def encodePOS(inner_POS):
    if inner_POS in POS_CONVERSION:
        return POS_CONVERSION[inner_POS]
    raise Exception("no such pos:" + inner_POS)

def has_cyrillic(morph_data):
    for morph_data_token in morph_data:
        if language_utils.is_cyrillic(morph_data_token['token']):
            return True
    return False



def normalize_gloss(gloss):
    return gloss.strip('-').split('{')[0].split('[')[0]


bad_files, num_tokens, num_sentences = convert_folder_conll("D:/ForElan/ForSIL_CORPUS/evenki_texts_corpus_05112018",
                   "D:/Projects/morphology_scripts/data/test.txt",
                    []
                     )

for filename, e in bad_files:
    print("%s:%s" % (filename, e))

print("Total tokens: %s. Total sentences: %s" % (num_tokens, num_sentences))

print(sorted(list(FON_SET)))
sorted_glosses = sorted(list(GLOSSES.keys()))
for gloss in sorted_glosses:
    filename_set = GLOSSES[gloss]
    print(gloss, '\t', ';'.join(sorted(list(filename_set))))