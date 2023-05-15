
import sys
import os
import time
import traceback

import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from io import StringIO
import atexit
from email.generator import Generator
from html import escape

def as_string(self, unixfrom=False, maxheaderlen=0, policy=None):
    """Return the entire formatted message as a string.

    Optional 'unixfrom', when true, means include the Unix From_ envelope
    header.  For backward compatibility reasons, if maxheaderlen is
    not specified it defaults to 0, so you must override it explicitly
    if you want a different maxheaderlen.  'policy' is passed to the
    Generator instance used to serialize the message; if it is not
    specified the policy associated with the message instance is used.

    If the message object contains binary data that is not encoded
    according to RFC standards, the non-compliant data will be replaced by
    unicode "unknown character" code points.
    """
    policy = self.policy if policy is None else policy
    fp = StringIO()
    g = Generator(fp,
                  mangle_from_=False,
                  maxheaderlen=maxheaderlen,
                  policy=policy)
    g.flatten(self, unixfrom=unixfrom)
    return fp.getvalue()
from email.message import Message
Message.as_string=as_string

example_yaml='''
#  =========== autosend yaml template ============
# specify the email SMTP server
username: "username"
password: "password"
server: smtp.example.com
port: 25
tls: False
timeout: 15

# specify the email subject format, where {path} implies the work_dir running the python script,
# {curtime} implies the current date and time, and {status} may be running or complete 
subject_format: "【符合保密要求，可在手机端查阅】{path}日志 [{curtime}] [{status}]"

# specify the email sender's and receivers' addresses
sender: "example@example.com"
receivers: 
- "example@example.com"

# send logs by email only if the program runs after the specific seconds
send_after_seconds: 3600

# send logs by email EVERY specific seconds if the program is keep running
send_periods: 86400

# whether clear history logs after autosending so that the next sending will not contain repeated 
clear_after_send: True

# whether send html format logs instead of plain text
html: True
'''

def simulate_terminal_output(output_str):
    width = 140
    current_pos = 0
    lines = []
    current_line = ""
    
    # Iterate through each character in the input string
    for char in output_str:
        # Handle control characters
        if char == '\b':
            if current_pos > 0:
                current_pos -= 1
                current_line = current_line[:-1]
        elif char == '\r':
            current_pos = 0
            current_line = ""
        elif char == '\n':
            lines.append(current_line)
            current_line = ""
            current_pos = 0
        else:
            # Append printable characters to current line
            if current_pos >= width:
                lines.append(current_line)
                current_line = ""
                current_pos = 0
            current_line += char
            current_pos += 1
    lines.append(current_line)
    return lines

def lines_to_text(lines,plain=False):
    if plain:
        return '\n'.join(lines)
    else:
        # Generate HTML document
        html_output = "<html><head><style>pre {font-family: 'Courier New', " \
                      "Courier, monospace; font-size: 14px;}</style></head><body><pre>"
        for line in lines:
            html_output += escape(line) + "<br/>"
        html_output += "</pre></body></html>"
        return html_output

class TextIOWrapperWithLogging:
    def __init__(self,enabled=True,config_addr='~/.autosend.yaml'):
        try:
            self.config = self.read_config(config_addr)
        except Exception:
            traceback.print_exc()
            print('#autosend: cannot read config at ~/.autosend.yaml, disable autosend')
            print('if you want to use this module, please create .autosend.yaml at ~/ using the following template')
            print(example_yaml)
            enabled=False
        self.enabled=enabled
        if not enabled:
            return
        self.buffer = StringIO()
        self.start_time = time.time()
        self.send_after_seconds = float(self.config.get('send_after_seconds',3600))
        self.send_periods = float(self.config.get('send_periods', 86400))
        self.sbj_fmt=self.config.get('subject_format',"【符合保密要求，可在手机端查阅】{path}日志 [{curtime}] [{status}]")
        self.clear_after_send = self.config.get('clear_after_send',True)
        self.html = self.config.get('html',True)

        self.start_time_str=time.strftime('%Y-%m-%d %H:%M', time.localtime(self.start_time))
        self.log_start_time=time.time()
        self.args='; '.join(sys.argv)
        self.cwd = os.getcwd()
        self.should_send = False

        self.path=os.path.basename(os.getcwd())
        self.__stdout__ = sys.stdout
        self.__stderr__ = sys.stderr
        print('#autosend: starting log')
        sys.stdout = self
        sys.stderr = self
        atexit.register(self.__del__)

    def read_config(self,path):
        with open(os.path.expanduser(path), "r", encoding='utf-8') as stream:
            return yaml.safe_load(stream)


    def write(self, text):
        self.buffer.write(text)
        sys.__stdout__.write(text)
        self.check()

    def writelines(self,texts,/):
        self.buffer.writelines(texts)
        sys.__stdout__.writelines(texts)
        self.check()

    def flush(self):
        sys.__stdout__.flush()

    def check(self):
        elapsed_time = time.time() - self.log_start_time
        self.should_send = time.time() - self.start_time > self.send_after_seconds
        if elapsed_time > self.send_periods:
            self.send_logs('running')

    def send_email(self, subject, body, attachments=()):
        sender = self.config['sender']
        receivers = self.config['receivers']
        username = self.config['username']
        password = self.config['password']
        server = self.config['server']
        port = self.config.get('port',0)
        timeout = self.config.get('timeout',15)
        tls = self.config.get('tls',False)

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(receivers)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html' if self.html else 'plain'))

        for attach_name,attach_data in attachments:
            attachment_part = MIMEApplication(attach_data, Name=attach_name)
            attachment_part['Content-Disposition'] = f'attachment; filename="{attach_name}"'
            msg.attach(attachment_part)

        smtp_server = smtplib.SMTP(server, port,timeout=timeout)
        if tls:
            smtp_server.starttls()
        smtp_server.login(username, password)
        smtp_server.sendmail(sender, receivers, msg.as_string())
        smtp_server.quit()

    def send_logs(self, status=''):
        if not self.should_send:
            return
        self.__stderr__.write('#autosend: sending log\n')
        self.__stderr__.flush()

        text_lines = simulate_terminal_output(self.buffer.getvalue())
        if self.clear_after_send:
            self.buffer = StringIO() 
        self.log_start_time = time.time()
        try:
            subject = self.sbj_fmt.format(
                path=self.path,
                curtime=self.start_time_str,
                status = status,
            )
            meta_info=[
                ' start_time: ' + self.start_time_str,
                'last update: ' + time.strftime('%Y-%m-%d %H:%M'),
                '   work_dir: ' + self.cwd,
                '       args: ' + self.args,
                '================= last 100 lines of the log ================='
            ]
            body=lines_to_text(meta_info + text_lines[-100:],plain=not self.html)
            attachments = [(f"logs_{time.strftime('%Y-%m-%d-%H-%M')}.txt", '\n'.join(text_lines))]
            self.send_email(subject, body, attachments)

        except Exception:
            self.__stderr__.write('#autosend: email sending failed:\n')
            self.__stderr__.write(traceback.format_exc())
            self.__stderr__.flush()

    def __del__(self):
        if not self.enabled:
            return
        self.enabled=False
        self.send_logs('completed')
        sys.stdout = self.__stdout__
        sys.stderr = self.__stderr__

if int(os.environ.get('LOCAL_RANK',os.environ.get('RANK',0)))==0:
    logger = TextIOWrapperWithLogging()

