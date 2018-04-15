# -*- coding: utf-8 -*-

'''
Graphers turn dataframes into graphs
'''

import pandas as pd
import string
import seaborn as sns
import datetime
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox

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
        plot = sns.barplot(x=to_plot.index, y=to_plot.values, palette = "muted")
        for rect, label in zip(plot.patches, to_plot.values.tolist()):
            if label == 0:
                continue
            height = rect.get_height()
            plot.text(rect.get_x() + rect.get_width()/2, height + 0.5, label, ha='center', va='bottom')
        plot.set(xlabel="Sender", ylabel="Messages sent")
        plot.get_figure().savefig("{}/sender_messages.png".format(output_folder))
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
        plot.get_figure().savefig("{}/weekday_messages.png".format(output_folder))
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
        plot.get_figure().savefig("{}/top_days_messages.png".format(output_folder))
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
        plot.fig.savefig("{}/time_in_day_messages.png".format(output_folder))
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
        plot.xaxis.labelpad = 25
        plot.get_figure().savefig("{}/top_stickers.png".format(output_folder))
        plot.get_figure().clf()

'''
Plots the most common words
'''
class WordCountGraph(Grapher):
    def graph(self, csvs, output_folder):
        df = pd.read_csv(csvs['words'], sep=',')
        # ignore contractions
        df = df[~df['word'].str.contains("\'")]

        # First graph: no filtering of words
        to_plot_1 = df.groupby('word', as_index=False).agg({"count": "sum"}).nlargest(15, 'count')
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot_1['word'],
            y=to_plot_1['count'],
            data=to_plot_1,
            palette = "muted"
        )
        plot.set(xlabel="Most common words", ylabel="Occurrences")
        plot.get_figure().savefig("{}/word_count_total.png".format(output_folder))
        plot.get_figure().clf()

        # Second graph: filter out most common words
        with open("word_lists/10000_most_common_words.txt") as f:
            common = f.readlines()
            common = [x.lower().strip() for x in common]
        to_plot_2 = df.groupby('word', as_index=False).agg({"count": "sum"})
        to_plot_2 = to_plot_2[~to_plot_2.word.isin(common)]
        to_plot_2 = to_plot_2[~to_plot_2.word.isin([str(x) for x in range(0,10)])]
        to_plot_2 = to_plot_2.nlargest(15, 'count')
        print(to_plot_2)
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot_2['word'],
            y=to_plot_2['count'],
            data=to_plot_2,
            palette = "muted"
        )
        plot.set(xlabel="Most common words (after filtering out 10,000 most common English words)", ylabel="Occurrences")
        plot.get_figure().savefig("{}/word_count_filtered_total.png".format(output_folder))
        plot.get_figure().clf()

graphers_to_plot = [
    SenderMessagesGraph(),
    WeekdayMessagesGraph(),
    TopDaysMessagesGraph(),
    TimeInDayMessagesGraph(),
    TopStickersMessagesGraph(),
]
