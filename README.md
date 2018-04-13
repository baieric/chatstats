# Chat Stats

Chats Stats is a data visualizer for a Facebook Messenger conversation. I made this to see my conversation data with my girlfriend. You don't need to be an experienced programmer to use it!

## Example

You can see the results of Chat Stats here: TODO

## How To

### Pre-requisites

You will need the following installed:

* Git
* Python
* Pip

### Step One: Scraping Conversation Data

To get your entire chat history:

1. Go to [m.facebook.com/messages](m.facebook.com/messages) and go to the chat you want to use.
2. Open the browser's console. In Chrome, press Ctrl + Shift + J (Windows / Linux) or Cmd + Opt + J (Mac).
3. Copy and paste the following command:
```
setInterval(function () {
document.getElementById('see_older')
.getElementsByClassName('content')[0].click();
}, 500);
```
4. Sit back and wait for your chat to load to the beginning. This can take a very long time, so start **Step Two** now. You may have to let the chat load overnight (or for a day or two, even).
5. **When your chat is fully loaded:** Press Ctrl + A to select the entire page. Create a new `rawchat.txt` file in your `chatstats` folder and copy and paste the page into it.

### Step Two: Get Set Up

1. Clone or fork this repository:
```
git clone https://github.com/baieric/chatstats.git
```
2. Install the dependencies:
```
pip install -r requirements.txt
```

### Step Three: Generate Graphs!

`rawchat.txt ` **must** be ready at this point.

Simply run:
```
python chatstats.py <output_folder>
```
This creates a directory `/generated/<output_folder>` in your `chatstats` folder. Here you can see the `chat.csv` file used to create all the graphs, and a `graphs` folder with every graph!

## Advanced Usage

TODO
