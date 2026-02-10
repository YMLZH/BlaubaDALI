# main.py for importing, defining, handling and controling all aspects and features of the project
import time
import sys
import os
import importlib
import multiprocessing
from hardware.keypad import Keypad
from core.dali_system import luba  # Für Not-Aus beim Abbruch

class MainController:
    def __init__(self):
        self.keypad = Keypad()
        self.current_input = ""
        self.active_process = None
        self.star_press_times = []

    def stop_scenario(self):
        """Bricht das laufende Szenario ab und schaltet alle Lichter aus."""
        if self.active_process and self.active_process.is_alive():
            print("!!! Szenario wird abgebrochen !!!")
            self.active_process.terminate()
            self.active_process.join()
            # Not-Aus: Alle Gruppen aus (optional, aber sicher)
            for g in range(16):
                luba.send(luba.CMD_ADD_16BIT, luba.dali_group(g, 0))
            luba.execute_tx_buffer()
        self.active_process = None

    def run_scenario_process(self, scenario_number):
        """Wird in einem eigenen Prozess aufgerufen."""
        try:
            module_name = f"scenarios.scenario_{scenario_number}"
            # Importiert und führt das Szenario aus
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Fehler beim Starten von Szenario {scenario_number}: {e}")

    def run(self):
        print("=== Blaubadali System Gestartet ===")
        print("Warte auf Eingabe (1-2 Stellen + #)...")
        
        try:
            while True:
                key = self.keypad.get_key()
                
                if key:
                    now = time.time()
                    
                    # Logik für *-Taste (Reset / Abbruch / Beenden)
                    if key == "*":
                        self.current_input = ""
                        self.star_press_times.append(now)
                        # Nur die letzten 3 Drücke behalten
                        self.star_press_times = [t for t in self.star_press_times if now - t <= 5]
                        
                        count = len(self.star_press_times)
                        print(f"Reset (Stern gedrückt {count}x)")
                        
                        if count == 2:
                            self.stop_scenario()
                        elif count == 3:
                            print("Beende main.py...")
                            self.stop_scenario()
                            break
                        continue

                    # Ziffern sammeln
                    if key.isdigit():
                        if len(self.current_input) < 2:
                            self.current_input += key
                            print(f"Aktuelle Eingabe: {self.current_input}")

                    # Bestätigung mit #
                    elif key == "#":
                        if self.current_input:
                            num = int(self.current_input)
                            print(f"Starte Szenario_{num}...")
                            
                            self.stop_scenario() # Falls noch eins läuft
                            
                            self.active_process = multiprocessing.Process(
                                target=self.run_scenario_process, 
                                args=(num,)
                            )
                            self.active_process.start()
                            self.current_input = ""
                        else:
                            print("Keine Nummer eingegeben!")

                # Prüfen, ob Szenario von selbst fertig wurde
                if self.active_process and not self.active_process.is_alive():
                    print("Szenario beendet. Zurück im Warte-Modus.")
                    self.active_process = None

                time.sleep(0.05)

        finally:
            self.keypad.cleanup()
            luba.close()

if __name__ == "__main__":
    controller = MainController()
    controller.run()