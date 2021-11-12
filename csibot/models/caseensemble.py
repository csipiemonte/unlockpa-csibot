from numpy.random import seed
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from gensim.models import Word2Vec
from csibot.webservices.exceptions import BotNotTrained, BotTopicsError, W2vFileError
import pandas as pd
from .base import Base
from .utils import *
from .w2v_utils import *
from ..config import config

from .spacyutil import spacyHelper, tokenUtil,vectorize_util


class Caseensemble(Base):

    def __init__(self, bot, synonyms, knowledgeBase, stopwords, compounds):
        ## Chiamo il costruttore base per inizializzare le variabili comuni:
        super().__init__(bot, synonyms, knowledgeBase, stopwords, compounds)

        self.k = self.botData['confidence_tfidf'][0]
        self.k_w2v = self.botData['confidence_wv'][0]
        self.k_lsa = self.botData['confidence_lsa'][0]
        self.w2vmodelpath = os.path.join(config.get('W2VMODEL', 'path'), config.get('W2VMODEL', 'filename'))
        self.methodtype = str(config.get('W2VMODEL', 'methodtype'))
        print('[SIMILARITY CONFIDENCE THRESHOLD]: {}'.format(self.k_w2v))

        ## Inizializzo le variabili specifiche della classe, utilizzando dove possibile gli
        ## oggetti già inizializzati:
        self.n_topics = self.botData['n_topics'][0]
        self.n_clusters =  self.botData['n_cluster'][0]
        self.clusterModel = None
        self.lsa_model = None
        self.sim_model = None
        self.spacy_nlp=spacyHelper.spacyInitializer(self.stopwordsList)

    def fitModelW2v(self):
        """
        fitModel learn the internal model from the input data
        """
        # Replace special characters
        self.df['DOMANDA_CLEAN'] = self.df['question'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è'))
        self.df['RISPOSTA_CLEAN'] = self.df['answer'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è'))

        ## Create lists of words to identify
        self.parComposte = dict(self.dfComp.to_dict('split')['data'])
        self.sinonimi = dict(self.dfSyn.to_dict('split')['data'])

        # Create document corpus consisting of questions
        documents = self.df['DOMANDA_CLEAN']
        documents = documents.str.lower()

        ## Similarity model
        # Lemmatizer, stemmer, punctuation handling, compound words, synonyms
        self.stemmer = nltk.stem.snowball.ItalianStemmer()

        ## Word2Vec
        documents = documents.tolist()
        # Create document corpus consisting of both answers and questions
        complete_document = self.df['DOMANDA_CLEAN'] + ' ' + self.df['RISPOSTA_CLEAN']
        complete_document = complete_document.str.lower()


        ## Word2Vec
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
        self.w2vmodel = model.fit(X)
        self.w2vmatrix = model.transform(X)


        # Create domain dictionary to retrieve typos in user input queries
        def LemNormalizeForDict(text):
            return nltk.word_tokenize(text.lower().translate(self.remove_punct_dict))

        # Create the vocabulary
        LemDictionary = CountVectorizer(tokenizer=LemNormalizeForDict, stop_words=self.stopwordsList)
        LemDictionary.fit_transform(complete_document)

        self.dizionario =  list(set(list(LemDictionary.vocabulary_.keys())\
                       + list(self.dfSyn.synonym_word.apply(lambda x: str.replace(x, '_', ' '))) \
                       + list(self.dfSyn.base_token.apply(lambda x: str.replace(x, '_', ' ')))))
        self.tagger = None

    def fitModelClus(self):
        """
        fitModel learn the internal model from the input data
        """
        seed(50)

        # Replace special characters
        self.df['DOMANDA_CLEAN'] = self.df['question'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è')).apply(lambda x: str.replace(x, "€", 'euromoneta'))
        self.df['RISPOSTA_CLEAN'] = self.df['answer'].apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è')).apply(lambda x: str.replace(x, "€", 'euromoneta'))

        # Create document corpus consisting of questions
        documents = self.df['DOMANDA_CLEAN']
        documents = documents.str.lower()
        # Create document corpus consisting of both answers and questions
        complete_document = self.df['DOMANDA_CLEAN'] + ' ' + self.df['RISPOSTA_CLEAN']
        complete_document = complete_document.str.lower()

        ## Parameter definition
        # Lemmatizer, stemmer, punctuation handling, compound words, synonyms
        self.stemmer = nltk.stem.snowball.ItalianStemmer()
        self.parComposte = dict(self.dfComp.to_dict('split')['data'])
        self.sinonimi = dict(self.dfSyn.to_dict('split')['data'])

        # Learn model:
        #   Step 1: vectorizer
        #   Step 2: tfidf
        #   Step 3: SVD decomposition
        #   Dictionary
        #def LemNormalize(text):
        #    return [stemNounVerbs(x,self.tagger,stemmer) for x in SubstituteSynonyms(
        #        LemTokens(nltk.word_tokenize(SubstituteCompoundWords(text.lower().translate(self.remove_punct_dict), parComposte))
        #                  , self.tagger), sinonimi, flagSplitNgrams = False)
        #            if x not in self.stopwordsList]

        documents=vectorize_util.SubstituteCompoundWords_vectorized(documents, self.parComposte)
        documents=documents.fillna("")

        _spacylemmacountvectorizer = spacyHelper.SpacyLemmaCountVectorizer(self.spacy_nlp,self.sinonimi,self.stemmer)


        #LemVectorizer = CountVectorizer(tokenizer= _spacylemmacountvectorizer, stop_words=None)
        tfidfTran = TfidfTransformer()

        if self.botData['n_topics'][0] <= 1 or self.botData['n_topics'][0] > self.df.shape[0]:
            self.tagger = None
            raise BotTopicsError(self.botData['id'][0], self.botData['n_topics'][0], self.df.shape[0])

        nTopics = self.n_topics

        lsaComponent = TruncatedSVD(n_components = nTopics)

        # Select which model to use as similarity model
        # is_lsa_sim true -> Approach II: similarity evaluated using LSA matrix
        lsa_model = Pipeline(steps=[('vectorizer', _spacylemmacountvectorizer),
                    ('tfidf', tfidfTran),
                    ('lsa',lsaComponent)])
        # is_lsa_sim false -> Similarity evaluated using TF-IDF matrix
        sim_model = Pipeline(steps=[('vectorizer', _spacylemmacountvectorizer),
                                    ('tfidf', tfidfTran)])

        # TF-IDF sim model
        self.sim_model = sim_model.fit(documents)
        self.sim_matrix = self.sim_model.transform(documents)

        # Lsa model
        self.lsa_model = lsa_model.fit(documents)
        self.lsa_matrix = self.lsa_model.transform(documents)


        # ## Get clusters
        # if self.botData['n_cluster'][0] <= 1 or self.botData['n_cluster'][0] > self.df.shape[0]:
        #     print('Wrong number of provided clusters. Default number is 2.')
        #     nCluster = 2
        # else:
        #     nCluster = self.n_clusters
        #
        # kmean_model = KMeans(n_clusters=nCluster, random_state=0)
        # clusModel = Pipeline(steps=[('vectorizer', LemVectorizer),
        #                             ('tfidf', tfidfTran),
        #                             ('lsa',lsaComponent),
        #                             ('kmean', kmean_model)])
        # self.clusterModel = clusModel.fit(documents)
        # self.df['cluster'] = clusModel.named_steps['kmean'].labels_


        # Create domain dictionary to retrieve typos in user input queries
        #def LemNormalizeForDict(text):
        #   return nltk.word_tokenize(text.lower().translate(self.remove_punct_dict))
        #LemDictionary = CountVectorizer(tokenizer=LemNormalizeForDict, stop_words=self.stopwordsList)
        #LemDictionary.fit_transform(complete_document)
        #self.dizionario =  list(LemDictionary.vocabulary_.keys()) + list(self.dfSyn.synonym_word)

    def fitModel(self):
        # Train Cluster, LSA and TF-IDF similarity models
        self.fitModelClus()
        # Train w2v model
        self.fitModelW2v()


    def predictOutput(self, queryInput):
        """
        Predict answers with similarity > k
        :param queryInput: text of query (str)
        :return: answers (list of dicts)
        """

        if self.sim_model is None or self.w2vmodel is None:
            self.tagger = None
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
        
        
        # Apply models
        newQuery = self.w2vmodel.transform(X_query)
        cos_w2v = cosine_similarity(newQuery, self.w2vmatrix)
        cos_w2v = cos_w2v.astype(np.float64)

        # Tf-idf
        newQuery = self.sim_model.transform([queryInput])
        cos_TfIdfsim = cosine_similarity(newQuery, self.sim_matrix)

        # LSA
        newQuery = self.lsa_model.transform([queryInput])
        cos_lsa = cosine_similarity(newQuery, self.lsa_matrix)

        # Add column "Similarity" to initial df
        currentAnswer = addSimilarityEnsemble(self.df.copy(), cos_w2v, threshold=self.k_w2v, colName='similarityW2V')
        currentAnswer = addSimilarityEnsemble(currentAnswer, cos_TfIdfsim, threshold=self.k, colName='similarityTFIDF')
        currentAnswer = addSimilarityEnsemble(currentAnswer, cos_lsa, threshold=self.k_lsa, colName='similarityLSA')
        currentAnswer['similarity'] = currentAnswer[['similarityW2V','similarityTFIDF','similarityLSA']].mean(axis=1)
        currentAnswer['rank_medio'] = currentAnswer[['similarityW2V_rank', 'similarityTFIDF_rank', 'similarityLSA_rank']].mean(axis=1)
        currentAnswer = currentAnswer.sort_values(['similarity'], ascending=False)
        #currentAnswer = currentAnswer.sort_values(['rank_medio'], ascending=True)

        #writer = pd.ExcelWriter('risposta.xlsx')
        #currentAnswer.to_excel(writer, 'Sheet1')
        #writer.save()
        # Return list of answers with similarity >= k
        selectedAnswers = currentAnswer[(currentAnswer.similarity >= self.k)]

        return [
            {
                'text': selectedAnswers.answer.values[i],
                'confidence': selectedAnswers.similarity.values[i],
                'index_ques':selectedAnswers.question_number.values[i]
            } for i in range(len(selectedAnswers.similarity.values))
        ]
