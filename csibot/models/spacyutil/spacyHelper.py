## from
## https://github.com/mpavlovic/spacy-vectorizers/blob/master/vectorizers.py

import numpy as np
import spacy
from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer, VectorizerMixin
from sklearn.base import TransformerMixin, BaseEstimator
from scipy.sparse import csr_matrix
from spacy.lang.it.stop_words import STOP_WORDS

#our class

from .tokenUtil import stem_token,substitute_synonyms,token_cleaning


def spacyInitializer(stopWordList):

    print("### LOADING spacy italian model ###")
    spacy_nlp = spacy.load("it_core_news_sm",disable=['parser', 'ner'])
    print("### spacy italian model : LOADED ###")   
    #spacy.lang.it.stop_words.STOP_WORDS=set()  # erase all standard stopwords
    for new_sw in stopWordList: # add
         STOP_WORDS.add(new_sw)   
    print("### spacy stopwords : configured ###") 
    lemma_lookup = spacy_nlp.vocab.lookups.get_table("lemma_lookup")
    del lemma_lookup[spacy_nlp.vocab.strings["parente"]]
    del lemma_lookup[spacy_nlp.vocab.strings["parenti"]]
    del lemma_lookup[spacy_nlp.vocab.strings["dimora"]]
    del lemma_lookup[spacy_nlp.vocab.strings["dimore"]]
    return spacy_nlp

# Central classes for lemmatization-stemming-vectorization


class SpacyLemmaCountVectorizer(CountVectorizer):
    
    def __init__(self,spacy_nlp,dictSynonyms,stemmer=None,multi_iters=False, batch_size=10000, n_threads=2,input='content', encoding='utf-8',
                 decode_error='strict', strip_accents=None,
                 lowercase=True, preprocessor=None, tokenizer=None,
                 stop_words=None, token_pattern=r"(?u)[^\r\n ]+",
                 ngram_range=(1, 1), analyzer='word',
                 max_df=1.0, min_df=1, max_features=None,
                 vocabulary=None, binary=False, dtype=np.int64, 
                 nlp=None, ignore_chars='!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~', 
                 join_str=" ", use_pron=False):
        
        super().__init__(input, encoding, decode_error, strip_accents, 
                                                   lowercase, preprocessor, tokenizer,
                                                   stop_words, token_pattern, ngram_range, 
                                                   analyzer, max_df, min_df, max_features,
                                                   vocabulary, binary, dtype)
        self.ignore_chars = ignore_chars
        self.join_str = ' ' # lemmas have to be joined for splitting
        self.use_pron = use_pron
        self.translate_table = dict((ord(char), None) for char in self.ignore_chars) # not used; alpha char already filtered by get_token
        self.nlp=spacy_nlp
        self.n_threads=n_threads
        self.batch_size=batch_size
        self.multi_iters=multi_iters
        self.stemmer=stemmer
        self.dictSynonyms=dictSynonyms

    def get_token(self, token):
        if self.stemmer:
            return stem_token(substitute_synonyms(token_cleaning(self.nlp,token),self.dictSynonyms), self.stemmer)
        else:
            return substitute_synonyms(token_cleaning(self.nlp,token),self.dictSynonyms)[0]

    def docs_generator(self, raw_documents):
        docs_generator = self.nlp.pipe(raw_documents, batch_size=self.batch_size, n_threads=self.n_threads)
        return docs_generator if self.multi_iters == False else list(docs_generator)    
        
    def lemmatize_from_docs(self, docs):
        for doc in docs:
            lemmas_gen = (self.get_token(token) for token in doc if token_cleaning(self.nlp,token)!=None)  # generator expression
            yield self.join_str.join(lemmas_gen) if self.join_str is not None else [lemma for lemma in lemmas_gen]
    
    def lemmatize_from_raw(self,raw_documents):
        spacy_docs=self.docs_generator(raw_documents)
        docs_lemmatized = [doc_lemmatized for doc_lemmatized in self.lemmatize_from_docs(spacy_docs)]
        return docs_lemmatized
    
    def build_tokenizer(self):
        return lambda doc: doc.split()
    
    def transform(self, documents):
        spacy_docs=self.docs_generator(documents)
        raw_documents = self.lemmatize_from_docs(spacy_docs)
        return super(SpacyLemmaCountVectorizer, self).transform(raw_documents)
    
    def fit_transform(self, documents, y=None):
        spacy_docs=self.docs_generator(documents)
        doc_lemmatized = self.lemmatize_from_docs(spacy_docs)
        return super(SpacyLemmaCountVectorizer, self).fit_transform(doc_lemmatized, y)
    
class SpacyWord2VecVectorizer(BaseEstimator, VectorizerMixin):
    
    def __init__(self, sparsify=True):
        self.sparsify = sparsify

    def fit(self, spacy_docs, y=None):
        return self
    
    def fit_transform(self, spacy_docs, y=None):
        # TODO this method is not thread safe!
        X = np.array([doc.vector for doc in spacy_docs])
        return csr_matrix(X) if self.sparsify else X
    
    def transform(self, spacy_docs):
        return self.fit_transform(spacy_docs, None)