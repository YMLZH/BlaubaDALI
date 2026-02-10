"""
HOLISTISCHE BETRACHTUNG DES LED-OUTPUTS (Szenario 6 - Zeitangepasst):
---------------------------------------------------
Dieses Szenario erzeugt eine "langsame absteigende Puls-Rampe" für Gruppe 0 und 1.
Es simuliert Belichtungsintervalle mit langen Erholungsphasen bei sinkender Intensität:

1. ABLAUF: 11 Helligkeitsstufen von 100% bis 50% in 5%-Schritten.

2. NEUE ZEIT-LOGIK (Intervall-Training):
   - Belichtungsphase: 3 Minuten (180s) AN pro Helligkeitsstufe.
   - Regenerationsphase: 30 Minuten (1800s) AUS (Dunkelheit) nach jeder Stufe.

3. ZIELGRUPPEN: Nur Gruppe 0 und Gruppe 1.

Gesamtdauer: Ca. 333 Minuten (~5,5 Stunden).
Ideal für: Langzeitstudien zur Erholungsrate bei intermittierender Belichtung.
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
start_pause = 10        # Vorlaufzeit vor Szenario-Beginn
duration_on = 180       # Belichtung: 3 Minuten (3 * 60s)
duration_off = 1800     # Ruhephase: 30 Minuten (30 * 60s)
active_groups = [0, 1]  # Betroffene DALI-Gruppen

# Helligkeitsstufen von 100% abwärts bis 50%
percent_steps = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50]

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================
def set_groups(groups, percent):
    """Setzt eine Liste von Gruppen auf einen Prozentwert."""
    dali_val = perc_to_dali(percent)
    for grp in groups:
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] Gruppen {groups} -> {status}")

# =============================================================================
# HAUPTABLAUF
# =============================================================================
print(f"== Szenario 6: Startet in {start_pause} Sekunden ==")
time.sleep(start_pause)



for i, percent in enumerate(percent_steps, start=1):
    print(f"\n>>> INTERVALL {i}/{len(percent_steps)}: {percent}% Helligkeit")
    
    # 1. BELICHTUNGSPHASE (3 Min)
    set_groups(active_groups, percent)
    print(f"    Bestrahlung läuft für {duration_on // 60} Min...")
    time.sleep(duration_on)
    
    # 2. RUHEPHASE (30 Min) - nur wenn es nicht der letzte Schritt ist
    if i < len(percent_steps):
        set_groups(active_groups, 0)
        print(f"    Ruhephase läuft für {duration_off // 60} Min...")
        time.sleep(duration_off)

# =============================================================================
# ABSCHLUSS
# =============================================================================
set_groups(active_groups, 0)
print("\n== Szenario 6 beendet: Alle Intervalle abgeschlossen ==")