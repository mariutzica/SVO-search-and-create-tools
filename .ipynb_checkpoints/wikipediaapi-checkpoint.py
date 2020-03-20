import requests
from lxml import html

def get_top_wikipedia_entry(term):
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    TITLE = term
    PARAMS = {
            'action': "query",
            'srsearch': TITLE,
            'format': "json",
            'list':"search",
            'srwhat':"text",
        }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()

    top_result_title = ''
    top_result_pageid = -1

    result = {}
    num_results = len(DATA['query']['search'])
    if num_results > 0:
        result_titles = [result['title'].lower() for result in DATA['query']['search']]
        desired_result = False
        result_index = 0
        try:
            result_index = result_titles.index(TITLE)
            desired_result = True
        except ValueError:
            try:
                desired_result = True
                result_index = result_titles.index(TITLE.lower())
            except:
                #print('Value not found. Check for possible misspelling.')
                pass
        except:
            #print('Something went wrong.')
            pass
        
        #top_result = DATA['query']['search'][desired_result]
        top_result_title = DATA['query']['search'][result_index]['title']
        top_result_pageid = DATA['query']['search'][result_index]['pageid']
        result = DATA['query']['search'][result_index]
        
    return result
        
def parse_wikipedia_page(pageid):
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            'action': "parse",
            'pageid': pageid,
            'format': "json"
        }

    pos = []
    defs = []
    nyms = []
    f = open('pageid_error.log','w')
    result = ''
    try:
        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        tree = html.fromstring(DATA['parse']['text']['*'])
        all_elem = tree.xpath('//div[@class="mw-parser-output"]//text()')
        result = ''.join(all_elem).split('.mw-parser-output')[0]
    except:
        f.write(pageid)
    f.close()
    return result