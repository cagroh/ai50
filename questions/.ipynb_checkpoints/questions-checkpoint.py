import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # CG: initialize resulting dictionary:
    result = dict()

    # CG: build search_dir by adding the category number to the starting dir:
    search_dir = directory + os.sep

    # CG: walk down the directory tree:
    for root, dirs, files in os.walk(search_dir):

        # CG: get a list of all files in the directory:
        filenames = [(os.path.join(root, file)) for file in files]

        # CG: ignore empty entries:
        if len(filenames) == 0:
            continue

        # CG: add an entry in the arrays for each file found:
        for i in range(len(filenames)):

            # CG: open the file:
            f = open(filenames[i], mode='r', encoding='utf-8')
            
            #CG: read the content:
            contents = f.read()
            
            result.update ({files[i]: contents})

            # CG: close the file:
            f.close()

    # CG: return the resulting dictionary:
    return result


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # CG: helper to extract and tokenize the words from the document, lowercase and rid of punctuation:
    #     (adapted from sentiment.py)
    def extract_words(document):
        return list(
            word.translate({ord(i): None for i in string.punctuation}).lower() for word in nltk.word_tokenize(document)
            if any(c.isalpha() for c in word)
        )

    # CG: initialize resulting list:
    result = list()

    # CG: extract and tokenize the words from the document, lowercase and rid of punctuation:
    tokenized_document = extract_words(document)

    # CG: iterate thru all words in the tokenized document:
    for word in tokenized_document:

        # CG: test if the word is not a stop word:
        if word not in nltk.corpus.stopwords.words("english"):

            # CG: add the word to the list:
            result.append (word)

    # CG: sort the list:
    result = (sorted(result))

    # CG: return the result:
    return result


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # CG: initialize a set of unique words:
    words_set = set()

    # CG: initialize dictionary of documents and words with their respective count inside each document:
    word_doc_count = dict()

    # CG: loop over all documents to come-up with a set of unique words and a dictionary with word and it's frequence inside a document:
    for document in documents:

        # CG: initialize subdictionary of words and their respective count inside the document:
        word_occurrences = dict()

        # CG: add the entire set of words of the document to the set of unique words:
        words_set.update(documents[document])

        # CG: loop over all words in the document:
        for word in documents[document]:

            # CG: check if the word already exists in the list:
            if word in word_occurrences:

                # CG: compute one more occurence:
                word_occurrences[word] += 1
            else:

                # CG: first occurence:
                word_occurrences[word]  = 1

        # CG: add the subdictionary to the corpus:
        word_doc_count[document] = word_occurrences

    # CG: the following code was adapted from tfidf.py: 
    # CG: initialize dictionary of idfs:
    idfs = dict()
    
    # CG: iterate thru all unique words:
    for word in words_set:
        
        # CG: compute word total frequency:
        f = sum(word in word_doc_count[docname] for docname in word_doc_count)

        # CG: compute IDFs
        idf = math.log(len(word_doc_count) / f)
        
        # CG: save the IDF for the word:
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # CG: let's signal some activity:
    #print (f"Searching for terms inside documents...")

    # CG: initialize dictionary to store occurrences of a word inside a file:
    occurrences = dict()

    # CG: loop over all words in the query:
    for word in query:

        # CG: loop over all files:
        for file in files:

            # CG: compute the occurences of a word in a file:
            occurrences[word+'|'+file]=list(files[file]).count(word)

    # CG: the following code was adapted from tfidf.py:
    # CG: initialize dictionary of files and their respective total TF-IDF:
    dtfidfs = dict()

    # CG: loop over all files:
    for filename in files:

        # CG: initialize total TF-IDF count:
        tfidfs = 0

        # CG: loop over all words in the query:
        for word in query:

            # CG: compute word frequency inside a file:
            tf = occurrences[word+'|'+filename]

            # CG: accumulate total TF-IDF of this file:
            tfidfs += tf * idfs[word]

        # CG: store file's TF-IDF:
        dtfidfs[filename] = tfidfs

    # CG: sort the resulting dictionary:
    dtfidfs = dict(sorted(dtfidfs.items(), key=lambda row: row[1], reverse=True))

    # print (dtfidfs)
    
    # CG: initialize resulting list:
    result = list()

    # CG: build the resuling list, topped to n elements:
    result = list(dtfidfs.keys())[:n]
    
    # CG: return the resulting list:
    return result


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # CG: initialize dictionary of sentences and their respective total IDF:
    sentence_idf = dict()

    # CG: loop over all sentences:
    for sentence in sentences:

        # CG: initialize list of unique occurrencies of query words found in the sentence:
        words_found  = list()

        # CG: initialize total TF-IDF count:
        sum_idfs = 0

        # CG: loop over all words in the query:
        for word in query:

            # CG: check if a word is in the sentence:
            if word in sentences[sentence]:

                # CG: accumulate total IDF of this sentence:
                sum_idfs += idfs[word]

        # CG: loop over all word in the sentence:
        for word in sentences[sentence]:

            # CG: check if the word is in the query:
            if word in query:

                    # CG: add the word to the list:
                    words_found.append (word)

        # CG: store sentence's IDF alongside with its query term density in the dictionary:
        sentence_idf[sentence] = (sum_idfs, len(words_found) / len(sentences[sentence]))

    # CG: sort the resulting dictionary:
    sentence_idf = dict(sorted(sentence_idf.items(), key = lambda x: (x[1][0], x[1][1]), reverse=True))

    # CG: initialize resulting list:
    result = list()

    # CG: build the resuling list, topped to n elements:
    result = list(sentence_idf.keys())[:n]

    # CG: return the resulting list:
    return result


if __name__ == "__main__":
    main()
