"""
(Szenario 5):
---------------------------------------------------
Dieses Szenario führt eine zyklische Zwei-Zonen-Beleuchtung aus. Es wiederholt 
ein asynchrones Abschaltmuster insgesamt 4-mal (Iterationen).

1. JEDER DURCHLAUF (Iteration):
   - Gruppe 0 & 1: Starten mit 60% Helligkeit für 10 Minuten (600s).
   - Gruppe 2 & 3: Starten mit 30% Helligkeit für 20 Minuten (1200s).
   
2. VERSATZ-LOGIK:
   Innerhalb eines Zyklus gehen erst die helleren Gruppen (0/1) aus, während 
   die dunkleren Gruppen (2/3) noch weitere 10 Minuten leuchten.

3. REGENERATIONSPHAUSE:
   Nachdem alle Gruppen in einem Zyklus erloschen sind, folgt eine 
   30-minütige (1800s) Dunkelphase, bevor der nächste Zyklus startet.

Gesamtdauer: Ca. 3,5 Stunden.
"""

import time
from core.dali_system import luba, perc_to_dali

# =============================================================================
# INITIALISIERUNG
# =============================================================================
luba.clear_tx_buffer()

# =============================================================================
# KONFIGURATIONSPARAMETER
# =============================================================================
start_pause = 5       # Vorlaufzeit vor dem ersten Start
loop_sleep = 0.2      # Taktung der Überwachung (CPU-Schonung)
iterations = 4        # Anzahl der Gesamtzyklen
pause_after = 1800    # Pause zwischen den Zyklen (Sekunden)

# Definition der Zielwerte und Leuchtdauern pro Gruppe
group_config = {
    0: {"percent": 60, "on_time": 600},
    1: {"percent": 60, "on_time": 600},
    2: {"percent": 30, "on_time": 1200},
    3: {"percent": 30, "on_time": 1200},
}

# =============================================================================
# START-VERZÖGERUNG
# =============================================================================
print(f"== Szenario 5: Vorlaufzeit {start_pause} Sekunden ==")
time.sleep(start_pause)

# DALI-Werte einmalig vorab berechnen
for grp in group_config:
    group_config[grp]["dali"] = perc_to_dali(group_config[grp]["percent"])

# =============================================================================
# HAUPTABLAUF (ZYKLEN)
# =============================================================================

for cycle in range(1, iterations + 1):
    print(f"\n--- STARTE ZYKLUS {cycle} von {iterations} ---")
    
    start_time = time.time()
    group_state = {grp: True for grp in group_config}

    # 1. SCHRITT: Alle Gruppen für diesen Zyklus einschalten
    for grp, cfg in group_config.items():
        print(f"[Hardware] GRP {grp} -> ON ({cfg['percent']}%)")
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, cfg["dali"]))
    luba.execute_tx_buffer()

    # 2. SCHRITT: Überwachung der Leuchtzeiten (innerhalb des Zyklus)
    while any(group_state.values()):
        elapsed = time.time() - start_time
        command_sent = False
        
        for grp, active in group_state.items():
            if active and elapsed >= group_config[grp]["on_time"]:
                print(f"[Hardware] GRP {grp} Zeit erreicht -> OFF")
                luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, 0))
                group_state[grp] = False
                command_sent = True
        
        if command_sent:
            luba.execute_tx_buffer()
            
        time.sleep(loop_sleep)

    # 3. SCHRITT: Pause nach dem Zyklus (nicht nach dem letzten Durchlauf)
    if cycle < iterations:
        print(f"Zyklus {cycle} beendet. Pause: {pause_after}s...")
        time.sleep(pause_after)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 5 beendet: Alle Zyklen erfolgreich durchlaufen ==")