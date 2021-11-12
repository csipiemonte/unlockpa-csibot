#from nltk.corpus import stopwords
from spacy.lang.it.stop_words import STOP_WORDS
import string
class Base:


    def verifyDataframes(self, bot, sysnonyms, knowledgeBase, stopwordsInput, compounds):
        """
        Verify data frame coherence
        :param bot: mandatory (pd.dataframe)
        :param sysnonyms: could be empty (pd.dataframe)
        :param knowledgeBase: mandatory (pd.dataframe)
        :param stopwordsInput: could be empty (pd.dataframe)
        :param compounds: could be empty (pd.dataframe)
        """
        # Check data frames:
        # bot and knowledgeBase data frames must not be empty
        if knowledgeBase.empty:
            raise Exception('Empty data frame KnowledgeBase. Procedure stopped.')
        if bot.empty:
            raise Exception('Empty data frame Bot definition. Procedure stopped.')
        # Retrieve id bot
        idBot = bot['id'][0]
        # Warning if other data frames Empty:
        if compounds[(compounds['id_bot'] == idBot)].empty:
            print('Data frame COMPOUNDS empty for bot ' + str(idBot) + '.')
        if sysnonyms[(sysnonyms['id_bot'] == idBot)].empty:
            print('Data frame SYNONYMS empty for  bot ' + str(idBot) + '.')
        if stopwordsInput[(stopwordsInput['id_bot'] == idBot)].empty:
            print('Data frame STOPWORDS empty for bot ' + str(idBot) + '.')

    def set_n_answers(self, n):
        """
        Set maximum number of similar answer to retrieve from query method
        :param n: number of anwsers to retrieve (int)
        :return:
        """
        self.n = n

    def __init__(self, bot, sysnonyms, knowledgeBase, stopwordsInput, compounds):
        """
        Initialize class from data frames
        :param bot: model definition (pd.dataframe)
        :param sysnonyms: synonims (pd.dataframe)
        :param knowledgeBase: q&a (pd.dataframe)
        :param stopwordsInput: stopwords (pd.dataframe)
        :param compounds: compound words (pd.dataframe)
        """
        self.verifyDataframes(bot, sysnonyms, knowledgeBase, stopwordsInput, compounds)

        idBot = bot['id'][0]
        # Keep only necessary columns
        self.df = knowledgeBase[(knowledgeBase['id_bot'] == idBot)]
        self.dfComp = compounds[(compounds['id_bot'] == idBot)][['compound_word', 'base_token']]
        self.dfSyn = sysnonyms[(sysnonyms['id_bot'] == idBot)][['synonym_word', 'base_token']]
        self.botData = bot
        self.n = 5
        self.remove_punct_dict = dict((ord(punct), ' ') for punct in string.punctuation)

        # Set stopwords:
        wordsToAddDF = stopwordsInput[((stopwordsInput['id_bot'] == idBot)) & (stopwordsInput['to_keep'] == False)]
        wordsToRemoveDF = stopwordsInput[(stopwordsInput['id_bot'] == idBot) & (stopwordsInput['to_keep'] == True)]
        wordsToAdd = []
        wordsToRemove = []
        for word in wordsToAddDF['stopword']:
            wordsToAdd.append(word)
        for word in wordsToRemoveDF['stopword']:
            wordsToRemove.append(word)
        self.stopwordsList = set(list(STOP_WORDS)+ [''] + wordsToAdd).difference(wordsToRemove)

        # Model attributes
        self.dizionario = None
        self.model = None
        self.matrix = None

    def fitModel(self):
        """
        Model fitting from input dataset
        """
        # Questo metodo può contenere un apprendimento di base o essere esteso/sovrascritto dai vari modelli
        pass

    def predictOutput(self, queryInput):
        """
        Predict answers with similarity > k
        Override this method from every model
        :param queryInput: text of query (str)
        :return: answers (list of dicts)
        """
        return []

    def query(self, text, tenant='-1'):
        """
        Get input query and return list of max n answer
        :param text: text of query (str)
        :return: answers (list of dicts)
        """
        null_answer={
                        'text': str(-1),
                        'confidence': 0
                    }
        if text is not None and len(text)>=4:
            result = self.predictOutput(text)[:self.n]
            if len(result) == 0:
                result.append(null_answer)
        else:
            result=[]
            result.append(null_answer)
        
         
        return result
