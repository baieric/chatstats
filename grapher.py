'''
Graphers turn dataframes into graphs
'''

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
from slugify import slugify

import constants
import util
import config

class Grapher(object):
    '''
    Interface for Grapher, which reads a dataframe and outputs a graph
    '''
    # outputs a graph bitmap to the output_folder
    def graph(self, data, output_folder, parent_folder):
        raise NotImplementedError( "Implement the graph function for a concrete Grapher" )

    def __init__(self, type=None):
        self.type = type


class SenderMessagesGraph(Grapher):
    '''
    Plots the number of messages sent by each sender
    '''
    def graph(self, data, output_folder, parent_folder):
        to_plot = data[config.SENDER_COLUMN_NAME].value_counts()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot.index,
            y=to_plot.values,
            order=to_plot.index,
            palette = config.PALETTE
        )

        # add number text above each bar
        for rect, label in zip(plot.patches, to_plot.values.tolist()):
            if label == 0:
                continue
            height = rect.get_height()
            plot.text(
                rect.get_x() + rect.get_width()/2,
                height + 0.5, label,
                ha='center',
                va='bottom'
            )

        TITLE = "Number of messages sent"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class CallDurationGraph(Grapher):
    '''
    Plots the longest calls
    '''
    def graph(self, data, output_folder, parent_folder):
        data = data[data['type'] == 'Call'].sort_values('call_duration',ascending=False).head(10)

        sns.set(style="darkgrid")
        plot = sns.barplot(
            data=data,
            y=data.date,
            x=data.call_duration,
            orient='h',
            palette = config.PALETTE
        )

        TITLE = "Longest calls"
        plt.suptitle(TITLE, y = 1)
        plot.set(ylabel="Day of call", xlabel="Call duration in seconds")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class WeekdayMessagesGraph(Grapher):
    '''
    Plots the number of messages sent in each weekday
    '''
    def graph(self, data, output_folder, parent_folder):
        data['weekday'] = data['datetime'].dt.day_name()
        to_plot = data.groupby(['weekday', config.SENDER_COLUMN_NAME], as_index=False)[['type']].count()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['weekday'],
            y=to_plot['type'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            order=constants.WEEKDAYS,
            palette = config.PALETTE
        )

        TITLE = "Messages by weekday"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class TopDaysMessagesGraph(Grapher):
    '''
    Plots the top 5 days with most messages
    '''
    def graph(self, data, output_folder, parent_folder):
        to_plot = data.groupby(['date', config.SENDER_COLUMN_NAME], as_index=False)[['type']].count()
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['date'],
            y=to_plot['type'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            order=to_plot.groupby('date').type.sum().sort_values(ascending=False).head(5).index,
            palette = config.PALETTE
        )
        TITLE = "Days with the most messages"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class TimeInDayMessagesGraph(Grapher):
    '''
    Plots the frequency of messages for time in the day
    '''
    def graph(self, data, output_folder, parent_folder):
        # get hour
        data['time'] = data['datetime'].dt.time.apply( lambda x: x.hour )

        to_plot = data.groupby(['time', config.SENDER_COLUMN_NAME], as_index=False)[['type']].count().sort_values('time')

        sns.set(style="darkgrid")
        plot = sns.barplot(
            data=to_plot,
            x='time',
            y='type',
            hue=config.SENDER_COLUMN_NAME,
            palette = config.PALETTE
        )
        TITLE = "Messages by hour of day"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class PerTermMessagesGraph(Grapher):
    '''
    Plots the frequency of messages for each 4 month term
    '''
    def graph(self, data, output_folder, parent_folder):
        to_plot = data.groupby(['term', config.SENDER_COLUMN_NAME], as_index=False)[['type']].count()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            data=to_plot,
            y='term',
            x='type',
            hue=config.SENDER_COLUMN_NAME,
            orient='h',
            palette = config.PALETTE
        )

        TITLE = "Messages by trimester"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")

        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class TopStickersMessagesGraph(Grapher):
    '''
    Plots the frequency of messages for time in the day
    '''
    def graph(self, data, output_folder, parent_folder):
        to_plot = data.groupby(['sticker', config.SENDER_COLUMN_NAME], as_index=False)[['type']].count()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['sticker'],
            y=to_plot['type'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            hue_order=to_plot[config.SENDER_COLUMN_NAME].unique(),
            order=to_plot.groupby('sticker').type.sum().sort_values(ascending=False).head(10).index,
            palette = config.PALETTE
        )

        sticker_files = ["{}/{}".format(parent_folder, t.get_text())  for t in plot.get_xticklabels()]

        def plotImage(x, y, im):
            # TODO hard-coded size of images, breaks in some cases
            width = 1
            height = 2
            bb = Bbox.from_bounds(x,y,width, height)
            bb2 = TransformedBbox(bb,plot.transData)
            bbox_image = BboxImage(bb2,
                                norm = None,
                                origin=None,
                                clip_on=False)

            bbox_image.set_data(im)
            plot.add_artist(bbox_image)

        # TODO hard coded coordinates of images, breaks in some cases
        x = -0.5
        y = plot.patches[0].get_y()-2.5
        for file in sticker_files:
            img =  plt.imread(file)
            plotImage(x, y, img)
            x += 1

        TITLE = "Most frequent stickers"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='', xticklabels=[])
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.xaxis.labelpad = 25
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class WordsPerMessageGraph(Grapher):
    '''
    Plots the average number of words per message
    '''
    def graph(self, data, output_folder, parent_folder):
        data['words'] = data.content.str.strip().str.split()
        data = data.dropna(subset=['words'])
        data = data[data['type'] == 'Generic']
        data['num_words'] = data['words'].apply(lambda x: len(x))
        to_plot = data.groupby([config.SENDER_COLUMN_NAME], as_index=False)[['num_words']].mean()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            data=to_plot,
            y='num_words',
            x=config.SENDER_COLUMN_NAME,
            palette = config.PALETTE
        )

        # add number text above each bar
        for rect, label in zip(plot.patches, to_plot.values.tolist()):
            if label[1] == 0:
                continue
            height = rect.get_height()
            plot.text(
                rect.get_x() + rect.get_width()/2,
                height + 0.1, round(float(label[1]), 2),
                ha='center',
                va='bottom'
            )

        TITLE = "Average number of words per message"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')

        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class WordCountGraph(Grapher):
    '''
    Plots the most common words
    '''
    def graph(self, data, output_folder, parent_folder):
        data = util.group_words_by_sender(data)
        # words only
        data = data[data['type'] == 'word']
        # ignore contractions
        data = data[~data.word.str.contains("\'", na=False)]
        # ignore words under 4 chars
        data = data[data['word'].str.len() > 4]

        # filter out most common words
        with open("word_lists/common.txt") as f:
            common = f.readlines()
            common = [x.lower().strip() for x in common]
        to_plot = data.groupby([config.SENDER_COLUMN_NAME,'word'], as_index=False)[['n_w']].sum()
        to_plot = to_plot[~to_plot.word.isin(common)]

        # ignore numbers
        to_plot = to_plot[~to_plot.word.isin([str(x) for x in range(0,10)])]

        sns.set(style="darkgrid")
        plot = sns.barplot(
            y=to_plot['word'],
            x=to_plot['n_w'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            palette = config.PALETTE,
            orient="h",
            order=to_plot.groupby('word').n_w.sum().sort_values(ascending=False).head(10).index,
        )

        TITLE = "Most common words"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class NameGraph(Grapher):
    '''
    Plot who says whose names
    '''
    def graph(self, data, output_folder, parent_folder):
        data = util.group_words_by_sender(data)
        names = data[config.SENDER_COLUMN_NAME].unique().tolist()
        first_names = sorted([x.split()[0].lower() for x in names])
        to_plot = data[data['word'].isin(first_names)].groupby(['word', config.SENDER_COLUMN_NAME], as_index=False)[['n_w']].sum()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['word'],
            y=to_plot['n_w'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            palette = config.PALETTE,
        )

        TITLE = "Names said in chat"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='', xticklabels=["\"{}\"".format(x) for x in first_names])
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

