"""
(Szenario 91):
---------------------------------------------------
Dieses Szenario dient der Charakterisierung der Hardware durch eine lineare 
aufsteigende Performance-Rampe. Es ist für elektrische und radiometrische 
Messungen optimiert.

1. ABLAUF:
   Das System durchläuft 10 Helligkeitsstufen in 10%-Schritten (10% bis 100%).

2. MESS-INTERVALLE:
   - Belichtung: Jede Stufe leuchtet für 10 Sekunden (ON).
   - Referenz-Pause: Zwischen den Stufen folgt eine 20-sekündige Dunkelphase (OFF). 
     Dies dient der thermischen Stabilisierung und der Messung des Dunkelstroms.

3. ZIELGRUPPEN:
   Alle vier Gruppen (0, 1, 2, 3) werden simultan geschaltet, um die maximale 
   Systemlast und Gesamtrahlungsleistung zu erfassen.
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
start_pause = 5       # Vorlaufzeit (Sekunden)
loop_sleep = 0.2      # Taktung der Überwachung
on_time = 10          # Dauer der aktiven Messung pro Stufe (Sekunden)
off_time = 20         # Dauer der Stabilisierung/Dunkelmessung (Sekunden)
groups = [0, 1, 2, 3] # Alle verfügbaren Gruppen

# Aufsteigende Helligkeitsstufen
power_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# =============================================================================
# HILFSFUNKTION
# =============================================================================
def set_all_active(percent):
    """Schaltet alle definierten Gruppen auf den Zielwert."""
    dali_val = perc_to_dali(percent)
    for grp in groups:
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] Mess-Status: {status}")

# =============================================================================
# HAUPT-MESSABLAUF
# =============================================================================
print(f"== Szenario 91: Performance-Test startet in {start_pause}s ==")
time.sleep(start_pause)



for percent in power_levels:
    print(f"\n>>> STARTE MESSPUNKT: {percent}% Helligkeit")
    
    # 1. SCHRITT: Einschalten auf Ziel-Level
    set_all_active(percent)
    
    # 2. SCHRITT: Haltezeit für Messung
    start_time = time.time()
    while (time.time() - start_time) < on_time:
        time.sleep(loop_sleep)
    
    # 3. SCHRITT: Ausschalten für Dunkelreferenz / Abkühlung
    print(f"    Messpunkt {percent}% beendet. Start Pause ({off_time}s)...")
    set_all_active(0)
    time.sleep(off_time)

# =============================================================================
# ABSCHLUSS
# =============================================================================
print("\n== Szenario 91 beendet: Alle Messpunkte erfasst ==")