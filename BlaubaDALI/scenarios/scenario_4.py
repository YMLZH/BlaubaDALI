"""
(Szenario 4):
---------------------------------------------------
Dieses Szenario erzeugt ein zweistufiges Abschaltmuster. Alle vier Lichtgruppen
starten zeitgleich, enden jedoch versetzt, um unterschiedliche Bereiche oder
Belichtungszeiten zu bedienen:

1. STARTPHASE: Alle Gruppen (0, 1, 2, 3) schalten nach 5s Vorlauf ein.
   - Gruppe 0 & 1: 60% Helligkeit.
   - Gruppe 2 & 3: 30% Helligkeit.

2. ABSCHALTPHASE:
   - Nach 10 Minuten (600s): Gruppe 0 und 1 schalten aus.
   - Nach insgesamt 20 Minuten (1200s): Gruppe 2 und 3 schalten aus.
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
start_pause = 5    # Vorlaufzeit in Sekunden
loop_sleep = 0.2   # Taktung der Überwachungsschleife

# Definition der Zielwerte und Leuchtdauern
group_config = {
    0: {"percent": 60, "on_time": 600},
    1: {"percent": 60, "on_time": 600},
    2: {"percent": 30, "on_time": 1200},
    3: {"percent": 30, "on_time": 1200},
}

# =============================================================================
# START-VERZÖGERUNG
# =============================================================================
print(f"== Szenario 4: Startet in {start_pause} Sekunden ==")
time.sleep(start_pause)

# Prozentwerte für das DALI-Protokoll vorbereiten
for grp in group_config:
    group_config[grp]["dali"] = perc_to_dali(group_config[grp]["percent"])

# =============================================================================
# HAUPTABLAUF
# =============================================================================
# Zeitstempel für den gemeinsamen Start setzen
start_time = time.time()
group_state = {grp: True for grp in group_config}

# 1. SCHRITT: Alle Gruppen simultan einschalten

for grp, cfg in group_config.items():
    print(f"[Hardware] GRP {grp} -> ON ({cfg['percent']}%) für {cfg['on_time']}s")
    luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, cfg["dali"]))
luba.execute_tx_buffer()

# 2. SCHRITT: Überwachung der individuellen Laufzeiten
while any(group_state.values()):
    elapsed = time.time() - start_time
    command_sent = False
    
    for grp, active in group_state.items():
        # Falls die Gruppe noch leuchtet, aber ihre Zeit abgelaufen ist
        if active and elapsed >= group_config[grp]["on_time"]:
            print(f"[Hardware] GRP {grp} Zeit abgelaufen -> Schalte OFF")
            luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, 0))
            group_state[grp] = False
            command_sent = True
    
    # Befehl nur ausführen, wenn ein OFF-Kommando in den Puffer geschrieben wurde
    if command_sent:
        luba.execute_tx_buffer()
        
    time.sleep(loop_sleep)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 4 beendet: Alle Gruppen erfolgreich abgeschaltet ==")