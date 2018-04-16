# -*- coding: utf-8 -*-

'''
Graphers turn dataframes into graphs
'''

import pandas as pd
import numpy as np
import string
import seaborn as sns
import datetime
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
import matplotlib.font_manager as font_manager

import constants

class Grapher(object):
    '''
    Interface for Grapher, which reads a CSV and outputs a graph
    '''
    # outputs a graph bitmap to the output_folder
    def graph(self, csvs, output_folder):
        raise NotImplementedError( "Implement the graph function for a concrete Grapher" )

class SenderMessagesGraph(Grapher):
    '''
    Plots the number of messages sent by each sender
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')
        to_plot = df['sender'].value_counts()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot.index,
            y=to_plot.values,
            order=to_plot.index,
            palette = "muted"
        )

        # add number text above each bar
        for rect, label in zip(plot.patches, to_plot.values.tolist()):
            if label == 0:
                continue
            height = rect.get_height()
            plot.text(rect.get_x() + rect.get_width()/2, height + 0.5, label, ha='center', va='bottom')

        plot.set(xlabel="Sender", ylabel="Messages sent")
        plot.get_figure().savefig(
            "{}/sender_messages.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

class WeekdayMessagesGraph(Grapher):
    '''
    Plots the number of messages sent in each weekday
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.weekday_name
        to_plot = df.groupby(['weekday', 'sender'], as_index=False)[['message']].count()
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['weekday'],
            y=to_plot['message'],
            hue=to_plot['sender'],
            data=to_plot,
            order=constants.WEEKDAYS,
            palette = "muted"
        )
        plot.set(xlabel="Day of the week", ylabel="Messages sent")
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/weekday_messages.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

class TopDaysMessagesGraph(Grapher):
    '''
    Plots the top 5 days with most messages
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')

        # convert date column to only store date and not time
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df["date"].apply( lambda d : datetime.datetime(year=d.year, month=d.month, day=d.day)).map(lambda x:x.date())

        to_plot = df.groupby(['date', 'sender'], as_index=False)[['message']].count()
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['date'],
            y=to_plot['message'],
            hue=to_plot['sender'],
            data=to_plot,
            order=to_plot.groupby('date').message.sum().sort_values(ascending=False).head(5).index,
            palette = "muted"
        )
        plot.set(xlabel="Top 5 Days With Most Messages", ylabel="Messages sent")
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/top_days_messages.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

class TimeInDayMessagesGraph(Grapher):
    '''
    Plots the frequency of messages for time in the day
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')

        # convert date column to only store time
        df['date'] = pd.to_datetime(df['date']).dt.time.apply( lambda x: x.hour*60 + x.minute )

        to_plot = df.groupby(['date', 'sender'], as_index=False)[['message']].count().sort_values('date')

        # have to set labels manually because I can't figure out how to do it programmatically :(
        labels=[None, "12:00am", "3:20am", "6:40am", "10:00am", "1:20pm", "4:40pm", "8:00pm", "11:20pm"]

        sns.set(style="darkgrid")
        plot = sns.lmplot(
            data=to_plot,
            x='date',
            y='message',
            hue='sender',
            fit_reg=False,
            scatter_kws={"s": 10},
            palette = "muted"
        )
        plot.set(xlabel="Time in a Day", ylabel="Messages sent", xticklabels=labels)
        plot.set_xticklabels(rotation=15)
        plot.fig.savefig(
            "{}/time_in_day_messages.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.fig.clf()

class PerMonthMessagesGraph(Grapher):
    '''
    Plots the frequency of messages each month
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')

        # convert date column to only month
        df['date'] =  pd.to_datetime(df['date']).apply( lambda d : d.strftime('%Y-%m'))

        to_plot = df.groupby(['date', 'sender'], as_index=False)[['message']].count()

        num_months = len(to_plot['date'].unique().tolist())
        fifth = int(num_months / 5)
        sns.set(style="darkgrid")
        plot = sns.lmplot(
            data=to_plot,
            x='date',
            y='message',
            hue='sender',
            fit_reg=False,
            scatter_kws={"s": 10},
            palette = "muted"
        )
        plot.set(xlabel="Months", ylabel="Messages sent")
        plot.set(xticks=[0, fifth * 1, fifth * 2, fifth * 3, fifth * 4, num_months - 1])
        plot.fig.savefig(
            "{}/per_month_messages.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.fig.clf()

class TopStickersMessagesGraph(Grapher):
    '''
    Plots the frequency of messages for time in the day
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['messages'], sep=',')

        to_plot = df[df['type'] == "sticker"].groupby(
            ['files', 'sender'],
            as_index=False
        )[['date']].count()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['files'],
            y=to_plot['date'],
            hue=to_plot['sender'],
            data=to_plot,
            hue_order=to_plot.sender.unique(),
            order=to_plot.groupby('files').date.sum().sort_values(ascending=False).head(10).index,
            palette = "muted"
        )

        with open("{}/message_dir.txt".format(output_folder)) as f:
            message_dir = f.readlines()[0]

        sticker_files = ["{}/{}".format(message_dir, t.get_text())  for t in plot.get_xticklabels()]

        def plotImage(x, y, im):
            # TODO hard-coded size of images, breaks in some cases
            bb = Bbox.from_bounds(x,y,1, 2)
            bb2 = TransformedBbox(bb,plot.transData)
            bbox_image = BboxImage(bb2,
                                norm = None,
                                origin=None,
                                clip_on=False)

            bbox_image.set_data(im)
            plot.add_artist(bbox_image)

        # TODO hard coded coordinates of images, breaks in some cases
        x = -0.5
        y = plot.patches[0].get_y()-2
        for file in sticker_files:
            img =  plt.imread(file)
            plotImage(x, y, img)
            x += 1

        plot.set(xlabel="Top 10 Stickers Used", ylabel="Occurrences", xticklabels=[])
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.xaxis.labelpad = 25
        plot.get_figure().savefig(
            "{}/top_stickers.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()


class WordCountGraph(Grapher):
    '''
    Plots the most common words
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['words'], sep=',')
        # ignore contractions
        df = df[~df.word.str.contains("\'", na=False)]
        # text only
        df = df[df['type'] == 'text']

        # filter out most common words
        with open("word_lists/10000_most_common_words.txt") as f:
            common = f.readlines()
            common = [x.lower().strip() for x in common]
        to_plot_2 = df.groupby(['sender','word'], as_index=False)[['occurrences']].sum()
        to_plot_2 = to_plot_2[~to_plot_2.word.isin(common)]

        # ignore numbers
        to_plot_2 = to_plot_2[~to_plot_2.word.isin([str(x) for x in range(0,10)])]

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot_2['word'],
            y=to_plot_2['occurrences'],
            hue=to_plot_2['sender'],
            data=to_plot_2,
            palette = "muted",
            order=to_plot_2.groupby('word').occurrences.sum().sort_values(ascending=False).head(15).index,
        )

        for item in plot.get_xticklabels():
            item.set_rotation(90)

        plot.set(
            xlabel="Most common words (after filtering out 10,000 most common English words)",
            ylabel="Occurrences"
        )
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/word_count_filtered_total.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

class NameGraph(Grapher):
    '''
    Plot who says whose names
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['words'], sep=',')

        names = df.sender.unique().tolist()
        first_names = [x.split()[0].lower() for x in names]
        to_plot = df[df['word'].isin(first_names)].groupby(['sender','word'], as_index=False)[['occurrences']].sum()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['word'],
            y=to_plot['occurrences'],
            hue=to_plot['sender'],
            data=to_plot,
            palette = "muted",
        )

        plot.set(
            xlabel="Name said in chat",
            ylabel="Occurrences",
            xticklabels=["\"{}\"".format(x) for x in first_names]
        )
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/names.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()


