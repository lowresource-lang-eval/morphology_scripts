#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"
import os
import traceback
import random

import language_utils
import eaf_utils


EVENKI_LANGUAGE_CODE = "ev"

CONLL_DELIMITER = '\t'
CONLL_NEW_LINE = '\n'
CONLL_NO_VALUE = '_'

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
CODE_SWITCHING = set()

FEATURE_TABLE = None
FEATURE_FILENAME = "../resources/feature_table.csv"


def convert_folder_conll(folder_name, output_filename_train, output_filename_test,
                         filenames_restriction,
                         filenames_filter=None):
    file_num = 0
    bad_files = []
    num_tokens = 0
    num_sentences = 0
    with open(output_filename_train, 'w', encoding='utf-8', newline='') as fout_train:
        with open(output_filename_test, 'w', encoding='utf-8', newline='') as fout_test:
            for filename in os.listdir(folder_name):
                if eaf_utils.is_eaf(filename) and \
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
    print("%s files converted" % file_num)
    return bad_files, num_tokens, num_sentences

"""
converts eaf files from the http://siberian-lang.srcc.msu.ru project
to the format specified at https://lowresource-lang-eval.github.io
"""
def convert_file_conll(filename, filenames_filter,
                       fout_train, fout_test):
    total_num_sentences = 0
    num_tokens = 0
    text_data = eaf_utils.get_text_data(filename, EVENKI_LANGUAGE_CODE)
    if not text_data:
        raise Exception("Empty filename: %s" % filename)


    for sentence_num, text_data_sentence in enumerate(text_data):
        if not text_data_sentence['morphology'] or \
                has_cyrillic(text_data_sentence['morphology']):
            continue
        base_filename = os.path.basename(filename)
        if base_filename in filenames_filter and sentence_num in filenames_filter[base_filename]:
            continue
        if random.random() > 0.35:
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

def convert_folder_morpheme(folder_name, output_filename_train, output_filename_test,
                         filenames_restriction,
                         filenames_filter=None):
    file_num = 0
    bad_files = []
    num_tokens = 0
    num_sentences = 0
    with open(output_filename_train, 'w', encoding='utf-8', newline='') as fout_train:
        with open(output_filename_test, 'w', encoding='utf-8', newline='') as fout_test:
            for filename in os.listdir(folder_name):
                if eaf_utils.is_eaf(filename) and \
                    (len(filenames_restriction) == 0 or filename in filenames_restriction):
                    try:
                        print("=======", filename, "==============")

                        file_num_tokens, file_num_sentences = \
                            convert_file_morpheme(os.path.join(folder_name, filename),
                                               filenames_filter,
                                               fout_train, fout_test)
                        file_num += 1
                        num_tokens += file_num_tokens
                        num_sentences += file_num_sentences
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                        bad_files.append((filename, e))
    print("%s files converted" % file_num)
    return bad_files, num_tokens, num_sentences


def convert_file_morpheme(filename, filenames_filter,
                       fout_train, fout_test):
    total_num_sentences = 0
    num_tokens = 0
    text_data = eaf_utils.get_text_data(filename, EVENKI_LANGUAGE_CODE)
    if not text_data:
        raise Exception("Empty filename: %s" % filename)


    for sentence_num, text_data_sentence in enumerate(text_data):
        if not text_data_sentence['morphology'] or \
                has_cyrillic(text_data_sentence['morphology']):
            continue
        base_filename = os.path.basename(filename)
        if base_filename in filenames_filter and sentence_num in filenames_filter[base_filename]:
            fout = fout_train
        else:
            fout = fout_test
        """if random.random() > 0.1:
            fout = fout_train
        else:
            fout = fout_test"""

        fout.write(CONLL_NEW_LINE)
        total_num_sentences += 1
        num_sentence_tokens = write_all_tokens_data_morpheme(text_data_sentence, fout, filename)
        num_tokens += num_sentence_tokens
    return num_tokens, total_num_sentences

def write_all_tokens_data_morpheme(text_data_sentence, fout, filename):
    morph_data = text_data_sentence['morphology']
    for morph_data_token in morph_data:
        write_token_data_morpheme(morph_data_token, filename, fout)
    return len(morph_data)

