"""
(Szenario 7 - Zeitangepasst):
---------------------------------------------------
Dieses Szenario erzeugt ein langlaufendes, überlagertes Belichtungsmuster.
Zwei unterschiedliche Zeitpläne laufen parallel via Multithreading:

1. LANGZEIT-KOMPONENTE (Gruppe 0 & 1):
   - Schaltet einmalig für 20 Minuten (1200s) auf 50% Helligkeit ein.
   - Schaltet nach Ablauf der 20 Minuten permanent aus.

2. PULS-KOMPONENTE (Gruppe 2 & 3):
   - Führen insgesamt 2 lange Belichtungszyklen aus.
   - Ein Zyklus besteht aus: 5 Min (300s) AN (50%) -> 5 Min (300s) AUS (Pause).

3. INTERAKTION:
   - Minute 0-5:   Alle Gruppen (0,1,2,3) sind AN.
   - Minute 5-10:  Nur GRP 0+1 sind AN (GRP 2+3 machen Pause).
   - Minute 10-15: Alle Gruppen (0,1,2,3) sind AN.
   - Minute 15-20: Nur GRP 0+1 sind AN (GRP 2+3 machen Pause/sind fertig).

Gesamtdauer: 20 Minuten.
"""

import threading
import time
from core.dali_system import luba, perc_to_dali

# =============================================================================
# INITIALISIERUNG
# =============================================================================
luba.clear_tx_buffer()

# =============================================================================
# KONFIGURATIONSPARAMETER
# =============================================================================
# Gruppen-Zuweisung
grp_long = [0, 1]       # Langzeit-Belichtung
grp_fast = [2, 3]       # "Puls"-Belichtung (jetzt im Minutenbereich)

# Zeitsteuerung (umgerechnet in Sekunden)
duration_long_on = 20.0 * 60  # 20 Minuten = 1200s
duration_fast_on = 5.0 * 60   # 5 Minuten = 300s
duration_fast_off = 5.0 * 60  # 5 Minuten = 300s
iterations_fast = 2           # Anzahl der Intervalle für GRP 2+3

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================
def switch_group(grp, percent):
    """Direktes Schalten einer Gruppe mit Log-Ausgabe."""
    dali_val = perc_to_dali(percent)
    luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] GRP {grp:02d} -> {status}")

# =============================================================================
# TEIL-ABLAUF 1: LANGZEIT-ZYKLUS (Thread 1)
# =============================================================================
def long_group_cycle():
    print(">>> Start Langzeit-Phase (GRP 0+1) für 20 Min")
    for grp in grp_long:
        switch_group(grp, 50)
    
    time.sleep(duration_long_on)
    
    for grp in grp_long:
        switch_group(grp, 0)
    print("<<< Langzeit-Phase beendet (GRP 0+1 OFF)")

# =============================================================================
# TEIL-ABLAUF 2: INTERVALL-ZYKLUS (Thread 2)
# =============================================================================
def fast_group_cycle():
    for iteration in range(1, iterations_fast + 1):
        print(f">>> Start Intervall {iteration}/{iterations_fast} (GRP 2+3) für 5 Min")
        for grp in grp_fast:
            switch_group(grp, 50)
            
        time.sleep(duration_fast_on)
        
        for grp in grp_fast:
            switch_group(grp, 0)
        print(f"<<< Intervall {iteration} beendet (GRP 2+3 OFF)")
        
        # Pause nach dem Puls (außer beim letzten Durchlauf)
        if iteration < iterations_fast:
            print(f"    Intervall-Pause: {duration_fast_off/60} Min...")
            time.sleep(duration_fast_off)

# =============================================================================
# HAUPTPROGRAMM (Szenario-Steuerung)
# =============================================================================
print("== Szenario 7: Start-Pause 5 Sekunden ==")
time.sleep(5)



# Threads definieren
thread_1 = threading.Thread(target=long_group_cycle)
thread_2 = threading.Thread(target=fast_group_cycle)

# Beide Threads gleichzeitig starten
thread_1.start()
thread_2.start()

# Das Skript wartet hier, bis beide "Arme" fertig sind
thread_1.join()
thread_2.join()

print("\n== Szenario 7 beendet: Alle Langzeit-Intervalle abgeschlossen ==")