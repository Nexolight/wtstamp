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
                  [-W [dd.mm.yyyy]] [-M [mm.yyyy]]

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


### Capabilities

**Views:**

* Saldo view which will show required and done work for the whole year, month, week and day plus the difference/balance at the moment (realtime).
* Day view which will show start, end, worktime, breaktime and break ranges. For ongoing days or breaks this is realitime.
* Week and Month view. Shows a table with the non-free days listed with their dates, start, end, required worktime and work done. For ongoing days this is realtime.

**Settings allow you to change:**

* Application data directory
* The format times and dates are presented (limited)
* Time to work per day
* When a year is considered a "new year" worktime wise (affects some views)
* The calculation cycles itself. Files are either ignored or read depending on that.
* workdays, holidays, specialdays


### What does it better, or why this tool exists?

I was bothered by systems which refuse to take work after 8pm into acount
or add an extra 30min break no matter if taken or not. So I switched to 
a trust based worktime system in my company. That means no more timestamping.
However in order to have some control and also an insurance in the worst case
I thought I need a timestamp tool.

Be sure that this one is capable of taking even extraordinary worktimes into
account. By definition here a day ends when the user ends it. 
That can be past 12pm as well and it still count's toward the day before 12pm.

Furthermore the possibility to easily edit the raw json files and options
to personalize the tool are what I personally like.
