# local imports
from inputters import TrainOutDataManager, TrainInDataManager
from text_preparation import *
from .._base import OutExpanderFactory, OutExpanderArticleInput, OutExpander

# import in-expanders SH, acx and maddog, scibert_sklearn, scibert_allennlp and sci_dr
from AcroExpExtractors.AcroExpExtractor_Schwartz_Hearst import (
    AcroExpExtractor_Schwartz_Hearst, )
from AcroExpExtractors.AcroExpExtractor_Yet_Another_Improvement2 import (
    AcroExpExtractor_Yet_Another_Improvement,)
from AcroExpExtractors.AcroExpExtractor_MadDog import (
    AcroExpExtractor_MadDog,)
from AcroExpExtractors.AcroExpExtractor_Scibert_Sklearn import (
    AcroExpExtractor_Scibert_Sklearn,)

# external imports
import pdb
import json
from os import path
import requests
import spacy
import yake as yake
from rake_nltk import Rake
from fuzzywuzzy import fuzz
from  collections import Counter

class FactorySearchEngine(OutExpanderFactory):
    def __init__(self, *args, **kwargs):
        arguments = args[0].split(',')
        self.in_expander = arguments[0]
        self.type_experiment = arguments[1]


    def get_expander(
        self, train_data_manager: TrainOutDataManager, execution_time_observer=None
    ):

        try:
            if train_data_manager.dataset_name == 'MSHCorpus':
                search_results_filepath = 'acrodisam/out_expanders/impl/search_results_cache/MSH_search_results.json'
            if train_data_manager.dataset_name == 'CSWikipedia_res-dup':
                search_results_filepath = 'acrodisam/out_expanders/impl/search_results_cache/CSWiki_search_results.json'
            if train_data_manager.dataset_name == 'ScienceWISE':
                search_results_filepath = 'acrodisam/out_expanders/impl/search_results_cache/ScienceWISE_search_results.json'
            if train_data_manager.dataset_name == 'SDU-AAAI-AD-dedupe':
                search_results_filepath = 'acrodisam/out_expanders/impl/search_results_cache/SDU_search_results.json'
        except Exception:
            print("No cached search results found for dataset name: " + search_results_filepath)

        return _ExpanderSearchEngine(self.type_in_expander, self.type_experiment, search_results_filepath, )

