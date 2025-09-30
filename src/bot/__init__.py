#
# bot/__init__.py
#
# @author n1ghts4kura
#

import time
import threading as t

import blaster
import chassis
import conn
import conn as serial
import game_msg
import gimbal
import robot
import sdk

def main_loop() -> None:
    sdk.enter_sdk_mode()
    
    try:
        while True:
            data = serial.read_serial()

            if data.startswith("game msg push"):
                game_msg.process(data)
        
            time.sleep(0.5)
    except:
        pass

    sdk.exit_sdk_mode()

def start_loop() -> None:
    """Start the main loop in a separate thread."""
    loop_thread = t.Thread(target=main_loop, daemon=True)
    loop_thread.start()

__all__ = [
    "blaster",
    "chassis",
    "conn",
    "game_msg",
    "gimbal",
    "robot",
    "sdk",
]
