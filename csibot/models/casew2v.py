from ..config import config
from .base import Base
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from .utils import *
from .w2v_utils import  *
import os
from csibot.webservices.exceptions import BotNotTrained, W2vFileError

from .spacyutil import spacyHelper, tokenUtil,vectorize_util

class Casew2v(Base):

    # def __init__(self):
    #     super().__init__()
    #     self.k = float(config.get('W2VMODEL', 'k_w2v'))
    #     self.w2vmodelpath = os.path.join(config.get('W2VMODEL', 'path'), config.get('W2VMODEL', 'filename'))
    #     self.methodtype = str(config.get('W2VMODEL', 'methodtype'))
    #     print('[SIMILARITY CONFIDENCE THRESHOLD]: {}'.format(self.k))

    def __init__(self, bot, synonyms, knowledgeBase, stopwords, compounds):
        ## Chiamo il costruttore base per inizializzare le variabili comuni:
        super().__init__(bot, synonyms, knowledgeBase, stopwords, compounds)

        self.k = self.botData['confidence_wv'][0]
        self.w2vmodelpath = os.path.join(config.get('W2VMODEL', 'path'), config.get('W2VMODEL', 'filename'))
        self.methodtype = str(config.get('W2VMODEL', 'methodtype'))
        self.spacy_nlp=spacyHelper.spacyInitializer(self.stopwordsList)
        print('[SIMILARITY CONFIDENCE THRESHOLD]: {}'.format(self.k))
        

    def fitModel(self):
        """
        fitModel learn the internal model from the input data
        """
        # Replace special characters
        self.df['DOMANDA_CLEAN'] = self.df['question'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è'))
        self.df['RISPOSTA_CLEAN'] = self.df['answer'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è'))

        # Create document corpus consisting of questions
        documents = self.df['DOMANDA_CLEAN'].str.lower().tolist()
        # Create document corpus consisting of both answers and questions
        complete_document = self.df['DOMANDA_CLEAN'] + ' ' + self.df['RISPOSTA_CLEAN']
        complete_document = complete_document.str.lower()

        ## Create lists of words to identify
        self.parComposte = dict(self.dfComp.to_dict('split')['data'])
        self.sinonimi = dict(self.dfSyn.to_dict('split')['data'])

        def w2vMethodTypeSwitcher(methodtype):
            """
            This function implements a switcher to select the chosen MethodType
            :param methodtype: param defined in file config.ini
            :return: corresponding method type which defines a specific class
            """
            switcher = {
                "max": MaxEmbeddingVectorizer,
                "mean": MeanEmbeddingVectorizer,
                "tfidf": TfidfEmbeddingVectorizer,
            }
            print('[CHOSEN EMBEDDING METHOD TYPE]: {}'.format(methodtype))
            return switcher.get(methodtype)

        # Load model and create dictionary {word: np.array of embeddings}
        # se la colonna wordvec_path del bot è valorizzata uso lei, altrimenti prendo da config:
        if self.botData['wordvec_path'][0]:
            path = self.botData['wordvec_path'][0]
        else:
            path = self.w2vmodelpath

        try:
            w2vmodel = Word2Vec.load(path)
        except:
            self.tagger = None
            raise W2vFileError((self.botData['id'][0]),path)

        w2v = dict(zip(w2vmodel.wv.index2word, w2vmodel.wv.vectors))

        # Create the matrix of preprocessed QUESTIONS (list of lists of tokens)
        #X = [LemNormalizeForW2v(text=doc,
        #                            remove_punct_dict=self.remove_punct_dict,
        #                            parComposte=self.parComposte,
        #                            tagger=self.tagger,
        #                            sinonimi=self.sinonimi,
        #                            stopwordsList=self.stopwordsList) for doc in documents]
        
        X=LemNormalizeForW2v_spacy(documents, self.parComposte, self.spacy_nlp, self.sinonimi)

        # Instantiate class with chosen method type
        model = w2vMethodTypeSwitcher(methodtype=self.methodtype)(w2v)

        # Fit and transform model
        self.model = model.fit(X)
        self.matrix = model.transform(X)

        # Create domain dictionary to retrieve typos in user input queries
        #def LemNormalizeForDict(text):
        #    return nltk.word_tokenize(text.lower().translate(self.remove_punct_dict))

        # Create the vocabulary
        #LemDictionary = CountVectorizer(tokenizer=LemNormalizeForDict, stop_words=self.stopwordsList)
        #LemDictionary.fit_transform(complete_document)

        #self.dizionario =  list(set(list(LemDictionary.vocabulary_.keys())\
        #               + list(self.dfSyn.synonym_word.apply(lambda x: str.replace(x, '_', ' '))) \
        #               + list(self.dfSyn.base_token.apply(lambda x: str.replace(x, '_', ' ')))))
        #self.tagger = None

    def predictOutput(self, queryInput):
        """
        Predict answers with similarity > k
        :param queryInput: text of query (str)
        :return: answers (list of dicts)
        """
        if self.model is None:
            raise BotNotTrained(self.botData['id'][0])

        queryInput = queryInput.replace("€", "euro moneta").replace("$", "dollaro")

        # Retrieve and handle typos
        #queryInput = ' '.join(SubstituteTyposErrors([queryInput],
        #                                   GetTyposErrors([queryInput],
        #                                                  self.tagger,
        #                                                  self.dizionario,
        #                                                  self.stopwordsList,
        #                                                  self.remove_punct_dict),
        #                                   self.remove_punct_dict))

        # Create the matrix of preprocessed QUESTIONS (list of lists of tokens)
        #X_query = [LemNormalizeForW2v(text=queryInput,
        #                                  remove_punct_dict = self.remove_punct_dict,
        #                                  parComposte = self.parComposte,
        #                                  tagger = self.tagger,
        #                                  sinonimi = self.sinonimi,
        #                                  stopwordsList = self.stopwordsList)]

        X_query=LemNormalizeForW2v_spacy([queryInput], self.parComposte, self.spacy_nlp, self.sinonimi)
                                          
        # Apply model
        newQuery = self.model.transform(X_query)
        # Evaluate cosine similarity
        cos_w2v = cosine_similarity(newQuery, self.matrix)
        # Convert from float32 to float64 (problems of float32 with json)
        cos_w2v = cos_w2v.astype(np.float64)

        # Add column "Similarity" to initial df
        currentAnswer = addSimilarity(self.df, cos_w2v)

        # Return list of answers with similarity >= k
        selectedAnswers = currentAnswer[(currentAnswer.similarity >= self.k)]

        return [
            {
                'text': selectedAnswers.answer.values[i],
                'confidence': selectedAnswers.similarity.values[i]
            } for i in range(len(selectedAnswers.similarity.values))
        ]
