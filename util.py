'''
Util functions shared between different modules
'''

import matplotlib.font_manager as font_manager
import numpy as np
import math
import string
import config

def add_custom_fonts():
    '''
    Allow us to use fonts from our fonts folder
    '''
    font_dirs = ['fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)

def get_rows_cols(n):
    rows = math.floor(math.sqrt(n))
    while(n % rows != 0):
         rows = rows - 1
    cols = int(n / rows)
    return rows, cols

def tf_idf(words, group):
    groups = words.groupby([group], as_index=False)[['n_w']].sum().rename(columns={'n_w': 'n_d'})
    tf = words.merge(groups, on=group, how="left")
    tf['tf'] = tf.n_w/tf.n_d
    c_d = tf[group].nunique()
    idf = tf.groupby('word', as_index=False)[[group]].count().rename(columns={group: 'i_d'})
    idf['idf'] = np.log(c_d/idf.i_d.values)
    tf_idf = tf.merge(idf, on="word", how="left").rename(columns={'0': 'idf'})
    tf_idf['tf_idf'] = tf_idf.tf * tf_idf.idf
    tf_idf = tf_idf.sort_values('tf_idf', ascending=False)

    return tf_idf

def group_words_by_sender(words, get_tfidf=False):
    words = words.groupby([config.SENDER_COLUMN_NAME, 'type', 'word'], as_index=False)[['n_w']].sum()

    if not get_tfidf:
        return words

    return tf_idf(words, config.SENDER_COLUMN_NAME)

def group_words_by_term(words, get_tfidf=False):
    words = words.groupby(['term', 'type', 'word'], as_index=False)[['n_w']].sum()

    if not get_tfidf:
        return words

    return tf_idf(words, 'term')

def is_hashtag(word):
    return word.startswith("#") and len(word[1:].strip(string.punctuation)) > 0 and not word[1:].isdigit()

# column name for term
def to_term(month):
    MONTHS_PER_YEAR = 12

    if MONTHS_PER_YEAR % config.TERMS_PER_YEAR != 0:
        raise ValueError("config.TERMS_PER_YEAR must be evenly divisible by 12")

    term_length = int(MONTHS_PER_YEAR / config.TERMS_PER_YEAR)

    for i in range(1, config.TERMS_PER_YEAR + 1):
        if month < (i * term_length) + 1:
            if config.TERMS_PER_YEAR in config.TERM_SUFFIX:
                return "T{} {}".format( i, config.TERM_SUFFIX[config.TERMS_PER_YEAR][i-1] )
            else:
                return "T{}".format( i )

    raise ValuError("month value must be from 1 to 12 inclusive")
