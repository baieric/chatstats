# -*- coding: utf-8 -*-

'''
converts the raw chat text into a CSV file "chat.csv", where each line is a line
from a message in the chat (format: date,sender,content)
'''

import re
import sys
import os
from datetime import date, timedelta, datetime

import util

# TODO we don't do anything with these skip arrays right now.
prefixes_to_skip = [
    "You missed a call from",
    "You set your nickname to",
    "Reminder,"
]
suffixes_to_skip = [
    "missed a call from you.",
    "changed the chat colors",
    "changed the chat colors.",
    "changed the conversation picture."
]
mids_to_skip = [
    " named the conversation: ",
    "set the nickname for",
    "set the emoji to",
    "responded Going to"
]
whole_lines_to_skip = [
    "You cleared your nickname."
]

def from_today(line):
    pattern = re.compile("^[0-9]{1,2} (hour|hours|minute|minutes|seconds|second) ago")
    return pattern.match(line)

def from_yesterday(line):
    pattern = re.compile("^Yesterday at 1?[0-9]:[0-5][0-9](am|pm)")
    return pattern.match(line)

def month_str(line):
    pattern = re.compile("^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [1-3]?[0-9]")
    return pattern.match(line)

def get_date(line):
    words = line.split()
    day = None
    year_pattern = re.compile("^[0-9]{4}$")

    if len(words) < 2:
        return None

    words_today = ["hours", "hour", "minute", "minutes", "seconds", "second", "now"]
    months = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if from_today(line):
        day = date.today()
    elif from_yesterday(line):
        day = date.today() - timedelta(1)
    elif month_str(line):
        year_exists = len(words) > 2 and year_pattern.match(words[2])
        try:
            if year_exists:
                day = datetime.strptime(words[0] + words[1] + words[2], '%b%d,%Y')
            else:
                day = datetime.strptime(words[0] + words[1] + str(date.today().year), '%b%d%Y')
        except:
            return None

    if day is not None:
        return day.strftime(util.DATE_FORMAT)

    # handle day of the week case separately due to complexity
    try:
        idx = util.WEEKDAYS.index(words[0])
    except:
        return None

    # get how many days ago weekdays[idx] was from today
    delta = (date.today().weekday() + 6 - idx) % 7 + 1
    day = date.today() - timedelta(days=delta)
    return day.strftime(util.DATE_FORMAT)

def format_msg(line):
    # some annoying strings that should be removed or turned into emoji
    pre_to_post = [
        ('frown emoticon', ' 😞 '),
        ('slightsmile emoticon', ' 🙂 '),
        ('grumpy emoticon', ' 😠 '),
        ('slightgrin emoticon', ' 😃 '),
        ('cry emoticon', ' 😢 '),
        ('gasp emoticon', ' 😮 '),
        ('heart emoticon', ' ❤️ '),
        ('wink emoticon', ' 😉 '),
        ('tongue emoticon', ' 😛 '),
        ('unsure emoticon', ' 😕 '),
        ('kiss emoticon', ' 😗 '),
        ('Like, thumbs up', ' 👍 '),
        ('Send voice messages with Messenger for mobile.', ''),
        ('Send videos with Messenger for mobile.', '')
    ]
    for pre, post in pre_to_post:
        line = line.replace(pre, post)

    # TODO remove this line after debugging
    if "emoticon" in line:
        print line

    return line.strip()

def make_csv(outputfolder):
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    with open("rawchat.txt") as f:
        rawchat = f.readlines()
        # remove the first 3 lines
        for _ in range(3):
            rawchat.pop(0)
        # remove the last 4 lines
        for _ in range(4):
            rawchat.pop()
        rawchat = [x.strip() for x in rawchat]

    # get the two people's names (assume different names)
    # TODO kinda hacky
    user1 = rawchat[0]
    pattern = re.compile("^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [1-3]?[0-9]")
    for idx, line in enumerate(rawchat):
        if pattern.match(line) and rawchat[idx+1] != user1:
            user2 = rawchat[idx+1]
            break

    outfile = '{}/chat.csv'.format(outputfolder)
    with open(outfile, 'w+') as csv:
        current = rawchat[0]
        if user1 == current:
            next = user2
        else:
            next = user1
        idx = 1
        msgs = []


        def append_to_file(msg_list, date):
            for msg in msg_list:
                csv.write("{},{},{}\n".format(
                    date,
                    util.to_csv_str(current),
                    util.to_csv_str(msg)
                ))

        csv.write("date,sender,content\n")
        while True:
            line = rawchat[idx]
            if idx == len(rawchat) - 1:
                date = get_date(line)
                append_to_file(msgs, date)
                break

            date = get_date(line)
            # TODO we can do a check if the date is >= previous date, for error checking maybe
            if date is not None:
                tmp_idx = idx
                while rawchat[idx+1] not in [current, next]:
                    # TODO we're skipping system messages right now, assuming we did not improperly get date
                    # TODO perhaps we can use the system message data as well
                    idx += 1
                append_to_file(msgs, date)
                msgs = []
                if rawchat[idx+1] != current:
                    tmp = next
                    next = current
                    current = tmp
                idx += 2
                continue

            line = format_msg(line)
            if len(line) > 0:
                msgs.append(line)
            idx += 1
    return outfile

def main(argv):
    if len(argv) != 1:
        print 'Usage: {} <outputfolder>'.format(sys.argv[0])
        sys.exit(2)
    outputfolder = "generated/{}".format(argv[0])

    make_csv(outputfolder)

if __name__ == "__main__":
    main(sys.argv[1:])
