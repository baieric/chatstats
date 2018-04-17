# ChatStats

ChatsStats is a data visualizer for a Facebook Messenger conversation. Try it out with your group chats or your significant other. You don't need to be an experienced programmer to use it!

TODO: Examples here

## How To

Note: Not tested on Windows.

### Pre-requisites

You will need the following installed:

* Git
* Python3
* Pip3

### Step One: Getting Your Facebook Data

To get your entire chat history:

1. Go to [https://www.facebook.com/settings](https://www.facebook.com/settings). At the bottom of the settings list is an option "Download a copy of your Facebook data." Select it and follow the instructions.
2. Facebook takes a few minutes to generate a download link for you. You can do **Step Two** while waiting for the link.
3. Once you receive an email from Facebook with a download link, save the file to your computer and unzip it. Note that this is very sensitive information, so be careful storing it.

### Step Two: Set Up ChatStats

1. Clone or fork this repository:
```
git clone https://github.com/baieric/chatstats.git
```
2. Install the dependencies:
```
pip3 install -r requirements.txt
```

### Step Three: Generate Graphs!

1. Go to your Facebook data folder, and open `index.htm` in your browser.
2. Go to the "Messages" page on the left navbar. Find the conversation you want to use and go to its page.
3. Copy the page's URL from your browser, and run the following command:
```
python3 chatstats.py <conversation_url>
```
This creates a folder in `chatstats/my_data/` with all the graphs in image files, as well as some underlying data files used to create those graphs.

Have fun! If you need help deciding what conversations you want to try, check out the `messages` folder in your Facebook data and sort by size. Try it out on all of your largest conversations!

## Contribute

Feel free to [request a feature](https://github.com/baieric/chatstats/issues/new) or make a pull request.

## Advanced Usage

If you want to make your own graphs or otherwise extend ChatStats, keep reading.

### Specific Commands

There are two main steps involved in the `chatstats.py` command:

1. Parsing the HTML of the conversation page into csv files
2. Manipulating the data in the csv files to generate the graphs

Since both steps can take a long time with large data, you may be interested in only doing one or the other.

To parse facebook HTML, run:
```
python3 fb_parser.py <conversation_url>
```
To generate graphs, you need the path to the specific `mydata/chat_123_firstname-lastname` subfolder of the chat you parsed previously. Run:
```
python3 plot_graphs.py <chatstats_chat_folder>
```

### CSV formats

ChatStats generates two CSV files, `messages.csv` and `words.csv`

**messages.csv** records every message in the conversation. Its columns are:
* **date**: datetime in "yyyy-MM-dd HH:mm:ss" format
* **sender**: full name of the message sender, e.g. "Jane Doe"
* **type**: one of `text | call | videochat | plan` or one of the file types `photo | sticker | gif | video | audio | file`. Additionally, a text can have a file attached, which has type `text+<file_type>`. Finally, there are broken links with type `badmedia`
* **message**: contains the text for type `text` or details for types `call | videochat | plan`. Empty for other types
* **files**: contains a list of files for file types, otherwise empty
* **reactions** contains a list of pairs of the form `['👍', 'Jane Doe']`, indicating what reacts the message received

**words.csv** records a count of every word or emoji used by each person. Its columns are:
* **sender**: full name of the word sender, e.g. "Jane Doe"
* **type**: one of `text | emoji`
* **word**: the word or emoji
* **occurrences**: the number of times the sender has said the word or emoji
