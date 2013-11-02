## Taskr 
===============
Time tracker for tasks.

### Instalation
```
# Clone repo
git clone https://github.com/rgp/taskr.git /usr/local/taskr

# Add taskr to PATH
echo "export PATH=$PATH:/usr/local/taskr/bin" >> ~/.bash_profile

```

### Usage

```
$ taskr -h

usage: taskr [-h] [-n 'write some code'] [-e estimated hours] [-i ] [-p ]
             [-r ] [-c ] [-cr ] [-d ] [-s ]

Taskr helps you keep track of time!

optional arguments:
  -h, --help             show this help message and exit
  -n ['write some code'] New task  
  -e estimated hours     Estimated time in hours
  -i                     Pause current task
  -p                     Pause current task
  -r [task id]           Resume current task
  -c                     Close current task
  -cr                    Close current task and resume previous paused one
  -d [task id]           Close current task
  -s                     Show taskr status
  
# Example
$ taskr -n "Install taskr"
$ taskr -s

```
