from .command import Command
from ..client import Client
from pandas import read_excel, ExcelFile
import numpy as np
import os


SHFAQ = 'FAQ_unite'
SHCOMP = 'Parole_Composte'
SHSYN = 'Sinonimi'
SHSTOP = 'Stopwords'
SHMODEL = 'Model_def'
SHLIST = [SHFAQ, SHCOMP, SHSYN, SHSTOP, SHMODEL]


class Insert(Command):
    """Insert data of new bot into the database"""

    name = 'insert'
    arguments = [
        dict(name='--endpoint', type=str, default='http://localhost:5401', help='Botmanager endpoint'),
        dict(name='--excel', type=str, default='data/faqNew.xlsx', help='FAQ file excel'),
    ]

    def main(self, args):
        self.log.info(f'Started with arguments: {args}')

        # Check if file exists
        if not os.path.isfile(args.excel):
            raise Exception(f'File {args.excel} non trovato')

        # Check if required sheets exist
        sheets = ExcelFile(args.excel).sheet_names
        sheet_mancanti = list(set(SHLIST) - set(sheets))
        if sheet_mancanti:
            raise Exception(f'Sheet mancanti in {args.excel}: {sheet_mancanti}')

        df = read_excel(args.excel, SHFAQ, converters={'question_number': str}).replace(np.nan, '', regex=True)
        dfComp = read_excel(args.excel, SHCOMP).replace(np.nan, '', regex=True)
        dfSyn = read_excel(args.excel, SHSYN).replace(np.nan, '', regex=True)
        dfStop = read_excel(args.excel, SHSTOP).replace(np.nan, '', regex=True)
        dfModel = read_excel(args.excel, SHMODEL)
        dfModel = self.correctNaN(dfModel)

        self.check_model(dfModel, args.excel)

        botmanager_client = Client(args.endpoint)
        result = botmanager_client.post('insert',
                                       bot=dfModel.to_dict('records')[0],
                                       knowledge_base=df.to_dict('records'),
                                       stopwords=dfStop.to_dict('records'),
                                       compound_words=dfComp.to_dict('records'),
                                       synonym_words=dfSyn.to_dict('records'),
                                       )
        self.log.info(result)

    def check_model(self, df, filename):
        if df.empty:
            raise Exception(f'Definizione del modello nello sheet {SHMODEL} del file {filename} non trovata')

        # Check coerence inside model definition

        # TF-IDF / LSA, with (with/o) clustering
        if df['num_algo'].get(0) == 1:
            # TF-IDF
            if not df['is_lsa_sim'].get(0):
                if np.isnan(df['confidence_tfidf'].get(0)):
                    raise Exception(f'Necessaria soglia per modello tfidf')
            # LSA
            else:
                if np.isnan(df['confidence_lsa'].get(0)):
                    raise Exception(f'Necessaria soglia per modello lsa')

            # Cluster coherence
            if df['is_cluster'].get(0) and (np.isnan(df['n_cluster'].get(0)) or df['n_cluster'].get(0) <= 1):
                raise Exception(f'Atteso numero minimo di cluster > 1')

        if df['num_algo'].get(0) == 2:
            if np.isnan(df['confidence_wv'].get(0)):
                raise Exception(f'Necessaria soglia per modello wv')

        if df['num_algo'].get(0) == 3:
            if (np.isnan(df['confidence_tfidf'].get(0)) or (np.isnan(df['confidence_wv'].get(0))) or (np.isnan(df['confidence_lsa'].get(0)))):
                raise Exception(f'Per Ensemble sono necessarie soglie per ogni modello: tfidf, lsa, wv')

    def correctNaN(self,df):

        if np.isnan(df['n_cluster'].get(0)):
            df['n_cluster'] = 0

        if np.isnan(df['n_topics'].get(0)):
            df['n_topics'] = 0

        if not (type(df['wordvec_path'].get(0)) is str):
            if np.isnan(df['wordvec_path'].get(0)):
                df['wordvec_path'] = ''

        if np.isnan(df['bot_version'].get(0)):
            df['bot_version'] = 0
        return(df)