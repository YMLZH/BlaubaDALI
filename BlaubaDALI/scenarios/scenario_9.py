"""
(Szenario 9):
---------------------------------------------------
Dieses Szenario erzeugt einen asymmetrischen Belichtungsverlauf. Eine Hauptgruppe
leuchtet deutlich länger und heller als die unterstützenden Nebengruppen:

1. STARTPHASE:
   Alle vier Gruppen (0, 1, 2, 3) schalten gleichzeitig ein.
   - Gruppe 0: 70% Helligkeit (Dominante Gruppe).
   - Gruppen 1, 2, 3: 10% Helligkeit (Begleitlicht).

2. ABSCHALTPHASE (Zeitversetzt):
   - Nach 1 Minute (60s): Gruppen 1, 2 und 3 schalten gleichzeitig aus.
   - Nach insgesamt 10 Minuten (600s): Gruppe 0 schaltet aus.

3. ZYKLUS:
   Standardmäßig ist 1 Durchlauf konfiguriert. Das Szenario endet, sobald 
   die 10-minütige Belichtung von Gruppe 0 abgeschlossen ist.

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
iterations = 1        # Anzahl der Gesamtwiederholungen
start_pause = 5       # Vorlaufzeit (Sekunden)
loop_sleep = 0.2      # Taktung der Überwachung (CPU-Schonung)

# Gruppe → Zielhelligkeit (%) + Einschaltdauer (Minuten umgerechnet in Sekunden)
group_config = {
    0: {"percent": 70, "on_time": 10 * 60},  # 10 Minuten Hauptlicht
    1: {"percent": 10, "on_time": 1 * 60},   # 1 Minute Begleitlicht
    2: {"percent": 10, "on_time": 1 * 60},
    3: {"percent": 10, "on_time": 1 * 60},
}

post_cycle_pause = 0  # Pause nach Ende eines Zyklus (Sekunden)

# =============================================================================
# VORBEREITUNG
# =============================================================================
print(f"== Szenario 9: Startet in {start_pause} Sekunden ==")
time.sleep(start_pause)

# DALI-Level vorab berechnen
for grp in group_config:
    group_config[grp]["dali"] = perc_to_dali(group_config[grp]["percent"])

# =============================================================================
# HAUPTSCHLEIFE (ZYKLEN)
# =============================================================================


for cycle in range(1, iterations + 1):
    print(f"\n--- STARTE ITERATION {cycle}/{iterations} ---")
    start_time = time.time()
    group_state = {grp: True for grp in group_config}

    # 1. SCHRITT: Alle Gruppen laut Konfiguration einschalten
    for grp, cfg in group_config.items():
        print(f"[Hardware] GRP {grp} -> ON ({cfg['percent']}%) für {cfg['on_time']/60} Min.")
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, cfg["dali"]))
    luba.execute_tx_buffer()

    # 2. SCHRITT: Überwachung der individuellen Laufzeiten
    while any(group_state.values()):
        elapsed = time.time() - start_time
        command_needed = False
        
        for grp, active in group_state.items():
            # Wenn Gruppe noch an ist, aber ihre Zeit abgelaufen ist
            if active and elapsed >= group_config[grp]["on_time"]:
                print(f"[Hardware] GRP {grp} Zeit erreicht -> OFF")
                luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, 0))
                group_state[grp] = False
                command_needed = True
        
        # Nur kommunizieren, wenn sich ein Status geändert hat
        if command_needed:
            luba.execute_tx_buffer()
            
        time.sleep(loop_sleep)

    # 3. SCHRITT: Optionale Pause nach dem Zyklus
    if post_cycle_pause > 0 and cycle < iterations:
        print(f"Zyklus beendet. Warte {post_cycle_pause}s bis zum nächsten Start...")
        time.sleep(post_cycle_pause)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 9 beendet: Asymmetrischer Ablauf abgeschlossen ==")