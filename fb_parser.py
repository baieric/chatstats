'''
Parses a Facebook conversation HTML file into useful CSV files
'''

import csv
import os
import sys

from bs4 import BeautifulSoup, NavigableString
from datetime import date, timedelta, datetime
from multiprocessing import Pool

import fbutil
import constants
import util

# TODO try async for making csvs
# pool = Pool()
# result1 = pool.apply_async(solve1, [A])    # evaluate "solve1(A)" asynchronously
# result2 = pool.apply_async(solve2, [B])    # evaluate "solve2(B)" asynchronously

def parse_msg(tag):
    '''
    returns:
    the type of message,
    the body text of the message,
    and any files in the message
    '''

    child = tag.contents[0]

    if len(tag.contents) > 1 and isinstance(child, NavigableString):
        # message is a call or attachment
        body = child.string
        second_child = tag.contents[1]

        if any(x in body for x in [' missed a call', ' called you', 'You called ']):
            type = "call"
            # append duration text to body, if necessary
            if second_child.string:
                duration = second_child.string
                body = "{} {}".format(body, duration)
            return type, body, None
        if any(x in body for x in [' missed a video chat', 'The video chat ended.']):
            type = "videochat"
            # append duration text to body, if necessary
            if second_child.string:
                duration = second_child.string
                body = "{} {}".format(body, duration)
            return type, body, None

        elif second_child.name == "br":
            # an attached link or plan
            # TODO debug print
            print("br found in msg body")
            print(tag)

            if child.string == " Plan Created: ":
                type = "plan"
                body = [x.string for x in tag.contents[2::2]]
                return type, body, None

            # find the tag with href
            link_child = second_child
            while isinstance(link_child, NavigableString) or not link_child.has_attr('href'):
                link_child = link_child.next_sibling

            # attach url if it doesn't already exist
            url = link_child['href']
            if url not in body:
                body = "{} {}".format(body, url)

            type = "text"
            return type, body, None

        else:
            type, files = fbutil.get_files([child for child in child.next_siblings])
            type = "text+{}".format(type)
            return type, body, files

    elif isinstance(child, NavigableString):
        type = "text"
        return type, tag.string, None
    else:
        type, files = fbutil.get_files(tag.contents)
        return type, None, files



def make_message_csv(thread, folder):
    '''
    Creates a csv in folder of all messages in conversation
    '''
    user = None
    time = None
    outfile = '{}/messages.csv'.format(folder)

    with open(outfile, 'w+') as csvfile:
        out = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        out.writerow(['date', 'sender', 'type', 'message', 'files', 'reactions'])

        for tag in thread.children:
            if tag.name in ["h3", None]:
                # skip header
                continue

            elif tag.has_attr("class") and tag['class'] == ["message"]:
                # start of new message
                header = tag.contents[0]
                dt_str = header.contents[1].string
                dt =  datetime.strptime(dt_str, "%A, %B %d, %Y at %I:%M%p %Z")

                # these results will be used when the message body is processed
                user = header.contents[0].string
                time = dt.strftime(constants.DATE_FORMAT)

            elif tag.name == "p":
                # message body
                if tag.string is None and len(tag.contents) == 0:
                    # tag is empty
                    continue

                type, message, files = parse_msg(tag)

                # add reacts if necessary
                sibling = tag.next_sibling
                reacts = None
                if fbutil.is_react(sibling):
                    reacts = []
                    for item in sibling.children:
                        react = item.string.split("  ")
                        reacts.append(react)

                # write the row
                out.writerow([
                    time,
                    user,
                    type,
                    message,
                    ", ".join(files) if files is not None else files,
                    reacts
                ])

            elif fbutil.is_react(tag):
                # reacts, already handled in message body case
                continue

            else:
                print(tag)
                if tag.has_attr("class"):
                    raise ValueError('unexpected message type: {} class={}'.format(tag.name, tag["class"]))
                else:
                    raise ValueError('unexpected message type: {}'.format(tag.name))
    # end make_message_csv

def make_csvs(chat_html_file):
    """
    makes output folder and makes all csv files
    """
    # remove file prefix if necessary
    FILE_PREFIX = 'file://'
    if chat_html_file.startswith(FILE_PREFIX):
        filename = chat_html_file[len(FILE_PREFIX):]

    # get html object
    print("Parsing HTML... This may take a minute!")
    with open(filename) as fp:
        soup = BeautifulSoup(fp, 'lxml')

    # make output folder
    output_folder = util.get_output_folder(filename, soup.title.string)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # save reference to fb folder
    outfile = '{}/message_dir.txt'.format(output_folder)
    with open(outfile, 'w+') as file:
        file.write(filename.rsplit('/', 2)[0])

    print("Generating csv files...")
    thread = soup.find_all("div", "thread")[0]

    make_message_csv(thread, output_folder)

    return output_folder

def main(argv):
    # Check correctness of args
    if len(argv) != 2:
        print('Usage: {} <conversation_file>'.format(argv[0]))
        sys.exit(2)

    filename = argv[1]
    make_csvs(filename)

if __name__ == "__main__":
    main(sys.argv)
