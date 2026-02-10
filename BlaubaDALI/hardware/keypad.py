# hardware/keypad.py for keypad interface input interpretation
import RPi.GPIO as GPIO
import time
import sys

class Keypad:
    def __init__(self):
        self.L_PINS = [11, 13, 15, 7]  # Reihen
        self.C_PINS = [33, 31, 12]     # Spalten
        self.KEYS = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["*", "0", "#"]
        ]
        self.last_key_pressed = None
        self.setup()

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        # Reihen als Ausgang: Wir setzen sie auf HIGH
        for pin in self.L_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
        # Spalten als Eingang: Mit Pull-Up (Standard ist also HIGH)
        for pin in self.C_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_key(self):
        """
        Scannt das Keypad. Gibt eine Taste nur zurück, wenn sie neu gedrückt wurde.
        """
        key_detected = None

        for r_idx, r_pin in enumerate(self.L_PINS):
            # Reihe auf LOW ziehen zum Scannen
            GPIO.output(r_pin, GPIO.LOW)
            
            for c_idx, c_pin in enumerate(self.C_PINS):
                # Wenn Spalte LOW ist, wurde die Taste an dieser Kreuzung gedrückt
                if GPIO.input(c_pin) == GPIO.LOW:
                    time.sleep(0.01) # Kurzer Check gegen elektrisches Rauschen
                    if GPIO.input(c_pin) == GPIO.LOW:
                        key_detected = self.KEYS[r_idx][c_idx]
                        break
            
            # Reihe wieder auf HIGH setzen
            GPIO.output(r_pin, GPIO.HIGH)
            if key_detected:
                break

        # Logik: Nur zurückgeben, wenn die Taste vorher NICHT gedrückt war (Flankenerkennung)
        if key_detected:
            if key_detected != self.last_key_pressed:
                self.last_key_pressed = key_detected
                print(f"ERKANNT: Taste {key_detected}")
                sys.stdout.flush()
                return key_detected
        else:
            # Keine Taste erkannt -> Status zurücksetzen
            self.last_key_pressed = None

        return None

    def cleanup(self):
        GPIO.cleanup()