import re 

pattern = re.compile("^^([a-zA-Z0-9]+)_([a-zA-Z0-9]+)$")

def token_cleaning(spacy_nlp,token):
    if pattern.match(token.text):
        return (token.text, token)
    elif token.is_punct:
        return None 
    elif token.text.isspace():
        return None
    elif token.is_stop or (token.lemma_ in spacy_nlp.Defaults.stop_words):
        return None
    elif token.is_digit or token.like_num:                
        return ("valorenumero",token)
    elif token.is_alpha==False:   ## Probably is_punct and is_space are superfluous
        return None        
    else:
        return (token.lemma_,token)
def substitute_synonyms(token,dictSynonyms):
    return (dictSynonyms.get(token[0], token[0]).lower(),token[1])
def stem_token(mytoken,stemmer):
    if mytoken[1].pos_ in ["NOUN","VERB","ADJ"]:
        return stemmer.stem(mytoken[0])
    else:
        return mytoken[0]