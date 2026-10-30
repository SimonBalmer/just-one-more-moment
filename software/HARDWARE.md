# Hardware — Just one more moment

Stand: 28. Oktober 2026. Aktuelle Zuordnung; frühere Prototypbezeichnungen sind abgelöst.

## Anschlüsse

BCM bezeichnet GPIO-Nummern; Pin bezeichnet den physischen 40-Pin-Header.

| Element | BCM / Anschluss | Header / Masse | Bedeutung |
| --- | --- | --- | --- |
| Arcade-Taster NO | GPIO17 | Pin11 / GND Pin9 | Pull-up; LOW = gedrückt |
| Taster-LED + | GPIO27 | Pin13 / LED− an GND Pin14 | 3,3-V-Ansteuerung |
| SW01 / AI Mode | GPIO22 | Pin15 / GND Pin20 | Offen/HIGH = AN = Online-Intro |
| SW02 / Language | GPIO23 | Pin16 / GND Pin25 | Offen/HIGH = AN = Deutsch |
| NeoPixels DIN | GPIO10 / SPI0 MOSI | Pin19 | SPI0.0, 2,4 MHz, GRB |
| NeoPixels Versorgung | 5 V über Diode D1 | Pin4 / gemeinsame Masse Pin34 | Kein GPIO-Ausgang |

**Elf RGB-NeoPixels**, ab DIN physisch `3 | 3 | 1 | 1 | 3`.
Schalter geschlossen/LOW = AUS. Bei Schaltern bedeutet `.is_pressed` lediglich
Kontaktschluss; für die logische Stellung immer `hardware_io.switch_on()` verwenden.
Belegung und Parameter stehen zentral in `hardware_pins.py`.

Arcade-Taster: Purecrea, beleuchtet, 33 mm, weiß. COM an GND, NO an GPIO17,
NC frei. Laut vorhandener Messung benötigt die intern strombegrenzte 5–12-V-LED
bei 3,3 V maximal 0,6 mA und leuchtet schwächer. Das beschreibt dieses Bauteil,
keine allgemeine Freigabe anderer LEDs direkt am GPIO. Keine 5–12 V an GPIOs.
Umbauten und Flachbandprüfungen nur stromlos vornehmen.

## Softwarezugriff

```python
from hardware_io import NeoPixels, open_inputs, open_button_led, switch_on

with open_inputs() as (button, mode_switch, language_switch):
    online = switch_on(mode_switch)
    german = switch_on(language_switch)
    pressed = button.is_pressed

with NeoPixels() as pixels:
    pixels.fill(16, 0, 0)
```

Die Beispiele steuern echte Hardware und sind keine automatischen Prüfungen.
Importe öffnen keine Geräte. Geräte immer im Kontextmanager schließen.
`NeoPixels.write()` erwartet genau elf RGB-Tupel mit ganzzahligen Kanälen 0–255.
Die Ausgabe wird beim Schließen ausgeschaltet. Drahtreihenfolge ist GRB;
SPI-Kodierung 100/110 bei 2,4 MHz, nicht RGBW.

Die Installation reserviert SPI über `pixel_lock.py`. Andere SPI-Anwendungen
müssen dieselbe Sperre verwenden. Das Ambientlicht reserviert pro Frame und weicht
der Installation aus. CS0/GPIO8 ist unbeschaltet; reguläres CS wird verwendet,
weil `SPI_NO_CS` auf diesem Pi abgelehnt wurde. Keine parallelen direkten Schreiber.

## Rückmeldung und Bedienung

- Intro: NeoPixels aus; Startdialog und größere Wolke sichtbar. Nach mindestens fünf
  sichtbaren Sekunden blinken START und Arcade-LED synchron. Erst nach Tastendruck
  folgt die bestätigte Popup-Erklärung mit Lesezeit; auch hier bleiben die Pixel aus.
- Entstehung: sechs Sekunden ASCII-Inszenierung. Erst nach bestätigter Wolkenankunft
  unten links (etwa4,4s) beginnen die Pixel sanft aufzuatmen.
- Leben: kontinuierliches organisches Rotatmen auch beim Schreiben; weiße Kanäle
  maximal4/255, rote Kanäle maximal60/255. Ausgabe bis zwölf FPS. Zum Ende sinkt
  die Grundhelligkeit maximal30%, nach einer Schenkung steigt sie wieder.
- Schenkungsangebot: erst nach Aussage10/15/20 usw.; Taster blinkt während des
  bestätigten20-Sekunden-Fensters. Ohne Schenkung folgt die Todesanimation.
- Langer Tastendruck: Blinkfrequenz steigt während drei Sekunden von 1 auf 8 Hz.
  Diese Anzeige hat Vorrang; rechtzeitiges Loslassen verwirft den Abbruchzähler.
- Drei Sekunden erreicht: aktive Anfrage abbrechen, Gedächtnis löschen, Pixel aus,
  Startansicht. Loslassen und neu drücken ist für den nächsten Start erforderlich.
