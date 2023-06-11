import random
import pdb
from inputters import TrainOutDataManager
from text_preparation import *
from .._base import OutExpanderFactory, OutExpanderArticleInput, OutExpander
# kw_extracter = yake.KeywordExtracter()
import statistics
from statistics import mode
import json
from pprint import pprint
from os import path
import requests
import spacy
import yake as yake
from rake_nltk import Rake
import string

# import in-expanders SH, acx and maddog
from AcroExpExtractors.AcroExpExtractor_Schwartz_Hearst import (
    AcroExpExtractor_Schwartz_Hearst, )
from AcroExpExtractors.AcroExpExtractor_Yet_Another_Improvement2 import (
    AcroExpExtractor_Yet_Another_Improvement,)
from AcroExpExtractors.AcroExpExtractor_MadDog import (
    AcroExpExtractor_MadDog,)


cache_snippet_filepath = 'acrodisam/out_expanders/impl/ScienceWISE_search_results.json'

class FactorySearchEngine(OutExpanderFactory):
    def __init__(self, *args, **kwargs):
        self.type_in_expander = args
        pass


    def surrounding_5_words_as_context(acronym, text):
        splitted_text = text.split()
        position_acronym = splitted_text.index(acronym)
        context = splitted_text[position_acronym-3:position_acronym+2]
        for word in context:
            if word == acronym or word < 3:
                context.remove(word)
        return context


    def rake_as_context(acronym, text):
        rake_nltk_var = Rake()
        rake_nltk_var.extract_keywords_from_text(text)
        keywords_extracted = rake_nltk_var.get_ranked_phrases()
        for keyword in keywords_extracted:
            if acronym not in keyword:
                return keyword

    def spacy_as_context(acronym, text):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp.text()
        print(doc.ents)

    def get_expander(
        self, train_data_manager: TrainOutDataManager, execution_time_observer=None
    ):

            # pdb.set_trace()
        return _ExpanderSearchEngine(self.type_in_expander)


class _ExpanderSearchEngine(OutExpander):
    def __init__(self, in_expander):
        self.expander =  in_expander[0]
        self.sh_expander =  AcroExpExtractor_Schwartz_Hearst()
        self.acx_in_expander = AcroExpExtractor_Yet_Another_Improvement()
        self.maddog_expander = AcroExpExtractor_MadDog()

    def perform_search_query(self, AcronymForSearchQuery, context):
        subscription_key = "078e74d227da41d4ada52622eb655b9a"
        endpoint = "https://api.bing.microsoft.com/v7.0/search" 

        # Construct a request
        query = 'What does the abbreviation ' + AcronymForSearchQuery + ' mean in the context of ' + context + '?'
        print(query)
        # pdb.set_trace()
        mkt = 'en-US'
        params = {'q': query, 'mkt': mkt}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}

        # Call the API
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


    def yake_as_context(self, acronym, text):
        kw_extracter = yake.KeywordExtractor(n=2)
        keywords = kw_extracter.extract_keywords(text)
        for keyword in keywords:
            if acronym not in keyword[0]:
                # print(keyword[0])
                return keyword[0]
            
    def sh_expansion(self, acronym, text):
        found_expansion = self.sh_expander.get_best_expansion(acronym, text)
        return found_expansion
    
    def maddog_expansion(self, acronym, text):
        found_expansion = self.maddog_expander.get_best_expansion(acronym, text)
        return found_expansion

    def process_article(self, out_expander_input: OutExpanderArticleInput):
        predicted_expansions = []
        article_id =  out_expander_input.article.article_id
        article_text = out_expander_input.article.get_raw_text()
        
        for acronym in out_expander_input.acronyms_list:
            predicted_expansions = []
            ## reopen file because intermediate change has potentially occured
            with open(cache_snippet_filepath) as filepath:
                search_results_jsonfile = json.load(filepath)

            if article_id not in list(search_results_jsonfile.keys()):
                context = self.yake_as_context(acronym, article_text)
                bing_search_results =  self.perform_search_query(acronym, context)
                search_results_jsonfile[article_id] = {acronym: bing_search_results}
                print('Acronym added: ' + acronym + ' on article ' + article_id)
                with open(cache_snippet_filepath,  'w') as f:
                    f.write(json.dumps(search_results_jsonfile, sort_keys=True, indent=4, separators=(',',  ': ')))

            elif article_id in list(search_results_jsonfile.keys()):
                if acronym not in list(search_results_jsonfile[article_id].keys()):
                    context = self.yake_as_context(acronym, article_text)
                    bing_search_results = self.perform_search_query(acronym, context)
                    search_results_jsonfile[article_id][acronym] = bing_search_results
                    print('Acronym added (with already existing article): ' + acronym + ' on article ' + article_id)
                    with open(cache_snippet_filepath,  'w') as f:
                        f.write(json.dumps(search_results_jsonfile, sort_keys=True, indent=4, separators=(',',  ': ')))
            
            # if article and acronym cached, perform in-expansion on the stored search results
            concetenated_search_results = ''
            for search_result in search_results_jsonfile[article_id][acronym]:
                # search_result =  search_result.translate(str.maketrans('', '', string.punctuation))
                concetenated_search_results += search_result

            # pdb.set_trace()
            if self.expander == 'sh':
                found_expansion = self.sh_expansion(acronym, concetenated_search_results)
            elif self.expander == 'maddog':
                found_expansion = self.maddog_expansion(acronym, concetenated_search_results)
            predicted_expansions.append((found_expansion, 1))
        print(predicted_expansions)
        # pdb.set_trace()
        return predicted_expansions