# build-on-telegram-bot
Telegram bot hosted on AWS Lambda using Serverless framework for Build On ASEAN 2020 Hackathon

Bot URL: http://t.me/LambdaTrialBot

Steps to set up serverless and push code to AWS lambda run the bot:

# Install the Serverless Framework
$ npm install serverless -g

# Install the necessary plugins
$ npm install

# Put the bot token received into a file called serverless.yml
Open serverless.yml, then at TELEGRAM_TOKEN: <your_token>, replace <your_token> with your bot's token

# Install AWS CLI
https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

# Obtain AWS CLI session keys and tokens
Log into AWS Educate account, clivk on AWS Account tab, then click on AWS Educate Starter Account
On the vocareum webpage, click on Account Details, then show AWS CLI
Copy the text shown

# Update credentials file
For Windows: By default, credentials file will be located at C:\Users\\<your_user>\\.aws\credentials\n
Open credentials file, paste the text copied previously, then save the file

# Deploy it!
$ serverless deploy

# With the URL returned in the output, configure the Webhook (Only need to do this once)
$ curl -X POST https://<your_url>.amazonaws.com/dev/set_webhook
