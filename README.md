# Introduction
This is a tool that logs everything your program printing on the screen, 
and sends you an email when the program is finished or terminated.

# Usage
First, create ~/.autosend.yaml using the following 
template and modify the configs.
```
#  =========== autosend yaml template ============
# specify the email SMTP server
username: "username"
password: "password"
server: smtp.example.com
port: 25
tls: False
timeout: 15

# specify the email subject format, where: 
# {path} implies the work_dir running the python script,
# {curtime} implies the current date and time
# {status} implies the log type (may be running or complete) 
subject_format: "【符合保密要求，可在手机端查阅】{path}日志 [{curtime}] [{status}]"

# specify the email sender's and receivers' addresses
sender: "example@example.com"
receivers: 
- "example@example.com"

# send logs by email only if the program runs after the specific seconds
send_after_seconds: 3600

# send logs by email EVERY specific seconds if the program is keep running
send_periods: 86400

# whether send html format logs instead of plain text
html: True
```
 
Then add the following line in your code:
```
import autosend
```

After the program is finished or after a specific time,
you will get an email like:
```
【符合保密要求，可在手机端查阅】Python Scripts日志 [2023-05-14 13:45] [completed]
xx send to xx 2023-05-14 13:46:27

 start_time: 2023-05-14 13:45
last update: 2023-05-14 13:46
   work_dir: D:\Users\A\Documents\Python Scripts
       args: test.py
================= last 100 lines of the log =================
1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'date' is not defined
1684043182.6202037

1 attachments
```
