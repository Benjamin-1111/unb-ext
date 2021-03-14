
<h4 align="center">An extension for the unbeliva Discord Bot, made with pybeliva and discord.py slash ext </h4>

<p align="center">
  <a href="https://github.com/Benjamin-1111/unb-ext#description">
    <img src="https://img.shields.io/badge/description-green.svg"
         alt="description">
  </a>
    <a href="https://github.com/Benjamin-1111/unb-ext#installation">
    <img src="https://img.shields.io/badge/installation-green.svg"
         alt="installation">
    </a>
    <a href="https://github.com/Benjamin-1111/unb-ext#usage">
    <img src="https://img.shields.io/badge/usage-green.svg"
         alt="usage">
    </a>
    <a href="https://github.com/Benjamin-1111/unb-ext#license">
    <img src="https://img.shields.io/badge/license-green.svg"
         alt="license">
    </a>
</p>

---

## Description
This is an ext for the [unbeliva boat](https://unbelievaboat.com/) made with the [unb API](https://unbelievaboat.com/api/docs).
I've used [pybeliva](https://pypi.org/project/pybelieva/), [discord.py](https://pypi.org/project/discord.py/) and the [slash ext](https://pypi.org/project/discord-py-slash-command/)



## Requirements

- python 3.7+
- discord.py
- discord-py-slash-command
- pybeliva

## Installation
### modules:
- discord.py: 
```python
pip install discord.py
```

- discord-py-slash-command 1.0.9.5 
```py
pip install discord-py-slash-command
```

 - pybelieva
 ```py
 pip install pybelieva
 ```
### Setup:
- Download the SourceCode
- Fill in the Settings file with bot token and unbeliva Token
- Invite the Bot
- Run the Bot

## Authorization
### Discord API Token:
- Go to the [Discord Developer Portal](discord.com/developers/applications)
- Login
- Klick on 'New Application'
- Fill In the Bot name
(- Choose a Team, default is your Personal)
- Go to the 'Bot' tab in your application
- Klick on 'Add Bot'
- Klick on 'Yes, do it!'
- Activate *Presence Intent* and *Server Members Intent*
- Copy Token (Don't show this Token to anyone!!)
- Paste the Token in the settings file

### Unbeliva Token:
- Go to [Applications](https://unbelievaboat.com/applications) 
- Login if required
- Paste in your Bot's client ID (you can find it in the Discord Developer Portal)
- Copy Token and paste it into the settings file
- authorize the app via the link

## Usage
### User commands (slash commands)
```
 /shop buy item: Mond amount: 1
                 Mars
                 Saturn
                 Jupiter
 /lend amount: 100
 ```
### Owner settings (normal commands)
```
 -setlog <channel ID>
```
  creates a new webhook in the new channel and deletes the old one, and the new economy ext log gets logged there (in the main log of unb gets the channel mentioned)
  


## Limits
### Slash limits:

#### __**Slash Commands**__

Slash commands are a new way to make commands right within discord, discord.py will probably not support them as they are lacking features and requires a major rewrite to handle.

Bad command handler:
- No default argument system - the argument isn't passed if you don't pass it making handling harder.
- No Union/Optional system like d.py.
- You can't handle arguments yourself -required to use their parser.
- No way to invoke group commands - you can only invoke the sub-commands.
- No command aliases.

Limitations:
- 15 mins max per command - a token lasts 15 mins.
- Only one message can be hidden (the first one).
- Hidden messages cannot have embeds.
- Without a bot token you can't do much apart from send messages and etc - no API interaction.
- You only get ids for the parameters - if the parameter is a user you only get their ID.
- If using the webhook based integrations you cannot get any other events so you are limited to commands.

If you do want to use them there is a half maintained fork that has support for them (we will not support them here). It's not too hard to look for it. (There is also another repo that has them).

_credits: Zomatree#7757_

### pybeliva limits:
header example:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1595368487253 
```

429 Response Example:
```
{
  "message": "You are being rate limited.",
  "retry_after": 4329
}
```

Global 429 Response Example:
```
{
  "message": "You are being rate limited.",
  "global": true
}
```
_credits: [unbeliva boat API docs](https://unbelievaboat.com/api/docs)_

### discord.py limits (API limits):
```
REST:
        POST Message |  5/5s    | per-channel
      DELETE Message |  5/1s    | per-channel
 PUT/DELETE Reaction |  1/0.25s | per-channel
        PATCH Member |  10/10s  | per-guild
   PATCH Member Nick |  1/1s    | per-guild
      PATCH Username |  2/3600s | per-account
      |All Requests| |  50/1s   | per-account
WS:
     Gateway Connect |   1/5s   | per-account
     Presence Update |   5/60s  | per-session
 |All Sent Messages| | 120/60s  | per-session
 ```
also some header exmp:
```
30001 Maximum number of guilds reached (100)
30002 Maximum of pins reached (50)
30003 Maximums of guild roles reached (250)
30010 Maximum of reactions reached (20)
30013 Maximum of guild channels reached (500)
```
## License
This unbeliva extension is licensed under the MIT license.
