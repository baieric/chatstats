'''
Utility functions specifically for parsing Facebook HTML
'''

def is_react(tag):
    return tag is not None and tag.name == "ul" and tag['class'] == ['meta']

def clean_sticker(file):
    duplicate_likes = [
        "messages/stickers_used/851582_369239386556143_1497813874_n_369239383222810.png",
        "messages/stickers_used/851587_369239346556147_162929011_n_369239343222814.png"
    ]
    if file in duplicate_likes:
        return "messages/stickers_used/851557_369239266556155_759568595_n_369239263222822.png"
    else:
        return file

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
        if type == "sticker":
            file = clean_sticker(file)
        files.append(file)

    return type, files
