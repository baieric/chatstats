'''
Core functionality: use message data json to output graphs
'''

import os
import sys
import pandas as pd
import json
import string
import emoji
import ftfy
import datetime
import warnings

from grapher import message_graphers, word_graphers, bigram_graphers, trigram_graphers
import constants
import config
import util

def clean_type(row):
    if row.game:
        return 'Game'
    elif row.plan_update:
        return 'Plan Update'
    elif row.chat_update:
        return 'Chat Update'
    elif row.call_update:
        return 'Call Update'
    else:
        return row.type

def clean_data(data):
    '''
    Augment the raw Facebook data for our graphing use cases
    '''
    # set timezone
    data['datetime'] = pd.DatetimeIndex(
        pd.to_datetime(data['timestamp_ms'],unit='ms')
    ).tz_localize('UTC').tz_convert(config.TIMEZONE)

    # column for just date
    data['date'] = data["datetime"].apply(
        lambda d : datetime.datetime(year=d.year, month=d.month, day=d.day)
    ).map(lambda x:x.date())

    # column for term of date
    data['term'] =  pd.to_datetime(data['datetime']).apply(
        lambda d : "{} {}".format( d.strftime('%Y'), util.to_term(int(d.strftime('%m'))) )
    )

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

    # format text properly
    data['content'] = data['content'].apply(lambda x: ftfy.ftfy(x) if type(x) == str else x)

    # properly set message type, adding types 'Game', 'Plan Update', 'Chat Update'
    warnings.filterwarnings("ignore", 'This pattern has match groups')
    data['game'] = data['content'].str.contains(constants.GAME_REGEX, na=False)
    data['plan_update'] = data['content'].str.contains(constants.PLAN_UPDATE_REGEX, na=False)
    data['chat_update'] = data['content'].str.contains(constants.CHAT_UPDATE_REGEX, na=False)
    data['call_update'] = data['content'].str.contains(constants.CALL_UPDATE_REGEX, na=False)

    data['type'] = data.apply(lambda x: clean_type(x), axis=1)

    # add first name column
    data['sender_first_name'] = data['sender_name'].apply(lambda s: s.split()[0])

    return data

def make_row(r, word, type):
    return (
        r.sender_name,
        r.sender_first_name,
        r.datetime,
        r.date,
        r.term,
        word,
        type,
        1
    )

def word_data(data):
    '''
    Creates dataframe of words

    This can take a long time to run
    '''
    data['words'] = data.content.str.strip().str.split()
    data = data.dropna(subset=['words'])
    data = data[data['type'] == 'Generic']

    # create word count dataframe
    word_rows = list()
    bigram_rows = list()
    trigram_rows = list()

    for row in data[
        ['sender_name', 'sender_first_name', 'datetime', 'date', 'term', 'words']
    ].iterrows():
        r = row[1]

        two_words_ago = None
        one_word_ago = None

        for word in r.words:
            if word in constants.EMOJI_SHORTCUTS:
                word_rows.append( make_row(r, constants.EMOJI_SHORTCUTS[word], 'emoji') )
            elif word in emoji.UNICODE_EMOJI:
                word_rows.append( make_row(r, word, 'emoji') )
            elif util.is_hashtag(word):
                word_rows.append( make_row(r, word, 'hashtag') )
            else:
                for c in word:
                    if c in emoji.UNICODE_EMOJI:
                        word_rows.append( make_row(r, c, 'emoji') )

                word = word.lower().strip(string.punctuation)
                if len(word) > 0:
                    word_rows.append( make_row(r, word, 'word') )

            if two_words_ago is not None:
                trigram = "{} {} {}".format(two_words_ago, one_word_ago, word)
                trigram_rows.append( make_row(r, trigram, 'word') )
            two_words_ago = one_word_ago

            if one_word_ago is not None:
                bigram = "{} {}".format(one_word_ago, word)
                bigram_rows.append( make_row(r, bigram, 'word') )
            one_word_ago = word

    column_names = [
        'sender_name',
        'sender_first_name',
        'datetime',
        'date',
        'term',
        'word',
        'type',
        'n_w'
    ]

    words = pd.DataFrame(word_rows, columns=column_names)
    bigrams = pd.DataFrame(bigram_rows, columns=column_names)
    trigrams = pd.DataFrame(trigram_rows, columns=column_names)

    return words, bigrams, trigrams

def main(argv):
    if len(argv) != 2:
        print('Usage: {} <message_folder>'.format(argv[0]))
        sys.exit(2)

    print("Plotting graphs... This may take a minute.")

    message_arg =  argv[1]
    CHAT_FILE = "message.json"

    result_messages = []
    json_template = {}
    # get messages.json and its directory
    if message_arg.endswith(CHAT_FILE):
        json_file = message_arg
        chat_folder = message_arg[:-len(CHAT_FILE)]
    else:
        chat_folder = message_arg
        if not chat_folder.endswith("/"):
            chat_folder = "{}/".format(chat_folder)
        json_file = "{}{}".format(chat_folder, CHAT_FILE)

    for file in os.listdir(chat_folder):
        if file.endswith(".json") and file != "message.json":
            # Print the file name to debug
            print(os.path.join(chat_folder, file))
            with open(os.path.join(chat_folder, file)) as f:
                data = json.load(f)
                if (len(json_template) == 0):
                    json_template = data
                messages = data["messages"]
                result_messages += messages

    json_template['messages'] = result_messages

    with open(os.path.join(chat_folder, "message.json"),'w') as f:
        f.write(json.dumps(json_template, indent=2))

    # get the parent folder of the messages directory
    parent_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(chat_folder))))

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
    words, bigrams, trigrams = word_data(messages)
    for grapher in word_graphers:
        grapher.graph(words, output_folder, parent_folder)

    for grapher in bigram_graphers:
        grapher.graph(bigrams, output_folder, parent_folder)

    for grapher in trigram_graphers:
        grapher.graph(trigrams, output_folder, parent_folder)

    print("Results saved in {}".format(output_folder))

if __name__ == "__main__":
    main(sys.argv)
