# Tele2 Profit [![Release](https://img.shields.io/github/v/release/raritetmolodoy/tele2-profit?color=black&label=%20)](https://github.com/raritetmolodoy/tele2-profit/releases)

Console application that allows you to quickly sell your Tele2 data on their **Market**



## Disclaimer
_От автора:_  
Я не несу ответственности за ваши номера (если они улетят в бан или еще чего по-хуже).  
Скрипт не делает ничего запрещенного, а лишь "нажимает кнопочки, которые вы могли
бы нажать в их приложении, потратив в 10 (да-да) раз больше времени".  
Скрипт не ворует данные и не каким образом не взаимодействует ни с чем-либо кроме
оффициального (но не публичного) API Tele2.
Если возникли какие-либо проблемы в работе - откройте обсуждение на вкладке Issues и,
если, нашли решение, предложите автору, буду очень признателен. Так как скрипт очень
чувствителен к региону, из которого он запускается, проблемы возникнуть могут, и не факт,
что конкретно ваша проблема вообще решаема (например, старый тариф без поддержки
Маркета и т.п). Спасибо за понимание)


## Features
* Quick market listing of your Tele2 data
* Bumping up lots that haven't been sold
* Asynchronous queries to _Tele2 API_ allow to perform multiple actions simultaneously


## Demo (v1.0.0 on Windows 10)
![imgur demo gif](https://i.imgur.com/xKTTRDS.gif)


## Installation (basic - *Windows x64 only [x32 work in progress]*)
#### Steps:
1. Go to [latest release](https://github.com/raritetmolodoy/tele2-profit/releases/latest)
and download **zip**-archive (tele2-profit@\<version\>.zip)
2. Unarchive wherever you want and run **exe**-files.
3. You are good to go!


## Source installation (advanced - _Any OS_)
#### Steps:
1. Clone repository
2. Setup virtual environment (optional)  
    2.1. Create **venv** with `python -m venv venv`  
    2.2. Activate by running this command (just paste it after previous and hit enter) `venv\Scripts\activate`
3. Install dependencies with `pip install -r requirements.txt`
4. You are also good to go!

#### Command list (Windows):
* `git clone https://github.com/raritetmolodoy/tele2-profit.git`
* `cd tele2-profit`
* `python -m venv venv`
* `venv\Scripts\activate`
* `pip install -r requirements.txt`

#### Command list (Unix - bash):
* `git clone https://github.com/raritetmolodoy/tele2-profit.git`
* `cd tele2-profit`
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip3 install -r requirements.txt`


## Usage
1. Login with running `python auth.py` (or auth.exe if built version). Access token works 4 hours, then it needs to be updated.  
**note: access-token saves on your PC _only_, in `./config.json` file** 
2. Run `python main.py` (or main.exe if built version) and select action.

### FYI: Current Tele2 market lot requirements

#### Gigabytes
* Minimum GB amount - **1 GB**
* Minimum GB price - **15 rub/GB**, maximum - **50 rub/GB**

#### Minutes
* Minimum minute amount - **50 min**
* Minimum minute price - **0.8 rub/min**, maximum - **2 rub/min**

### Listing lots
**Preparing lots is done with this syntax: `<lot amount> <lot price>`**  
For example: `60 80` - 60 minutes (or gb) will be listed for 80 rub.  

**Standard syntax can be shortened to just `<lot amount>`**   
For example: `68` -  68 minutes (or gb) will be listed with **minimum** possible price *(in this case - 55 rub if minutes, 1020 rub if gb)*.  
When done leave input field empty (just hit enter) and you will jump to the next part.


## TODO
* Use refresh token to support longer auth persistence (currently 4 hours)

## Donations
Special thanks to my donators:
* Кирилл - 100 rub
* Alex - 300 rub
* Никита - 300 rub  

If you want to support my work - *79044979272* (qiwi, sber, tinkoff)