def write_token_data_morpheme(morph_data_token, filename, fout):
    tokens_data = normalize_tokens(morph_data_token)
    part_word = ''
    part_analysis = ''
    for token_data in tokens_data:
        if token_data['is_multiword']:
            continue
        part_word += token_data['normalized_token']
        normalized_morpheme = token_data['normalized_morphemes'][0]

        part_analysis += normalized_morpheme + ' '
        for i in range(1, len(token_data['normalized_glosses'])):
            normalized_morpheme = token_data['normalized_morphemes'][i]
            if normalized_morpheme == '':
                continue
            normalized_gloss = token_data['normalized_glosses'][i]
            if normalized_gloss in GLOSSES:
                GLOSSES[normalized_gloss].add(filename)
            else:
                GLOSSES[normalized_gloss] = {filename}
            part_analysis += normalized_morpheme + '_' + normalized_gloss + ' '
    fout.write(part_word + '\t' + part_analysis.strip() + '\r\n')


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
    tokens_data = normalize_tokens(morph_data_token)
    num_tokens = len(tokens_data)
    for token_data in tokens_data:
        token_number = generate_number(token_id, token_data['is_multiword'], num_tokens)

        write_single_token_data(token_number, token_data,
                                filename, fout)
        if not token_data['is_multiword']:
            token_id += 1
    return token_id


def generate_number(token_id, is_multiword, num_tokens):
    starting_num = token_id + 1
    if is_multiword:
        return str(starting_num) + "-" + str(starting_num + num_tokens - 2)
    return str(starting_num)

def write_single_token_data(token_number, tokens_data,
                            filename, fout):
    normalized_glosses = tokens_data['normalized_glosses']
    normalized_token = tokens_data['normalized_token']
    normalized_lemma = tokens_data['normalized_lemma']
    normalized_pos = tokens_data['normalized_pos']
    normalized_features = tokens_data['normalized_features']

    if len(normalized_glosses) > 1:
        base_filename = os.path.basename(filename)
        for normalized_gloss in normalized_glosses[1:]:
            if normalized_gloss in GLOSSES:
                GLOSSES[normalized_gloss].add(base_filename)
            else:
                GLOSSES[normalized_gloss] = {base_filename}


    #ID
    output_line = token_number
    output_line += CONLL_DELIMITER
    #FORM
    output_line += normalized_token
    output_line += CONLL_DELIMITER

    for symbol in normalized_token:
        FON_SET.add(symbol)

    #LEMMA
    output_line += normalized_lemma
    output_line += CONLL_DELIMITER
    #UPOS
    output_line += normalized_pos
    output_line += CONLL_DELIMITER
    #XPOS
    output_line += CONLL_NO_VALUE
    output_line += CONLL_DELIMITER
    #FEATS
    if normalized_features == '':
        normalized_features = CONLL_NO_VALUE
    output_line += normalized_features
    output_line += CONLL_DELIMITER
    #HEAD
    output_line += CONLL_NO_VALUE
    output_line += CONLL_DELIMITER
    #DEPREL
    output_line += CONLL_NO_VALUE
    output_line += CONLL_DELIMITER
    #DEPS
    output_line += CONLL_NO_VALUE
    output_line += CONLL_DELIMITER
    #MISC
    output_line += CONLL_NO_VALUE


    fout.write(output_line + CONLL_NEW_LINE)


def normalize_tokens(morph_data_token):
    tokens_data = []
    multiword, normalized_tokens = language_utils.normalize_tokens(morph_data_token)
    if multiword != '':
        tokens_data.append({'normalized_token' : multiword,
                            'normalized_glosses' : [],
                            'normalized_lemma' : CONLL_NO_VALUE,
                            'normalized_pos' : CONLL_NO_VALUE,
                            'normalized_features' : CONLL_NO_VALUE,
                            'normalized_morphemes' : CONLL_NO_VALUE,
                            'is_multiword': True})
    
    for normalized_token_glosses in normalized_tokens:
        starting_index = normalized_token_glosses['starting_index']
        normalized_token = normalized_token_glosses['normalized_token']
        normalized_glosses = normalized_token_glosses['normalized_glosses']
        normalized_morphemes = normalized_token_glosses['normalized_morphemes']

        normalized_lemma = get_lemma(starting_index, morph_data_token, normalized_glosses)


        normalized_pos = processPOS(morph_data_token['pos'],
                                    morph_data_token['analysis'][starting_index]['fon'],
                                  normalized_token,
                                  normalized_glosses)
        normalized_features = normalize_features(get_features(morph_data_token, normalized_pos, normalized_glosses))
        tokens_data.append({'normalized_token' : normalized_token,
                            'normalized_glosses' : normalized_glosses,
                            'normalized_morphemes' : normalized_morphemes,
                            'normalized_lemma' : normalized_lemma,
                            'normalized_pos' : normalized_pos,
                            'normalized_features' : normalized_features,
                            'is_multiword' : False})
    return tokens_data


def get_lemma(starting_index, morph_data_token, normalized_glosses):
    lemma = morph_data_token['analysis'][starting_index]['fon']
    for i in range(starting_index + 1, len(normalized_glosses)):
        analysis = morph_data_token['analysis'][i]
        gloss_normalized = normalized_glosses[i]
        if language_utils.is_derivative(gloss_normalized):
            lemma += analysis['fon'].strip('-')
        else:
            break

    return language_utils.normalize_token(lemma)