class LongWordGraph(Grapher):
    '''
    Plots the most common words over a certain length
    '''
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['words'], sep=',')
        # ignore contractions
        df = df[~df.word.str.contains("\'", na=False)]
        # text only
        df = df[df['type'] == 'text']

        to_plot_2 = df.groupby(['sender','word'], as_index=False)[['occurrences']].sum()

        sns.set(style="darkgrid")

        n = 6
        to_plot_2 = to_plot_2[to_plot_2.word.str.len() > n]
        plot = sns.barplot(
            x=to_plot_2['word'],
            y=to_plot_2['occurrences'],
            hue=to_plot_2['sender'],
            data=to_plot_2,
            palette = "muted",
            order=to_plot_2.groupby('word').occurrences.sum().sort_values(ascending=False).head(15).index,
        )

        for item in plot.get_xticklabels():
            item.set_rotation(90)

        plot.set(
            xlabel="Most common words with length greater than {}".format(n),
            ylabel="Occurrences"
        )
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/words_longer_than_{}.png".format(output_folder, n),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

'''
Plots the most common emojis
'''
class EmojiCountGraph(Grapher):
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['words'], sep=',')
        # emoji only
        df = df[df['type'] == 'emoji']

        to_plot_2 = df.groupby(['sender','word'], as_index=False)[['occurrences']].sum()

        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot_2['word'],
            y=to_plot_2['occurrences'],
            hue=to_plot_2['sender'],
            data=to_plot_2,
            palette = "muted",
            order=to_plot_2.groupby('word').occurrences.sum().sort_values(ascending=False).head(15).index,
        )

        add_custom_fonts()

        for item in plot.get_xticklabels():
            item.set_family('Symbola')

        plot.set(
            xlabel="Most common emoji",
            ylabel="Occurrences"
        )
        plot.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        plot.get_figure().savefig(
            "{}/emoji_total.png".format(output_folder),
            bbox_inches='tight',
            pad_inches=0.5
        )
        plot.get_figure().clf()

def add_custom_fonts():
    font_dirs = ['fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)

graphers_to_plot = [
    SenderMessagesGraph(),
    WeekdayMessagesGraph(),
    TopDaysMessagesGraph(),
    TimeInDayMessagesGraph(),
    TopStickersMessagesGraph(),
    PerMonthMessagesGraph(),
    WordCountGraph(),
    EmojiCountGraph(),
    LongWordGraph(),
    NameGraph()
]
