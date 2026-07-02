import yaml
import importlib.metadata
from datetime import datetime
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

# extract presidio analyzer version for reproducability
version = importlib.metadata.version("presidio-analyzer")

# get the current date and time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# init dictionary to dump to yaml later
dict_for_yaml = {
    'presidio_analyzer_version': version,
    'generation_date_of_this_file': current_time,
    'entities': {
        'en': set()
    }
}

# init default analyzer engine to catch nlp-based entities
analyzer = AnalyzerEngine()
analyzer_entities = analyzer.get_supported_entities(language="en")

# add nlp entities to our english set
for entity in analyzer_entities:
    dict_for_yaml['entities']['en'].add(entity)

# init raw registry and load predefined recognizers strictly for english
registry = RecognizerRegistry()
registry.load_predefined_recognizers(languages=["en"])

# extract entities directly from raw registry
for recognizer in registry.recognizers:
    lang = recognizer.supported_language
    
    # if language is english or global (none), add its entities
    if not lang or lang == 'en':
        for entity in recognizer.supported_entities:
            dict_for_yaml['entities']['en'].add(entity)

# convert english set to a sorted list for clean yaml output
dict_for_yaml['entities']['en'] = sorted(list(dict_for_yaml['entities']['en']))

print(f"found {len(dict_for_yaml['entities']['en'])} valid supported entities for english")

# dump dict to yaml file
output_filename = "english_presidio_entities.yaml"

with open(output_filename, 'w', encoding='utf-8') as yaml_file:
    # default_flow_style=false ensures standard yaml block format
    # sort_keys=false keeps metadata keys at the top
    yaml.dump(dict_for_yaml, yaml_file, default_flow_style=False, sort_keys=False)

print(f"\nsuccessfully dumped valid english entities to {output_filename} at {current_time}")