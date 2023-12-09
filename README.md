# XDR ALERT WEBEX BOT ( Part 1 )

This project is about creating a webex bot dedicated to XDR Alerts. The goals is to use this bot to manage alerts sent by XDR. This is about sending Alerts and Manage Security Operators Selected actions.

XDR alerts are supposed to be sent to a list of Security Operators. Make them know that there is a Security issue within the company, and make them able to take actions from formulars displayed in the alerts.

This project mixes two other projects together which are :

- [Webex_Team_Chat_Bot_Python](https://github.com/pcardotatgit/Webex_Team_Chat_Bot_Python)
- [webex_for_xdr_part-2_alert_cards_examples](https://github.com/pcardotatgit/webex_for_xdr_part-2_alert_cards_examples)

Actually the Webex chat bot in this project had been improved compare to the **Webex_Team_Chat_Bot_Python** project.

This new version of the webex bot manages for you the **ngrok** setup if you decide to use ngork to expose your bot into the INTERNET. And if so the bot is able to automatically update the Bot Webhook with the ngrok public url. Second, this new version of the bot is able to automatically list the room IDs of the Webex users who contacted it. The goal here is to send alerts to every user the is connected to. 

Every connected user will receive the same alerts. Then everyone will be aware of a new alert. And Second every action or query sent by any user will be seen by every user. Thru this way the Bot acts as some kind of logging systems that collect and gather history of all alerts and Security Operator activity.

The main thing you will learn in this chapter is to how create and use Webex Bot Webhook. How webhook can be used to track messages sent into the Bot Webex Room, and how the bot logic can send back into the room messages that will depends on what was originally sent into the room.

# Installation

## Prerequisit

You must have created a webex bot first. If your bot is located into your laptop then use **ngork** to make it available on the INTERNET.
This requires you to have an ngrok account with a valid ngro authentication token. The free ngrok tier gives you that.

Have a look to the instructions here for that [Create a webex bot](https://github.com/pcardotatgit/Webex_Team_Chat_Bot_Python)

## Step 1. Create a working directory

Create a working directory into your laptop. Open a terminal CMD window into it. Name It XDR_BOT for example.

## Step 2. Copy the code into your laptop

The Download ZIP Method

The easiest way for anyone not familiar with git is to copy the ZIP package available for you in this page. Click on the Code button on the top right of this page. And then click on Download ZIP.

Unzip the zip file into your working directory.

The "git clone" method with git client

And here under for those of you who are familiar with Github.

You must have a git client installed into your laptop. Then you can type the following command from a terminal console opened into your working directory.

    git clone https://github.com/pcardotatgit/webex_for_xdr_part-3_webhook_bot.git

## Step 3. Go to the code subfolder

Once the code unzipped into your laptop, then Go to the code subfolder.

## Step 4. Create a Python virtual environment

It is still a best practice to create a python virtual environment. Thank to this you will create a dedicated package with requested modules for this application.

### Create a virtual environment on Windows

    python -m venv venv 

### Create a virtual environment on Linux or Mac

    python3 -m venv venv

Depending on the python version you installed into your Mac you might have to type either 

- python -m venv venv

or maybe

- python3 -m venv venv    : python3 for python version 3.x  

or maybe 

- python3.9 -m venv venv  : if you use the 3.9 python version

And then move to the next step : Activate the virtual environment.

### Activate the virtual environment on Windows

    venv\Scripts\activate

### Activate the virtual environment on Linux or Mac

    source venv/bin/activate    

## Step 5. Install needed python modules

You can install them with the following 2 commands one after the other ( Windows / Mac / Linux ):

The following command might be required if your python version is old.

    python -m pip install --upgrade pip   

Then install required python modules ( Windows / Mac / Linux )

    pip install -r requirements.txt

## Edit config.py and Set the initialization variables

Edit the **config.py** script and set correctly the following variables

- bot_email = "the mail you gave to your bot when you created it"
- bot_name = "the name you gave to your bot when you created it"
- bearer = "the brearer token that was generated when when you created your bot"
- webhook_url = 'https//bot_public_url' . Set the bot public URL if you don't use ngrok. If you use ngrok you can keep this empty
- webhook_name = 'bot_WebHook'  any meaningful name for your bot
- use_ngrok=0 # 1 = Yes we use NGROK locally. 0 = No we expose the bot to internet trhu port forwarding
- ngrok_token = 'Your ngrok token'

You are ready to run the bot

## Start the Bot

    python webex_bot.py

You should see the bot starting. The bot manages automatically the bot webhook creation or update.

Wait for the messages that tells you that the bot is ready

## Test the bot

As a Webex user, before starting the bot, in webex find it thanks to it's mail and send it any message.
Thanks to this the bot will know you and then you will receive every alert it send.

Any Webex user who want to interact with the bot has to do exactly the same.

Once a Webex Space is created between you and the bot, then send the **ping** message to the bot. The expected result is a **PONG** answer received by all connected users.

Then you can type **help**. The bot will share with you some guide lines about commands to use.

If you send **alert_card** then you shoud see the alert adaptive card we created thank to the **4-send-advanced_dynamic_alert_message_to_room_example.py script** in the **webex_for_xdr_part-2_alert_cards_examples** project.

The **alert_card.py** script is the script that generated the adptative card JSON data. It is inspired from the 4-send-advanced_dynamic_alert_message_to_room_example.py script of the **../webex_for_xdr_part-2_alert_cards_examples** project. In this current project this script is specialized in the adaptive card creation. It is used as a resources by the main script **webex_bot.py**

Messages sent to the bot room are computed by the **def do_POST(self):** function into the **webex_bot.py** script.
Every time a message is sent to the bot room, this catched by the **def do_POST(self):** function.

As you will see into this function we just do some string comparision ( startwith ) into an if statement in order to trigger different specific actions. A default branch catch messages that are not understood by the bot.

We do a check of user mail in order to avoid the script to compute any message sent by the bot itself. This would create a message computing loop.

If you send the **alert_card** message to the bot then this one display the XDR Alert adaptive card we already work on in the previous labs. But you will see that nothing happen if you select objects to block or isolate into the formular.

This is a normal behavior.

## This Bot is not able to collect submitted data !

Nothing happen if you select objects to block or isolate into the formular. The reason of this is because the webhook we created is only dedicated to manage messages.

If you have a look to the **create_webhook()** function into the **webex_bot.py"" script the webhook **resource = messages**.

In order to handle variable submitted into the formular we need a **resource=attachmentActions** webhook.

## Delete Webhooks

Time to time as you do a lot of test, webhooks might mess up.

Then us the **delete_webhooks.py** script in order to delete all webhooks attached to the bot

    python delete_webhooks.py
    
## Where to go Next ? : Manage submitted fomular data

Go to the next chapter in order to learn how to handle the data we select into the formular

[webex_for_xdr_part-4_webhook_bot_that_handle_submitted_data](https://github.com/pcardotatgit/webex_for_xdr_part-4_webhook_bot_that_handle_submitted_data)

Go to the previous chapter 

[webex_for_xdr_part-2_alert_cards_examples](https://github.com/pcardotatgit/webex_for_xdr_part-2_alert_cards_examples)