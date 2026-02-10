"""
(Szenario 92):
---------------------------------------------------
Dieses Szenario ist eine spezialisierte Variante der Performance-Rampe, die sich 
ausschließlich auf die Einzel-Charakterisierung von Gruppe 0 konzentriert.

1. ABLAUF:
   Lineare Steigerung der Helligkeit in 10 Stufen (10% bis 100%) nur für GRP 0.

2. MESS-INTERVALLE:
   - Belichtung: 10 Sekunden (ON) pro Stufe für die radiometrische Erfassung.
   - Referenz-Pause: 20 Sekunden (OFF) zwischen den Stufen zur thermischen 
     Entlastung und Nullpunkt-Kalibrierung der Messgeräte.

3. ZIELGRUPPEN:
   Nur Gruppe 0. Alle anderen Gruppen (1, 2, 3) bleiben während des gesamten 
   Szenarios permanent ausgeschaltet.

Ideal für: Kalibrierung einzelner LED-Treiber-Kanäle und Ermittlung der 
spezifischen Effizienz einzelner Gruppen.
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
start_pause = 5       
loop_sleep = 0.2      
on_time = 10          # Messdauer (Sekunden)
off_time = 20         # Beruhigungszeit (Sekunden)
active_groups = [0]   # Exklusiv Gruppe 0

# Test-Rampe
power_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# =============================================================================
# HILFSFUNKTION
# =============================================================================
def set_test_groups(groups, percent):
    """Schaltet die Zielgruppen auf den gewünschten Level."""
    dali_val = perc_to_dali(percent)
    for grp in groups:
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] Einzelkanal-Test GRP {groups} -> {status}")

# =============================================================================
# HAUPT-MESSABLAUF
# =============================================================================
print(f"== Szenario 92: Einzelkanal-Test (GRP 0) startet in {start_pause}s ==")
time.sleep(start_pause)



for percent in power_levels:
    print(f"\n>>> MESS-PUNKT: GRP 0 auf {percent}%")
    
    # 1. SCHRITT: ON-Phase
    set_test_groups(active_groups, percent)
    
    # 2. SCHRITT: Haltezeit
    start_time = time.time()
    while (time.time() - start_time) < on_time:
        time.sleep(loop_sleep)
    
    # 3. SCHRITT: OFF-Phase (Dunkelreferenz)
    print(f"    Messung beendet. Dunkelpause ({off_time}s) läuft...")
    set_test_groups(active_groups, 0)
    time.sleep(off_time)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 92 beendet: Kanal-Charakterisierung abgeschlossen ==")