'''
Plots the most common emojis
'''
class EmojiCountGraph(Grapher):
    def graph(self, data, output_folder, parent_folder):
        data = util.group_words_by_sender(data)
        to_plot = data[data['type'] == 'emoji']

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['word'],
            y=to_plot['n_w'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            palette = config.PALETTE,
            order=to_plot.groupby('word')[['n_w']].sum().sort_values('n_w',ascending=False).head(10).index,
        )

        util.add_custom_fonts()

        for item in plot.get_xticklabels():
            item.set_family('EmojiOne')
            item.set_fontsize(20)

        emojis = [x.get_text() for x in plot.get_xticklabels()]
        print("Your top emojis:")
        print("   ".join(["{}. {}".format(i+1, e) for i, e in enumerate(emojis)]))

        TITLE = "Most frequent emoji"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()

class SenderDistinguishingWordsGraph(Grapher):
    '''
    Plots the most distinctive words per sender
    '''
    def graph(self, data, output_folder, parent_folder):
        if self.type == None:
            raise ValueError("Grapher type must be set to a string")

        data = util.group_words_by_sender(data, get_tfidf=True)
        data = data[data['word'].str.len() > 1]
        data = data[data['type'] == 'word']
        senders = data[config.SENDER_COLUMN_NAME].unique().tolist()
        N = len(senders)
        rows, cols = util.get_rows_cols(N)

        fig, ax = plt.subplots(figsize=(cols * 2, rows * 3), ncols=cols, nrows=rows, squeeze=False)
        plt.subplots_adjust(
            left    =  0.2,
            bottom  =  0.1,
            right   =  2,
            top     =  0.9,
            wspace  =  0.5,
            hspace  =  1.1
        )

        for i in range(N):
            ax[int(i / cols)][i % cols].set_title(senders[i], y = 1)
            to_plot = data[data[config.SENDER_COLUMN_NAME] == senders[i]]
            to_plot = to_plot.head(10)[[config.SENDER_COLUMN_NAME,'word','tf_idf']]
            plot = sns.barplot(
                y=to_plot['word'],
                x=to_plot['tf_idf'],
                data=to_plot,
                palette = config.PALETTE,
                orient="h",
                ax=ax[int(i / cols)][i % cols]
            )
            plot.set(
                ylabel="",
                xlabel="Distinctiveness Score"
            )

        TITLE = "Our Most Distinguishing {}".format(self.type)
        plt.suptitle(TITLE, y = 1.09, fontsize=20)
        fig.savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        fig.clf()

