# Tele2 Profit
Simple console app that allows you to quickly sell your Tele2 data.

## Features
* Quick market listing of your Tele2 data
* Bumping up lots that haven't been sold

## Demo
![Imgur demo gif](https://i.imgur.com/xKTTRDS.gif)

## Installation
1. Clone repository
2. Setup virtual environment (optional)  
    2.1. Create **venv** with `python -m venv venv`  
    2.2. Activate by running `venv\Scripts\activate`

## Usage
1. Login with `auth.py`.
**note: access-token saves on your PC _only_ in `./config.json` file** 
2. Run `main.py` and select action.

### Current Tele2 market lot rules:  
##### Gigabytes:
* `Minimum GB amount - 1 GB`
* `Minimum GB price - 15 rub/GB, maximum - 50 rub/GB`
##### Minutes:
* `Minimum minute amount - 50 min`
* `Minimum minute price - 0.8 rub/min, maximum - 2 rub/min`

### Listing lots
Preparing lots is done with this syntax:
`<lot amount> <lot price>`, for example: `60 80` - 60 minutes (or gb) 
will be listed for 80 rub.  
You can shortcut it by just `<lot amount>`, 
for example `68` -  68 minutes (or gb) will be listed with **minimum**
possible price *(in this case 55 rub if minutes, 1020 rub if gb)*.
When done leave blank (just hit enter) and you will jump to next part.

## TODO
* Use refresh token to support longer auth persistence (currently 240 min.)

