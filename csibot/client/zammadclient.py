from urllib.parse import urljoin
import requests
import json
import logging

class Zammadclient:
    
    def __init__(self):
        self.log = logging.Logger('default log', level=logging.DEBUG)
    def get_article(self, url):
        resp = requests.get(url, headers={'Authorization':'Token token=wjJKFwWzKvUbr09OQANsieDYzJOEplBYiXCCIZNRSYexCYm1GBo0skn39W4mHf8U'})
        if resp.status_code != 200:
            self.log.error("Errore Chiamata Zammad Status:{}".format(resp.status_code))
            self.log.error("Errore Chiamata Zammad Response:{}".format(resp.text))
            return "errore chiamata zammad"
        else:
            return list(resp.json()['assets']['KnowledgeBaseAnswerTranslationContent'].values())[0]['body']
    
