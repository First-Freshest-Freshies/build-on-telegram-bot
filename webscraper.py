from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import boto3
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

nltk.download('stopwords')
nltk.download('punkt')

# Testing purposes
# raw = {"validity": True, "text": "Just now, the US CNBC website reported that several US Growler electronic warplanes were mysteriously attacked when they flew to the South China Sea again. These warplanes were all out of control midway, but these warplanes were out of control for only a few seconds. Then the US military ordered the request. All fighters over the South China Sea withdrew."}

def process_data_function(raw_data):
    # Break up into 2-sentence-chunks
    if raw_data["validity"] == True:
        raw_sentences = nltk.sent_tokenize(raw_data["text"])
        print(raw_sentences)
    sentence_chunk_search_query_tuples = []
    for i in range(len(raw_sentences) - 1):
        sentence_chunk = raw_sentences[i] + " " + raw_sentences[i + 1]
        comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
        # TODO: Run each chunk through AWS comprehend sentiment analysis (to check negation)
        # comprehend.detect_sentiment(Text=sentence_chunk, LanguageCode='en')
        keywords_dict = comprehend.detect_key_phrases(Text=sentence_chunk, LanguageCode='en')
        keywords_list = keywords_dict["KeyPhrases"]
        keywords_list.sort(key = lambda x:x["Score"],reverse = True)
        #print(keywords_list)
        aws_keyphrases = ""
        aws_keywords = []
        for dict in keywords_list:
            aws_keyphrases += dict["Text"].lower() + " "
        aws_keywords = aws_keyphrases.split()
        stop_words = set(stopwords.words('english'))
        filtered_words = [w for w in aws_keywords if not w in stop_words]
        search_query = " ".join(filtered_words)
        sentence_chunk_search_query_tuples.append((sentence_chunk, search_query))
    return sentence_chunk_search_query_tuples

def webscraper_function(raw_data):
    processed_data = process_data_function(raw_data)
    google_search_list = []
    for (sentence_chunk, search_query) in processed_data:
        preprocessed_query = "\"" + search_query + "\""
        url = 'https://encrypted.google.com/search?q={}&tbs=cdr:1,cd_min:1/1/0'.format(preprocessed_query)
        # print(url + '\n')
        # print('#############################################\n')

        # Open a HTMLSession to execute JavaScript code to fully render webpage
        with HTMLSession() as session:
            r = session.get(url)
            r.html.render(sleep=1)

        # Input this HTML Object into BeautifulSoup to parse and access individual tags and their text content
        soup = BeautifulSoup(r.html.raw_html, 'html.parser')

        center = soup.find('div', id='center_col')

        articles = center.find_all('div', class_='rc')

        temp_dict = {}
        temp_dict["sentence_chunk"] = sentence_chunk
        temp_dict["url"] = []
        temp_dict["title"] = []
        temp_dict["synopsis"] = []
        temp_dict["date"] = []

        for article in articles:
            header = article.find('div', class_='r').find('a', href=True)
            link = header['href']
            title = header.find('h3').text
            title = re.sub('\s\.\.\.$', '', title)

            try:
                synopsis = article.find('span', class_='st').text

                if re.search('^[a-zA-Z]+\s\d+,\s\d+', synopsis):
                    date = re.findall('^[a-zA-Z]+\s\d+,\s\d+', synopsis)[0]
                    synopsis = re.sub('^[a-zA-Z]+\s\d+,\s\d+ - ', '', synopsis)
                    synopsis = re.sub('\s\.\.\.$', '', synopsis)
                elif re.search('^\d+\s[a-zA-Z]+\s[a-zA-Z]+', synopsis):
                    date = re.findall('^\d+\s[a-zA-Z]+\s[a-zA-Z]+', synopsis)[0]
                    synopsis = re.sub('^\d+\s[a-zA-Z]+\s[a-zA-Z]+ - ', '', synopsis)
                    synopsis = re.sub('\s\.\.\.$', '', synopsis)
            except:
                synopsis = article.find('div', class_='P1usbc').text    # Factchecker's 'synopsis' (Claim + Claim by who + Factcheck done by who + Rating of truthfulness)
                date = "Factchecker"    # Indicates that this is a factchecker response
            temp_dict["url"].append(link)
            temp_dict["title"].append(title)
            if len(synopsis) > 0:
                temp_dict["synopsis"].append(synopsis)
            temp_dict["date"].append(date)
        google_search_list.append(temp_dict)

    # Testing purposes
    # for dictionary in google_search_list:
    #     for key, value in dictionary.items():
    #         print(key)
    #         print(value)

    return google_search_list
        # TODO: pass up 1 or 2 credible sources to main telegram script

# webscraper_function(raw)
