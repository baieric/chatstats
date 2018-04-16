'''
Util functions shared between different modules
'''
import csv
import os
import sys
import unicodedata
import re
import matplotlib.font_manager as font_manager

def get_csvs(chat_folder):
    '''
    return a dictionary of all generated csv files
    '''
    messages_csv = '{}/messages.csv'.format(chat_folder)
    if not os.path.exists(messages_csv):
        print('messages.csv not found. Generate messages.csv with fb_parser.py')
        sys.exit(2)

    words_csv = '{}/words.csv'.format(chat_folder)
    if not os.path.exists(words_csv):
        print('words.csv not found. Generate words.csv with fb_parser.py')
        sys.exit(2)

    csv_dict = dict()
    csv_dict['messages'] = messages_csv
    csv_dict['words'] = words_csv

    return csv_dict

def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def get_output_folder(filename, title_str):
    '''
    from the HTML title and filename, generate a folder name
    '''
    title = slugify(title_str[len("Conversation with "):])
    chat_num = os.path.basename(filename)[:-len(".html")]
    if len(title) > 0:
        folder_name = "chat_{}_{}".format(chat_num, title)
    else:
        folder_name = "chat_{}".format(chat_num)
    return "my_data/{}".format(folder_name)


def add_custom_fonts():
    '''
    Allow us to use fonts in our fonts folder
    '''
    font_dirs = ['fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)
