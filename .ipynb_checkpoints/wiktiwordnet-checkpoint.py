import pandas as pd
from parse_variable import clean_input

# load wiktiwordnet data
def load_primary_wiktiwordnet(svocatpath = 'Create WiktiWordNet/svo_wiktionary_categorization/'):
    cat_matter = pd.read_csv(svocatpath+'lookup_noun_matter.csv')
    cat_bodies = pd.read_csv(svocatpath+'lookup_noun_body.csv')
    cat_roles = pd.read_csv(svocatpath+'lookup_noun_roles.csv')
    cat_objects = cat_matter.append(cat_bodies, ignore_index = True)\
                            .append(cat_roles, ignore_index = True)

    cat_props = pd.read_csv(svocatpath+'lookup_noun_properties.csv')
    cat_attr = pd.read_csv(svocatpath+'lookup_noun_attributes.csv')
    cat_properties = cat_props.append(cat_attr, ignore_index = True)

    cat_processes = pd.read_csv(svocatpath+'lookup_noun_processes.csv')

    cat_domains = pd.read_csv(svocatpath+'lookup_domains.csv')
    
    return cat_objects, cat_properties, cat_processes, cat_domains

def load_secondary_wiktiwordnet(svocatpath = 'Create WiktiWordNet/svo_wiktionary_categorization/'):
    objects = pd.read_csv(svocatpath+'seconddeg_objects.csv')
    processes = pd.read_csv(svocatpath+'seconddeg_processes.csv')
    properties = pd.read_csv(svocatpath+'seconddeg_properties.csv')
    domains = pd.read_csv(svocatpath+'seconddeg_domains.csv')
    
    return objects, properties, processes, domains

def categorize_terms(phrase, evaluation):
    
    primary_objects, primary_properties, primary_processes, \
                    primary_domains = load_primary_wiktiwordnet()
    
    phrase_clean = clean_input(phrase)
    
    terms_found = []
    for key in evaluation['class_information'].keys():
        terms_found.extend(evaluation['class_information'][key])
    
    classes_missing = []
    for key in evaluation['class_information'].keys():
        if evaluation['class_information'][key] == []:
            classes_missing.append(key)

    new_categorizations = {}
    for term in phrase_clean.split():
        if not term in terms_found:
            
            new_categorizations[term] = {}
            #if term in primary_domains['term'].tolist():
            #    defs = primary_domains.loc[primary_domains['term']==term,\
            #                            'definition'].tolist()
            if term in primary_processes['term'].tolist() and 'Process' in classes_missing:
                defs = primary_processes.loc[primary_processes['term']==term,\
                                        'definition'].tolist()
                new_categorizations[term]['Process'] = '\n'.join(defs)
            if term in primary_properties['term'].tolist() and 'Property' in classes_missing:
                defs = primary_properties.loc[primary_properties['term']==term,\
                                        'definition'].tolist()
                new_categorizations[term]['Property'] = '\n'.join(defs)
            if term in primary_objects['term'].tolist() and 'Phenomenon' in classes_missing:
                defs = primary_objects.loc[primary_objects['term']==term,\
                                        'definition'].tolist()
                new_categorizations[term]['Phenomenon'] = '\n'.join(defs)
                
    return new_categorizations

def categorize_single_term(term):
    
    primary_objects, primary_properties, primary_processes, \
                    primary_domains = load_primary_wiktiwordnet()
    
    new_categorization = {}
    if term in primary_processes['term'].tolist():
        
        defs = primary_processes.loc[primary_processes['term']==term,\
                                        'definition'].tolist()
        new_categorization['Process'] = '\n\n'.join(defs)
    if term in primary_properties['term'].tolist():
        defs = primary_properties.loc[primary_properties['term']==term,\
                                        'definition'].tolist()
        new_categorization['Property'] = '\n\n'.join(defs)
    if term in primary_objects['term'].tolist():
        defs = primary_objects.loc[primary_objects['term']==term,\
                                        'definition'].tolist()
        new_categorization['Phenomenon'] = '\n\n'.join(defs)
                
    return new_categorization