class TermDistinguishingWordsGraph(Grapher):
    '''
    Plots the most distinctive words per term
    '''
    def graph(self, data, output_folder, parent_folder):
        if self.type == None:
            raise ValueError("Grapher type must be set to a string")

        data = util.group_words_by_term(data, get_tfidf=True)
        data = data[data['word'].str.len() > 1]
        data = data[data['type'] == 'word']
        terms = sorted(data.term.unique().tolist())
        N = len(terms)
        rows, cols = util.get_rows_cols(N)

        fig, ax = plt.subplots(figsize=(cols * 2, rows * 3), ncols=cols, nrows=rows, squeeze=False)
        plt.subplots_adjust(
            left    =  0.2,
            bottom  =  0.1,
            right   =  2,
            top     =  0.9,
            wspace  =  0.5,
            hspace  =  1.1
        )

        for i in range(N):
            ax[int(i / cols)][i % cols].set_title(terms[i], y = 1)
            to_plot = data[data['term'] == terms[i]]
            to_plot = to_plot.head(10)[['term','word','tf_idf']]
            plot = sns.barplot(
                y=to_plot['word'],
                x=to_plot['tf_idf'],
                data=to_plot,
                palette = config.PALETTE,
                orient="h",
                ax=ax[int(i / cols)][i % cols]
            )
            plot.set(
                ylabel="",
                xlabel="Distinctiveness Score"
            )

        TITLE = "Each Term's Most Distinguishing {}".format(self.type)
        plt.suptitle(TITLE, y = 1.09, fontsize=20)
        fig.savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        fig.clf()

class HashtagGraph(Grapher):
    '''
    Plots the most used hashtags
    '''
    def graph(self, data, output_folder, parent_folder):
        data = util.group_words_by_sender(data)
        to_plot = data[data['type'] == 'hashtag']

        sns.set(style="darkgrid")
        plot = sns.barplot(
            y=to_plot['word'],
            x=to_plot['n_w'],
            hue=to_plot[config.SENDER_COLUMN_NAME],
            data=to_plot,
            palette = config.PALETTE,
            orient="h",
            order=to_plot.groupby('word').n_w.sum().sort_values(ascending=False).head(10).index,
        )

        TITLE = "Most frequent hashtags"
        plt.suptitle(TITLE, y = 1)
        plot.set(xlabel='', ylabel='')
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/{}.png".format(output_folder, slugify(TITLE)),
            bbox_inches='tight',
            pad_inches=config.PAD_INCHES
        )
        plot.get_figure().clf()


message_graphers = [
    SenderMessagesGraph(),
    WeekdayMessagesGraph(),
    TopDaysMessagesGraph(),
    TimeInDayMessagesGraph(),
    PerTermMessagesGraph(),
    # ChatStats is failing to parse stickers right now! This is probably easy to fix, please file a pull request <3
    # TopStickersMessagesGraph(),
    WordsPerMessageGraph(),
]

word_graphers = [
    EmojiCountGraph(),
    NameGraph(),
    HashtagGraph(),
    SenderDistinguishingWordsGraph("Words"),
    TermDistinguishingWordsGraph("Words"),
]

bigram_graphers = [
    SenderDistinguishingWordsGraph("Bigrams"),
    TermDistinguishingWordsGraph("Bigrams"),
]

trigram_graphers = [
    SenderDistinguishingWordsGraph("Trigrams"),
    TermDistinguishingWordsGraph("Trigrams"),
]

# Unused:
# CallDurationGraph(),
# WordCountGraph(),
