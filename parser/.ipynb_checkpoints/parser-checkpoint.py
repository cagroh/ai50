import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | NP VP
NP -> N | Det N | Det Adj N | Adj NP | NP P NP | NP Adv | P NP | Det N P | P Det N
VP -> V | VP NP | NP VP | VP P | VP P NP | VP Det NP | VP Conj VP | Adv VP | VP Adv
Adj -> Adj Adj
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # CG: make the sentence all lowercase and tokenize it:
    tokenized_sentence = nltk.tokenize.word_tokenize(sentence.lower())

    # CG: create a copy to iter over:
    working_sentence = tokenized_sentence.copy()

    # Loop over all words in the copy of the tokenized list:
    for aword in working_sentence:

        # CG: let's initialize our indicator as False:
        word_is_OK = False

        # CG: loop over all chars in a word:
        for achar in aword:

            # CG: check if there are alphabetic characters in the word:
            if achar in "abcdefghijklmnopqrstuvwxyz":

                # CG: if there are, make signal to True:
                word_is_OK = True

        # CG: Any word that doesn’t contain at least one alphabetic character (e.g. . or 28) should be excluded from the returned list:
        if not word_is_OK:

            # CG: remove the word from the list:
            tokenized_sentence.remove (aword)

    # CG: return the tokenized sentence:
    return tokenized_sentence


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # CG: initialize resulting list:
    result = []

    # CG: loop over all 3rd-level branches of a tree:
    for subtree in tree.subtrees(filter=lambda t: t.height() == 3):

        # CG: check if the subtree is an NP:
        if subtree.label() == 'NP':

            # CG: make sure it does not repeat in the result:
            if subtree not in result:

                # CG: add the subtree branch to the resulting list:
                result.append (subtree)

    # CG: return the resulting list:
    return result


if __name__ == "__main__":
    main()
