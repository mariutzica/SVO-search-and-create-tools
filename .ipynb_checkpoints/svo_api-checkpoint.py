# code for ontology API
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON as sqjson
import pandas as pd
import numpy as np
from parse_variable import clean_input
import wikipediaapi as wapi
import nltk

def search_ontology_for_term_variables(term):
    #print('Searching ontology for class for {}'.format(term))
    sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
    sparql.setQuery("""
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX svu: <http://www.geoscienceontology.org/svo/svu#>
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

                    SELECT DISTINCT ?variable ?varlabel
                    WHERE {{ ?variable a svu:Variable .
                           ?variable svu:subLabel ?label  .
                           optional {{ ?variable rdfs:label ?varlabel .}} .
                           BIND (STR(?label) as ?name).
                           FILTER regex(?name,"^{}$","i") .}}
                    """.format(term))
    sparql.setReturnFormat(sqjson)

    results = []
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(e)
    
    if results != []:
        data = pd.DataFrame(columns = ['term','variable','varlabel'])
        for result in results["results"]["bindings"]:
            v = result["variable"]["value"]
            vl = result["varlabel"]["value"]
            data = data.append({'term':term,'variable':v,'varlabel':vl}, ignore_index = True)
        #print('Successfully finished query.')
    return data


def search_ontology_for_term_variables_main(term):
    #print('Searching ontology for class for {}'.format(term))
    sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
    sparql.setQuery("""
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX svu: <http://www.geoscienceontology.org/svo/svu#>
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

                    SELECT DISTINCT ?variable ?rel ?varlabel
                    WHERE {{ ?variable a svu:Variable .
                            ?variable rdfs:label ?varlabel .
                           ?variable ?rel ?obj  .
                           ?obj rdfs:label ?label .
                           BIND (STR(?label) as ?name).
                           FILTER regex(?name,"^{}$","i") .
                           }}
                    """.format(term))
    sparql.setReturnFormat(sqjson)

    results = []
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(e)
    
    if results != []:
        data = pd.DataFrame(columns = ['variable','varlabel'])
        for result in results["results"]["bindings"]:
            rel = result["rel"]["value"]
            v = result["variable"]["value"]
            if 'hasRecorded' in rel and not v in data['variable'].tolist():
                vl = result["varlabel"]["value"]
                data = data.append({'variable':v,'varlabel':vl}, ignore_index = True)
        #print('Successfully finished query.')
    return data

# look up term in ontology, return its class(es) if exact match found
def search_ontology_for_term_class(term):
    #print('Searching ontology for class for {}'.format(term))
    sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
    sparql.setQuery("""
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX svu: <http://www.geoscienceontology.org/svo/svu#>

                    SELECT DISTINCT ?class ?cllabel
                    WHERE {{ ?term a ?class .
                            ?term rdfs:label ?label .
                           ?class rdfs:label ?cllabel .
                           BIND (STR(?label) as ?name).
                           FILTER regex(?name,"^{}$","i") .}}
                    """.format(term))
    sparql.setReturnFormat(sqjson)

    results = []
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(e)

    data = pd.DataFrame(columns = ['class','class label'])
    if results != []:
        for result in results["results"]["bindings"]:
            c = result["class"]["value"]
            l = result["cllabel"]["value"]
            data = data.append({'class':c,'class label':l}, ignore_index = True)
    return data

# look up peripheral term in ontology; at this point this is agnostic to how
# the term is connected to the variable, but in the future it will be expanded
# to weigh main components more heavily than context or reference components.
def search_ontology_for_term_subtypes(term, cl):
    #print('Searching ontology for peripheral var terms for {}'.format(term))
    sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
    sparql.setQuery("""
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX svu: <http://www.geoscienceontology.org/svo/svu#>

                    SELECT DISTINCT ?stype ?stypelabel
                    WHERE {{ ?term a svu:{} . 
                            ?stype svu:isTypeOf ?term .
                           ?term rdfs:label ?label .
                           ?stype rdfs:label ?stypelabel  .
                           BIND (STR(?label) as ?name).
                           FILTER regex(?name,"^{}$","i") .}}
                    """.format(cl, term))
    sparql.setReturnFormat(sqjson)
    
    results = []
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(e)

    data = pd.DataFrame(columns = ['sub category','sub category label'])
    if results != []:
        for result in results["results"]["bindings"]:
            st = result["stype"]["value"]
            sl = result["stypelabel"]["value"]
            data = data.append({'sub category':st,'sub category label':sl}, ignore_index = True)
            
    return data