def get_features(morph_data_token, normalized_pos, normalized_glosses):
    global FEATURE_TABLE
    if FEATURE_TABLE is None:
        FEATURE_TABLE = read_feature_table(FEATURE_FILENAME)
    feature_list = []
    for normalized_gloss in normalized_glosses:
        if language_utils.is_slip_unknown(normalized_gloss):
            return []
        if normalized_gloss.startswith('?') or normalized_gloss.endswith('?'):
            return []
        if language_utils.is_cyrillic(normalized_gloss) \
                or normalized_gloss == '':
            continue

        if normalized_gloss.endswith('.PL'):
            normalized_gloss = 'PL'
        feature_key = normalized_pos + "#" + normalized_gloss
        if feature_key in FEATURE_TABLE:
            feature_list += FEATURE_TABLE[feature_key]
        else:
            feature_key_all = "ALL#" + normalized_gloss
            if feature_key_all in FEATURE_TABLE:
                feature_list += FEATURE_TABLE[feature_key_all]
            else:
                print("BAD:====" + feature_key + ":" + str(morph_data_token))
    feature_list = add_default_features(feature_list, normalized_pos)
    feature_list = modify_features(feature_list, normalized_pos, morph_data_token['analysis'][0]['fon'])
    feature_list = list(set(feature_list))
    return feature_list


def modify_features(feature_list, normalized_pos, stem):



    is_imperfective = False
    is_non_futurum = False
    is_singular = False
    is_plural = False
    for feature_key, feature_value in feature_list:
        if normalized_pos == CONLL_VERB and is_imperfective_feature(feature_key, feature_value):
            is_imperfective = True
        elif normalized_pos == CONLL_VERB and is_non_futurum_feature(feature_key, feature_value):
            is_non_futurum = True
        elif is_non_singular_feature(feature_key, feature_value):
            is_plural = True
        elif is_singular_feature(feature_key, feature_value):
            is_singular = True

    if is_non_futurum:
        if is_imperfective:
            feature_list.remove(('Tense', 'Nfut'))
            feature_list.remove(('Aspect', 'Imp'))
            feature_list.append(('Tense', 'Prs'))
        elif stem == 'bi':
            feature_list.remove(('Tense', 'Nfut'))
            feature_list.append(('Tense', 'Prs'))
        else:
            feature_list.remove(('Tense', 'Nfut'))
            feature_list.append(('Tense', 'Past'))

    if is_plural and is_singular:
        feature_list.remove(('Number', 'Sing'))

    return feature_list


def add_default_features(feature_list, normalized_pos):
    if normalized_pos in [CONLL_NOUN, CONLL_PROPER, CONLL_PRON]:
        return add_default_features_nominal(feature_list)
    if normalized_pos in [CONLL_VERB]:
        return add_default_features_verbal(feature_list)
    return feature_list

def add_default_features_nominal(feature_list):
    is_singular = True
    is_nominative = True
    for feature_key, feature_value in feature_list:
        if is_nominative and is_non_nominative_case_feature(feature_key, feature_value):
            is_nominative = False
        if is_singular and is_non_singular_feature(feature_key, feature_value):
            is_singular = False
    if is_singular:
        feature_list.append(('Number', 'Sing'))
    if is_nominative:
        feature_list.append(('Case', 'Nom'))
    return feature_list

def add_default_features_verbal(feature_list):
    is_indicative = True
    is_finite = True
    for feature_key, feature_value in feature_list:
        if is_indicative and is_non_indicative_feature(feature_key, feature_value):
            is_indicative = False
        if is_finite and is_non_finite_feature(feature_key, feature_value):
            is_finite = False
    if is_indicative and is_finite:
        feature_list.append(('Mood', 'Ind'))
        feature_list.append(('VerbForm', 'Fin'))
    return feature_list

def is_non_nominative_case_feature(feature_key, feature_value):
    return feature_key == 'Case' and feature_value != 'Nom'

def is_non_singular_feature(feature_key, feature_value):
    return feature_key == 'Number' and feature_value != 'Sing'

def is_singular_feature(feature_key, feature_value):
    return feature_key == 'Number' and feature_value == 'Sing'

def is_non_indicative_feature(feature_key, feature_value):
    return feature_key == 'Mood' and feature_value != 'Ind'

def is_non_finite_feature(feature_key, feature_value):
    return feature_key == 'VerbForm' and feature_value != 'Fin'

def is_imperfective_feature(feature_key, feature_value):
    return feature_key == 'Aspect' and feature_value == 'Imp'

def is_non_futurum_feature(feature_key, feature_value):
    return feature_key == 'Tense' and feature_value == 'Nfut'

