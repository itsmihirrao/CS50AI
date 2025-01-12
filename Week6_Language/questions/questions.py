import nltk
import sys
import os
import math
import string

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
    fileMap = {}
   
    for file in os.listdir(directory):
        fileDir = str(os.path.join(directory, str(file)))
        with open(fileDir, encoding="utf8") as f:
            fileMap[file] = f.read().replace('\n', '')

    return fileMap


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokDoc = []
    tokenized = nltk.word_tokenize(document.lower())
    
    # Go through words in tokenized document
    for word in tokenized:
        # If the word is not a stopword or has no punctuation, add to the tokenized Document list
        if word not in nltk.corpus.stopwords.words("english"):
            if noPunctuation(word):
                tokDoc.append(word)
    
    return tokDoc


# Checks to see if a word has any punctuation in it
def noPunctuation(word):
    for c in word:
        if c in string.punctuation:
            return False

    return True


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = {}
    words = set()

    # Create a set of all words in all documents so words don't repeat
    for document in documents:
        for word in documents[document]:
            words.add(word)

    # Loop through all words and calculate idf values
    for word in words:
        numDocs = 0

        for document in documents:
            if word in documents[document]:
                numDocs += 1
        
        # Divide the number of total documents by the number of documents word appears in
        word_idf = len(documents.keys()) / numDocs
        idfs[word] = math.log(word_idf)

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    topFiles = []
    docScores = {}

    for file in files:
        total = 0

        # Calculate tfidf values for each document
        for word in query:

            # If the word is in the file, multiply the number of times it appears in the file by its idf value
            if word in files[file]:
                tf = files[file].count(word)
                total += tf * idfs[word]

        # Assign the document its total score
        docScores[file] = total

    # Sort the documents based on their score from greatest to least
    docScores = sorted(docScores.items(), key=lambda x: x[1], reverse=True)
    docScores = docScores[:n]
    
    # Extract file names and return the best matching files
    for file in docScores:
        topFiles.append(file[0])

    return topFiles


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    topSents = []
    topSentences = {}

    for sentence in sentences.keys():
        # Get sum of idf values for each word and assign it to be the sentences's score
        total = 0

        for word in query:
            if word in idfs and word in sentences[sentence]:
                total += idfs[word]
        
        # Dict that maps a sentence to its summed idf value and query term density value
        topSentences[sentence] = (total, qtd(sentences[sentence], query))

    # Sort sentences based on total idf value and if they're the same, use the qtd value
    topSentences = sorted(topSentences.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)
    topSentences = topSentences[:n]

    # Extract sentences from sorted list and return the best matching sentences
    for sent in topSentences:
        topSents.append(sent[0])

    return topSents


# Calculates the query term density given a word and a sentence
def qtd(sentence, query):
    numQueryWordsInSen = 0

    # Store the number of times a word in the query also appears in the sentence
    for word in query:
        if word in sentence:
            numQueryWordsInSen += 1

    return numQueryWordsInSen / len(sentence)


if __name__ == "__main__":
    main()
