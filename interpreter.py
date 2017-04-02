import graphviz as gv
import nltk
import csv
import webbrowser
import codecs
import nltk.stem.wordnet as wn
from nltk.parse.stanford import StanfordDependencyParser as sdp

lemmatizer = wn.WordNetLemmatizer()

dependency_parser = sdp(
    path_to_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0.jar",
    path_to_models_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0-models.jar"
)

# Constants
VERB = ['VB', 'VBP', 'VBD', 'VBZ']
NOUN = ['NN', 'NNS', 'VBG', "NNP", "NNPS"]


def load_file(filename="input.txt"):
    """ loads a text file into a string
    
    :param filename: name of file to read
    :return: string content of file
    """
    with codecs.open(filename, "r", "utf-8") as f:
        return f.read()


def strip_parens(text):
    """ strips parenthesis from a string (works with nested parentheses)
        note that this method will leave the extra spaces behind, but this will not affect tokenization
    
    :param text: original string
    :return: text stripped of parenthetical words
    """
    left_parens = []
    right_parens = []
    paren_indices = []  # pairs that correspond to the [beginning, end] of each parenthetical expression

    for index, character in enumerate(text):
        if character is '(':
            left_parens.append(index)
        elif character is ')' and len(left_parens) > 0:
            right_parens.append(index)
            if len(right_parens) == len(left_parens):
                paren_indices.append([left_parens[0], right_parens[-1]])
                left_parens = []
                right_parens = []

    num_right_parens = len(right_parens)
    if num_right_parens is not 0:
        paren_indices.append([left_parens[-1 - num_right_parens + 1], right_parens[num_right_parens - 1]])

    index = 0
    output = ""
    for [beginning, end] in paren_indices:
        output += text[index:beginning]
        index = end + 1
    output += text[index:]

    return output


def lengthy_structured_tokenization(text):
    """ Tokenizes paragraphs and returns paragraphs and their associated sentences
    
    :param text: formatted text
    :return: Ordered rank 2 tensor: Outer array represents paragraphs. Inner array are sentences of the paragraph.
    """
    output = []
    paragraphs = tokenize_passage(text)

    for paragraph in paragraphs:
        sentences = nltk.sent_tokenize(paragraph)
        output.append(sentences)

    return output


def tokenize_passage(text):
    """ Tokenizes a passage by paragraph
    
    :param text: passage
    :return: array of paragraphs
    """
    output = []
    for s in text.splitlines():
        paragraph = s.strip()
        if len(paragraph) > 0:
            output.append(paragraph)
    return output


def get_dependency_graphs(tokenized_text):
    """ returns a dependency graph for each sentence in tokenized text
    
    :param tokenized_text: tokenized text array
    :return: array in same format with dependency graphs for each sentence
    """
    return [
        [get_dependency_graph(sentence) for sentence in paragraph]
        for paragraph in tokenized_text
    ]


def get_dependency_graph(text):
    """ uses Stanford CoreNLP to compute the dependency graph of a sentence
    
    :param text: English sentence (string).
    :return: nltk dependency graph
    """
    results = dependency_parser.raw_parse(text)
    dependency_graph = results.__next__()
    return dependency_graph


def save_dependency_graph(dependency_graph, output_folder="out/", view=False):
    """ render a dependency graph using GraphVis
    
    :param dependency_graph: nltk dependency graph
    :param output_folder: path to output files
    :return: 
    """
    src = gv.Source(convert_to_dot(dependency_graph))
    sentence = sentence_from_graph(dependency_graph)
    if len(sentence) > 100:
        sentence = sentence[:100] + "..."
    src.render(output_folder + sentence, view=view)


def convert_to_dot(dependency_graph):
    """ convert dependency graph to dot format
        based on the to_dot method 
        (@link http://www.nltk.org/_modules/nltk/parse/dependencygraph.html#DependencyGraph.to_dot)
    
    :param dependency_graph: dependency graph to convert
    :return: dot graph string
    """

    # Start the digraph specification
    s = 'digraph G{\n'
    s += 'edge [dir=forward]\n'
    s += 'node [shape=oval]\n'

    # Draw the remaining nodes
    for node in sorted(dependency_graph.nodes.values(), key=lambda v: v['address']):
            s += '\n%s [label="%s %s\n(%s)"]' % (node['address'], node['address'], node['word'], node['tag'])
            for rel, deps in node['deps'].items():
                for dep in deps:
                    if rel is not None:
                        s += '\n%s -> %s [label="%s"]' % (node['address'], dep, rel)
                    else:
                        s += '\n%s -> %s ' % (node['address'], dep)
    s += "\n}"

    return s


def sentence_from_graph(dependency_graph):
    """ get original sentence from a dependency graph
    
    :param dependency_graph: nltk dependency graph
    :return: original English sentence
    """
    words = [dependency_graph.get_by_address(i)['word']
             for i in sorted(dependency_graph.nodes)
             if dependency_graph.get_by_address(i)['word'] is not None]
    return " ".join(words)


def get_right_text_section(dg, node):

    start_index = node['address']
    end_index = find_max_node_index(dg, node)

    output = ""
    for n in range(start_index, end_index + 1):
        word = dg.get_by_address(n)['word']
        if word:
            output += " " + word

    return output.strip()


