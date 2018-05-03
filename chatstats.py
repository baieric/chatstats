'''
Core functionality: use message data json to output graphs
'''

import os
import sys
import pandas as pd
import numpy as np
import json
import string
import emoji
import ftfy

from grapher import message_graphers, word_graphers
import constants

def clean_data(data):
    '''
    Augment the raw Facebook data for our graphing use cases
    '''
    # set timezone
    TIMEZONE = 'US/Eastern'
    data['datetime'] = pd.DatetimeIndex(pd.to_datetime(data['timestamp'], unit='s')).tz_localize('UTC').tz_convert(TIMEZONE)

    # clean up sticker data
    data['sticker'] = data['sticker'].apply(lambda s: s['uri'] if not pd.isnull(s) else None)
    duplicate_likes = [
        "messages/stickers_used/851582_369239386556143_1497813874_n_369239383222810.png",
        "messages/stickers_used/851587_369239346556147_162929011_n_369239343222814.png"
    ]
    data['sticker'] = data['sticker'].replace(
        duplicate_likes,
        "messages/stickers_used/851557_369239266556155_759568595_n_369239263222822.png"
    )

    # add first name column
    data['sender_first_name'] = data['sender_name'].apply(lambda s: s.split()[0])

    return data

def word_data(data):
    '''
    Creates dataframe of word counts for each participant, including TF-IDF values

    This can take a long time to run
    '''
    data = data[data['type'] == 'Generic']
    data['words'] = data.content.str.strip().str.split()
    data = data.dropna(subset=['words'])

    # create word count dataframe
    rows = list()
    for row in data[['sender_name', 'words']].iterrows():
        r = row[1]
        for word in r.words:
            # normalize unicode
            word = word.replace("\u00e2\u0080\u0099", "'")
            word = ftfy.ftfy(word)

            if word in constants.EMOJI_SHORTCUTS:
                rows.append((r.sender_name, constants.EMOJI_SHORTCUTS[word], 'emoji', 1))
            elif word in emoji.UNICODE_EMOJI:
                rows.append((r.sender_name, word, 'emoji', 1))
            elif word.startswith("#") and len(word[1:].strip(string.punctuation)) > 0 and not word[1:].isdigit():
                rows.append((r.sender_name, word, 'hashtag', 1))
            else:
                for c in word:
                    if c in emoji.UNICODE_EMOJI:
                        rows.append((r.sender_name, c, 'emoji', 1))

                word = word.lower().strip(string.punctuation)
                if len(word) > 0:
                    rows.append((r.sender_name, word, 'word', 1))

    words = pd.DataFrame(rows, columns=['sender_name', 'word', 'type', 'n_w'])
    words = words.groupby(['sender_name', 'type', 'word'], as_index=False)[['n_w']].sum()

    # calculate tf-idf values
    senders = words.groupby(['sender_name'], as_index=False)[['n_w']].sum().rename(columns={'n_w': 'n_d'})
    tf = words.merge(senders, on="sender_name", how="left")
    tf['tf'] = tf.n_w/tf.n_d
    c_d = tf.sender_name.nunique()
    idf = tf.groupby('word', as_index=False)[['sender_name']].count().rename(columns={'sender_name': 'i_d'})
    idf['idf'] = np.log(c_d/idf.i_d.values)
    tf_idf = tf.merge(idf, on="word", how="left").rename(columns={'0': 'idf'})
    tf_idf['tf_idf'] = tf_idf.tf * tf_idf.idf
    tf_idf = tf_idf.sort_values('tf_idf', ascending=False)

    return tf_idf

def main(argv):
    if len(argv) != 2:
        print('Usage: {} <message_folder>'.format(argv[0]))
        sys.exit(2)

    print("Plotting graphs...")

    message_arg =  argv[1]
    CHAT_FILE = "message.json"

    # get messages.json and its directory
    if message_arg.endswith(CHAT_FILE):
        json_file = message_arg
        chat_folder = message_arg[:-len(CHAT_FILE)]
    else:
        chat_folder = message_arg
        if not chat_folder.endswith("/"):
            chat_folder = "{}/".format(chat_folder)
        json_file = "{}{}".format(chat_folder, CHAT_FILE)

    # get the parent folder of the messages directory
    parent_folder = os.path.dirname(os.path.dirname(os.path.dirname(chat_folder)))

    # open json file as dict
    json_data = json.loads(open(json_file).read())

    # create output folder for graphs
    output_folder = 'my_data/{}'.format(json_data["thread_path"])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # generate graphs that use message data
    messages = clean_data(pd.DataFrame(json_data["messages"]))
    for grapher in message_graphers:
        grapher.graph(messages, output_folder, parent_folder)

    # generate graphs that use word data
    words = word_data(messages)
    for grapher in word_graphers:
        grapher.graph(words, output_folder, parent_folder)

    print("Results saved in {}".format(output_folder))

if __name__ == "__main__":
    main(sys.argv)
