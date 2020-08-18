def get_spelling_score(text):
    """
    Takes in text
    Returns dictionary with "spelling"    
    """
    
    # list pre-processing
    word_lst = []
    start = 0
    for i in range(len(text)):
        if not text[i].isalpha():
            word_lst.append(text[start:i])
            start = i+1
    word_lst = list(set(word_lst))
    word_lst.sort()
    while "" in word_lst:
        word_lst.remove("")
    # import package
    from spellchecker import SpellChecker
    spell = SpellChecker()
    # find those words that may be misspelled
    misspelled = spell.unknown(word_lst)
    # scoring
    score = 1- len(misspelled) / len(word_lst)
    return {"spelling": score}



def get_reading_score(text):
    """
    Takes in text
    Returns dictionary with "reading"    
    """
    
    import textstat
    age = textstat.text_standard(text, float_output = True) + 5
    return {"reading": age/18}



def get_literacy_score(text):
    """
    Takes in text
    Returns dictionary with "spelling", "reading", and "literacy"   
    """
    dic = get_spelling_score(text)
    reading = get_reading_score(text)
    dic.update(reading)
    score = dic["spelling"] * dic["reading"]
    dic["literacy"] = score
    return dic



def get_sentiment_score(text):
    """
    Takes in string of text
    Returns a dictionary of "sentiment"
    """
    import boto3
    comprehend = boto3.client("comprehend")
    response = comprehend.detect_sentiment(Text=paragraph, LanguageCode = "en")
    pos = response["Positive"]
    neg = response["Negative"]
    neu = response["Neutral"]
    mix = response["Mixed"]
    return {"sentiment": neu+mix}



def get_lit_sent_score(text):
    """
    Takes in string of text
    Returns a dictionary of "spelling", "reading", "literacy", and "sentiment"
    """
    dic = get_literacy_score(text)
    sentiment = get_sentiment_score(text)
    dic.update(sentiment)
    return dic


#text = "hello there"
#print(get_literacy_score(text))
