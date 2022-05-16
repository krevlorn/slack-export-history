import os
import json
import shutil
import requests
import argparse

from datetime import datetime
from pick import pick

def auth(token):
    try: 
        r = requests.post('https://slack.com/api/auth.test', data = {'token': token})
        r.raise_for_status()

        data = r.json()
        
        if data['ok']:
            print(f"Successfully authenticated for team {data['team']} (ID {data['team_id']}) and user {data['user']} (ID {data['user_id']})")
            return True
        else:
            print(f"Something went wrong. Error: {data['error']}")
            return False

    except Exception as e:
        print(f'Something went wrong. Status code: {r.status_code}')
        return False

def retrieve_data(endpoint, payload, headers):
    try: 
        print(f"Retriving data for endpoint {endpoint}")
        r = requests.get(f'https://slack.com/api/{endpoint}', params = payload, headers = headers)
        r.raise_for_status()
        print(f'Data retrieved OK. Status code: {r.status_code}')

        data =  r.json()
        
        if data['ok']:
            with open(f'{endpoint}.json', 'w') as f:
                json.dump(data, f)
        else:
            print(f"Error: {data['error']}")

    except Exception as e:
        print(f'Something went wrong. Status code: {r.status_code}')

def fetch_users():
    with open('users.list.json') as f:
        users_dump = json.loads(f.read())
        users = {}
        for member in users_dump['members']:
            # if not member['is_bot']:
            users[member['id']] = {
                'name': member['name'], 
                'real_name': member['profile']['real_name']
            }
    return users

def fetch_conversations():
    with open('conversations.list.json') as f:
        conversations_dump = json.loads(f.read())
        conversations_dict = {}
        conversations_list = []
        for conver in conversations_dump['channels']:
            if conver['is_im']:
                conversations_dict[conver['id']] = {
                    'user_id': conver['user'], 
                    'user_name': users[conver['user']]['name']
                }

            elif conver['is_mpim']:
                conversations_dict[conver['id']] = {
                    'user_id': conver['id'], 
                    'user_name': conver['name']
                }
                
            conversations_list.append(conver['id'])

        return (conversations_dict, conversations_list)

        '''
        if conver['is_mpim']:
            channels[conver['id']] = {
                'creator': conver['creator'], 
            }
        if conver['is_channel']:
            channels[conver['id']] = {
                'creator': conver['creator'], 
                'is_private': conver['is_private']
            }
        '''

def fetch_conv_types():
    type_list = ['im', 'mpim']

    option, index = pick(type_list, 'Select the conversation type')

    return type_list[index]

def alert_user():
    option_list = ['ok', 'cancel']

    option, index = pick(option_list, 'ALERT: This program will replace all contents of the slack_data folder. ' + 
    '\nPlease make sure to back up previously downloaded export history, ' + 
    '\nthen press ok to continue or cancel to quit the program.')

    if option_list[index] == 'cancel':
        quit()

def fetch_message_data(payload, headers):
    r = data = None
    back = 0

    try: 
        # while there are older messages
        while r == None or data['has_more']:
            # and it is not the first request
            if r != None:
                # change the 'latest' argument to fetch older messages
                payload['latest'] = data['messages'][-1]['ts'] 
            
            r = requests.get(f'https://slack.com/api/conversations.history', params = payload, headers = headers)
            r.raise_for_status()
            print(f'Data retrieved OK. Status code: {r.status_code}')

            data =  r.json()
            if data['ok']:
                messages = []
                for message in data['messages']:
                    messages.append({
                    'user_id': message['user'], 
                    'user_name': users[message['user']]['name'],
                    'text': message['text'],
                    'ts': message['ts'],
                    'date': datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S')
                })
                with open(f"chat_{payload['username']}_({back}-{back + len(data['messages']) - 1}).json", 'w') as f:
                    json.dump(messages, f)
                back += len(data['messages'])
            else:
                print(f"Error: {data['error']}")

    except Exception as e:
        print(e)
        print(f'Something went wrong. Status code: {r.status_code}')

if __name__ == "__main__":

    print('Welcome to Slack Export Manager!')

    # Define parser to pass OAuth token
    parser = argparse.ArgumentParser(description = 'Export Slack history')

    parser.add_argument('--token', required = True, help = "OAuth Access Token")
    parser.add_argument('--oldest', required = False, help = "UNIX Time Stamp of Oldest Entry")
    parser.add_argument('--latest', required = False, help = "UNIX Time Stamp of Newest Entry")
    args = parser.parse_args()

    # Do Auth Test to check user
    if auth(args.token):
        # Define the payload to do requests at Slack API
        PAYLOAD = {
            'oldest': args.oldest ,
            'latest': args.latest
        }

        HEADER = {
            'Authorization': 'Bearer ' + args.token
        }

        # Alert user of overwriting data
        alert_user()

        # Create a directory where to store the data
        dir = 'slack-data'
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        os.chdir(dir) 

        # Retrieve users and conversations lists
        retrieve_data('users.list', PAYLOAD, HEADER)  
        users = fetch_users()

        # conv_type = fetch_conv_types()

        PAYLOAD['types'] = fetch_conv_types()
        retrieve_data('conversations.list', PAYLOAD, HEADER)

        # Select chat to export
        title = 'Please select the conversation to export: '
        convers, options = fetch_conversations()

        option, index = pick([f"Chat {option} with {convers[option]['user_name']}" for option in options], title)
        PAYLOAD['channel'] = options[index]
        PAYLOAD['username'] = convers[options[index]]['user_name']

        # Export chat
        print('\nPreparing to export chat ...\n')
        fetch_message_data(PAYLOAD, HEADER)

    else:
        # Auth fail
        pass
        