class _ExpanderSearchEngine(OutExpander):
    def __init__(self, in_expander, search_results_filepath ):
        self.expander =  in_expander[0]
        self.type_experiment =  in_expander[1]
        self.sh_expander =  AcroExpExtractor_Schwartz_Hearst()
        self.acx_expander = AcroExpExtractor_Yet_Another_Improvement()
        self.maddog_expander = AcroExpExtractor_MadDog()
        self.search_results_filepath = search_results_filepath

    def surrounding_5_words_as_context(self, acronym, text):
        splitted_text = text.split()
        position_acronym = splitted_text.index(acronym)
        context = splitted_text[position_acronym-3:position_acronym+2]
        for word in context:
            if word == acronym or word < 3:
                context.remove(word)
        return context

    def rake_as_context(self, acronym, text):
        rake_nltk_var = Rake()
        rake_nltk_var.extract_keywords_from_text(text)  
        keywords_extracted = rake_nltk_var.get_ranked_phrases()
        for keyword in keywords_extracted:
            if acronym not in keyword:
                return keyword

    def spacy_as_context(self, acronym, text):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp.text()
        return doc.ents

    def yake_as_context(self, acronym, text):
        kw_extracter = yake.KeywordExtractor(n=2)
        keywords = kw_extracter.extract_keywords(text)
        for keyword in keywords:
            if acronym not in keyword[0]:
                # print(keyword[0])
                return keyword[0]

    def perform_search_query(self, AcronymForSearchQuery, context):
        subscription_key = "insert subscription query here"
        endpoint = "https://api.bing.microsoft.com/v7.0/search" 

        # Construct a request
        query = 'What does the abbreviation ' + AcronymForSearchQuery + ' mean in the context of ' + context + '?'
        mkt = 'en-US'
        params = {'q': query, 'mkt': mkt}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        print(query)

        # Call the Bing api
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            list_of_snippets = []
            json_data = response.json()
            for item in json_data["webPages"]["value"]:
                if "snippet" in item:
                    list_of_snippets.append(item["snippet"])
                    
            return list_of_snippets
        except Exception as ex:
            raise ex
            
    def sh_expansion(self, acronym, text):
        found_expansion = self.sh_expander.get_best_expansion(acronym, text)
        return found_expansion
    
    def maddog_expansion(self, acronym, text):
        found_expansion = self.maddog_expander.get_best_expansion(acronym, text)
        return found_expansion
    
    def acx_expansion(self, acronym, text):
        found_expansion = self.acx_expander.get_best_expansion(acronym, text)
        return found_expansion

    def process_article(self, out_expander_input: OutExpanderArticleInput):
        predicted_expansions = []
        article_id =  out_expander_input.article.article_id
        article_text = out_expander_input.article.get_raw_text()
        
        # loop through every acronym in the given article
        for acronym in out_expander_input.acronyms_list:
            ## reopen file because intermediate change has potentially occured
            with open(self.search_results_filepath) as filepath:
                search_results_jsonfile = json.load(filepath)

            ## if article not in jsonfile, add the article_id with the acronym and its obtained search results
            if article_id not in list(search_results_jsonfile.keys()):
                context = self.yake_as_context(acronym, article_text)
                bing_search_results =  self.perform_search_query(acronym, context)
                search_results_jsonfile[article_id] = {acronym: bing_search_results}
                print('Acronym added: ' + acronym + ' on article ' + article_id)
                with open(self.search_results_filepath,  'w') as f:
                    f.write(json.dumps(search_results_jsonfile, sort_keys=True, indent=4, separators=(',',  ': ')))

            ## if article in jsonfile, add the acronym and its obtained search results within the already existing artielid 
            ### meaning; if an article contains more than 1 acronym, this code is executed
            elif article_id in list(search_results_jsonfile.keys()):
                if acronym not in list(search_results_jsonfile[article_id].keys()):
                    context = self.yake_as_context(acronym, article_text)
                    bing_search_results = self.perform_search_query(acronym, context)
                    search_results_jsonfile[article_id][acronym] = bing_search_results
                    print('Acronym added (with already existing article): ' + acronym + ' on article ' + article_id)
                    with open(self.search_results_filepath,  'w') as f:
                        f.write(json.dumps(search_results_jsonfile, sort_keys=True, indent=4, separators=(',',  ': ')))

            # select if expansion is done per search result, or per all search results concatenated
            if self.type_experiment == 'concatenated results':
                if self.expander == 'sh':
                    found_expansion = self.sh_expansion(acronym, concetenated_search_results)
                elif self.expander == 'maddog':
                    found_expansion = self.maddog_expansion(acronym, concetenated_search_results)
                elif self.expander == 'acx':
                    found_expansion = self.acx_expansion(acronym, concetenated_search_results)

            elif self.type_experiment == 'per_search_result':
                # if article and acronym cached, perform in-expansion on the stored search results
                concetenated_search_results = ''
                for search_result in search_results_jsonfile[article_id][acronym]:
                    # search_result =  search_result.translate(str.maketrans('', '', string.punctuation))
                    concetenated_search_results += search_result

                # CODE FOR EXPANSION PER SEARCH RESULTS
                list_of_expansions = []
                for search_result in search_results_jsonfile[article_id][acronym]:
                    if self.expander == 'sh':
                        best_acronym_per_search_result = self.sh_expansion(acronym, search_result)
                    elif self.expander == 'maddog':
                        best_acronym_per_search_result = self.maddog_expansion(acronym, search_result)
                    elif self.expander == 'acx':
                        best_acronym_per_search_result = self.acx_expansion(acronym, search_result)
                    if best_acronym_per_search_result != '':
                        list_of_expansions.append(best_acronym_per_search_result)
                occurance_count = Counter(list_of_expansions)
    
                if len(list_of_expansions) > 0:
                    found_expansion = occurance_count.most_common(1)[0][0]
                else:
                    found_expansion = ''



            predicted_expansions.append((found_expansion, 1))
        print(predicted_expansions)
        return predicted_expansions