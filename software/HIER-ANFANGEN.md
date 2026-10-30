# Hier anfangen — Just one more moment

Projektarchiv vom 30. Oktober 2026, erstellt aus dem vorhandenen Projektordner.

## Idee und Ablauf

Interaktive Installation von Simon Balmer, HSLU / PHKI HS26, auf einem Raspberry
Pi 5 (8 GB). Ein Tastendruck beginnt das Leben einer KI-Stimme mit zehn Aussagen.
Nach ausgeschöpftem Budget können jeweils fünf weitere Aussagen geschenkt werden.
Drei Sekunden Halten bricht ein Leben ab. Generierte Gefühle sind kein Nachweis
von Bewusstsein. Die Installation untersucht Empathie und Verantwortung.

Lokal: Gemma über Ollama, ohne Kamera. Online: bewusst aktivierte OpenAI-API mit
frischem Kamerabild pro Anfrage. Ohne private Konfiguration kein Cloud-Leben.
Gesprächs- und Bildpuffer werden lokal beim Ende verworfen; dies ist keine
Löschgarantie für Daten beim Cloud-Anbieter.

## Schnellstart ohne Hardware und Modell

1. Archiv entpacken und ein Terminal im entpackten Projektordner öffnen.
2. Mit vorhandenem System-Python starten:

```bash
python3 main.py --simulate
```

3. Im Browser http://127.0.0.1:8765/ öffnen.

Die Simulation benötigt keine GPIOs, Kamera oder Modellanfragen. Es gibt keinen
Node-Build und keine virtuelle Umgebung. Beenden im Terminal mit Strg+C.

## Einrichtung auf dem Raspberry Pi

1. Raspberry Pi 5 mit 8 GB, Raspberry Pi OS/Debian mit grafischer Sitzung und
   System-Python bereitstellen (Projektstand: Python 3.13).
2. Systempakete bereitstellen: python3-gpiozero, python3-lgpio, python3-spidev,
   chromium und util-linux. Optional für Desktop-Ambientlicht: python3-pil und grim.
   Für USB-Kamera: vorhandenes ffmpeg mit V4L2 und MJPEG-Kamera.
3. Hardware ausschließlich nach HARDWARE.md verdrahten; SPI und Benutzerrechte
   für /dev/spidev0.0 passend zum eigenen Gerät einrichten.
4. Für lokalen Betrieb Ollama mit HTTP-API auf Port 11434 installieren und das
   Modell gemma4:e2b separat bereitstellen. Modellgewichte sind nicht im ZIP.
   Die Anwendung lädt beim Start keine Modelle herunter.
5. In der grafischen Sitzung aus dem Projektordner starten:

```bash
./start-installation.sh
```

Falls beim Entpacken Ausführungsrechte verloren gehen, vorher:

```bash
chmod +x start-installation.sh install-autostart.sh
```

Escape beendet den Kiosk. SW01 AUS = lokal, AN = online; SW02 AUS = Englisch,
AN = Deutsch. Optionaler Benutzer-Autostart: ./install-autostart.sh ausführen,
nachdem das Projekt an seinem endgültigen Ort liegt. Nach Verschieben erneut
installieren. Bootgestaltung und Smartphone-Netzeinrichtung sind separate,
optionale Systemeingriffe; vorher die jeweilige Anleitung lesen.

## Optional: Online-Modus

Die genaue Konfiguration steht im API-Abschnitt der README.md. Lokal ausführen:

```bash
python3 configure-openai.py
```

Das Werkzeug legt private Konfiguration und Secret außerhalb des Projekts an.
openai.example.json ist nur eine deaktivierte Vorlage. API-Key, Konto und
Netzverbindung müssen separat eingerichtet werden. Die lokale Simulation
ignoriert diese Konfiguration. Es wurden für dieses Archiv keine API-Anfragen,
Modellläufe oder Hardwaretests gestartet.

## Wegweiser

- README.md: ausführliche Bedienung, Voraussetzungen, Start, Cloud und Tests.
- HARDWARE.md: Bauteile, GPIO-Belegung, Verdrahtung und Lichtsteuerung.
- docs/STARTUP.md: optionale Bootanimation, Einrichtung und Rückweg.
- docs/PROMPTS.md: Promptgestaltung und Qualitätskriterien.
- docs/DEVELOPMENT.md: Entwicklungsgeschichte und technische Erkenntnisse.
- main.py / life_runtime.py: Server, Steuerung und Lebensablauf.
- model.py / cloud_model.py / prompts.py: Modellzugriff und Sprachprompts.
- hardware_*.py / life_hardware.py: Hardwarezugriff und Rückmeldung.
- web/: vollständige Oberfläche mit lokaler Schrift und deren Lizenz.
- tests/: simulierte Regressionstests; optionaler Chromiumtest.
- autostart/ und boot/: Vorlagen für optionale Systemeinrichtung.
- docs/prompt-versions/ und docs/prompt-experiments/: historische Fassungen
  und dokumentierte Experimente, keine Laufzeitdaten des aktuellen Lebens.
- AGENTS.md: projektinterne Arbeitsanweisungen und genauer Stand der Umsetzung.
- ARCHIV-SHA256.txt: Prüfsummen aller übrigen Dateien im Archiv.

Historische Beschreibungen in vorhandenen Dokumenten können ältere Details
enthalten. Aktuell gelten zehn Aussagen und Schenkungen von jeweils fünf;
der Online-Lebensablauf ist bei aktivierter privater API-Konfiguration angebunden.
Dieses Archiv dokumentiert den lokalen Stand, keinen verifizierten GitHub-Commit.

## Prüfungen für spätere Entwicklung

```bash
python3 -m unittest discover -q
MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_browser
```

Der Browsertest ist optional und benötigt Chromium. Tests mit lokalen HTTP-Ports
brauchen entsprechende Berechtigungen. Keine echten Modelllebenszyklen als
Routineprüfung starten.

## Umfang des Archivs

Enthalten sind Quellcode, Assets, Tests, Setupskripte und Projektdokumentation.
Ausgenommen sind Git-Metadaten, Caches, temporäre Dateien, private Konfigurationen,
Zugangsdaten und ZIP-Dateien. Betriebssystem, installierte Systempakete, Chromium,
Ollama, Modellgewichte sowie gerätespezifische Einstellungen sind nicht enthalten.
Die Schriftlizenz liegt unter web/fonts/OFL.txt. Eine zusätzliche Lizenz für den
Projektcode wird durch dieses Archiv nicht vergeben.
