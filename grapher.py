# -*- coding: utf-8 -*-

'''
Graphers turn dataframes into graphs
'''

import pandas as pd
import string
import seaborn as sns

import util

'''
Interface for Grapher, which reads a CSV and outputs a graph
'''
class Grapher(object):
    # outputs a graph bitmap to the outputfolder
    def graph(self, chatfile, wordfile, outputfolder):
        raise NotImplementedError( "Implement the graph function for a concrete Grapher" )

'''
Plots the number of messages sent by each sender
'''
class SenderMessagesGraph(Grapher):
    def graph(self, chatfile, wordfile, outputfolder):
        df = pd.read_csv(chatfile, sep=',')
        to_plot = df['sender'].value_counts()

        sns.set(style="darkgrid")
        plot = sns.barplot(x=to_plot.index, y=to_plot.values, palette = "muted")
        for rect, label in zip(plot.patches, to_plot.values.tolist()):
            if label == 0:
                continue
            height = rect.get_height()
            plot.text(rect.get_x() + rect.get_width()/2, height + 0.5, label, ha='center', va='bottom')
        plot.set(xlabel="Sender", ylabel="Messages sent")
        plot.get_figure().savefig("{}/sender_messages.png".format(outputfolder))
        plot.get_figure().clf()


class WeekdayMessagesGraph(Grapher):
    def graph(self, chatfile, wordfile, outputfolder):
        df = pd.read_csv(chatfile, sep=',')
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.weekday_name
        to_plot = df.groupby(['weekday', 'sender'], as_index=False)[['content']].count()
        sns.set(style="darkgrid")
        plot = sns.barplot(
            x=to_plot['weekday'],
            y=to_plot['content'],
            hue=to_plot['sender'],
            data=to_plot,
            order=util.WEEKDAYS,
            palette = "muted"
        )
        plot.set(xlabel="Day of the week", ylabel="Messages sent")
        plot.get_figure().savefig("{}/weekday_messages.png".format(outputfolder))
        plot.get_figure().clf()

class WordCountGraph(Grapher):
    def graph(self, chatfile, wordfile, outputfolder):
        df = pd.read_csv(wordfile, sep=',')

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
        plot.get_figure().savefig("{}/word_count_total.png".format(outputfolder))
        plot.get_figure().clf()

        # Second graph: filter out most common words
        with open("10000_most_common_words.txt") as f:
            common = f.readlines()
            common = [x.lower().strip() for x in common]
        to_plot_2 = df.groupby('word', as_index=False).agg({"count": "sum"})
        to_plot_2 = to_plot_2[~to_plot_2.word.isin(common)]
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
        plot.get_figure().savefig("{}/word_count_filtered_total.png".format(outputfolder))
        plot.get_figure().clf()

graphers_to_plot = [SenderMessagesGraph(), WeekdayMessagesGraph(), WordCountGraph()]
