# telegram-cli
telegram-cli is a telegram command line interface written in python with curses.

## Requirements
- telethon python package
- python 3.7

## Usage 
First you should set your telegram `app api_id` and `app api_hash` in `auth.txt`. 

You can get tham [here](https://my.telegram.org/apps)

You should have something like this:

./auth.txt
```
234876
23csbcxaasd34azxcnasd51mxzcmzse4
```

---
Than clone the repo and run in shell

`pipenv install`  or `pip install telethon`

`pipenv run python3 app.py` or `python3 app.py`


_okay i'm bad in writing text_
## TODO
- message reply
- insert mode
- show images (in ascii & external viewer)
- download files
- new message highlighting
- auth mechanism
- redrawing everything when window resize
- search messages/chats
- scrolling