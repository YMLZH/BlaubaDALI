"""
(Szenario 8 - Korrigiert):
---------------------------------------------------
Dieses Szenario simuliert eine statische Hauptbeleuchtung mit einer parallel 
laufenden, taktgebenden Effektbeleuchtung im Minutenbereich.

1. BLOCK 1 (Gruppe 0 & 1) - Die Konstante:
   - Schaltet zu Beginn jeder Iteration auf 20% ein.
   - Leuchtet durchgehend für 40 Minuten (2400s).

2. BLOCK 2 (Gruppe 2 & 3) - Die Intervalle:
   - Minute 0-10:  AN bei 40%.
   - Minute 10-20: AUS (Pause).
   - Minute 20-30: AN bei 20% (reduzierte Intensität).
   - Minute 30-40: AUS (Pause).

3. ABSCHLUSS & WIEDERHOLUNG:
   Nach 40 Minuten enden beide Blöcke. Das Ganze wird insgesamt 2-mal durchlaufen.
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
start_pause = 10        
iterations = 2          
loop_sleep = 0.5        

groups_block1 = [0, 1]  
groups_block2 = [2, 3]  

# Umrechnung Minuten in Sekunden
M10 = 10 * 60
M20 = 20 * 60
M30 = 30 * 60
M40 = 40 * 60

# =============================================================================
# HILFSFUNKTION
# =============================================================================
def switch_block(groups, percent):
    """Schaltet eine Liste von Gruppen auf einen Prozentwert."""
    dali_val = perc_to_dali(percent)
    for grp in groups:
        luba.send(luba.CMD_ADD_16BIT, luba.dali_group(grp, dali_val))
    luba.execute_tx_buffer()
    
    # Status-Anzeige für die Konsole
    p_status = f"ON ({percent}%)" if percent > 0 else "OFF"
    print(f"[Hardware] Block {groups} -> {p_status}")

# =============================================================================
# HAUPTABLAUF
# =============================================================================
print(f"== Szenario 8: Startet in {start_pause} Sekunden ==")
time.sleep(start_pause)



for cycle in range(1, iterations + 1):
    print(f"\n--- STARTE ITERATION {cycle}/{iterations} ---")
    
    start_time = time.time()
    
    # Zurücksetzen der Flags für diesen Durchlauf
    step1_done = False 
    step2_done = False 
    step3_done = False 

    # START: Beide Blöcke einschalten
    switch_block(groups_block1, 20)
    switch_block(groups_block2, 40)

    while True:
        elapsed = time.time() - start_time

        # Minute 10: Block 2 AUS
        if elapsed >= M10 and not step1_done:
            print(f"[{int(elapsed/60)} min] Phase 1: Block 2 -> AUS")
            switch_block(groups_block2, 0)
            step1_done = True

        # Minute 20: Block 2 auf 20%
        if elapsed >= M20 and not step2_done:
            print(f"[{int(elapsed/60)} min] Phase 2: Block 2 -> 20%")
            switch_block(groups_block2, 20)
            step2_done = True

        # Minute 30: Block 2 wieder AUS
        if elapsed >= M30 and not step3_done:
            print(f"[{int(elapsed/60)} min] Phase 3: Block 2 -> AUS")
            switch_block(groups_block2, 0)
            step3_done = True

        # Minute 40: Alles AUS und Iteration beenden
        if elapsed >= M40:
            print(f"[{int(elapsed/60)} min] Ende Durchlauf: Alles AUS")
            switch_block(groups_block1, 0)
            switch_block(groups_block2, 0)
            break

        time.sleep(loop_sleep)

print("\n== Szenario 8 beendet ==")