# Protocol Generators Experiment

## Setup

To run this experiment, download the following versions of the PROHOW dataset:
 - [English](https://www.kaggle.com/paolop/human-instructions-english-wikihow)
 - [Spanish](https://www.kaggle.com/paolop/human-instructions-spanish-wikihow)

You will need a triplestore which exposes a SPARQL endpoint, like the one offered by Virtuoso OpenLink

## Data Filtering
 
From these datasets, we extract a subset of articles we are interested in using this tool:
 - [PROHOW extractor script](https://github.com/paolo7/extractor-script)
 
 This script is run with the following configuration:
 ```
list_of_allowed_languages = ["en","es"]
list_of_allowed_categories = ["http://es.wikihow.com/Categor%C3%ADa:Desayunos","http://www.wikihow.com/Category:Breakfast" # 468
                              ,"http://www.wikihow.com/Category:Recipes","http://es.wikihow.com/Categor%C3%ADa:Recetas" # 15681
                              ,"http://es.wikihow.com/Categor%C3%ADa:Recetas-para-dietas-especiales","http://www.wikihow.com/Category:Specialty-Diet-Recipes"
                              ,"http://www.wikihow.com/Category:Food-Preparation","http://www.wikihow.com/Category:Food-Preparation" # 16733
                              ,"http://www.wikihow.com/Category:Cooking-for-Children"
                              ,"http://www.wikihow.com/Category:Drinks","http://es.wikihow.com/Categor%C3%ADa:Bebidas"
                              ,"http://www.wikihow.com/Category:Holiday-Cooking","http://es.wikihow.com/Categor%C3%ADa:Comidas-festivas"
                              ,"http://www.wikihow.com/Category:Party-Snacks","http://es.wikihow.com/Categor%C3%ADa:Bocadillos-para-fiestas"
                               ]
perform_sparql_filtering = True
remove_multiple_methods = True
remove_multiple_requirements = True
min_number_of_steps = 4
max_number_of_steps = 20
min_number_of_requirements = 4
max_number_of_requirements = 20
owl_sameAs_required_prefixes = [["http://es.wikihow.com/","http://www.wikihow.com/"]]
save_simplified = True
concatenate_label_abstract = False
parse_html_into_text = True
 ```
 
## Triplestore Creation

The simplified triples extracted in the previous phase are loaded in triplesotre (I used Virtuoso).

## Protocol Generator

The protocol `dependency_extractor.py` is configured to access the dataset at the given enpoint (`http://localhost:8890/sparql/` by default).

The `dependency_extractor.py` is run and the following files are generated:

 - `all_labels.txt` contains instance-label pairs
 - `all_dependencies.txt` contains instance-instance pairs, where the second instance need to come after the first
 - `all_turtle` the same as the previous ones, but in valid RDF Turtle format (just add a random prefix for `:`, like the line: `PREFIX : <http://e.c>`


 ## Results in Numbers
 
- The original datasets has 254.349 instructions, about 120.000 each per language

Data Filtering
 - In the selected category there were 21.635 (91.4% loss from dataset)
 - After the filtering we got 5.867 (72.8% loss from previous step)
 - Of those there are 2887 pairs of English-Spanish versions of the same set of instructions (1.5% loss from previous step)

Protocol Generator
 - Then we filter out those pairs that do not have exactly the same number of steps and requirements, losing ??? pairs
 - Then the Protocol Generator tries to assign each requirement to the first steps that requires it, to generate a more interesting graph 
 - The Protocol Generator deletes those graphs that are not isomorphic, as we want exactly similar protocols
 - The Protocol Generator deletes those graphs that have less than 5 requirements assigned to tasks further than the first one
 - Finally we get ??? pairs of instructions/protocols
