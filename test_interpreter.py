import interpreter as interp


def check_string(input_string, stripped_string):
    assert (interp.strip_parens(input_string) == stripped_string)


def test_strip_basic():
    check_string("this is a test (and I hope it works).",
                 "this is a test .")


def test_strip_nested():
    check_string("(i am (nested))",
                 "")


def test_strip_very_nested():
    check_string("x (i am (super (duper (nested))) lol)",
                 "x ")


def test_strip_left_unbalanced():
    check_string("(x ((i am (super (duper (nested))) lol)",
                 "(x (")


def test_strip_right_unbalanced():
    check_string("x (i am (super (duper (nested))) lol))",
                 "x )")


def test_paragraph_tokenization():
    paragraphs = interp.lengthy_structured_tokenization(interp.load_file('test1.txt'))
    # Assert paragraph tokenization
    assert (len(paragraphs) == 3)
    # Assert sentence tokenization
    assert (len(paragraphs[0]) == 3)
    assert (len(paragraphs[1]) == 1)
    assert (len(paragraphs[2]) == 6)


def check_present_tense(verb, baseline):
    assert(interp.convert_to_present_tense(verb) == baseline)


def test_present_tense_ran():
    check_present_tense("ran", "run")


def test_present_tense_running():
    check_present_tense("running", "run")


def test_present_tense_run():
    check_present_tense("run", "run")


def test_present_tense_provided():
    check_present_tense("provided", "provide")


def test_present_tense_sought():
    check_present_tense("sought", "seek")

