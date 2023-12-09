'''
    version_20231109
    Python webex bot for XDR alerts
    Manages Only Sent messages into the bot room
    Manages ngrok tunnel setup
    Manages webex webhook creation and updates
'''
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request as urllib2
import json
import ssl
import re
import requests
from operator import itemgetter
from config import *
from crayons import *
import sys
from alert_card import create_card_content

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
#Dest_Room_ID=''
Dest_Room_ID_List=[]
# USED FOR OFF-LINE DEBUG
debug_flag = True

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # Received message management
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        print(cyan('Webhook triggered',bold=True))
        webhook = json.loads(body)
        print(green('    Retreive message',bold=True))
        result = send_webex_get('https://webexapis.com/v1/messages/{0}'.format(webhook['data']['id']))
        result = json.loads(result)
        if webhook['data']['personEmail'] != bot_email: # to avoid the bot to compute the messages it send to the rooms
            in_message = result.get('text', '').lower()
            in_message = in_message.replace(bot_name.lower(), '')
            print(yellow("Message from a user ( and not from bot ):",bold=True))
            print(cyan(in_message,bold=True))
            if in_message.startswith('help') or in_message.startswith('hello'):
                print(yellow("help received let's reply",bold=True))
                msg = '''**How To Use:**\n- **help**, bring this help; \n- **alert_card**, send alert card to every user 
                \n
                '''     
                for room in Dest_Room_ID_List:
                    send_webex_post("https://webexapis.com/v1/messages",
                                {"roomId": room, "markdown": msg})
            elif in_message.startswith('ping'):
                print(yellow("let\'s reply to this ping",bold=True))
                for room in Dest_Room_ID_List:
                    send_webex_post("https://webexapis.com/v1/messages",{"roomId": room, "markdown": "*PONG !*"}  ) 
            elif in_message.startswith('alert_card'):
                print(yellow("alert",bold=True))
                alert_message="Suspicious Activity Detected"
                cards_content=create_card_content(alert_message)
                for room in Dest_Room_ID_List:
                    load_alert_card_and_send_it(cards_content,room)                                
            else:
                for room in Dest_Room_ID_List:
                    send_webex_post("https://webexapis.com/v1/messages",
                                {"roomId": room, "markdown": "*I don't understand this*"})
        else:
            # the bot doesn't compute the message it send
            print(cyan('This is a reply sent by BOT itself. Don t handle it',bold=True))
        return "true"
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts=False):
    if type(data) == 'str':
        return data.encode('utf-8')
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.items()
        }
    return data

def get_bot_room_id(BOT_ACCESS_TOKEN):
    URL = 'https://webexapis.com/v1/people/me'
    headers = {
        "Authorization": "Bearer "+BOT_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }    
    the_id=requests.get(URL, headers=headers).json().get('id')
    print('bot room id : ',red(f'{the_id}',bold=True))
    return(the_id)
    
def send_webex_get(url):
    request = urllib2.Request(url,
                              headers={"Accept": "application/json",
                                       "Content-Type": "application/json"})
    request.add_header("Authorization", "Bearer " + bearer)
    contents = urllib2.urlopen(request, context=ctx).read()
    return contents

def send_webex_post(url, data):
    request = urllib2.Request(url, json.dumps(data).encode('utf-8'),
                              headers={"Accept": "application/json",
                                       "Content-Type": "application/json"})
    request.add_header("Authorization", "Bearer " + bearer)
    contents = urllib2.urlopen(request, context=ctx).read()
    return contents
    
def load_alert_card_and_send_it(cards_content,Dest_Room_ID):
    headers = {'Authorization': 'Bearer ' + bearer,
               'Content-type': 'application/json;charset=utf-8'}
    print(cyan(cards_content))
    attachment={
    "roomId": Dest_Room_ID,
    "markdown": "!  XDR ALERT !",
    "attachments": cards_content
    }
    response = requests.post("https://webexapis.com/v1/messages", json=attachment,headers=headers)
    if response.status_code == 200:
        # Great your message was posted!
        #message_id = response.json['id']
        #message_text = response.json['text']
        print("New message created")
        #print(message_text)
        print("====================")
        print(response)
    else:
        # Oops something went wrong...  Better do something about it.
        print(response.status_code, response.text)    
    
def webex_print(header, message):
    global investigation_report
    if debug_flag:
        print(header + message.replace('\n', ''))
    investigation_report.append(header + message)
    return

def delete_webhook(webhook_id):

    url = "https://webexapis.com/v1/webhooks/" + webhook_id

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + bearer
    }

    requests.request("DELETE", url, headers=headers, data=payload)

