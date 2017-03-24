# Tags: type_tag
# st : step
# re : requirement
# co : requirement consumable, usually ingredient
# nc : requirement non-consumable, usually a tool
# Tags: language_tag
# en : English
# es : Spanish
import simple_label_parser, codecs

def process_label(language_tag,type_tag,label):
    label = label.decode("utf8")
    print label
    modified_label = simple_label_parser.parse_label(language_tag,type_tag,label)
    print modified_label
    return modified_label.strip()+"\n"

label_file = open("labels.txt","r")
label_file_modified = codecs.open("labels_converted.txt","w","utf-8")
for line in iter(label_file):
    if len(line) > 1 and not line.startswith("#"):
        language_tag = line.split(' ', 1)[0]
        rest = line.split(' ', 1)[1]
        type_tag = rest.split(' ', 1)[0]
        rest = rest.split(' ', 1)[1]
        id = rest.split(' ', 1)[0]
        label = rest.split(' ', 1)[1]
        #print language_tag
        #print type_tag
        #print id
        #print label
        label_file_modified.write(language_tag+u" "+type_tag+u" "+id+u" "+process_label(language_tag,type_tag,label))
    else:
        label_file_modified.write(line.decode("utf-8"))
label_file.close()
label_file_modified.close()
