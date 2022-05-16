*NOTE: This repo was forked from margaritageleta/slack-export-history.git*

# Export DM conversations from Slack
To do so, follow two steps:

## (1) Clone this repo
`git clone git@github.com:krevlorn/slack-export-history.git`

## (2) Create a Slack App
Go to https://api.slack.com/apps and go straight to `Create New App`. Choose your Workspace and press `Create App`. Then, click on your app and go to `Add features and functionality` -> `Permissions` -> `Scopes` and add the following scopes in `User Token Scopes` (be careful, `User Token Scopes` NOT `Bot Token Scopes`):

+ `channels:history`
+ `channels:read`
+ `groups:history`
+ `groups:read`
+ `im:history`
+ `im:read`
+ `mpim:history`
+ `mpim:read`
+ `users:read`

Then install the app in your workspace (you can go to `OAuth & Permissions` section and press `Reinstall app`), accept the permissions and copy the OAuth Access Token. 


## Run program to download the messages

1. Open a terminal/cmd session and run `python3 slack.py --token COPY_YOUR_OAUTH_TOKEN_HERE`. 
2. Review the warning and choose **ok**.  Note that the *slack_data* folder is placed in the root containing the python script.
3. Choose the conversation type.  Currently DM (im) and multi-person DM (mpim) are supported.
4. Select the conversation to download.
5. Download will be done in 100 message files.  Archive after completion to save and continue exporting more conversations!