def add_webhook():
    print("New Webhook Name: {}".format(webhook['name'].encode('utf8')))
    print("New Webhook Url: {}".format(webhook['targetUrl']))    
    url = "https://webexapis.com/v1/webhooks"
    payload = "{\"name\": \"" + webhook_name + "\",\"targetUrl\": \"" + webhook_url + "\",\"resource\": \"messages\",\"event\": \"created\"}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    
def create_webhook(webhook_name,webhook_url):
    webhook_name=str(webhook_name.encode('utf8'))
    print(f"        New Webhook Name: {webhook_name}")
    print(f"        New Webhook Url: {webhook_url}")    
    url = "https://webexapis.com/v1/webhooks"
    payload = "{\"name\": \"" + webhook_name + "\",\"targetUrl\": \"" + webhook_url + "\",\"resource\": \"messages\",\"event\": \"created\"}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print('         ',green(response,bold=True))


def update_webhook():

    url = "https://webexapis.com/v1/webhooks"
    payload = "{\"name\": \"" + webhook_name + "\",\"targetUrl\": \"" + webhook_url + "\",\"status\": \"active\"}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer
    }

    requests.request("PUT", url, headers=headers, data=payload)

        
def get_bot_status():
    url = "https://webexapis.com/v1/rooms"
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + bearer
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json_loads_byteified(response.text)
    print(yellow("Bot is currently member of the following Webex Rooms:",bold=True))
    print()
    room_choices=[]
    index=0
    global Dest_Room_ID_List
    if 'items' in data:
        for room in data['items']:
            print(green(f"{index}    ID: {room['title']}",bold=True))
            Dest_Room_ID_List.append(room['id'])
            room_choices.append(room['title']+';'+room['id'])
            index+=1
    print()       
    url = "https://webexapis.com/v1/webhooks"
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json_loads_byteified(response.text)
    print(green("Bot is currently configured with webhooks:",bold=True))
    global Dest_Room_ID    
    Dest_Room_ID=get_bot_room_id(bearer)    
    if 'items' in data:
        for webhook in data['items']:
            print(" => ID: {}".format(webhook['id']))
            #print("     Name: {}".format(webhook['name'].encode('utf8')))
            webhook_name1=str(webhook['name'].encode('utf8'))
            if "'" in webhook_name1:
                webhook_name1=webhook_name1.split("'")[1]
            print("     Existing Webhook Name: {}".format(webhook_name1))
            print("     Existing Webhook Url: {}".format(webhook['targetUrl']))
            print(green("     Status: {}".format(webhook['status']),bold=True))
            print(cyan(f"     Bot Room ID : {Dest_Room_ID}",bold=True))
            print("     WebHook Name from config.py : {}".format(webhook_name))
            if webhook_name1 != webhook_name:
                print("    === REMOVING WEBHOOK ===")
                delete_webhook(webhook['id'])
                print("    === REMOVED ===")
            if webhook['status'] != 'active':
                print("    === UPDATING WEBHOOK STATUS ===")
                update_webhook()
                print("    === STATUS UPDATED ===")
            if (webhook['targetUrl'] != webhook_url):
                print("    === NEED TO UPDATE WEBHOOK ===")
                delete_webhook(webhook['id'])
                print("    === OLD WEBHOOK REMOVED ===")
                print("    === ADDING NEW WEBHOOK ===")
                #add_webhook()
                create_webhook(webhook_name,webhook_url)
                print("    === NEW WEBHOOK ADDED ===")
                
        if len(data['items']) == 0:
            print("    === NO WEBHOOKS DETECTED - CREATE NEW WEBHOOK===")
            create_webhook(webhook_name,webhook_url)
            print(green(f"     Bot Room ID : {Dest_Room_ID}",bold=True))            
            print("    === NEW WEBHOOK ADDED  ===")  
def main():
    print() 
    print(white(f'==== Webex Bot version : {version} ====',bold=True))
    print()
    global webhook_url
    if use_ngrok:
        print("-- Starting up NGROK Tunnel...")
        # create the tunneling via ngrok
        ngrok.set_auth_token(ngrok_token)
        ngrok_tunnel = ngrok.connect(web_server_listening_port)
        webhook_url  = ngrok_tunnel.public_url   
        print()
        print(cyan(f'- OK NGROK URL is : {webhook_url}',bold=True))  
        print() 
    else:
        print(yellow('-We use don t use NGROK, but the Bot public URL is : {webhook_url} ',bold=True),blue(f' {webhook_url} ',bold=True))
        if webhook_url=="":
            print(red(' You must assign an URL value to the [ webhook_url ] variable in ( config.py ) file first !',bold=True))
            sys.exit()
    print()
    get_bot_status()
    print(yellow("Bot Ready for listening to messages in Bot Room, the Web Server listens on local Port 3000. Ready",bold=True))
    print()
    print(green("Contact the bot in it's room and test with a ping message ",bold=True))
    httpd = HTTPServer(('localhost', 3000), SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__== "__main__":
    main()
