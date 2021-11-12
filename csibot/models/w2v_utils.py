from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import defaultdict
# Create 3 classes, 1 for each Method Type:
# 1) MeanEmbeddingVectorizer: np.array with an average word vector for each doc
# 2) MaxEmbeddingVectorizer: np.array with a max word vector for each doc
# 3) TfidfEmbeddingVectorizer: np.array with an average word vector weighted with the tfidf for each doc

# 1) MeanEmbeddingVectorizer
class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.dim = len(next(iter(word2vec.values())))

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        This function returns a np.array with averages word vectors for all words in a doc
        :param X: list of lists of tokens (one list for each doc)
        :return: np.array with an average word vector for each doc
        """
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])


# 2) MeanEmbeddingVectorizer
class MaxEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.dim = len(next(iter(word2vec.values())))

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        This function returns a np.array with averages word vectors for all words in a doc
        :param X: list of lists of tokens (one list for each doc)
        :return: np.array with an average word vector for each doc
        """
        return np.array([
            np.max([self.word2vec[w] for w in words if w in self.word2vec]
                   or [np.zeros(self.dim)], axis=0)
            for words in X
        ])


# 3) MeanEmbeddingVectorizer
class TfidfEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(next(iter(word2vec.values())))

    def fit(self, X, y=None):
        """
        This function fits the input with a TfidfVectorizer and
         updates a self.word2weight dictionary {word: tdifd}
        :param X: list of lists of tokens (one list for each doc)
        :return: self: updated class
        """
        tfidf = TfidfVectorizer(analyzer=lambda x: x)
        tfidf.fit(X)
        # if a word was never seen - it must be at least as infrequent
        # as any of the known words - so the default idf is the max of
        # known idf's
        max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(
            lambda: max_idf,
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
        return self

    def transform(self, X):
        """
        This function returns a np.array with weighted averages word vectors for all words in a doc.
        The weights are defined in fit() function through tf-idf vectorizer
        :param X: list of lists of tokens (one list for each doc)
        :return: np.array with an average weighted word vector for each doc
        """
        return np.array([
            np.mean([self.word2vec[w] * self.word2weight[w]
                     for w in words if w in self.word2vec] or
                    [np.zeros(self.dim)], axis=0)
            for words in X
        ])