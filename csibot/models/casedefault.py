from .base import Base


class CaseDefault(Base):

    def __init__(self, bot=None, synonyms=None, knowledgeBase=None, stopwords=None, compounds=None):

        if bot is not None and knowledgeBase is not None:
            super().__init__(bot, synonyms, knowledgeBase, stopwords, compounds)
        else:
            # Create default idbot
            self.set_n_answers(5)