def search_ontology_for_term_associations_by_class(term, cl):
    #print('Searching ontology for peripheral var terms for {}'.format(term))
    sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
    sparql.setQuery("""
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX svu: <http://www.geoscienceontology.org/svo/svu#>

                    SELECT DISTINCT ?obj ?objlabel
                    WHERE {{?var a svu:Variable .
                            ?var svu:subLabel ?label .
                           BIND (STR(?label) as ?name).
                           FILTER regex(?name,"^{}$","i") .
                           ?term rdfs:label ?label .
                           ?var svu:subLabel ?objlabel .
                           ?obj a svu:{} .
                           ?obj rdfs:label ?objlabel .}}
                    """.format(term, cl))
    sparql.setReturnFormat(sqjson)
    
    results = []
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(e)

    if results != []:
        data = pd.DataFrame(columns = ['associated entity','entity label'])
        for result in results["results"]["bindings"]:
            obj = result["obj"]["value"]
            objl = result["objlabel"]["value"]
            data = data.append({'associated entity':obj,'entity label':objl}, \
                               ignore_index = True)
            
    return data

def rank_variable_match(phrase, results):
    var_list = np.unique(results['variable'])
    results_ranked = pd.DataFrame(columns = ['variable id', 'variable label', \
                                             'rank', 'term combination', 'main'])
    
    for v in var_list:
        var_results = results.loc[results['variable']==v]
        var_id = var_results['variable'].iloc[0]
        var_label = var_results['varlabel'].iloc[0]
        rank = len(var_results)
        stars = '*' * len(var_results.loc[var_results['asterisk']==True])
        terms_present = np.unique(var_results['term'])
        term_comb = []
        for term in phrase.split():
            if term in terms_present:
                term_comb.append(term)
        term_matched = ' '.join(term_comb)
        results_ranked.loc[len(results_ranked)] = [ var_id, var_label, rank, \
                                                   term_matched, stars ]
    
    results_ranked['len_label'] = results_ranked['variable label'].str.len()
    
    results_ranked = results_ranked.sort_values(by=['rank','term combination','len_label'], \
                                                ascending=[False,True,True])\
                                                .drop(columns=['len_label'])
    return results_ranked
        
# look up phrase in ontology
def search_ontology(phrase):
    
    #clean phrase to match syntax in ontology
    phrase_clean = clean_input(phrase)
    
    result = pd.DataFrame()
    for term in phrase_clean.split():
        temp = search_ontology_for_term_variables(term)
        temp['asterisk'] = False
        result = result.append(temp, ignore_index=True, sort=False)
        # if a variable has the term as its main object, 
        # then that variable gets an additional point
        temp = search_ontology_for_term_variables_main(term)
        temp['asterisk'] = True
        result = result.append(temp, ignore_index=True, sort=False)
    
    result = result.fillna('')
    result = rank_variable_match(phrase, result)
        
    return result

def get_term_class(term):
    class_info = search_ontology_for_term_class(term)
    classes = class_info['class label'].tolist()
    c = []
    if 'Phenomenon' in classes:
        c.append('Phenomenon')
    if 'Process' in classes:
        c.append('Process')
    if 'Property' in classes:
        c.append('Property')
    return c

def break_up_phrase_by_class(phrase):
    #clean phrase to match syntax in ontology
    phrase_clean = clean_input(phrase)
    classes = ['Phenomenon', 'Process', 'Property']
    
    results = pd.DataFrame()
    variable_categories = {'Phenomenon':[], 'Process': [], 'Property':[]}
    for term in phrase_clean.split():
        term_classes = get_term_class(term)
        for cat in term_classes:
            variable_categories[cat].append(term)
        
    changes_made = True
    while changes_made:
        changes_made = False
        for cat in variable_categories.keys():
            if len(variable_categories[cat]) == 1:
                to_remove = variable_categories[cat][0]
                for cat2 in [c for c in classes if c!=cat]:
                    if to_remove in variable_categories[cat2]:
                        variable_categories[cat2].remove(to_remove)
                        changes_made = True
    
    return variable_categories
    
