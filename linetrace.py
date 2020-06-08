#!/usr/bin/env python
#TODO: for debugging purposes we could *also* listen to keyboard events

import sys
import imp
import time
import signal
import os
import threading
from websocket_server import WebsocketServer

# Define global variables
stepper = True
do_step = False

def debug_signal_handler(signal, frame):
     server.send_message_to_all("0")
     os._exit(1)

# Called when a client sends a message
signal.signal(signal.SIGINT, debug_signal_handler)

def message_received(client, server, message):
   global stepper, do_step, sys, p
   if message == "b":
      stepper = True
   if message == "c":
      stepper = False
   if message == "s":
      do_step = True
   if message == "e":
      os.kill(os.getpid(), signal.SIGINT)

server = WebsocketServer(host="0.0.0.0", port=8001)
server.set_fn_message_received(message_received)
p = threading.Thread(target=server.serve_forever)
p.start()

def trace_lines(frame, event, arg):
    global stepper, do_step
    if event != 'line':
        return
    server.send_message_to_all(str(frame.f_lineno))
    while stepper and not do_step:
       time.sleep(.01)
    do_step = False

def traceit(frame, event, arg):
    global stepper
    co = frame.f_code
    filename = co.co_filename
    if not filename.endswith('zoef.py'):
        return
    return trace_lines

sys.settrace(traceit)

# rospy.init_node() for some reason needs to be called from __main__ when importing in the regular way.
# https://answers.ros.org/question/266612/rospy-init_node-inside-imported-file
test = imp.load_source("zoef", "/home/zoef/workdir/zoef.py")
server.send_message_to_all("0")
server.shutdown()
