from IPython.display import display, HTML
import svo_api
import textwrap
import wiktiwordnet

def ask_for_var_input():
    return input(('What is the scientific variable you would like to describe?\n'
                  'Please keep your description relatively brief. Examples include:\n' 
                  'crop yield, soil moisture, food availability, drought.\n\n>>>  '))

def print_variable_search_results(variable):
    
    # look up entries in ontology to see if any matches are available
    results = svo_api.search_ontology(variable)
    
    if len(results) > 0:
        print('I found some variable(s) already in the ontology.')
        print('They are listed below. If you see one or more * by a search result,')
        print('it means that result has some of the terms you were interested in')
        print('as part of it main object of observation. This means it is a great match!')
        print("The more *s you see, the better the match. If you see no *s, then")
        print("the terms you were searching for were found in the context of the")
        print("variable returned.")
        results.rename(columns = {'variable label': 'variable', 'rank':'rank', \
                                 'term combination': 'terms matched', \
                                  'asterisk':'foucus of measurement'})
        display(HTML(results.drop(columns = ['variable id']).head(10).to_html(index=False)))
        
    else:
        print('Unfortunately, I did not find any results in the ontology. But not to worry!')
        print('There are a few more ways we can try to get you closer to the variable you need.')
    
    return len(results)
        
def print_class_information(variable):
    
    results = svo_api.break_up_phrase_by_class(variable)
    
    phenomenon_present = False
    property_present = False
    
    print('The following variable components were found in the input:')
    if results['Phenomenon'] != []:
        print('Phenomenon : ', ', '.join(results['Phenomenon']), ' '+u'\u2713')
        phenomenon_present = True
    else:
        print('Phenomenon : not found ', ' '+ '\u2717')
    if results['Process'] != []:
        print('Process : ', ', '.join(results['Process']), ' '+u'\u2713')
    else:
        print('Process : not found ', ' '+ '\u2717')
    if results['Property'] != []:
        print('Property : ', ', '.join(results['Property']), ' '+u'\u2713')
        property_present = True
    else:
        print('Property : not found ', ' '+ '\u2717')
        
    if phenomenon_present and property_present:
        print('You inputted a phenomenon and a property, so you have satisfied')
        print('the minimum requirements for a variable.')
    elif phenomenon_present:
        print('You inputted at least one phenomenon, but you did not input a')
        print('property. To find some suggestions, keep working through')
        print('this notebook.')
    elif property_present:
        print('You inputted at least one property, but you did not input a')
        print('phenomenon. To find some suggestions, keep working through')
        print('this notebook.')
    else:
        print('Unfortunately, we did not detect either a phenomenon or a property')
        print('in your input. For some additional suggestions, keep working through')
        print('this notebook.')
        
    return results
    
def provide_initial_evaluation(variable):
    print('Okay. You entered {}.\nLet me look up some information on this variable.\n'\
         .format(variable))
    print('Unfortunately this step has not been optimized yet, so it may take a little while.')
    print('Thank you for your patience!')
    
    # if overall match found, then return the variables that match
    num_results = print_variable_search_results(variable)
    
    # if component matches found, return their classes and state any missing
    # requirements
    variable_class_information = print_class_information(variable)
    
    evaluation = { 'search results': num_results, \
                   'class_information': variable_class_information }
    
    return evaluation

