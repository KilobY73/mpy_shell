# MicroPython Shell

Shell runs under MicroPython

## Builtin Command
+ cd
+ cp
+ cat
+ echo
+ exit
+ ls
+ rm & rm -r
+ mkdir
+ mv

## Implemented feature
+ Variable substitute
+ `&` background task
+ `\` backslash new line
+ Directly run scripts under current work directory
+ `>` and `>>` redirect for builtin command

## Usage
```
import sh
sh.start()
```
