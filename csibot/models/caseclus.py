from ..config import config
from .base import Base
from csibot.webservices.exceptions import BotNotTrained, BotTopicsError, BotClusterError
import pandas as pd
from numpy.random import seed
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from .utils import *

from .spacyutil import spacyHelper, tokenUtil,vectorize_util


class Caseclus(Base):

    # def __init__(self):
    #     super().__init__()
    #     self.k = float(config.get('CLUSTERING', 'k'))
    #     self.n_topics = int(config.get('CLUSTERING', 'n'))
    #     self.n_clusters = int(config.get('CLUSTERING', 'n_cluster'))
    #     # is_cluster and is_lsa_sim parameters can be used to select different approaches:
    #     #   - is_cluster = false and is_lsa_sim = false -> Approach I: similarity using TF-IDF matrix
    #     #   - is_cluster = false and is_lsa_sim = TRUE -> Approach IIa: similarity using topic of LSA matrix
    #     #   - is_cluster = TRUE and is_lsa_sim = false -> Approach IIb: clustering and similarity using TF-IDF
    #     #   - is_cluster = TRUE and is_lsa_sim = TRUE -> Approach IIc: clustering and similarity using topic of LSA matrix
    #     self.is_cluster = bool(int(config.get('CLUSTERING', 'is_cluster')))
    #     self.is_lsa_sim = bool(int(config.get('CLUSTERING', 'is_lsa_sim')))
    #     self.clusterModel = None

    def __init__(self, bot, synonyms, knowledgeBase, stopwords, compounds):
        ## Chiamo il costruttore base per inizializzare le variabili comuni:
        super().__init__(bot, synonyms, knowledgeBase, stopwords, compounds)

        ## Inizializzo le variabili specifiche della classe, utilizzando dove possibile gli
        ## oggetti già inizializzati:
        self.n_topics = self.botData['n_topics'][0]
        self.n_clusters =  self.botData['n_cluster'][0]

        # is_cluster and is_lsa_sim parameters can be used to select different approaches:
        #   - is_cluster = false and is_lsa_sim = false -> Approach I: similarity using TF-IDF matrix
        #   - is_cluster = false and is_lsa_sim = TRUE -> Approach IIa: similarity using topic of LSA matrix
        #   - is_cluster = TRUE and is_lsa_sim = false -> Approach IIb: clustering and similarity using TF-IDF
        #   - is_cluster = TRUE and is_lsa_sim = TRUE -> Approach IIc: clustering and similarity using topic of LSA matrix
        self.is_cluster = self.botData['is_cluster'][0]
        self.is_lsa_sim = self.botData['is_lsa_sim'][0]
        print(type(self.is_lsa_sim))
        print(self.is_lsa_sim)
        self.k = self.botData['confidence_lsa'][0] if self.is_lsa_sim else self.botData['confidence_tfidf'][0]
        self.clusterModel = None
        self.spacy_nlp=spacyHelper.spacyInitializer(self.stopwordsList)


    def fitModel(self):
        """
        fitModel learn the internal model from the input data
        """
        seed(50)


        # Replace special characters
        self.df['DOMANDA_CLEAN'] = self.df['question'].apply(lambda x: str.replace(x, '?', ' ')).apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è')).apply(lambda x: str.replace(x, "€", 'euromoneta'))
        self.df['RISPOSTA_CLEAN'] = self.df['answer'].apply(lambda x: str.replace(x, '?', ' ')).apply(lambda x: str.replace(x, '/', ' ')).apply(lambda x: str.replace(x, "’", ' ')).apply(lambda x: str.replace(x, "é", 'è')).apply(lambda x: str.replace(x, "€", 'euromoneta'))

        # Create document corpus consisting of questions
      
        documents= self.df['DOMANDA_CLEAN']
        documents= documents.str.lower()
        # Create document corpus consisting of both answers and questions
        
        complete_document = self.df['DOMANDA_CLEAN'] + ' ' + self.df['RISPOSTA_CLEAN']
        complete_document= complete_document.str.lower()

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
        #                  ,self.tagger), sinonimi, flagSplitNgrams = False)
        #            if x not in self.stopwordsList]
        
        #substitute compounds words : new version
        
        documents=vectorize_util.SubstituteCompoundWords_vectorized(documents, self.parComposte)
        documents=documents.fillna("")

        _spacylemmacountvectorizer = spacyHelper.SpacyLemmaCountVectorizer(self.spacy_nlp,self.sinonimi,self.stemmer, ngram_range=(1, 2))#, max_df=0.98, min_df=2)
        

        #print(_spacylemmacountvectorizer.lemmatize_from_raw(documents))
        #_spacylemmacountvectorizer.fit_transform(documents)
        #print(_spacylemmacountvectorizer.get_feature_names())

        
        
        #LemVectorizer = CountVectorizer(tokenizer=LemNormalize, stop_words=None)
        
        tfidfTran = TfidfTransformer()

        if self.botData['n_topics'][0] <= 1 or self.botData['n_topics'][0] >= self.df.shape[0]:
            self.tagger = None
            raise BotTopicsError(self.botData['id'][0], self.botData['n_topics'][0], self.df.shape[0])
        else:
            nTopics = self.n_topics

        lsa_model = TruncatedSVD(n_components = nTopics)

        # Select which model to use as similarity model
        # is_lsa_sim true -> Approach II: similarity evaluated using LSA matrix
        if self.is_lsa_sim:
            model = Pipeline(steps=[('vectorizer', _spacylemmacountvectorizer),
                    ('tfidf', tfidfTran),
                    ('lsa',lsa_model)])
        else: # is_lsa_sim false -> Similarity evaluated using TF-IDF matrix
            model = Pipeline(steps=[('vectorizer', _spacylemmacountvectorizer),
                    ('tfidf', tfidfTran)])

        # Fit models and retrieve FAQ matrix representation
        self.model = model.fit(documents)
        self.matrix = self.model.transform(documents)

        ## Get clusters
        if self.botData['is_cluster'][0]:
            if self.botData['n_cluster'][0] <= 1 or self.botData['n_cluster'][0] >=  self.df.shape[0]:
                self.tagger = None
                raise BotClusterError(self.botData['id'][0], self.botData['n_cluster'][0], self.df.shape[0])
            else:
                nCluster = self.n_clusters

            kmean_model = KMeans(n_clusters=nCluster, random_state=0)

            clusModel = Pipeline(steps=[('vectorizer', _spacylemmacountvectorizer),
                    ('tfidf', tfidfTran),
                    ('lsa',lsa_model),
                    ('kmean', kmean_model)])

            self.clusterModel = clusModel.fit(documents)

            self.df['cluster'] = clusModel.named_steps['kmean'].labels_

        #nuovo_df = self.df
        #print(nuovo_df.head)
        #print('------------ Salvo file excel ---------')
        #writer = pd.ExcelWriter('output.xlsx')
        #nuovo_df.to_excel(writer, 'Sheet1')
        #writer.save()
        #REMOVED because there's no reference dictionary
        # Create domain dictionary to retrieve typos in user input queries
        #def LemNormalizeForDict(text):
        #    return nltk.word_tokenize(text.lower().translate(self.remove_punct_dict))
        #LemDictionary = CountVectorizer(tokenizer=LemNormalizeForDict, stop_words=self.stopwordsList)
        #LemDictionary.fit_transform(complete_document)
        #self.dizionario =  list(LemDictionary.vocabulary_.keys()) + list(self.dfSyn.synonym_word)
        #self.tagger = None


    def predictOutput(self, queryInput):
        """
        Predict answers with similarity > k
        :param queryInput: text of query (str)
        :return: answers (list of dicts)
        """

        if self.model is None:
            raise BotNotTrained(self.botData['id'][0])


        queryInput = queryInput.lower()
        queryInputCompound=SubstituteCompoundWords(queryInput,self.parComposte)


        queryInput = [queryInputCompound.replace("€", "euromoneta").replace("$", "dollaro").replace("?","")]
        # queryInput = [queryInput]
        #print('tipo input:', queryInput)
        # Retrieve and handle typos
        
        #REMOVED because there's no reference dictionary
        #queryInput = SubstituteTyposErrors(queryInput,
        #                                   GetTyposErrors(queryInput,
        #                                                  self.spacy_nlp,
        #                                                  self.dizionario,
        #                                                  self.stopwordsList,
        #                                                  self.remove_punct_dict),
        #                                   self.remove_punct_dict)
       # print('queryInput:', queryInput)

        # Apply model
        newQuery = self.model.transform(queryInput)
        #print('NEWQUERY TYPE CLUS',type(newQuery))

        # Evaluate cosine similarity
        cos_TfIdfsim = cosine_similarity(newQuery, self.matrix)
        #print('COSCLUS', cos_TfIdfsim)
        #print('COSCLUS TYPE', type(cos_TfIdfsim))
        currentAnswer = addSimilarity(self.df, cos_TfIdfsim)
        selectedAnswers = currentAnswer[(currentAnswer.similarity >= self.k)]

        # is_cluster discriminates if kmeans clustering must be used
        # if is_cluster equal false -> Only similarity is evaluated
        # if is_cluster equal true -> Clustering used as filter
        if self.is_cluster:
            clusterQuery = self.clusterModel.predict(queryInput)[0]
            print('Domanda utente appartiene al cluster {}'.format(clusterQuery))
            # Return list of answers with similarity >= k and belonging to the same aestimated cluster
            selectedAnswers = selectedAnswers[selectedAnswers.cluster == clusterQuery ]

            #print(selectedAnswers)
        # for i in range(len(selectedAnswers.similarity.values)):
        #     print('RISPOSTA', selectedAnswers.answer.values[i])
        #     print('TYPE RISPOSTA', type(selectedAnswers.answer.values[i]))
        #     print('CONFIDENCE', selectedAnswers.similarity.values[i])
        #     print('TYPE CONFIDENCE', type(selectedAnswers.similarity.values[i]))

        return [
            {
                'text': selectedAnswers.answer.values[i],
                'confidence': selectedAnswers.similarity.values[i],
                'index_ques':selectedAnswers.question_number.values[i]
            } for i in range(len(selectedAnswers.similarity.values))
        ]
    def vectorOutput(self, queryInput):
        """
        Predict answers with similarity > k
        :param queryInput: text of query (str)
        :return: answers (list of dicts)
        """
        if self.model is None:
            raise BotNotTrained(self.botData['id'][0])

        queryInputCompound=SubstituteCompoundWords(queryInput,self.parComposte)
        queryInput = [queryInputCompound.replace("€", "euromoneta").replace("$", "dollaro")]

        # Apply model
        newQuery = self.model.transform(queryInput)
        return newQuery
