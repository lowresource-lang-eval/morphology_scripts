#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"
import xml.etree.ElementTree as ET

TIER_PATH = "./basic-body/tier[@id='%s']"
EXMARALDA_BASIC = ".exb"

def is_esm(filename):
    return filename.endswith(EXMARALDA_BASIC)

def get_text_data(filename):
    """
    :param filename: EAF filename
    :return: a dictionary containing sentences, their translations and the interlinearization data
    """
    root = get_root(filename)
    sentence_borders = get_sentence_borders(root)
    words_split_morphemes = get_tier_data(root, 'mb')
    glosses = get_tier_data(root, 'ge')
    parts_of_speech = get_tier_data(root, 'ps')
    text_data = []
    for sentence_border in sentence_borders:
        sentence_start = sentence_border['time'][0]
        sentence_end = sentence_border['time'][1]
        text_data_sentence = dict()
        text_data_sentence['sentence'] = sentence_border['sentence']
        text_data_sentence['translation'] = sentence_border['translation']
        text_data_sentence['morphology'] = get_tokens_by_sentence(words_split_morphemes, glosses,
                                                                  parts_of_speech,
                                                                  sentence_start, sentence_end)
        text_data.append(text_data_sentence)
    return text_data

def get_tokens_by_sentence(words_split_morphemes,
                           glosses,
                          parts_of_speech,
                           sentence_start, sentence_end):
    morph_data = []
    for i in range(sentence_start, sentence_end):
        morph_data_word = dict()
        morph_data_word['token'] = words_split_morphemes[i]
        morph_data_word['analysis'] = glosses[i]
        morph_data_word['pos'] = parts_of_speech[i]
        morph_data.append(morph_data_word)
    return morph_data

def get_sentence_borders(root):
    events = []
    sentence_tier = get_tier(root, 'ts')
    translation_tier = get_tier(root, 'fr')
    for index, event in enumerate(sentence_tier):
        event_time = (get_event_number(event.attrib['start']),
                       get_event_number(event.attrib['end']))
        event = {'time' : event_time,
                 'sentence' : event.text,
                 'translation' : translation_tier[index].text}
        events.append(event)
    return events

def get_tier_data(root, tier_name):
    tier = get_tier(root, tier_name)
    tier_data = dict()
    for event in tier:
        event_number = get_event_number(event.attrib['start'])
        tier_data[event_number] = event.text
    return tier_data

def get_root(filename):
    tree = ET.parse(filename)
    return tree.getroot()

def get_tier(root, tier_name):
    return root.find(TIER_PATH % tier_name)

def get_event_number(event_code):
    return int(event_code.split('T')[-1])

text_data = get_text_data('D:/Projects/2019/LowResourceSharedTask/selkup/flk/'
              'BAG_1964_ItjaMousetrapped_flk/BAG_1964_ItjaMousetrapped_flk.exb')

for sentence in text_data:
    print(sentence)