"""
Util functions and constants shared by different modules
"""

DATE_FORMAT = '%Y-%m-%d'
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def to_csv_str(s):
    return "\"{}\"".format(s.replace("\"", "\"\""))
