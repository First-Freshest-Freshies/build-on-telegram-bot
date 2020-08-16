import json
import telegram
import os
import logging
import boto3


# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}


def configure_telegram():
    """
    Configures the bot with a Telegram Token.

    Returns a bot instance.
    """

    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.error('The TELEGRAM_TOKEN must be set')
        raise NotImplementedError

    return telegram.Bot(TELEGRAM_TOKEN)


def webhook(event, context):
    """
    Runs the Telegram webhook.
    """


    bot = configure_telegram()
    logger.info('Event: {}'.format(event))

    if event.get('httpMethod') == 'POST' and event.get('body'):
        logger.info('Message received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        chat_id = update.message.chat.id

        if update.message.text == '/start':
            text = """Welcome to @CheckFakeNewsBot! Ever wondered if an article that a friend or relative has sent you can be trusted? Just copy and paste it into here and I will tell you what I think of it!\n\nTo find out more about the guidelines of this bot, type /help"""

        elif update.message.text == '/help':
            text = """Judgement criteria:\n1. Literacy - Measured via a spell checker and a reading level estimator. The lower the score, the more spelling mistakes there are/easier it is to read.\n\n2. Sentiment - Measured via AWS Comprehend, an AI that uses machine learning and natural language processing. The lower the score, the more extreme positive/negative sentiments are present\n\n3. Google Search - Measured via an AI by comparing your text with its top 10 google search results. The higher the score, the more reliable the text is."""

        else:
            input = update.message.text
            # Backend score calculation here
            # Placeholder values for scores
            literacy = 68.6
            sentiment = 36.0
            google = 72.0
            text = """Here are your results!\n\nLiteracy score = """ + str(literacy) + """%\nSentiment score = """ + str(sentiment) + """%\nGoogle score = """ + str(google) + """%\n\nThis piece of text does not look professionally written and seems to purposefully trigger strong emotion. However, it appears to be sufficiently supported by credible sources. We recommend that you read this article with a pinch of salt and do further research to fully understand all sides of this story.\n\nHere are some credible links that may be relevant:\n<INSERT URL HERE>\n<INSERT URL HERE>\n\nHere are some useful tips to help you to better judge information in future: https://www.gov.sg/article/singapores-fight-against-fake-news-what-you-can-do"""

        bot.sendMessage(chat_id=chat_id, text=text)
        logger.info('Message sent')

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """

    logger.info('Event: {}'.format(event))
    bot = configure_telegram()
    url = 'https://{}/{}/'.format(
        event.get('headers').get('Host'),
        event.get('requestContext').get('stage'),
    )
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE
