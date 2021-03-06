# wtstamp

```

(c) 2017 Inc. All Rights Reserved.

Lucy von Kaenel - snow.dream.ch@gmail.com

```

```

./wtstamp -h

|-----------------------------------------------------------------------------|
|                                                                             |
| wtstamp - a flexible timestamp tool                                         |
|                                                                             |
|-----------------------------------------------------------------------------|
usage: wtstamp.py [-h] [-n] [-p] [-r] [-e] [-S] [-L] [-D [dd.mm.yyyy]]
                  [-W [dd.mm.yyyy]] [-M [mm.yyyy]] [-Y [yyyy]] {edit|insert}
                  
positional arguments:
  {edit|insert}                      Advanced Options
  
  {edit}
  -s, --set-start     <HH:MM> [dd.mm.yyyy] 
                                     Set the start time from the given day. When no day is given 
                                     either the last open day (1st) or the last closed day (2nd) is choosen
                                     
  -e, --set-end       <HH:MM | dd.mm.yyyy:HH:MM> [dd.mm.yyyy]
                                     Set the end time for the given day. 
                                     When no day is given, then the last closed day is choosen.
  
  -S, --move-start    <<s/+>HH:MM> [dd.mm.yyyy]
                                     Moves the start time from the given day (+=forward, s=backward). 
                                     When no day is given either the last open day (1st)
                                     or the last closed day (2nd) is choosen.
                                     
  -E, --move-End      <<s/+>HH:MM> [dd.mm.yyyy]
                                     Moves the end time from the given day (+=forward, s=backward). 
                                     When no day is given, then the last closed day is choosen.
   
  {insert}
  -n, --workday       <dd.mm.yyyy:HH:MM> <HH:MM>
                                     Inserts a new workday at the given day and time with the 
                                     specified length as positive offset.
                                     
  -b, --break         <dd.mm.yyyy> <dd.mm.yyyy:HH:MM> <HH:MM>
                                     Inserts a new break into the given workday, starting from the
                                     given day and time, with the specified positive offset for the break end.

optional arguments:
  -h, --help                         show this help message and exit
  -n, --stamp-new                    Starts a new workday
  -p, --stamp-pause                  Pauses the current workday
  -r, --stamp-resume                 Resumes the current workday
  -e, --stamp-end                    Ends the workday
  -S, --display-saldo                Displays the time saldo
  -L, --display-last                 Displays latest ended workday
  -D, --display-day   [dd.mm.yyyy]   Displays info about a workday - default this day
  -W, --display-week  [dd.mm.yyyy]   Displays summary of week - default this week
  -M, --display-month [mm.yyyy]      Displays summary of month - default this month
  -Y, --display-year  [yyyy]         Displays summary of the year
  -X, --display-proc                 Shows how long the caluclation took

```

### What is this?

A tool to make timestamps and calculations based on them on how long you have worked,
how long you need to work in order to meet the requirements.


### How does it work?

Every action is persisted within a folder / file structure named
after the corresponding date. The times are all stored as utc timestamp
and the files serialized as json to keep them raw and editable.

All calculations are realtime base on the settings in settings.yaml and these raw files
to keep things portable.


### Setup:

Clone the repository:

```
git clone https://github.com/Nexolight/wtstamp.git
```

cd into the directory and copy the template settings:

```
cp settings.yaml.template settings.yaml
```

Edit settings.yaml to your needs. It is preferred when available.

---


### Capabilities

**Stamps:**

* Start/End a Workday (only one open at a time).
* Start/Stop breaks.
* Move or set workday start & end times.
* Insert Workdays (remove not yet implemented - just remove the json file)
* Insert Workday breaks (remove not yet implemented - remove them manually from the json file).


Note: You can always remove or edit the workday files manually. They are found within
the application_data directory (see settings.yaml) 


**Views:**

* Saldo view which will show required and done work for the whole year, month, week and day plus the difference/balance at the moment (realtime).
* Day view which will show start, end, worktime, breaktime and break ranges. For ongoing days or breaks this is realitime.
* Week view. Shows a table with the non-free days listed with their dates, start, end, required worktime and work done. For ongoing days this is realtime.
* Month view. (Just like week view)
* Year view. (Just like month view)

**Settings allow you to change:**

* Application data directory
* The format times and dates are presented (limited)
* When a year is considered a "new year" worktime wise (affects some views)
* Calc cycles (User defined ranges with different work conditions)
  * Time to work per day
  * workdays
* Free days a.e. holidays or yearly specialdays


---


### Who wants to use this?

TLDR: Some command line nerds (with optional unusual worktimes) in case there's no
more suitable alternate or you just like it old school.

The tool itself doesn't lack essential features in my opinion based
on what I'm using it for. It is however not made for the casual user
which is intentional to some degree. At least the user needs to understand
yaml config files, read comments there, understand json and must be able to use the console.

The tool was not made for companies but for personal usage. It's not intended to be used
as a service provided via some web interface (although it might be possible).


---


### What does it better, or why this tool exists?

TLDR: Honestly I never looked for anything similar and coded this straight
away for my own purpose. 

I was bothered by systems which refuse to take work after 8pm into acount
or add an extra 30min break no matter if taken or not. So I switched to 
a trust based worktime system in my company. That means no more timestamping.
However in order to have some control and also an insurance in the worst case
I thought I need a more flexible timestamp tool which can do especially these things:

* It will always do the calculations on query time based on it's raw files. So it is always possible to change the way things are calculated and displayed 
afterwards.

* It is capable of taking extraordinary worktimes into account. Starting a day at a.e `01.08.2017 11:00` and ending it at `02.08.2017 01:00` is not a problem. The 
day ends when a user ends it and it will all count towards the start date.

* It allows changing work conditions while keeping the calculations correct. You could work 'that many' minutes per day at 'these' days during a 'certain' timespan 
and always add other timespans with different workdays and worktime per day.

* The possibility to easily edit the raw json files and options
to personalize the tool are what I personally like.

* Usage and pretty output views on command line but that's probably not an unique thing.
