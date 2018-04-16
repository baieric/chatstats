'''
Utility functions specifically for parsing Facebook HTML
'''

def is_react(tag):
    return tag is not None and tag.name == "ul" and tag['class'] == ['meta']

def get_files(tags):
    '''
    given a list of file tags, returns type of file and list of files
    '''
    if tags[0].has_attr('src'):
        attr = 'src'
    elif tags[0].has_attr('href'):
        attr = 'href'
    else:
        raise ValueError("Unexpected file tags: {}".format(tags))

    url = tags[0][attr]
    files = []

    if url.startswith("messages/photos"):
        type = "photo"
    elif url.startswith("messages/stickers"):
        type = "sticker"
    elif url.startswith("messages/gifs"):
        type = "gif"
    elif url.startswith("messages/videos"):
        type = "video"
    elif url.startswith("messages/audio"):
        type = "audio"
    elif url.startswith("messages/files"):
        type = "file"
    else:
        type = "badmedia"

    for item in tags:
        file = item[attr]
        files.append(file)

    return type, files
