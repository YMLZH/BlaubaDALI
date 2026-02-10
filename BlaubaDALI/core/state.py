# core/state.py for abortion of running scripts
import threading
stop_event = threading.Event()