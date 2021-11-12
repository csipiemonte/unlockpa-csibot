import nltk
import itertools
from num2words import num2words
import pandas
import os

from .spacyutil import spacyHelper, tokenUtil,vectorize_util

#############################################
############ Error handling #################
#############################################



#############################################
############ Text preprocessing #############
#############################################

def SubstituteCompoundWords(text, dictionary):
    """
    SubstituteCompoundWords replace Compund words starting from a dictionary
    :param text: original text
    :param dictionary: dictionary of compaund words
    :return: corrected text
    """
    for word in sorted(dictionary.keys(), key=len, reverse=True):
       if word.lower() in text:
           text = text.replace(word, dictionary.get(word))
    return text

def SubstituteSynonyms(lst, dictionary, flagSplitNgrams):
    """
    SubstituteSynonyms replace synonyms to their master term
    :param lst: list of terms
    :param dictionary: dictionary of synonyms
   :return: list of terms eventually replaced
    """
    for i, val in enumerate(lst):
        for word in dictionary.keys():
            if val == word:
                lst[i] = dictionary.get(val)

    if flagSplitNgrams is True:
        lst = map(lambda char: char.replace("_", " "), lst)
        lst = list(itertools.chain(*[l.split() for l in lst]))
    return lst




def FromNumberToText(x):
    """
       This function converts numbers like 20 to words like "venti"
       https://pypi.org/project/num2words/
        :param x: input token (single word)
        :return: x: if x it is a number it is converted into words
        """
    if x.isdigit():
        x = num2words(int(x), lang='it')
    return x



def LemNormalizeForW2v_spacy(raw_documents, parComposte, spacy_nlp, sinonimi):
    if not (isinstance(raw_documents, pandas.DataFrame)):
        raw_documents_df=pandas.Series(raw_documents) 
    raw_documents_df=vectorize_util.SubstituteCompoundWords_vectorized(raw_documents_df, parComposte)
    _spacylemmacountvectorizer = spacyHelper.SpacyLemmaCountVectorizer(spacy_nlp,sinonimi,None)
    return _spacylemmacountvectorizer.lemmatize_from_raw(raw_documents_df)


def CreateCorpusDoc(path, flagMerge=False):
    corpus = []
    for root, dirs, files in os.walk(path):
        for doc in files:
            if doc.endswith('.txt'):
                print('[READING FILE] {}'.format(doc))
                # Read the txt file
                with open(os.path.join(root, doc), mode='r', encoding='latin-1') as f:
                    text = f.read()
                    corpus.append(text)
                print('Read')
    print('[CORPUS LENGHT {}'.format(len(corpus)))
    if flagMerge is True:
        # The function returns a list of docs merged into a compact one
        corpus = ' '.join(corpus)
    else:
        # The function returns a list of lists (one for each doc)
        corpus = list(map(lambda x: [x], corpus))
    return corpus


#############################################
############ Similarity #####################
#############################################
def addSimilarity(originalData, similarity):
    """
    addSimilarity add the column 'similarity' to a data frame
    :param originalData: original data frame
    :param similarity: similarity matrix
    :return: original data frame sorted by the similarity column
    """
    correctAnswer = originalData
    correctAnswer['similarity'] = similarity.T
    return correctAnswer.sort_values(['similarity'], ascending=False)

def addSimilarityEnsemble(originalData, similarity, colName = 'similarity', threshold = 0.3):
    """
    addSimilarity add the column 'similarity' to a data frame
    :param originalData: original data frame
    :param similarity: similarity matrix
    :return: original data frame sorted by the similarity column
    """
    similarity[similarity < threshold] = 0
    correctAnswer = originalData
    correctAnswer[colName] = similarity.T
    correctAnswer[colName+'_rank'] = correctAnswer[colName].rank(method='min', ascending=False)
    return correctAnswer

