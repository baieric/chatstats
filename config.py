'''
Configurable constants
'''

# timezone used in plotting graphs with datetime information
TIMEZONE = 'US/Eastern'

# for graphs that seperate data by term
TERMS_PER_YEAR = 3

# suffix to add to a term's name for readability
TERM_SUFFIX = {
    3: ["Winter", "Spring", "Fall"]
}

# which column to use to label senders
# either "sender_name" (full name) or "sender_first_name" (first name only)
SENDER_COLUMN_NAME = "sender_first_name"

# colour palette for seaborn plots
PALETTE = "muted"

# padding around the plot image
PAD_INCHES = 0.1
