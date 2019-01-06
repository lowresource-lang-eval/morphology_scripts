#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import xml.etree.ElementTree as ET



GLOSS_XPATH = ".//TIER[@TIER_ID='gl%s']/ANNOTATION/REF_ANNOTATION"
FON_XPATH = ".//TIER[@TIER_ID='fon%s']/ANNOTATION/REF_ANNOTATION"
POS_XPATH = ".//TIER[@TIER_ID='pos%s']/ANNOTATION/REF_ANNOTATION"
FONWORD_XPATH = ".//TIER[@TIER_ID='fonWord%s']/ANNOTATION/REF_ANNOTATION"
FONWORD1_XPATH = ".//TIER[@TIER_ID='fonWord1']/ANNOTATION/REF_ANNOTATION"
FONWORD2_XPATH = ".//TIER[@TIER_ID='fonWord2']/ANNOTATION/REF_ANNOTATION"
RUS_XPATH = ".//TIER[@TIER_ID='rus%s']/ANNOTATION/REF_ANNOTATION"
LANGUAGE_XPATH = ".//TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION"


ANNOTATION_VALUE_XPATH = '/ANNOTATION_VALUE'

ANNOTATION_REF_ATTRIBUTE = 'ANNOTATION_REF'
ANNOTATION_ID_ATTRIBUTE = 'ANNOTATION_ID'

EAF_EXTENSION = '.eaf'

def get_text_data(filename, language_code):
    root = get_root(filename)
    tier_nums_sentences = get_sentences(root, language_code)
    text_data = []
    for tier_num, sentences in tier_nums_sentences:
        for sentence in sentences:
            text_data_sentence = dict()
            text_data_sentence['sentence'] = get_annotation_value_from_element(sentence)
            translation = get_translation_by_sentence(root, sentence, tier_num)
            text_data_sentence['translation'] = translation

            if translation == 'Потом этот человек зашел в один чум.':
                test_debug = 9

            text_data_sentence['morphology'] = get_tokens_by_sentence(root, sentence, tier_num,
                                                                      translation, filename)
            text_data.append(text_data_sentence)
    return text_data


def get_sentences(root, language_code):
    language_xpath_with_code = LANGUAGE_XPATH % language_code
    sentences = root.findall(language_xpath_with_code)
    if sentences:
        return [('', sentences)]
    #extra logic for dialogues
    language_xpath_with_code1 = LANGUAGE_XPATH % (language_code + '1')
    language_xpath_with_code2 = LANGUAGE_XPATH % (language_code + '2')
    return [('1', root.findall(language_xpath_with_code1)),
            ('2', root.findall(language_xpath_with_code2))]

def get_tokens_by_sentence(root, sentence, tier_num, translation, filename):
    sentence_id = get_element_id(sentence)
    fon_words = get_fon_words_by_id(root, sentence_id, tier_num)
    morph_data = []
    for fon_word in fon_words:
        morph_data_word = dict()
        token = get_annotation_value_from_element(fon_word, translation)
        morph_data_word['token'] = token
        morph_data_word['analysis'] = get_analysis(root, fon_word, tier_num, token, translation)
        morph_data_word['pos'] = determinePOS(root, fon_word, tier_num,
                                              morph_data_word['analysis'], filename)
        morph_data.append(morph_data_word)
    return morph_data


def get_translation_by_sentence(root, sentence, tier_num):
    sentence_id = get_element_id(sentence)
    return get_annotation_value_from_element(root.find(RUS_XPATH % tier_num + "[@" +
                                                       ANNOTATION_REF_ATTRIBUTE +
                                                   "='" + sentence_id + "']"))


def get_analysis(root, fon_word, tier_num, fon_token, translation):
    fon_word_id = get_element_id(fon_word)
    fons = get_fons_by_id(root, fon_word_id, tier_num)
    analysis = []
    if len(fons) == 0:
        raise Exception(
            'No fon elements for fonWord with id %s (%s), sentence: %s' % (fon_word_id, fon_token, translation))

    for fon in fons:
        fon_id = get_element_id(fon)
        gloss = get_gloss_by_id(root, fon_id, tier_num)

        fon_value = get_annotation_value_from_element(fon, translation)
        if fon_value is None:
            raise Exception(
                'No fon element for fonWord %s with id: %s, sentence: %s' % (fon_word_id, fon_token, translation))

        if gloss is None:
            raise Exception(
                'No gloss element for fonWord %s with id: %s, sentence: %s' % (fon_word_id, fon_token, translation))

        glossValue = get_annotation_value_from_element(gloss, translation)
        if glossValue is None:
            raise Exception(
                'No gloss element for fonWord %s with id: %s, sentence: %s' % (fon_word_id, fon_token, translation))


        analysis.append({'fon': fon_value, 'gloss': glossValue})
    return analysis


def determinePOS(root, fon_word, tier_num, analysis, filename):
    fon_word_id = get_element_id(fon_word)
    pos_element = get_pos_by_id(root, fon_word_id, tier_num)
    if pos_element is None:
        return None
    return get_annotation_value_from_element(pos_element)





def get_root(filename):
    tree = ET.parse(filename)
    return tree.getroot()



def get_annotation_value_from_element(element, translation=None):
    element_text = element.find('.' + ANNOTATION_VALUE_XPATH).text
    if element_text:
        return element_text.strip()
    error_text = 'Empty element found: %s' % element.attrib
    if translation is not None:
        error_text += ' for sentence %s' % translation
    raise Exception(error_text)


def get_element_id(element):
    return element.attrib[ANNOTATION_ID_ATTRIBUTE]


def get_fon_words_by_id(root, annotation_id, tier_num):
    return root.findall(FONWORD_XPATH % tier_num + "[@" +
                        ANNOTATION_REF_ATTRIBUTE +
                        "='" + annotation_id + "']")


def get_fons_by_id(root, annotation_id, tier_num):
    return root.findall(FON_XPATH % tier_num + "[@" +
                        ANNOTATION_REF_ATTRIBUTE +
                        "='" + annotation_id + "']")



def get_pos_by_id(root, annotation_id, tier_num):
    return root.find(POS_XPATH % tier_num + "[@" +
                     ANNOTATION_REF_ATTRIBUTE +
                     "='" + annotation_id + "']")


def get_gloss_by_id(root, annotation_id, tier_num):
    return root.find(GLOSS_XPATH % tier_num + "[@" +
                     ANNOTATION_REF_ATTRIBUTE +
                     "='" + annotation_id + "']")


def is_eaf(filename):
    return filename.endswith(EAF_EXTENSION)
