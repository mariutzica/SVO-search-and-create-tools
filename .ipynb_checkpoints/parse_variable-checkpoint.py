import re

def clean_input(s):
    pattern = re.compile('[^a-zA-Z0-9 _]+')
    return pattern.sub('-', s)