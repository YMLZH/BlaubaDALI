"""
(Szenario 3):
---------------------------------------------------
Dieses Szenario erzeugt eine absteigende Helligkeits-Rampe (Stufen-Dimmung). 
Es simuliert eine schrittweise Reduzierung der Lichtintensität über einen 
längeren Zeitraum für die Gruppen 0, 1, 2 und 3:

1. ABLAUF: Das System durchläuft nacheinander 5 Helligkeitsstufen:
   100% -> 80% -> 60% -> 40% -> 20%.

2. TIMING PRO STUFE: 
   - Jede Stufe leuchtet für 2 Minuten (120s).
   - Es folgt eine Regenerationspause von 30 Minuten (1800s), bevor die 
     nächste (dunklere) Stufe zündet.
"""

import time
from core.dali_system import luba, perc_to_dali

# =============================================================================
# INITIALISIERUNG & HELFER
# =============================================================================
# Puffer leeren, um einen sauberen Start zu gewährleisten
luba.clear_tx_buffer()

def set_all_groups(percent):
    """Setzt die Gruppen 0, 1, 2 und 3 simultan auf den gewünschten Wert."""
    dali_val = perc_to_dali(percent)
    for grp in [0, 1, 2, 3]:
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    
    status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] Alle Gruppen (0-3) -> {status}")

# =============================================================================
# KONFIGURATION
# =============================================================================
start_pause = 5         # Vorlaufzeit vor Szenario-Beginn
on_time = 120           # Leuchtdauer pro Helligkeitsstufe (Sekunden)
pause_after = 1800      # Pause nach jeder Leuchtphase (Sekunden)

# Die nacheinander abzuarbeitenden Helligkeitsstufen
routine_percents = [100, 80, 60, 40, 20]

# =============================================================================
# HAUPTPROGRAMM (Szenario-Steuerung)
# =============================================================================
print(f"== Szenario 3: Start-Pause {start_pause} Sekunden ==")
time.sleep(start_pause)

# 

# Durchlauf der Helligkeits-Rampe
for i, percent in enumerate(routine_percents):
    print(f"\n>>> Starte Stufe {i+1}/{len(routine_percents)}: {percent}% Helligkeit")
    
    # 1. SCHRITT: Licht einschalten
    set_all_groups(percent)
    
    # 2. SCHRITT: Haltezeit (Leuchtphase)
    print(f"    Leuchtphase für {on_time}s läuft...")
    time.sleep(on_time)
    
    # 3. SCHRITT: Licht ausschalten
    set_all_groups(0)
    
    # 4. SCHRITT: Regenerationspause (außer nach der allerletzten Stufe)
    if i < len(routine_percents) - 1:
        print(f"    Leuchtphase beendet. Starte Pause: {pause_after}s...")
        time.sleep(pause_after)
    else:
        print("    Letzte Stufe beendet.")

print("\n== Szenario 3 beendet: Helligkeits-Rampe komplett durchlaufen ==")