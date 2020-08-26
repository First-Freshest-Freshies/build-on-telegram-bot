import json
import telegram
import os
import logging
import boto3
import botocore
import hashlib


input_text = update.message.text

date_time = str(update.message.date)
literacy_score = 1
sentiment_score = 2
google_score = 3

log_dates= [str(update.message.date),"23/02/1999"]
URLs = ['www.news1.com','www.news2.com']
Titles = ['Title of the news1','Title of news2']
Sypnopses= [1,2,3]
AI_inputs = 'Hellllllllllllo this t3xt i5 unrjlaibale'
AI_outputs = 'hello this text is unreliable'

#All above are sample date, basically you can store in string, num and lists.


def dynamo_call(input_text,date_time,literacy_score,sentiment_score,google_score,log_dates,URLs,Titles,Sypnopses,AI_inputs,AI_outputs):

	update = telegram.Update.de_json(json.loads(event.get('body')), bot)
    chat_id = update.message.chat.id
    client = boto3.resource('dynamodb')
    #Not sure if above is already declared in the main body code

	megastring = str(input_text) + str(date_time) + str(literacy_score) + str(sentiment_score) + str(google_score) + str(log_dates) + str(URLs) + str(Titles) + str(Sypnopses) + str(AI_inputs) + str(AI_outputs) + str(chat_id)
	#Creates a megastring from input date used to create unique hash id

	mhasher = hashlib.sha256()
	mhasher.update(megastring.encode('utf-8'))
	hashid = mhasher.hexdigest()#unique hash id produced

	TableName = 'TelegramTable'
	table = client.Table(TableName)

	try:
	    response = table.update_item(
	    Key={'hashid': hashid},
	    UpdateExpression='SET {} = :val1, {} =:val2, {} = :val3, {} = :val4, {} = :val5, {} = :val6, {} = :val7, {} = :val8, {} = :val9, {} = :val10, {} = :val11, {}= :val12'.format('input_text','date_time','literacy_score','sentiment_score','google_score','log_dates','URLs','Titles','Sypnopses','AI_inputs','AI_outputs','chat_id'),
	    ExpressionAttributeValues={":val1": input_text, ":val2": date_time,":val3": literacy_score,":val4": sentiment_score,":val5": google_score,":val6": log_dates,":val7": URLs,":val8": Titles,":val9": Sypnopses,":val10": AI_inputs, ":val11": AI_outputs, ":val12": chat_id}
	    )
	#Stores data in table called 'TelegramTable' if it exists in dynamodb, using the hashid as the main key

	except botocore.exceptions.ClientError as e:

	    if e.response['Error']['Message'] == 'Requested resource not found':
	        createtable = client.create_table(
	            TableName=TableName,
	            KeySchema=[
	                {
	                    'AttributeName': 'hashid',
	                    'KeyType': 'HASH'  # Partition key
	                },
	            ],
	            AttributeDefinitions=[
	                {
	                    'AttributeName': 'hashid',
	                    'AttributeType': 'S'
	                },

	            ],
	            ProvisionedThroughput={
	                'ReadCapacityUnits': 5,
	                'WriteCapacityUnits': 5
	            }
	        )

	        bot.sendMessage(chat_id=chat_id, text = 'New Table has been created, check yor dynamodb')
	    #Creates table 'Telegram Table if it doesn't exist in dynamodb
"""I created only one dynamo call that contains everything, I haven't tested splitting it into 2 yet, and i cant test coz my serverless at home, Soz-aiken"""
