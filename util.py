'''
Util functions shared between different modules
'''

import matplotlib.font_manager as font_manager

def add_custom_fonts():
    '''
    Allow us to use fonts from our fonts folder
    '''
    font_dirs = ['fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)
