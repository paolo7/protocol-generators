import re

def parse_label(language_tag,type_tag,label):
    # remove parenthesis
    label = re.sub(r'\([^)]*\)', '', label)
    # remove numbers
    label = re.sub(r'([&#199;&#209;])+', '', label)
    label = ''.join([i for i in label if not i.isdigit()])
    label = re.sub(r' +',' ',label).strip()
    label = label.lower()
    #if type_tag == "co":
        #return parse_consumable(language_tag,label)
    return label

def parse_consumable(language_tag,label):
    if language_tag == "en":
        if " of " in label:
            label = ' '.join(label.split(' of ', 1)[-1]).strip()
    if language_tag == "es":
        if " de " in label:
            label = ' '.join(label.split(' de ', 1)[-1]).strip()
    return label
