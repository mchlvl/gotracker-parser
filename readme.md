# Docs

Parses logs created with [gotracker](https://github.com/mchlvl/gotracker).

## Manage

### Build


```
set PYTHONOPTIMIZE=1 && pyinstaller --onedir cli.spec
```

## Run

- CMD (exe)

  ```
  cd dist
  cli
  ```

- Bash (exe)

  ```
  cd dist
  ./cli
  ```

- Python

  ```
  python parser/cli.py
  ```

## Help

```
$ python parser/cli.py -h
usage: cli.py [-h] [-n NLOGS] [-p {day,week,month,year}]
              [-l {0,1,2,3,4,5,6,7}] [-d] [-nl NLARGEST] [-m MINDURATION] [-i]
              [-f FIND]

Input arguments

optional arguments:
  -h, --help            show this help message and exit
  -n NLOGS, --numberlogs NLOGS
                        Time selection - last N logs available are selected
  -p {day,week,month,year}, --per {day,week,month,year}
                        Group results by
  -l {0,1,2,3,4,5,6,7}, --level {0,1,2,3,4,5,6,7}
                        Aggregation level.
  -d, --detailed        Display detailed result breakdown (level 5).
  -nl NLARGEST, --nlargest NLARGEST
                        Number of records per aggregation level to display.
  -m MINDURATION, --minduration MINDURATION
                        Duration in secods that need to be satisfied on
                        aggregate level.
  -i, --resetindex      Whether the full index is to be displayed. Recommended
                        for further cmd filtering.
  -f FIND, --find FIND  String to find
```

## Quick start

### Total

```
$ python parser/cli.py
INFO: loaded 1 files resulting in data of size (210, 9)
INFO: Level: '0', reports up to '10' records (totals) of duration >= '120s', per 'day'

                     min       max PotentialDuration RecordedDuration  %ofPotential
Year Month Day
2019 10    17   00:00:48  19:56:10          19:55:22         19:54:06         99.89
```

### Detailed

```
$ python parser/cli.py -d
INFO: loaded 1 files resulting in data of size (210, 9)
INFO: Level: '5', reports up to '10' records (totals) of duration >= '120s', per 'day'

                                                    Duration  Count DurationExe  %OfExe DurationTotal  %OfTotal
Year Month Day Executable   ExecutableName Project
2019 10    17  explorer.exe                         18:26:14      6    18:26:14  100.00      19:54:06     92.64
               Away                                 00:44:22     12    00:44:22  100.00      19:54:06      3.72
               chrome.exe   Google Chrome  YouTube  00:30:48    109    00:43:01   71.60      19:54:06      2.58
                                           Twitch   00:04:20     23    00:43:01   10.08      19:54:06      0.36
```

### Result filtering

The stdouts are predefined pandas strings that can be further analysed. Note the optional setting `-i` which prints all index values.

The quality of output depends on how does individual page log the text in the window title. E.g. Netflix does not provide the details tab, whereas YouTube does.

#### Time spent on Netflix

```
$ python parser/cli.py -n 7 -p week -nl 50 -m 0 -l 5 -f netflix
```

#### Detailed time spent on YouTube

Note - special syntax `2:youtube` signals that you search in second last index column (here `Project`) for string `youtube`.

```
$ python parser/cli.py -n 7 -p week -nl 50 -m 120 -l 5 -f 2:youtube
```
