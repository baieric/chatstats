'''
Graphers read CSVs outputted by Trackers and graph the data
'''
import pandas as pd
import seaborn as sns
from numpy import sum

from tracker import SenderMessageCounter, WeekdayMessageCounter
import util

'''
Interface for Grapher, which reads a CSV and outputs a graph
'''
class Grapher(object):
    # outputs a graph bitmap to the outputfolder
    def graph(self, chatfile, outputfolder):
        raise NotImplementedError( "Implement the graph function for a concrete Grapher" )

'''
Plots the number of messages sent by each sender
'''
class SenderMessagesGraph(Grapher):
    def graph(self, chatfile, outputfolder):
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
    def graph(self, chatfile, outputfolder):
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

graphers_to_plot = [SenderMessagesGraph(), WeekdayMessagesGraph()]
