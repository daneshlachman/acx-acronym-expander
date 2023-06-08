import random
import pdb
from inputters import TrainOutDataManager
from text_preparation import *
from .._base import OutExpanderFactory, OutExpanderArticleInput, OutExpander
# kw_extracter = yake.KeywordExtracter()

import json
from pprint import pprint
from os import path
import requests
import spacy
import yake as yake
from rake_nltk import Rake

# import in-expanders SH, acx and maddog
from AcroExpExtractors.AcroExpExtractor_Schwartz_Hearst import (
    AcroExpExtractor_Schwartz_Hearst, )
from AcroExpExtractors.AcroExpExtractor_Yet_Another_Improvement2 import (
    AcroExpExtractor_Yet_Another_Improvement,)
from AcroExpExtractors.AcroExpExtractor_MadDog import (
    AcroExpExtractor_MadDog,)


cache_snippet_filepath = 'acrodisam/out_expanders/impl/search_results_cache.json'

class FactorySearchEngine(OutExpanderFactory):
    def __init__(self, *args, **kwargs):
        self.in_expander = AcroExpExtractor_Schwartz_Hearst()
        self.acx_in_expander = AcroExpExtractor_Yet_Another_Improvement()
        self.maddog_in_expander = AcroExpExtractor_MadDog()
        cache_snippet_filepath = 'acrodisam/out_expanders/impl/search_results_cache.json'
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
        # raws_text = 'The meaning of PDF is a computer file format for the transmission of a multimedia document that is not intended to be edited further and appears unaltered in most computer environments; also : a document that uses this format. Portable Document Format (PDF), standardized as ISO 32000, is a file format developed by Adobe in 1992 to present documents, including text formatting and images, in a manner independent of application software, hardware, and operating systems. Based on the PostScript language, each PDF file encapsulates a complete description of a fixed-layout flat document, including the text, fonts, vector'
        # expansion_dict = self.in_expander.get_all_acronym_expansion(raw_text)

        if not path.isfile(cache_snippet_filepath):
            raise Exception("File not found")
        
        with open(cache_snippet_filepath) as filepath:
            search_results_jsonfile = json.load(filepath)
        

        # acronym_expansions = {}
        # acronym_articles = {}
        # execution_time_observer.start()
        # for acronym, expansion_articles in train_data_manager.acronym_db.items():
        #     distinct_expansions = []
        #     distinct_articles = []
        #     for exp_article in expansion_articles:
        #         pdb.set_trace()
        #         if not (exp_article[0] in (item for sublist in distinct_expansions for item in sublist)):

        #             pdb.set_trace()
        #             preproc_text = train_data_manager.get_preprocessed_articles_db()[exp_article[1]]
        #             expansion_without_spaces = get_expansion_without_spaces(exp_article[0])
        #             preproc_text_with_acronym = preproc_text.replace(expansion_without_spaces, acronym)
        #             context = FactorySearchEngine.yake_as_context(acronym, preproc_text_with_acronym)
        #             distinct_expansions.append([exp_article[0], context])

        #     acronym_expansions[acronym] = distinct_expansions



            execution_time_observer.stop()

            # pdb.set_trace()
        return _ExpanderSearchEngine(search_results_jsonfile, train_data_manager)


# HETZELFDE DOEN ALS BIJ RANDOM, ALLEEN EXTRA DICT MAKEN VOOR ALLEEN DE ARTICLE_IDS OF TXT VAN DE ARTICLE_IDS (FF KIJKEN
# WAT HANDIG IS)

class _ExpanderSearchEngine(OutExpander):
    def __init__(self, cached_contexts: dict, trainer):
        self.cached_contexts = cached_contexts
        self.trainer = trainer
        self.sh_expander =  AcroExpExtractor_Schwartz_Hearst()
        self.bing_factory = FactorySearchEngine()

    def perform_search_query(self, AcronymForSearchQuery, context):
        subscription_key = "77b60d329a8e42879ea9bb112e162468"
        endpoint = "https://api.bing.microsoft.com/v7.0/search" 

        # Construct a request
        query = 'What does the abbreviation ' + AcronymForSearchQuery + ' mean in the context of ' + context
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
        # pdb.set_trace()
        for keyword in keywords:
            if acronym not in keyword[0]:
                # print(keyword[0])
                return keyword[0]
    
    def process_article(self, out_expander_input: OutExpanderArticleInput):
        predicted_expansions = []

        with open(cache_snippet_filepath) as filepath:
            search_results_jsonfile = json.load(filepath)

        # pdb.set_trace()
        # Receive list of acronyms which should be expanded
        # loop through this list
        # for each acronym get its context and apply in-expander on context to find acronym
        # calculate some sort of probality
        # return list expansions with probabilities

        for acronym in out_expander_input.acronyms_list:
            # pdb.set_trace()
            list_of_cached_acronyms = list(self.cached_contexts.keys())
            if acronym not in list_of_cached_acronyms:
                # if out_expander_input.artile.article_id()
                article_text = out_expander_input.article.get_raw_text()
                context = self.yake_as_context(acronym, article_text)
                # search_results =  self.perform_search_query(acronym, context)
                # pdb.set_trace()
                # search_results_jsonfile[acronym] = search_results
                # with open(cache_snippet_filepath,  'w') as f:
                #     f.write(json.dumps(search_results_jsonfile, sort_keys=True, indent=4, separators=(',',  ': ')))
                # list_of_cached_acronyms.append(acronym)
                # pdb.set_trace()
                # search_results =  self.bing_factory.perform_search_query()

            # pdb.set_trace()

        # for acronym in out_expander_input.acronyms_list:
        #     expansions = self.acronym_expansion[acronym]
        #     random_expansion = random.choice(expansions)
        #     confidence = 1 / len(expansions)  
        #     predicted_expansions.append((random_expansion, confidence))
        #     pdb.set_trace()
        return predicted_expansions
