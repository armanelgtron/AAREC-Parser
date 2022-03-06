Armagetron Advanced recording parser
====================================

Parses aarec files to get information about them.

cli.py interface
----------------
#### arguments ####
`--human` - output human-friendly format, this is default

`--json` - spit out information in json to be parsed by another script

#### modes ####
##### mode 1: stats #####
This is intended to collect a bunch of stats and spit them out
when the end of the recording is reached.
At the moment, it doesn't collect any useful stats, and
there's no way to tell it what stats to collect and when.

##### mode 2: scores #####
This is the default mode.

Spit out scores on a certain event.
By default, on every match win, it spits out the winner, the teams scores,
and the player scores on every match win.