def get_term_associations(term):
    ontology_classes = ['Phenomenon', 'Process', 'Property']
    associations = {}
    for cl in ontology_classes:
        assoc_info = search_ontology_for_term_associations_by_class(term, cl)
        assoc_info = assoc_info.loc[(assoc_info['entity label']!=term) & \
                      ~assoc_info['entity label'].str.contains('@|\(')]
        associations[cl] = list(np.unique(assoc_info['entity label'].tolist()))    
    return associations

def get_phrase_associations(phrase, class_information):
    phrase_clean = clean_input(phrase)
    
    terms_found = []
    for key in class_information.keys():
        terms_found.extend(class_information[key])
    
    classes_missing = []
    for key in class_information.keys():
        if class_information[key] == []:
            classes_missing.append(key)
    
    phrase_associations = {}
    for term in phrase_clean.split():
        if term in terms_found:
            term_assoc = get_term_associations(term)
            assoc = {}
            for cl in term_assoc.keys():
                if cl in classes_missing:
                    assoc[cl] = term_assoc[cl]
            phrase_associations[term] = assoc
            
    return phrase_associations

def get_phrase_subtypes(class_information):
    
    subtypes = {}
    for cl, value in class_information.items():
        for term in value:
            term_subtypes = search_ontology_for_term_subtypes(term, cl)
            if len(term_subtypes) > 0:
                if not term in subtypes.keys():
                    subtypes[term] = {cl: term_subtypes['sub category label'].tolist()}
                else:
                    subtypes[term][cl] = term_subtypes['sub category label'].tolist()
                    
    return subtypes

def get_variable_components(state):
    
    components = {'Property':[], 'Phenomenon': [], 'Process': []}
    sentence = ''
    wikipedia_top_result = wapi.get_top_wikipedia_entry(state)
    if len(wikipedia_top_result) > 0:
        if 'pageid' in wikipedia_top_result.keys():
            pageid = wikipedia_top_result['pageid']
            title = wikipedia_top_result['title'].lower()
            page_text = wapi.parse_wikipedia_page(pageid)
            page_text = page_text.lower()
            
            searching = True
            occurrence = 1
            loops = 0
            while searching:
                sentence = title.join(page_text.split(title,occurrence)[:occurrence]).split('.')[-1] +\
                           title + \
                           page_text.split(title,occurrence)[-1].split('.')[0]
                if title + ' is ' in sentence:
                    searching = False
                else:
                    occurrence += 1
                loops += 1
                if loops >50:
                    searching = False
            
            if sentence == '':
                print('I\'m sorry, I was not able to find any information on {}.'\
                     .format(state))
            else:
                is_noun_nltk = lambda pos: pos[:2] == 'NN'
                is_adj_nltk = lambda pos: pos[:2] == 'JJ'

                tokenized = nltk.word_tokenize(sentence)
                word_pos = nltk.pos_tag(tokenized)
                
                nouns = []
                curr_noun = []
                for (word,pos) in word_pos:
                    if is_noun_nltk(pos):
                        curr_noun.append(word)
                    elif curr_noun != []:
                        nouns.append(' '.join(curr_noun))
                        curr_noun = []
                        
                for noun in nouns:
                    noun_variations = [noun]
                    for n in noun.split():
                        if not n in noun_variations:
                            noun_variations.append(n)
                    if ' ' in noun:
                        noun_variations.append(noun.replace(' ','-'))
                        noun_variations.append(noun.replace(' ',''))
                        
                    results = pd.DataFrame()
                    for n in noun_variations:
                        results = results.append(search_ontology_for_term_class(n),ignore_index=True)
                        
                    if len(results) > 0:
                        for key in components.keys():
                            if key in results['class label'].tolist():
                                components[key].append(noun)                        
                    
        else:
            print('I\'m sorry, I was not able to find any information on {}.'\
                 .format(state))
    else:
        print('I\'m sorry, I was not able to find any information on {}.'\
                 .format(state))
    return title, sentence, components