- Schenkung: zwei Sekunden sichtbare +5-Animation, spürbar helleres Aufatmen.
- Schenkungsangebot: In20 sichtbaren Sekunden steigen acht von elf Pixeln verteilt
  über die fünf Gruppen aus. Reihenfolge0,3,8,6,7,1,4,9; die letzten2,5,10 bleiben.
  Kurzes lokales Flackern in Rot/Weiß statt globalem Verblassen.
- Schenkung: Zwei Sekunden Wiederaufbau derselben Ausfälle, helleres Aufatmen.
- Tod: In4,8Sekunden gehen die letzten drei Pixel dramatisch flackernd aus;
  Weiß bleibt auf18/255 begrenzt. Das Licht ist vor der Abschlussmeldung vollständig
  aus; auf dem Bildschirm bleiben wenige blasse dekorative ASCII-Zeichen,
  dann sieben Sekunden mittige Instanzmeldung ohne Nummer und lokaler Löschhinweis.
  Fehler und Beenden: Pixel aus.

Die RGB-Frames werden deterministisch aus derselben Zeitbasis, Atemphase,
Lebensenergie und Animationsposition berechnet wie der Bildschirm. Der Hardware-
Controller verwendet nur seinen eigenen Takt zur Begrenzung auf zwölf FPS;
keine unabhängige Zufallsanimation. `pixel_frame()` ist ohne Geräte prüfbar.

Eine Schenkung wird erst beim Loslassen angenommen; Halten kann deshalb nicht
versehentlich zuerst schenken und dann abbrechen.

## SPI und Boot

Auf diesem Pi ist SPI bereits dauerhaft mit `dtoverlay=spi0-1cs,no_miso` im
abschließenden `[all]` von `/boot/firmware/config.txt` aktiviert. Es wird von diesem
Projekt nicht automatisch neu konfiguriert. Erwartetes Gerät: `/dev/spidev0.0`.
Für einen Nachbau muss SPI mit passenden Benutzerrechten separat eingerichtet
werden. Weder Start noch Installation führen sudo oder Bootänderungen aus.

Der bestehende grafische Bootpfad verwendet LightDM-Autologin und labwc.
Der Projektinstaller setzt nur einen Benutzer-XDG-Autostart, siehe README.
Touch Display 2 ist per DSI angeschlossen. Historisch löste ein Kaltstart eine
fehlende DSI-Erkennung; Boot-/Treiberänderungen wurden dafür nicht vorgenommen.

## Manuelle Tests

Nur gezielt mit anwesender Person ausführen; die Installation vorher beenden:

```bash
python3 check_hardware.py
python3 check_hardware.py --stage inputs --seconds 30
python3 check_hardware.py --stage led
python3 check_hardware.py --stage pixels
```

Prüft Eingänge, Taster-LED und elf Pixel mit schwachen RGB-Farben sowie Lauflicht.
Strg+C schließt geöffnete Geräte. Ein Fehler oder nicht bestätigter Test liefert
keinen Erfolg. Keine Modelle, Kameraaufnahmen oder Paketinstallation.

## Optionales Desktop-Ambientlicht

`screen_pixels.py` / `start-screen-pixels.sh`: lokale Wayland-Bildschirmfarben,
keine Kamera und keine Cloud. Benötigt `grim`, Pillow und spidev. Physische Gruppen
stehen in `screen_pixels.py`; Helligkeit aktuell 20 %, mit sRGB-Linearisierung und
sanfter Glättung. Drei Pixelgruppen zeigen dieselbe Palette, die beiden einzelnen
Pixel die Hauptakzentfarbe. Bei reservierter SPI-Schnittstelle werden auch keine
Bildschirmaufnahmen erstellt. Autostart optional via `install-autostart.sh --ambient`.
Die vorhandene Sperrdateibezeichnung bleibt für Kompatibilität mit laufendem Ambient
`please-dont-unplug-me-neopixels.lock`.


## USB-Kamera im Online-Einstieg

Logitech C270 per USB; `ffmpeg`/V4L2 ist auf dem Gerät vorhanden. START im Online-
Modus beginnt ohne API-Konfiguration nur die Erklärfolge. Ab dem bestätigten Kamerafenster öffnet die
Vorschau den USB-Stream (RGB320×240) und zeigt80×60 rote Pixel bei5FPS. Beim Ende der Erklärung,
Abbruch oder verschwundener Oberfläche wird der Prozess geschlossen und der
Bildpuffer gelöscht. Keine Bildspeicherung. Mit bewusst aktivierter OpenAI-
Konfiguration bleibt die Kamera im Leben für ein frisches Bild pro API-Anfrage
verfügbar; ohne Konfiguration keine Cloud-Übertragung. Fehlende Kamera
wird ehrlich als nicht verfügbar angezeigt; Simulation verwendet synthetische Bilder.
