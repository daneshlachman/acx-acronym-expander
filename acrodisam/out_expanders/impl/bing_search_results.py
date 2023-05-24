import random
import pdb
from inputters import TrainOutDataManager

from .._base import OutExpanderFactory, OutExpanderArticleInput, OutExpander

import json
from pprint import pprint
from os import path
import requests

# import in-expanders SH, acx and maddog
from AcroExpExtractors.AcroExpExtractor_Schwartz_Hearst import (
    AcroExpExtractor_Schwartz_Hearst, )
from AcroExpExtractors.AcroExpExtractor_Yet_Another_Improvement2 import (
    AcroExpExtractor_Yet_Another_Improvement,)
from AcroExpExtractors.AcroExpExtractor_MadDog import (
    AcroExpExtractor_MadDog,)

class FactoryRandom(OutExpanderFactory):
    def __init__(self, *args, **kwargs):
        self.in_expander = AcroExpExtractor_Schwartz_Hearst()
        self.acx_in_expander = AcroExpExtractor_Yet_Another_Improvement()
        self.maddog_in_expander = AcroExpExtractor_MadDog()
        self.cache_snippet_filepath = 'acrodisam/out_expanders/impl/search_results_cache.json'
        pass

    def perform_search_query(AcronymForSearchQuery):
        subscription_key = "77b60d329a8e42879ea9bb112e162468"
        endpoint = "https://api.bing.microsoft.com/v7.0/search" 

        # Construct a request
        mkt = 'en-US'
        params = {'q': AcronymForSearchQuery, 'mkt': mkt}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        # pdb.set_trace()
        
        # Call the API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            list_of_snippets = []
            json_data = response.json()
            for item in json_data["webPages"]["value"]:
                if "snippet" in item:
                    list_of_snippets.append(item["snippet"])

            pdb.set_trace()
            concetenated_snippets = ''
            for snippet, title in list_of_snippets, list:
                concetenated_snippets = concetenated_snippets + ' ' + snippet
            return concetenated_snippets
            # print(data)
        except Exception as ex:
            raise ex


    def acronym_context_generator(acronym, ):
        for key,value in train_data_manager.get_acronym_db():
            pass
            # pdb.set_trace()
    # problem = figure out how to let acronym, expansion and context coinside while also keeping in mind how the benchmark 
    # and experiments should take place (probably per acronym) 

    

    def get_expander(
        self, train_data_manager: TrainOutDataManager, execution_time_observer=None
    ):
        # raws_text = 'The meaning of PDF is a computer file format for the transmission of a multimedia document that is not intended to be edited further and appears unaltered in most computer environments; also : a document that uses this format. Portable Document Format (PDF), standardized as ISO 32000, is a file format developed by Adobe in 1992 to present documents, including text formatting and images, in a manner independent of application software, hardware, and operating systems. Based on the PostScript language, each PDF file encapsulates a complete description of a fixed-layout flat document, including the text, fonts, vector'
        # expansion_dict = self.in_expander.get_all_acronym_expansion(raw_text)

        if not path.isfile(self.cache_snippet_filepath):
            raise Exception("File not found")
        
        with open(self.cache_snippet_filepath) as filepath:
            search_results_jsonfile = json.load(filepath)
        

        # pdb.set_trace()dfasdff
        # FactoryRandom.perform_search_query('where does pdf stand for')
        # if AcronymForSearchQuery not in search_results_jsonfile:
        #     pass
        
        acronym_expansions = {}
        execution_time_observer.start()
        for acronym, expansion_articles in train_data_manager.acronym_db.items():
            pdb.set_trace()
            train_data_manager.get_preprocessed_articles_db()[expansion_articles[0][1]]
            distinct_expansions = list(
                {exp_article[0] for exp_article in expansion_articles}
            )
            acronym_expansions[acronym] = distinct_expansions

        execution_time_observer.stop()
        pdb.set_trace()
        return _ExpanderRandom(acronym_expansions)


class _ExpanderRandom(OutExpander):
    def __init__(self, acronym_expansion: dict):
        self.acronym_expansion = acronym_expansion

    def process_article(self, out_expander_input: OutExpanderArticleInput):
        predicted_expansions = []
        for acronym in out_expander_input.acronyms_list:
            expansions = self.acronym_expansion[acronym]
            random_expansion = random.choice(expansions)
            confidence = 1 / len(expansions)
            predicted_expansions.append((random_expansion, confidence))
            pdb.set_trace()

        return predicted_expansions
