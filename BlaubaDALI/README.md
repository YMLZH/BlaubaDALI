### DALI Lighting Control System (Luba-Core)
Dieses System ermöglicht die automatisierte Steuerung von DALI-Leuchten über einen Raspberry Pi, inklusive physischer Interaktion über ein Matrix-Keypad und ein robustes State-Management.

# Projektstruktur
.
├── main.py                 # Zentraler Einstiegspunkt & Szenarien-Auswahl
├── requirements.txt        # Python Abhängigkeiten (pyserial, RPi.GPIO)
├── README.md               # Diese Dokumentation
│
├── blaubadali/             # Luba-Protokoll & Treiber-Ebene
│   ├── __init__.py
│   ├── config.py           # Serielle Parameter (Port, Baudrate, Timeouts)
│   └── luba.py             # Low-Level Byte-Befehle für den DALI-Master
│
├── core/                   # System-Logik & Abstraktion
│   ├── __init__.py
│   ├── dali_system.py      # High-Level Befehle (Nutzt blaubadali)
│   └── state.py            # Globales State-Management
│
├── hardware/               # Physische Komponenten
│   ├── __init__.py
│   └── keypad.py           # Treiber & Logik für das Matrix-Keypad
│
└── scenarios/              # Bibliothek der Belichtungsmuster
    ├── scenario_1.py       # Full-House Belichtung
    ├── scenario_2.py       # Duo-Zonen-Belichtung
    ├── scenario_3.py       # Intensitäts-Gradient
    ├── scenario_4.py       # Asynchrone Zwei-Zonen-Beleuchtung
    ├── scenario_5.py       # Zyklische Belichtung mit Regenerationspause
    ├── scenario_6.py       # Absteigende Puls-Rampe (Langzeit)
    ├── scenario_7.py       # Multithreading (Parallel-Zeitpläne)
    ├── scenario_8.py       # Parallelbetrieb (Konstante + Pulse)
    ├── scenario_9.py       # Asymmetrischer Belichtungszyklus
    ├── scenario_91.py      # Performance-Test (Alle Gruppen)
    └── scenario_92.py      # Performance-Test (Nur Gruppe 0)
│
├── .ssh/                       # SSH-Informationen (nicht Projektrelevant, NUR für Updates relevant --> Ordner mit Inhalt lokal speichern)
│   ├── blaubad_rpi_key         # key-Datei für ssh auf den RasPi
│   ├── blaubad_rpi_key.pub     # key-Datei für ssh auf den RasPi in anderem Format
│   └── known_hosts             # Host-Datei für die key-Zuordnung

### Projekt-Update / Datei-Upload
# Die vier nachfolgenden Befehlte können in Gänze in der App PowerShell eingefügt werden und werden anschließend nacheinander ausgeführt. 
# Mit dieser Methode entfällt der login auf dem RasPi, alle Logins erfolgen automatisch mithilfe des Ordners .ssh.
# Die Abfolgde der Befehle stopt automatisch noch laufende Projekte auf dem RasPi, löscht das dort gespeicherte Projekt, spiechert ein neues Projekt an den selben Ablageort und aktiviert die live-Textausgabe per ssh
# Voraussetzung für den reibungslosen Ablauf ist:
#   1. Existenz des .ssh Ordners (nicht im Projekt lassen, schiebe den Ordner zuvor unter z.B. C:/User/Username)
#   2. Passe den Pfad, von dem aus das geupdatete Script kopiert werden soll in Befehl Nr. 2 an "C:\BlaubaD-Tests\BlaubaDALI" <-- hier deinen Pfad eingeben
#   3. Stelle eine Verbindung zwischen PC und RasPi her. Der RasPi ist im Netz "TP-Link_1984_5G" des LZH registriert, die Verbindung zwischen RasPi und Router muss nach aktuellem Stand jedoch per Ethernet erfolgen. Der ausführende PC muss sich im gleichen Netzwerk befinden (WLAN/Ethernet)
#   4. Wenn 1., 2. und 3. erfüllt sind, starte PowerShell und gebe die vier angepassten Befehle einzeln oder gesammelt in der Konsole ein.

ssh -i $env:USERPROFILE\.ssh\blaubad_rpi_key blaubad@192.168.1.102 "rm -rf ~/BlaubaDALI ~/dali-test* ~/blauba*"     
scp -i $env:USERPROFILE\.ssh\blaubad_rpi_key -r C:\BlaubaD-Tests\BlaubaDALI blaubad@192.168.1.102:~/
ssh -i $env:USERPROFILE\.ssh\blaubad_rpi_key blaubad@192.168.1.102 "sudo systemctl restart blaubadali.service"
ssh -i $env:USERPROFILE\.ssh\blaubad_rpi_key blaubad@192.168.1.102 "journalctl -u blaubadali.service -f -n 20"