def processPOS(pos, normalized_token, first_fon, normalized_glosses):
    if pos:
        return encodePOS(pos)
    return guessPOS(normalized_token, first_fon, normalized_glosses)

def guessPOS(normalized_token, first_fon, normalized_glosses):
    first_gloss = normalize_gloss(normalized_glosses[0])

    if first_gloss == 'FOC':
        return CONLL_PARTICLE
    if first_gloss.strip() == '':
        return CONLL_OTHER
    if language_utils.is_slip_unknown(first_gloss):
        return CONLL_OTHER
    if language_utils.is_noun_negation(first_fon, first_gloss):
        return CONLL_VERB
    if language_utils.is_special_verbal_form(first_gloss):
        return CONLL_VERB
    if language_utils.is_personal_pronoun(first_gloss):
        return CONLL_PRON
    if language_utils.is_special_noun_stem(first_gloss):
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


    if language_utils.is_determiner_translation(first_gloss, normalized_glosses):
        return CONLL_DET
    if language_utils.is_pronoun_translation(first_fon, first_gloss):
        return CONLL_PRON
    if language_utils.is_code_switching(normalized_token, normalized_glosses):
        CODE_SWITCHING.add(normalized_token)
        return CONLL_OTHER


    # there cannot be a verb without any morphemes
    # so a single-stem verb must be a SLIP
    if language_utils.is_verb_gloss(first_gloss) and len(normalized_glosses) == 1:
        return CONLL_OTHER

    if len(normalized_glosses) > 1:
        for i in range(1, len(normalized_glosses)):
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
    if language_utils.is_adjective_translation(possible_pos_set, normalized_glosses):
        return CONLL_ADJ

    if language_utils.is_adverb_translation(first_gloss, possible_pos_set):
        return CONLL_ADV
    if language_utils.is_numeric_translation(first_gloss):
        return CONLL_NUM

    return CONLL_NOUN


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

def normalize_features(features):
    features_sorted = sorted(features, key = lambda x: x[0] + '#' + x[1])
    feature_string = ""
    for feature in features_sorted:
        if feature[0] == "-":
            continue
        feature_string += "|" + feature[0] + "=" + feature[1]
    return feature_string.strip("|")


def read_feature_table(filename):
    feature_table = dict()
    if not os.path.exists(filename):
        raise Exception("File %s cannot be found" % filename)
    with open(filename, "r", encoding="utf-8") as fin:
        for line in fin:
            print(line)
            line_parts = line.strip().split("\t")
            feature_key = line_parts[0].strip() + "#" + line_parts[1].strip()
            feature_parts = line_parts[2].strip().split("|")
            feature_list = []
            for feature_part in feature_parts:
                feature_part_split = feature_part.split("=")
                if len(feature_part_split) < 2:
                    feature_list.append(("-", "-"))
                else:
                    feature_list.append((feature_part_split[0], feature_part_split[1]))
                    feature_table[feature_key] = feature_list
    return feature_table

def read_file_sentence_ids(filename):
    file_sentence_dict = dict()
    with open(filename, "r", encoding="utf-8") as fin:
        for line in fin:
            if (line.startswith("#19") or line.startswith("#20") or line.startswith("#Arch")) or ".exb" in line:
                file_sentence = line.strip().split(':')
                if len(file_sentence) < 2:
                    continue
                if file_sentence[1] == '':
                    continue
                filename = file_sentence[0].strip("#")
                sentence_num = int(file_sentence[1])
                if filename in file_sentence_dict:
                    file_sentence_dict[filename].append(sentence_num)
                else:
                    file_sentence_dict[filename] = [sentence_num]
    return file_sentence_dict



def main():
    file_sentence_dict = read_file_sentence_ids("D:\Projects\morphology_scripts\data\\train.txt")

    bad_files, num_tokens, num_sentences = convert_folder_morpheme(
        "D:/ForElan/ForSIL_CORPUS/evenki_texts_corpus_05112018",
        "D:/Projects/morphology_scripts/data/train_morph2.txt",
        "D:/Projects/morphology_scripts/data/test_morph2.txt",
        [],
        file_sentence_dict
    )

    for filename, e in bad_files:
        print("%s:%s" % (filename, e))

    print("Total tokens: %s. Total sentences: %s" % (num_tokens, num_sentences))

    print('\r\n'.join(sorted(list(FON_SET))))
    print('\r\n'.join(sorted(list(CODE_SWITCHING))))
    sorted_glosses = sorted(list(GLOSSES.keys()))
    for gloss in sorted_glosses:
        filename_set = GLOSSES[gloss]
        print(gloss, '\t', ';'.join(sorted(list(filename_set))))

if __name__ == '__main__':
    main()