def get_object_text_section(dependency_graph, node=None):
    """ Returns verb-object mapping
    
    :param dependency_graph: dependency graph
    :param node: current node we are visiting
    :return: map of verb string to array of corresponding objects
    """
    if node is None:
        node = dependency_graph.nodes[0]

    end_index = find_max_node_index(dependency_graph, node)

    output = {}
    current_verb = node if (node['tag'] in VERB) else dependency_graph.nodes[find_next_verb_index(dependency_graph, node, end_index)]

    while current_verb['address'] and current_verb['address'] <= end_index:
        verb_phrase = current_verb['word']

        next_v_index = find_next_verb_index(dependency_graph, current_verb, end_index)

        output_length_before_parse = len(output)

        compound_nouns = []
        for i in reversed(range(current_verb['address'] + 1, next_v_index)):
            possible_object = dependency_graph.nodes[i]
            word = possible_object['word']
            if word is not None and i not in compound_nouns:
                try:
                    for j in reversed(possible_object['deps']['compound']):
                        possible_compound_noun = dependency_graph.nodes[j]
                        if possible_compound_noun['tag'] in NOUN:
                            word = possible_compound_noun['word'] + " " + word
                            compound_nouns.append(j)
                except KeyError:
                    pass

                if possible_object['tag'] in NOUN:
                    add_verb(output, verb_phrase, word)

        output_length_after_parse = len(output)
        if output_length_before_parse == output_length_after_parse:
            add_verb(output, verb_phrase)

        current_verb = dependency_graph.nodes[next_v_index]

    return output


def add_verb(verb_map, verb_phrase, object_phrase=None):
    present_tense_verb = convert_to_present_tense(verb_phrase).lower()
    if present_tense_verb in verb_map:
        verb_map[present_tense_verb].append(object_phrase)
    else:
        verb_map[present_tense_verb] = [object_phrase]


def find_max_node_index(dg, node):
    children = node['deps']
    children_addresses = []
    for key, value in children.items():
        children_addresses.extend(value)

    max_val = node['address']
    for address in children_addresses:
        max_child_value = find_max_node_index(dg, dg.nodes[address])
        if max_child_value > max_val:
            max_val = max_child_value

    return max_val


def find_next_verb_index(dg, node, max_index):
    start_index = node['address']
    end_index = max_index

    for n in range(start_index + 1, end_index):
        if dg.get_by_address(n)['tag'] in VERB:
            return n

    return end_index + 1


def convert_to_present_tense(verb):
    """ convert a verb to present tense
    
    :param verb: verb in any form
    :return: present tense of verb
    """
    return lemmatizer.lemmatize(verb, 'v')


def analyze_verbs(graphs):
    """ analyzes the verb-object relationships in a graph
    
    :param graphs: 2D array of the dependency graphs of the given text
    :return: array of dictionary of verb-object mappings
    """
    return [
        [get_object_text_section(sentence_graph) for sentence_graph in paragraph_array]
        for paragraph_array in graphs
    ]


def generate_p1(mappings, file_name="app/data/p1.csv"):
    """ generate csv file that satisfies Part 1 of the requirements
    
    :param mappings: 2D array of verb-object relationships mappings
    :param file_name: name of csv file to save
    :return: csv (csv file corresponding to desired output for Part 1 of the problem)
    see <https://github.com/ACMWM/Logapps-TribeHacks-Challenge-2017#example-1-part-1-of-the-problem>
    """
    with open(file_name, 'w') as csv_file:
        fieldnames = ["paragraph #", "sentence #", "verb", "object"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(len(mappings)):
            for j in range(len(mappings[i])):
                mapping = mappings[i][j]
                for verb in mapping:
                    for object_phrase in reversed(mapping[verb]):
                        writer.writerow(
                            {
                                "paragraph #": str(i + 1),
                                "sentence #": str(j + 1),
                                "verb": verb,
                                "object": object_phrase
                            }
                        )


def generate_p2(mappings, file_name="app/data/p2.csv"):
    """ generate csv file that satisfies Part 2 of the requirements
    
    :param mappings: 2D array of verb-object relationships mappings
    :param file_name: name of csv file to save
    :return: csv (csv file corresponding to desired output for Part 2 of the problem)
    see <https://github.com/ACMWM/Logapps-TribeHacks-Challenge-2017#example-1-part-1-of-the-problem>
    """
    counts = {}
    verbs = set()
    for paragraph_array in mappings:
        for mapping in paragraph_array:
            for verb in mapping:
                for object_phrase in mapping[verb]:
                    if object_phrase is not None:
                        if object_phrase not in counts:
                            counts[object_phrase] = {}
                        if verb not in counts[object_phrase]:
                            counts[object_phrase][verb] = 1
                        else:
                            counts[object_phrase][verb] += 1
                        verbs.add(verb)

    fieldnames = [None] + sorted(counts.keys())

    with open(file_name, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for verb in sorted(verbs):
            writer.writerow(
                {
                    field: (counts[field][verb]
                            if verb in counts[field] else 0) if field is not None else verb
                    for field in fieldnames
                }
            )


def generate_noun_csv(p2="app/data/p2.csv", 
    p2i="app/data/p2i.csv", 
    p3="app/data/p3.csv", 
    nouns="app/data/nouns.txt"):
    with open(p2) as p2_file:
        with open(p2i, 'w') as p2i_file:
            csv.writer(p2i_file, delimiter=',').writerows(zip(*csv.reader(p2_file, delimiter=',')))

    with codecs.open(nouns, "r", "utf-8") as file:
        noun_list = set(file.read().split(","))

    with open(p2i) as p2i_file:
        with open(p3, 'w') as p3_file:
            writer = csv.writer(p3_file, delimiter=',')
            reader = csv.reader(p2i_file, delimiter=',')
            for row in reader:
                if row[0] in noun_list or row[0] == "":
                    writer.writerow(row)


def render_webpage(webpage="file:///Users/alex/github/phonics-node-backend/app/index.html"):
    webbrowser.open(webpage, new=2)
