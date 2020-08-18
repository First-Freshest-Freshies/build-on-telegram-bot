# NOTE: ignore the comments related to imports and PyTorch

# There's an import error here. unzip_requirements does not import
# Is it need to download serverless-python-dependencies?
'''
try:
    import unzip_requirements
except ImportError:
    pass
'''
import os
import sys
import json

# import torch  # cant import unzip_requirements, thus this also doesn't work
#import numpy as np
#from transformers import *


# Including ./vendored into system path (for importing own dependencies)
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

# Import can only happen after adding ./vendored to system path
import requests
from transformers import *  # attempting to package this tgt with vendored folder
import numpy as np          # note that numpy shld be compiled on Linux, not MacOS

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

# NOTE: run function is essentially a wrapper for the receive_message, handle_message and send_message functions
def run(event, context):
    """ Receive a message, handle it, and send a response """
    try:
        data = json.loads(event["body"])            # Converts incoming json to dictionary
        message, chat_id = receive_message(data)    # Extract message and chat_id from dictionary
        response = handle_message(message)          # Process message and format a response
        send_message(response, chat_id)             # Post json back to Telegram Server to send to user via bot
    except Exception as e:
        print(e)

    return {"statusCode": 200}                      # to prevent infinite triggering...

def receive_message(data):
    """ Extract message text and chat_id from 'json dictionary' data """
    try:
        message = str(data["message"]["text"])
        chat_id = data["message"]["chat"]["id"]
        return message, chat_id
    except Exception as e:
        print(e)
        return (None, None)

def send_message(message, chat_id):
    """
    Send a message to the Telegram chat defined by chat_id in Markdown parse_mode
    """
    data = {"text": message.encode("utf8"), "chat_id": chat_id, "parse_mode": "Markdown"}
    url = BASE_URL + "/sendMessage"

    try:
        requests.post(url, data)
    except Exception as e:
        print(e)



def handle_message(message):
    """
    Process a message from Telegram
    """

    # Command Responses (kwok done)
    start_message = \
    "I am the @ReliabilityBot! Ever wondered if an article that a friend or relative has sent you can be trusted? \
    Just copy and paste it into me and I will tell you what I think of it!\n\n\
    To find out more about how I work, type /aboutReliabilityBot"

    help_message = \
    "Simply copy and paste a message or article you recieve for me to analyse!\n\n\
    I have also found some useful tips to help you to better judge the reliability information in future:\n\
    - https://www.gov.sg/article/singapores-fight-against-fake-news-what-you-can-do \n\
    - https://sure.nlb.gov.sg/blog/fake-news/fn0006 \n\
    - https://www.betterinternet.sg/-/media/MLC/Files/SID-2018/Quick-Tips/1_How-to-spot-Fake-News_Tipsheet.pdf"

    aboutReliabilityBot_message = \
    "Judgement Criteria:\n\
    1. /aboutLiteracy - This shows how sophisticated the piece of text is. More sophisticated articles are more likely to be reliable!\n\n\
    2. /aboutSentiment - Indication of the text's overall objectivity. Balanced and unbiased articles are be more reliable!\n\n\
    3. /aboutGoogleSearch - This is an estimate of how well supported the text is by online articles. Greater corroboration = higher reliability!"

    aboutLiteracy_message = \
    "Literacy Score:\n\n\
    I will be using a spell checker and a reading level estimator. \
    The spell checker would flag misspelled words and produce a spelling score. \
    The reading level estimator is an AI that estimates the age required to understand the text.\
    I will then combine both results to determine the Literacy Score."

    aboutSentiment_message = \
    "Sentiment Score:\n\n \
    I will ask my friend AWS Comprehend, another AI that uses Machine Learning and Natural Language Processing for sentiment analysis. \
    Comprehend usually organises customer feedback on online shopping sites, but this time, she will tell me the sentiment of your input. \
    A confidence score of Positive, Negative, Neutral, and Mixed will be given. \
    I will then combine the Neutral and Mixed confidence to produce the Sentiment Score. Thanks Comprehend!!"

    aboutGoogleSearch_message = \
    "Google Search Score:\n\n\
    I determine this score in a few steps. \
    Firstly, I will conduct a Google Search using your input. \
    Next, another unamed AI will help me to compare the results against your input to determine the extent of corroboration. \
    In addition, I will determine the reliability and currency of the results based on its URL and date. \
    Finally, after I consider all the factors, I will give you the Google Search Score."

    invalid_command = \
    "Invalid command. Valid commands are /start /help /aboutReliabilityBot /aboutLiteracy /aboutSentiment /aboutGoogleSearch"

    # Command Handlers (kwok done)
    if message == "/start":
        return start_message
    elif message == "/help":
        return help_message
    elif message == "/aboutReliabilityBot":
        return aboutReliabilityBot_message
    elif message == "/aboutLiteracy":
        return aboutLiteracy_message
    elif message == "/aboutSentiment":
        return aboutSentiment_message
    elif message == "/aboutGoogleSearch":
        return aboutGoogleSearch_message
    elif message[0] == "/":
        return invalid_command

    # Validation Check (kwok done)
    valid = validation(message)
    if not valid["validity"]:
        return valid["text"]

    # NOTE: Everything below here is supposed to be ran after checking for proper user input (inside the if else conditionals above)

    # Literacy and Sentiment Analysis. Returns dictionary {"spelling", "reading", "literacy", "sentiment"} (kwok done)
    lit_sent_dic = get_lit_sent_score(raw_data)

    # TODO: Preprocess the user input. Returns processed_user_input 
    processed_data = process_data_function(raw_data)

    # TODO: Implement Web Scraper and call function here on processed_user_input. Returns dictionary of lists.
    webscraper_results = webscraper_function(processed_data)

    # TODO: Feed array in for loop to AI Sagemaker. Returns array of scores in range(0, 2)
    # (kwok asks: possible to abstract out as a function? declutter the "main" function, put into main_functions.py, or send directly to ai_function)
    relevance_score_array = []
    for i in range(len(web_scrape_dic['TITLE'])):
        sentence = ' '.join([web_scrape_dic['TITLE'], web_scrape_dic['SYNOPSIS']])
        relevance_score = ai_function(sentence)
        relevance_score_array.append(relevance_score)
    web_scrape_dic["relevance_score"] = web_scrape_dic #(kwok added this)

    # Compute Source and Date Scores (kwok done)
    web_scrape_dic = compute_url_date_score(web_scrape_dic) # iterate through url+date, add 2 keys url_score and date_score

    # TODO: Combine Source/Date/Relevance Scores + lit+sent scores into 1 dic (kwok done)
    compiled_dic = compile_scores(lit_sent_dic, web_scrape_dic) # adds "indiv_result_score" and "google"

    # TODO: dynamo call 1 # stores all the scores
    # TODO: dynamo call 2 # store all the AI relevant stuff


    # Craft response to user (kwok done)
    response = create_reply(compiled_dic)
    return response

        
