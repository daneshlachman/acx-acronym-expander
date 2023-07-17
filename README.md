# My MSc thesis
MSc thesis on "Using a Web Search Engine for Automatic Acronym Disambiguation"


This project contains the implementation of my search engine approach to acronym disambiguation as an out-expansion module within the [AcX system](https://github.com/JoaoLMPereira/acx-acronym-expander) which I built for my master thesis. My thesis report can be found [here](https://doi.org/10.13140/RG.2.2.28321.58728).

# Abstract
> With the development of scientific fields over time, an uncountable amount of new acronyms emerged, especially within the medical and technical fields. 
Apart from the rise of these new acronyms, already existing acronyms got new possible definitions in a slightly different context. For example, within only the medical field, RS can have 5 different syndrome definitions namely: Raynoud's syndrome Reiter's syndrome, Rett syndrome, Richter's syndrome, or Reye's syndrome. As a result, if a reader encounters an undefined acronym (e.g. RS) and looks up its definition, it finds multiple possible definitions within roughly the same context, which can ultimately lead to misinterpreting the text. This misinterpretation is even more likely to happen when a reader is not familiar with the related field of study.
> 
> Over the past decades, scientists have tried to mitigate the problem of acronym ambiguity (different expansions for the same acronym) by using a rule-based approach or machine-learning models with an annotated corpus that infer the expansion for a given acronym in text. However, no research has been done on how a search engine can be used for automatic acronym disambiguation. So, in this paper, we explore the approach of using the search engine Bing. Although Bing is not specifically designed nor trained to be used for automatic acronym expansion, in this paper, it is utilized as an approach to perform automatic acronym disambiguation.

# Environment
In order to run the Bing out-expander, the AcX system needs to be configured on your system. Please follow the steps on the [original AcX GitHub page](https://github.com/JoaoLMPereira/acx-acronym-expander) to get your environment ready. However, instead of cloning the original repository, clone this forked repository and execute the steps accordingly.

After getting the AcX system ready, install the keyword extraction method YAKE with: `pip install yake`

# Usage
The Bing out-expander can be run by multiple benchmarks, as each benchmark tests the out-expander with a different dataset.

python3 acrodisam/benchmarkers/out_expansion/<strong><em>\<choose benchmark file\><em><strong> --out-expander bing_search_result --out_expander_args sh,