def suggest_missing_components(variable, evaluation):
    if evaluation['search results'] > 0:
        phenomenon_present = evaluation['class_information']['Phenomenon'] != []
        process_present = evaluation['class_information']['Process'] != []
        property_present = evaluation['class_information']['Property'] != []
        
        if phenomenon_present and property_present:
            print('The previous results indicate that you already have ')
            print('a complete variable, so you\'re good to go!')
        elif phenomenon_present or property_present or process_present:
            print('Since I was able to find some relevant variables in SVO, ')
            print('let me look up some suggestions for you on how to complete ')
            print('your variable based on what we already have ...')
            
            results = svo_api.get_phrase_associations(variable, \
                                                      evaluation['class_information'])
            process_terms = evaluation['class_information']['Process']
            phenomenon_terms = evaluation['class_information']['Phenomenon']
            property_terms = evaluation['class_information']['Property']
            
            if not phenomenon_present and process_present:
                print('\nYou were missing a phenomenon but you had a process present.')
                for key,value in results.items():
                    if 'Phenomenon' in results[key].keys() and key in process_terms:
                        print('Here are some Phenomenon associations I found for the process') 
                        print(key,': ')
                        print('\n'.join(textwrap.wrap(', '.join(results[key]['Phenomenon']), \
                                                      width=70)))
            if not phenomenon_present and property_present:
                print('\nYou were missing a phenomenon but you had a property present.')
                for key,value in results.items():
                    if 'Phenomenon' in results[key].keys() and key in property_terms:
                        print('Here are some Phenomenon associations I found for the property') 
                        print(key,': ')
                        print('\n'.join(textwrap.wrap(', '.join(results[key]['Phenomenon']), \
                                                      width=70)))
            if not property_present and process_present:
                print('\nYou were missing a property but you had a process present.')
                for key,value in results.items():
                    if 'Property' in results[key].keys() and key in process_terms:
                        print('Here are some Property associations I found for the process')
                        print(key,': ')
                        print('\n'.join(textwrap.wrap(', '.join(results[key]['Property']), \
                                                      width=70)))
            if not property_present and phenomenon_present:
                print('\nYou were missing a property but you had a phenomenon present.')
                for key,value in results.items():
                    if 'Property' in results[key].keys() and key in phenomenon_terms:
                        print('Here are some Property associations I found for the phenomenon')
                        print(key,': ')
                        print('\n'.join(textwrap.wrap(', '.join(results[key]['Property']), \
                                                      width=50)))
            print('\nIf you still don\'t see the information you are looking to describe,')
            print('please head on over to the next step where we will do further analysis')
            print('of your variable using WiktiWordNet and Wikipedia.')
            
    else:
        print('It looks like I was not able to find any relevant information')
        print('in SVO for you. Let me check WiktiWordNet and Wikipedia to see ')
        print('if I can find some relevant information. Proceed to the next step!')
    
def categorize_uncategorized_terms(phrase, evaluation):
    
    results = wiktiwordnet.categorize_terms(phrase, evaluation)
    
    if (len(results)>0):
        print('Good news! I was able to fill some holes from SVO using WiktiWordNet.')
        for term, value in results.items():
            for cat, definition in value.items():
                print('I found a categorization for {} as a {}.'.format(term, cat))
                print('The definition(s) in this instance are \n\"{}\".'\
                      .format('\n'.join(textwrap.wrap(definition,width=70))))
    else:
        print('I do not have any additional information to provide at this time.')
    
            
def get_more_specific(phrase, evaluation):
    
    results = svo_api.get_phrase_subtypes(evaluation['class_information'])
    
    if len(results) > 0:
        print('Here are some suggestions on how to make your entry more ')
        print('specific (from SVO):')
        for term, value in results.items():
            print('For the term {} I found the following:'.format(term))
            for cl, words in value.items():
                print('When {} is a {}, its more specific types could be: '\
                     .format(term, cl))
                print('\n'.join(textwrap.wrap(', '.join(words),width=70)))
                
def look_up_variable_components_for_system_state(state):
    
    title, sentence, results = svo_api.get_variable_components(state)
    if sentence != '':
        print('I found a bit of documentation on {}.'.format(state))
        if title.lower() != state.lower():
            print('I did not find an exact match, but I did find some content on ')
            print(title.lower()+'.')
        print('Here is what my source says:\n')
        print('\n'.join(textwrap.wrap((sentence),width=70)))
        print('\n')
        
    nothing_found = True
    for cl, value in results.items():
        if value != []:
            nothing_found = False
            print('I found the following terms that could be a {}:'.format(cl))
            print('\n'.join(textwrap.wrap(', '.join(value),width=70)))
            
    if not nothing_found:
        print('Now that you have some ideas for components of relevant variables,')
        print('try doing a search for these terms in the ontology to see what is there.')
        
def get_suggested_category_for_term(term):
    
    categories = wiktiwordnet.categorize_single_term(term)
    
    for cat, defs in categories.items():
        if defs != '':
            print('\nI found the following definitions that could mean {} is a {}:'.format(term,cat))
            print('\n'.join(textwrap.wrap(defs,width=70)))