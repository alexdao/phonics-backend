import argparse as ap
import interpreter as interp

parser = ap.ArgumentParser(
    description="analyzes a passage of text using natural language processing",
    formatter_class=ap.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    "--nouns",
    dest="nouns",
    help="nouns csv file analyze using verb-object dependencies",
    default=None
)

parser.add_argument(
    "--text",
    dest="text",
    help="text to analyze using nlp",
    default="input.txt"
)

parser.add_argument(
    "--demo",
    dest="demo",
    action="store_true",
    help="demo an existing csv",
    default=False
)

parser.add_argument(
    "--graph",
    dest="graph",
    action="store_true",
    help="save graphs",
    default=False
)

args = parser.parse_args()

if args.demo:
    interp.render_webpage()
elif args.nouns:
    interp.generate_noun_csv(nouns=args.nouns)
    interp.render_webpage(webpage="file:///Users/alex/github/phonics-node-backend/app/index3.html")
else:
    text = interp.load_file(args.text)
    stripped_text = interp.strip_parens(text)
    tokenized_text = interp.lengthy_structured_tokenization(text)
    graphs = interp.get_dependency_graphs(tokenized_text)
    if args.graph:
        for paragraph_array in graphs:
            for sentence_graph in paragraph_array:
                interp.save_dependency_graph(sentence_graph)
    maps = interp.analyze_verbs(graphs)
    interp.generate_p1(maps)
    interp.generate_p2(maps)
    interp.render_webpage()
