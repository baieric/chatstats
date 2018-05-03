# Roadmap

## Bug Fixes and Improvements

* fix how stickers look in graphs
* figure out how to show better emojis in graphs
* get consistent colours for the legend
* fix/suppress warnings in plot_graph.py
* get better word lists for filtering
* auto-detect what properties to use for graphs based on number of people in the chat, number of messages, etc. ?
* toggle for whether to show full names

## Web UI Idea

* A web UI where you can paste your facebook data folder, and the UI will let you search conversations, and clicking them will generate the graphs!
* UI can list chats by size as well.

## New Graph Ideas

Message counting:

* Longest calls, maybe a time distribution of calls as well
* Days with the most positive emojis
* messages with the most reacts

Word counting:

* most swearing
* punctuation usage? Count: ? @ # ! $

Message content analysis (may require preprocessing):

* first time saying I love you? lol
* most common two-word pairs?
* change in frequency of certain words over time (maybe detect largest differences? most unique each month or term?)
* which pairs talk to each other the most in a group chat
* how long someone takes to respond
