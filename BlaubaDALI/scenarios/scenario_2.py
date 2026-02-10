"""
(Szenario 2):
---------------------------------------------------
Dieses Szenario kombiniert eine statische Langzeit-Beleuchtung mit einem 
intermittierenden Lichtzyklus:

1. DAUER-BESTRAHLUNG: Gruppen 0 und 1 schalten einmalig ein und leuchten 
   konstant für 40 Minuten (2400s). Danach schalten sie permanent aus.

2. INTERMITTIERENDE BESTRAHLUNG: Parallel dazu führen Gruppen 2 und 3 insgesamt 
   4 Durchläufe aus. Ein Durchlauf besteht aus:
   - 10 Minuten (600s) AN bei 80% Helligkeit.
   - 30 Minuten (1800s) AUS (Regenerationspause).
"""

import time
import threading
from core.dali_system import luba, perc_to_dali

# =============================================================================
# INITIALISIERUNG & HELFER
# =============================================================================
luba.clear_tx_buffer()

def switch_group(grp, percent):
    """Hilfsfunktion zum Senden eines DALI-Befehls für eine Gruppe."""
    dali_val = perc_to_dali(percent)
    luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    status = "ON" if percent > 0 else "OFF"
    print(f"[Hardware] GRP {grp} -> {status} ({percent}%)")

# =============================================================================
# TEIL-ABLAUF 1: BASIS-LICHT (Einmalig)
# =============================================================================
def run_basis_light():
    print(">>> Start Basis-Licht (GRP 0+1)")
    switch_group(0, 15)
    switch_group(1, 15)
    
    time.sleep(2400) # 40 Minuten leuchten lassen
    
    switch_group(0, 0)
    switch_group(1, 0)
    print("<<< Basis-Licht beendet (GRP 0+1 OFF)")

# =============================================================================
# TEIL-ABLAUF 2: ZYKLISCHES LICHT (4 Durchläufe)
# =============================================================================
def run_cyclic_light():
    for cycle in range(1, 5):
        print(f">>> Start Zyklus {cycle}/4 für GRP 2+3")
        switch_group(2, 15)
        switch_group(3, 15)
        
        time.sleep(600) # 10 Minuten AN
        
        switch_group(2, 0)
        switch_group(3, 0)
        print(f"<<< GRP 2+3 OFF (Zyklus {cycle} beendet)")
        
        if cycle < 4:
            print(f"... Pause für 30 Min (1800s) vor nächstem Zyklus ...")
            time.sleep(1800) # 30 Minuten AUS

# =============================================================================
# HAUPTPROGRAMM (Szenario-Steuerung)
# =============================================================================
print("== Szenario 2: Start-Pause 5 Sekunden ==")
time.sleep(5)

# Wir starten beide Abläufe in eigenen Threads, damit sie parallel laufen können
thread_basis = threading.Thread(target=run_basis_light)
thread_cycle = threading.Thread(target=run_cyclic_light)

thread_basis.start()
thread_cycle.start()

# Das Szenario-Skript bleibt aktiv, bis beide Threads fertig sind
thread_basis.join()
thread_cycle.join()

print("\n== Szenario 2 beendet: Alle Lichtphasen abgeschlossen ==")