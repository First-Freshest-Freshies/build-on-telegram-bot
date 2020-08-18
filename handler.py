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

def handle_message(message):
    """
    Process a message from Telegram
    """

    # Add in Command Handlers
    if message == '/start':
        response = "Welcome to FactCheck. See /help for a list of commands."
    elif message == '/help':
        response = "Send me 2 sentences to compare semantic textual similarity"
    else:
        response = "This is not a *command*."

    # NOTE: Everything below here is supposed to be ran after checking for proper user input (inside the if else conditionals above)

    # TODO: Literacy and Sentiment Analysis. Returns 2 scores in range(0, 2) RYANNNNN
    literacy_score = literacy_function(raw_data)

    # TODO: Preprocess the user input. Returns processed_user_input 
    processed_data = process_data_function(raw_data)

    # TODO: Implement Web Scraper and call function here on processed_user_input. Returns dictionary of lists.
    webscraper_results = webscraper_function(processed_data)

    # TODO: Feed array in for loop to AI Sagemaker. Returns array of scores in range(0, 2)
    relevance_score_array = []
    for i in range(len(dict['TITLE'])):
        sentence = ' '.join([dict['TITLE'], dict['SYNOPSIS']])
        relevance_score = ai_function(sentence)
        relevance_score_array.append(relevance_score)

    # TODO: Compute Source and Date Scores
    source_score = source_function(dict['URL']) # source_function will iterate through the array of URLs
    data_score = date_function(dict['DATE'])    # date_function will iterate through the array of dates

    # TODO: dynamo call 1 # stores all the scores
    # TODO: dynamo call 2 # store all the AI relevant stuff

    return response

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

