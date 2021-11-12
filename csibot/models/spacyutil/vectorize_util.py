import nltk
import itertools
import spacy
import os
import pandas as pd
import logging
import numpy
from string import punctuation

import spacy
from spacy.lang.it.stop_words import STOP_WORDS



def str_safe(s):
    if s is None:
        return ''
    else:
        return str(s)

def CSV2DataFrame(filepath,sep=";",encoding="utf-8"):
    try:
        df=pd.read_csv(filepath, encoding=encoding,sep=sep)
        df_new=df.replace(numpy.nan, "", regex=True) #remove NAN from dataframe
        return df_new
    except Exception as e:
        logging.error("Error loading resource "+filepath+": \n"+str(e)) 
        raise Exception("Error in the service configuration: "+ str(e)) from None

def loadConfigData(path):
    path=path+"//"
    df_synonyms=CSV2DataFrame(path+"synonyms.csv")
    df_composite_words=CSV2DataFrame(path+"composite-words.csv")
    df_stopwords=CSV2DataFrame(path+"stopwords.csv")
    df_classification=CSV2DataFrame(path+"mail_classified_no_signature_with_replacements.csv")
    return (df_synonyms,df_composite_words,df_stopwords,df_classification)

def SubstituteCompoundWords_vectorized(series, dictionary):

    for word in sorted(dictionary.keys(), key=len, reverse=True):    
        series = series.str.replace(word.lower(),dictionary[word].lower())
    return series
    

def substituteChars_vectorized(df, columnS, columnT, dictionary, deleteColumnS=False):
    """
    SubstituteCompoundWords replace Compund words starting from a dictionary
    :param text: original text
    :param columnS: source column
    :param columnT: target column
    :param dictionary: dictionary of compaund words
    :return: corrected text
    """
    if columnT!=columnS:
        df[columnT]=df[columnS]                                      ## copy the initial column 
    for char in sorted(dictionary.keys(), key=str.lower, reverse=True):    ## apply transformation
        df[columnT] = df[columnT].str.replace(char,dictionary[char])
    if deleteColumnS and columnS!=columnT:                           ## delete original column if requested
        df=df.drop(columns=columnS)
    return df
