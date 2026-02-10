"""
(Szenario 1):
---------------------------------------------------
Dieses Szenario dient als Standard-Belichtungstest. 
Es erzeugt eine gleichmäßige, zeitlich begrenzte Ausleuchtung über alle Kanäle.

1. STARTPHASE:
   Alle verfügbaren Gruppen (0 bis 4) schalten gleichzeitig auf 60% Helligkeit.

2. BELICHTUNGSPHASE:
   Die Beleuchtung bleibt für exakt 10 Minuten (600s) konstant aktiv.

3. ABSCHLUSSPHASE:
   Nach Ablauf der Zeit schalten alle Gruppen simultan aus.

Ideal für: Grundlegende Funktionstests des Gesamtsystems oder einfache 
Dauerbelichtungen ohne komplexe Intervall-Logik.
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
start_pause = 5       # Vorlaufzeit vor dem Start (Sekunden)
loop_sleep = 0.2      # Taktung der Überwachung (CPU-Schonung)

# Gruppen-Konfiguration: Alle auf 80% für 10 Minuten
group_config = {
    0: {"percent": 60, "on_time": 600},
    1: {"percent": 60, "on_time": 600},
    2: {"percent": 60, "on_time": 600},
    3: {"percent": 60, "on_time": 600},
}

# =============================================================================
# VORBEREITUNG
# =============================================================================
print(f"== Szenario 1: Full-House-Start in {start_pause} Sekunden ==")
time.sleep(start_pause)

# DALI-Levels vorbereiten
for grp in group_config:
    group_config[grp]["dali"] = perc_to_dali(group_config[grp]["percent"])

# =============================================================================
# START: GRUPPEN EINSCHALTEN
# =============================================================================

group_state = {grp: True for grp in group_config}
start_time = time.time()

for grp, cfg in group_config.items():
    print(f"[Hardware] GRP {grp} -> ON ({cfg['percent']}%) für {cfg['on_time']}s")
    luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, cfg["dali"]))
luba.execute_tx_buffer()

# =============================================================================
# ÜBERWACHUNGSSCHLEIFE
# =============================================================================
while any(group_state.values()):
    elapsed = time.time() - start_time
    command_needed = False
    
    for grp, active in group_state.items():
        if active and elapsed >= group_config[grp]["on_time"]:
            print(f"[Hardware] GRP {grp} Zeit abgelaufen -> OFF")
            luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, 0))
            group_state[grp] = False
            command_needed = True
    
    # Gebündeltes Ausführen, falls Gruppen abgelaufen sind
    if command_needed:
        luba.execute_tx_buffer()
        
    time.sleep(loop_sleep)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 1 beendet: Alle Gruppen erfolgreich abgeschaltet ==")