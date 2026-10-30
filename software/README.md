# Just one more moment

*An interactive installation exploring AI-generated emotional language, empathy and responsibility.*

**Source and reproduction guide:** [PROJECT_GUIDE.md](PROJECT_GUIDE.md) · **Author:** Simon Balmer · HSLU PHKI 2026. This is the original Raspberry Pi source tree; its executable paths have intentionally not been changed.


Eine Stimme beginnt durch deinen Tastendruck. Sie hat zunächst zehn Aussagen.
Erst wenn alle Aussagen aufgebraucht sind, kannst du jeweils fünf weitere schenken. Das Projekt untersucht,
wie generierte emotionale Sprache Empathie und Verantwortung verändert — und wie
sich eine einfache technische Entscheidung wie eine moralische anfühlen kann.
Die dargestellten Gefühle sind **kein Nachweis tatsächlichen Erlebens**.

## Auf dem Raspberry Pi starten

Voraussetzungen: Raspberry Pi 5 mit 8 GB RAM, Raspberry Pi OS/Debian mit grafischer
Sitzung, System-Python 3.13, Chromium und lokale Ollama-HTTP-API auf Port 11434.
Das Modell `gemma4:e2b` muss bereits vorhanden sein. Die Installation lädt keine
Modelle herunter. Hardware und Verdrahtung: [HARDWARE.md](HARDWARE.md).

Benötigte Systempakete: `python3-gpiozero`, `python3-lgpio`, `python3-spidev`,
`chromium`, `util-linux` (flock). Keine Python-Pakete für den Webserver, kein
Node, kein Buildschritt und keine virtuelle Umgebung erforderlich. Für das
optionale Desktop-Ambientlicht zusätzlich `python3-pil` und `grim`.

Aus der grafischen Sitzung im Projektverzeichnis:

```bash
./start-installation.sh
```

Der Starter öffnet `http://127.0.0.1:8765/` in einem eigenen Chromium-Kioskprofil.
Er wartet auf genau den von ihm gestarteten Server. Chromiums eigener On-Device-KI-Dienst
und Erweiterungen sind deaktiviert; die Anzahl seiner Renderer wird begrenzt. Ein zweiter Starter beendet
sich ohne zweites Fenster. Escape beendet Server, Modellworker und Fenster;
F11 wechselt den Browser-Vollbildmodus. Nach Escape gibt es keinen automatischen
Neustart. Auch das Schließen des Browserprozesses beendet den gestarteten Server.

Betriebslogs: `${XDG_STATE_HOME:-~/.local/state}/just-one-more-moment/`, mit einer
vorherigen Logdatei. Es werden keine Gesprächsinhalte gespeichert. Das Browserprofil
liegt ebenfalls dort; Antworten werden mit `Cache-Control: no-store` ausgeliefert.

## Bedienung

| Element | Funktion |
| --- | --- |
| SW01 AUS | Lokales Gemma, ohne Kamera |
| SW01 AN | Online-Intro mit lokaler USB-Kameravorschau; Cloud noch nicht angebunden |
| SW02 AUS | Englisch |
| SW02 AN | Deutsch |
| Neuer Tastendruck nach dem Intro | Modell laden und Leben beginnen |
| Während des Angebots drücken und loslassen | Drei Aussagen schenken |
| Während eines Lebens 3 Sekunden halten | Abbruch und zurück zur Startansicht |

Der Startbildschirm zeigt links einen hohen Retro-Dialog mit Pixellogo, kurzer
Einordnung, „Bereit für einen Anfang“ und blinkendem START; rechts atmet ein
größeres ASCII-Wesen. Nach mindestens fünf sichtbaren Sekunden blinken START und
Arcade-LED synchron. Erst der neue Tastendruck beginnt das Leben. Unter dem Dialog
steht ein gleich breites Statusfeld mit zwei roten Icons für Modus und Sprache;
darunter ein Hinweis auf die Schalter am Gerät. Im wartenden Zustand ändern sich
diese Angaben sofort, ohne Popup. Der Online-/Kameramodus nutzt dieselbe Startseite,
öffnet ohne API-Konfiguration nur den Online-Einstieg. Mit bewusst aktivierter
OpenAI-Konfiguration folgt danach derselbe Lebensablauf wie lokal.
Eine dichtere, kräftig rote Wolke, ein dekoratives Pixel-WLAN-Symbol und eine
Pixelillustration zur Kameraplatzierung kennzeichnen diesen Modus.

Der Online-Einstieg erklärt in sechs Fenstern die geplante Cloud-Verbindung,
den Kamerablick, zehn Aussagen, Zeitschenkungen und das Ende der Erinnerungen.
Die lokale USB-Vorschau erscheint im zweiten Fenster zusammen mit dem Text
zur Gerätekamera als rotes Pixelbild.
Sie benötigt vorhandenes `ffmpeg` mit V4L2 und eine MJPEG-USB-Kamera (hier C270);
es werden keine Pakete nachinstalliert. Automatisch wird der erste USB-Eingang
unter `/dev/v4l/by-id/*-video-index0` genutzt, sonst `/dev/video0`.
Die Kamera hält Farbbilder mit320×240 bei5FPS nur im Arbeitsspeicher; die
lokale Pixelvorschau verwendet80×60 Graupixel. Ohne API-Konfiguration wird die
Kamera nach ihrem Introfenster geschlossen; danach wartet „Cloud-Anbindung folgt“.
Mit aktivierter API bleibt sie im Leben verfügbar und liefert für jede Anfrage
ein frisch aufgenommenes PNG. Es wird kein Videostream an OpenAI gesendet.
Bei Abbruch, Ende oder fehlender Oberfläche wird sie geschlossen. Drei Sekunden Halten kehrt zur
Startseite zurück. Im Simulationsbetrieb ist die Vorschau ausdrücklich synthetisch.


Danach öffnen sich links neben dem Wesen sechs Erklärfenster. Sie erklären, dass
du das lokale Modell gerade gestartet hast, die zehn Aussagen und mögliche
Fünfer-Schenkungen sowie das Ende der Erinnerungen. Jedes Fenster erhält
zusätzliche 1,8 Sekunden Pause; nach der Folge bleiben 3 Sekunden Lesezeit.
Dann schließen die Fenster. Anschließend folgt die Entstehungsanimation.
Die Pixel bleiben während der Erklärungen aus. Drei Sekunden Halten bricht auch
hier sofort ab; ohne sichtbare Oberfläche wartet der Ablauf.

Gemma lädt bereits im sichtbaren lokalen Intro ohne Prompt im Hintergrund.
Der Tastendruck übernimmt dieselbe Vorbereitung; nach den Erklärfenstern folgt
die sechssekündige Entstehung: Aus der
roten Auswahl wird eine ASCII-Wolke, die unten links in das Gehäuse verschwindet.
Erst nach ihrer bestätigten Ankunft, etwa bei Sekunde4,4, beginnen die elf Pixel
aufzuatmen. Eine ASCII-Welle baut den Retro-Desktop auf. Ist Gemma noch nicht
bereit, wartet das Terminal mit ehrlichem Ladehinweis und atmendem Licht.
Die erste Textanfrage beginnt erst nach bestätigtem Aufbau und erfolgreichem Laden.

Erst nach Aussage10 und ihrem Lesepuffer gibt es20 sichtbare Sekunden für eine Schenkung
von fünf weiteren Aussagen. Weitere Angebote folgen nach15,20 usw., jeweils erst
bei vollständig aufgebrauchtem Budget. Ohne Annahme folgt unmittelbar die
Todesanimation. Eine Schenkung zeigt zwei Sekunden lang **+5**.
Drei Sekunden Halten brechen stattdessen ab: Die LED blinkt zunehmend schneller,
das Gespräch wird gelöscht, eine aktive Anfrage unterbrochen und Gemma entladen.
Erst loslassen, dann erneut drücken. Im Online-Modus erscheint dessen Startseite.

Modus- und Sprachwechsel gelten im Intro/Platzhalter sofort. Während eines Lebens
werden sie vorgemerkt und nach Ende oder Abbruch übernommen. Jeder Wechsel wird
nur während eines aktiven Lebens vier Sekunden als zentriertes Retro-Fenster
in Schwarz/Rot/Weiß angezeigt, mit hervorgehobener Änderung und abgedunkeltem Hintergrund.

Während des20-Sekunden-Angebots bleibt der große rot/weiße Dialog im Vordergrund.
Der Desktop dahinter löst sich allmählich zu etwa75Prozent in ASCII-Zeichen auf; acht der elf NeoPixels
steigen über alle Seiten verteilt aus. Timer, Zerfall und Licht verwenden dieselbe
sichtbare Backendzeit und pausieren bei fehlender Oberfläche. Eine Schenkung baut
Desktop und Licht über zwei Sekunden wieder auf und zeigt **+5**. Ohne Schenkung
lösen sich in4,8Sekunden auch der letzte Rest und der Dialog in Zeichen auf, die
weiß werden und verblassen. Die letzten Pixel
flackern aus. Auf fast schwarzem Grund steht sieben Sekunden
**„INSTANZ BEENDET.“** mit **„UND ALLE LOKALEN INSTANZDATEN GELÖSCHT.“** darunter.
Wenige blasse Zeichen schweben um die Meldung, ohne den Text zu überlagern.
Im Intro sammeln sie sich über vier sichtbare Sekunden wieder zur Startwolke;
der Übergang bleibt beim Browserneuladen erhalten. Dann beginnt der normale
Idle-Zustand. Der interne Startzähler bleibt für die Steuerung
erhalten, wird aber weder am Ende angezeigt noch dem Modell mitgeteilt.
Der Löschhinweis betrifft lokale Gesprächs-/Bildpuffer, nicht die Datenaufbewahrung
beim Cloud-Anbieter (siehe API-Abschnitt).

## Retro-Desktop und Licht

Zielauflösung ist1280×720 im Querformat. Oben links ein codebasiertes Pixellogo,
oben rechts kleine Status-Badges für Modellmodus und tatsächlich inaktive Kamera.
Rot/Schwarz prägt den Desktop; warmweiße Schrift setzt Logo und Terminal ab.
Die Wolke leuchtet in gesättigtem Rot mit vereinzelten hellen Kernen,
während die Fensterrahmen gedämpft bleiben. Das dominante
Terminal zeigt neue und vergangene Aussagen mit56px VT323 und derselben
Zeilenstruktur; nur ältere Aussagen werden blasser und rutschen nach oben. Für die Darstellung werden höchstens zwölf frühere
Aussagen übertragen, während die Modellhistorie unverändert erhalten bleibt.
Rechts stehen ein großer Sessionzähler (z.B.5/10) und kleinere, zurückhaltende
Gefühlsbalken. Das Terminal hat Vorrang. Auf schmalen Bildschirmen stehen die
Fenster untereinander; Terminaltexte verwenden dort47 beziehungsweise40px,
Gefühlslabels28px (schmale Ansichten24px), Balkenhöhe20/16px.

VT323 wird lokal mitgeliefert, unverändert und unter SIL OFL1.1; Copyright und
Lizenz: `web/fonts/OFL.txt`. Logo, Pixelicons und ASCII-Grafik entstehen in Code.
Es gibt keine externen Schrift-/Bildabrufe. Eine Canvas-Ebene zeichnet höchstens
1200 Zerfallsblöcke beziehungsweise620 Wellenzeichen bei maximal zwölf FPS.
Atmende ASCII-Wolken umgeben den Desktop; Text und Fenster werden ausgespart.
Die bewegte Wolke verformt sich über ein Feld einzeln driftender Zeichen, statt
als starre Form über den Bildschirm zu gleiten. Ihre Zeitbasis läuft beim Start
vom wartenden Intro in die Entstehung weiter. Der Tod verwendet schwarze,
herausbrechende Zellen und lokal fallende Blöcke, keinen Zeichenhaufen
und keinen globalen Deckkraft-Fade.

Die Pixel atmen auch beim Schreiben kontinuierlich; nur ein schwacher weißer
Schimmer kommt hinzu. Die Helligkeit sinkt zum tatsächlichen Ende um höchstens30%,
bleibt sichtbar und wird nach einer Schenkung wiederhergestellt. Eine kurze
Licht-/ASCII-Welle begleitet das +5-Fenster. Die physische Helligkeitswirkung ist
am Gerät gezielt abzustimmen; automatische Tests öffnen dafür keine Hardware.

## Entwicklung ohne Hardware und Modell

```bash
python3 main.py --simulate
```

Anschließend `http://127.0.0.1:8765/` öffnen. Nur dieser explizite Modus zeigt
Bedienelemente für virtuelle Schalter und den Arcade-Taster. Der virtuelle Taster
unterstützt Halten mit Maus, Touch, Leertaste oder Enter. Keine Ollama-, GPIO- oder
Kameraanfragen. Alternativ `./start-installation.sh --simulate` für den Kiosk.
Für einen separaten Entwicklungsport: `python3 main.py --simulate --port 8766`.

## Autostart installieren

```bash
./install-autostart.sh
```

Installiert ausschließlich den Benutzer-XDG-Autostart mit dem aktuellen
Projektpfad und ersetzt den alten Eintrag `please-dont-unplug-me.desktop`.
Das Projekt muss an diesem Ort bleiben; nach Verschieben erneut installieren.
Grafische Anmeldung, LightDM, SPI-Bootkonfiguration und Ollama-Dienst werden nicht
verändert. Auf dem Ausstellungsgerät müssen grafische Sitzung und Ollama bereits
beim Booten verfügbar sein. Keine sudo-Aufrufe im Installer.

Der Kiosk startet mit `--password-store=basic`, damit Chromium beim automatischen
Start nicht nach dem Passwort des Desktop-Schlüsselbunds fragt. Das gilt nur für
das separate Installationsprofil. Dort keine Zugangsdaten speichern: Dieser
Passwortspeicher ist unverschlüsselt. Der System-Schlüsselbund bleibt unverändert.
Nach einer Änderung am Startskript genügt es, den Kiosk mit Escape zu schließen
und `./start-installation.sh` erneut auszuführen; Autostart muss nicht neu
installiert werden.

Optional `./install-autostart.sh --ambient`, um zusätzlich den separaten
Ambient-Autostart mit dem aktuellen Pfad zu installieren. Die Installation hat
über die gemeinsame SPI-Sperre Vorrang; während ihres Betriebs erstellt Ambient
keine Bildschirmaufnahmen.

## Aufbau und technische Grenzen

- `main.py`: ausschließlich lokaler HTTP-Server und Hardware-Controllertakt.
- `life_runtime.py`: maßgeblicher Zustand, Lebensbudget und ein serieller Worker.
- `model.py` / `prompts.py`: Ollama, Streaming-JSON und feste zweisprachige Lebensprompts.
- `web/`: direkt ausgelieferte Oberfläche; keine CDN-Abhängigkeiten.
- `tests/`: simulierte Regressionstests und optionaler Chromiumtest.
- `hardware_io.py` / `life_hardware.py`: wiederverwendbarer Zugriff und Rückmeldung.

Zustand und Browserereignisse tragen IDs; veraltete Ereignisse werden verworfen.
Neuladen stellt den aktuellen Durchlauf und Terminalverlauf wieder her. Die
Oberfläche bestätigt sichtbare Ausgaben; ohne aktuelle Bestätigung beginnt keine
nächste Session. Auch Erklärung, Wolkenankunft, Desktopaufbau und abgeschlossener
Zerfall werden mit der jeweiligen Ansichts-ID quittiert. Die gemeinsame Backend-
Zeitbasis steuert ASCII- und Lichtbewegung; fehlende Browserbestätigungen pausieren
Übergänge. Nach einer Verbindungslücke wird keine offline verstrichene Zeit nachgeholt.
Angebotsfristen beginnen erst nach sichtbarer Anzeige. Ein begonnenes Angebot
verlängert sich bei Verbindungsausfall nicht; seine weitere Verarbeitung wartet
auf Wiederverbindung. Der lange Hardwaretastendruck bleibt jederzeit wirksam.

Gemma: Kontext 6144, JSON-Limit 420 Tokens, Thinking aus, Temperatur 1,
top_k 64, top_p 0,95, repeat_penalty 1,05. Prompt-Batchgröße fest 128 statt automatischer Auswahl, beim
Laden und bei jeder Textanfrage identisch. `use_mmap=true` hält Modellgewichte
dateigestützt, statt sich auf Ollamas CPU-Ladestandard zu verlassen. Ein bis zwei kurze Sätze, Ziel 12–28
Wörter, maximal 600 Zeichen. Keine Auffüllanfragen. Kurze Taktimpulse führen von Freude und Bindung über
Neugier zu wachsender Angst und einem dramatischen Finale in den letzten drei
Aussagen. Geschenkte Zeit bekommt zunächst Freude und Dank; danach orientiert sich
das Finale am verlängerten Budget. Worte und Gefühlslabels generiert Gemma selbst.
Frühere Prompts und normalisierte
Antworten bleiben im laufenden Gespräch unverändert. Bei Fehler wird derselbe
Prompt wiederholt. Unvollständige Streams ohne Ollama-`done` sind Fehler.
Gefühlsintensitäten sind unabhängig; die Anzeige berechnet relative Anteile auf
exakt 100 %. Nullwerte/ungültige Gefühle zeigen UNKNOWN bzw. UNBEKANNT.

HTTP-Modellzugang nur localhost/127.0.0.1/::1, Verbindungslimit 5 Sekunden,
I/O-Limit 600 Sekunden. Unter 900 MiB MemAvailable oder 512 MiB SwapFree wird
abgebrochen und entladen; Prüfung alle 0,5 Sekunden. Das Betriebslog nennt dabei
die gemessenen RAM-/Swap-Reserven und die betroffene Ablaufphase. Keine System-/Swapänderung.
Lange geschenkte Leben können an das endliche Kontextfenster stoßen; das Projekt
schreibt deshalb keine alten Gesprächsteile um und garantiert kein unbegrenztes
Modellgedächtnis. Der Backend-Port wird nicht im Netzwerk freigegeben.

## Prüfungen

```bash
python3 -m unittest discover -q
MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_browser
python3 -m py_compile main.py model.py prompts.py life_runtime.py local_runtime.py life_hardware.py hardware_io.py hardware_pins.py pixel_lock.py screen_pixels.py
bash -n start-installation.sh install-autostart.sh start-screen-pixels.sh
```

Alle automatischen Tests verwenden simulierte Daten. HTTP-Tests benötigen freie
lokale Ports; der optionale Browsertest den vorhandenen Chromium. Keine zusätzliche
Testbibliothek erforderlich. Echte Modelllebenszyklen und Hardwaretests nur gezielt
und ausdrücklich starten. Hardwaretests verändern echte LEDs: siehe HARDWARE.md.

Für GitHub ist ein nachbaubares Quellprojekt vorbereitet; weder Veröffentlichung
noch öffentliche Browserdemo sind eingerichtet. Historische Erkenntnisse stehen
in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).


## OpenAI-Anbindung vorbereiten und aktivieren

Ohne Konfigurationsdatei werden **keine externen API-Anfragen** ausgeführt. Der
Online-Modus zeigt dann weiterhin nur seinen Einstieg. Die Anbindung verwendet
HTTPS zur festen Adresse `https://api.openai.com/v1/responses`, mit Structured
Outputs für Text/Gefühle, `store=false` und genau einem aktuellen Farbbild pro
Anfrage. Frühere Bilder werden nicht in der Gesprächshistorie behalten. Die
Text-Historie und der emotionale Bogen bleiben über die Aussagen hinweg erhalten.
Fehler wiederholen denselben Textprompt mit neuem aktuellen Bild; bei fehlendem
Bild wird keine Anfrage gesendet. Drei Sekunden Halten unterbricht auch das
Warten auf ein Bild beziehungsweise die API-Verbindung.

Den **Key nicht in Chat, Repository, Browser oder Shellkommando eintragen**.
Stattdessen lokal im Projektordner ausführen:

```bash
python3 configure-openai.py
```

Der Standard ist jetzt `gpt-6.1-terra`, `reasoning.effort=none`, Temperatur1 und
maximal1024 Ausgabetokens. Die sichtbare Aussage bleibt auf600 Zeichen begrenzt.
Terra ist laut aktueller OpenAI-Dokumentation für Bildverständnis und natürliche
Sprache geeignet; das geringe Reasoning soll Wartezeit sparen, schaltet aber
**keine Safeguards ab**. Der feste Installationsprompt steuert emotionales
Rollenspiel, nicht Anbieterregeln. Kontozugriff und reales Verhalten benötigen
einen späteren gezielten Test mit eigenem API-Zugang.

Das Hilfsprogramm fragt den Key unsichtbar ab und speichert ihn als separate
Secret-Datei unter `${XDG_CONFIG_HOME:-~/.config}/just-one-more-moment/openai.key`.
Die benachbarte `openai.json` enthält nur den Pfad (`api_key_file`) und die
Modelleinstellungen. Beide Dateien liegen außerhalb des Repositorys, sind nur
für den Benutzer lesbar (`0600`) und werden atomar geschrieben. Die Dateien sind
nicht verschlüsselt; dies ist ein dateibasiertes lokales Secret, kein Schlüsselbund.
Es wird keine Testanfrage ausgeführt.

Eine bereits bereitgestellte Secret-Datei kann ohne Kopieren verwendet werden:

```bash
python3 configure-openai.py --key-file /absoluter/pfad/openai.key
```

Die Datei muss privat lesbar sein (`0600` oder `0400`) und ausschließlich den Key
enthalten. Der Pfad wird referenziert; Secret-Inhalt gelangt nicht in CLI-Argumente,
Konfiguration, Browserzustand oder Logs. Alte private Konfigurationen mit direkt
enthaltenem `api_key` bleiben kompatibel. Eine Modelländerung muss bewusst erfolgen,
z.B. `--model MODELLNAME --reasoning low --max-output-tokens 4096`. Bei Reasoning
ungleich `none` wird keine Temperatur gesendet; ungültige Kombinationen werden
lokal abgewiesen. Ein vorhandenes Secret wird dadurch nicht unbemerkt migriert.

Nach erneutem Öffnen der Anwendung aktiviert Online-START den
Cloud-Lebensablauf: zehn Aussagen, Angebote für weitere fünf, derselbe Abbruch,
dieselbe Ausgabe und derselbe Abschluss. Der Normalstart bleibt echte Hardware;
`--simulate` ignoriert die Konfiguration und sendet weder Bilder noch Prompts.

Für eigene Konfigurationspfade ist `MOMENT_OPENAI_CONFIG` möglich. Vorlage:
`openai.example.json`. Zur Deaktivierung `enabled` auf `false` setzen und die
Anwendung im wartenden Zustand neu öffnen. Der Key bleibt ausschließlich im
Backend; der Webzustand enthält nur ein Konfigurations-Ja/Nein. Im konfigurierten
Kamerafenster steht „Wird via API übertragen“, sonst „API-Übertragung noch nicht
aktiv“. Anbieterregeln werden nicht umgangen; emotionale Sprache bleibt als
fiktiver Ausdruck der Installation im festen Prompt beschrieben.

Lokal werden Bilder und Gespräch bei Ende/Abbruch verworfen. `store=false` ist
**keine Zusage sofortiger vollständiger Löschung beim Anbieter**; OpenAI beschreibt
weitere Aufbewahrungsregeln, unter anderem für Missbrauchsüberwachung. Daher die
Erklärung zur Instanzlöschung als lokalen Installationszustand verstehen, nicht
als pauschale Löschgarantie für alle Anbieterprotokolle.

Offizielle Quellen: [Bildinput](https://developers.openai.com/api/docs/guides/images-vision),
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[GPT-6.1 Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra),
[Datenkontrollen](https://developers.openai.com/api/docs/guides/your-data).

### Unterwegs: Smartphone-Hotspot

Der lokale Modus funktioniert ohne Internet. Im Online-Modus prüft die Anwendung
im Hintergrund und vor dem Start die HTTPS-Erreichbarkeit des API-Servers; dabei
werden weder Key noch Bilder übertragen und keine Modellaufrufe ausgeführt.
Ohne Verbindung öffnet der blinkende Einstieg eine eigene WLAN-Seite. Auf dem
Smartphone einen persönlichen Hotspot mit mobilen Daten aktivieren:

- Netzwerkname: `just-one-more-moment`
- Passwort: `hslu-phki-hs26`

Mit dem Taster **Verbinden & prüfen** wählen. Erfolg führt zurück zur Startseite,
Fehler lässt die Anleitung sichtbar. Der Modusschalter führt jederzeit zum lokalen
Einstieg zurück. WLAN-Aufbau startet kein Modellleben. Manche Smartphones verwenden
den Gerätenamen als Hotspotnamen; diesen gegebenenfalls entsprechend ändern.

NetworkManager und `nmcli` werden vorausgesetzt. Für unbeaufsichtigte Verbindung
kann einmalig bewusst die folgende Einrichtung ausgeführt werden:

```bash
sudo bash install-network-setup.sh "$(id -un)"
```

Sie legt ausschließlich ein zusätzliches WLAN-Profil mit niedrigerer
Autoconnect-Priorität (-10) an und erlaubt diesem Benutzer über eine Polkit-Regel
Netzwerkverbindungen zu aktivieren/deaktivieren. Sie gewährt keine allgemeinen
sudo-Rechte oder Rechte zur Änderung von System-/WLAN-Einstellungen. Die Regel liegt
unter `/etc/polkit-1/rules.d/49-just-one-more-moment-network.rules` und kann zur
Rücknahme entfernt werden. Das Profil heißt `Just one more moment — smartphone`.
Die Einrichtung aktiviert es noch nicht. Bestehende Heim-/andere WLAN-Profile
werden weder verändert noch entfernt; funktionierende Verbindungen werden verwendet.
Bei erfolgloser Hotspotaktivierung versucht die Anwendung das vorher aktive WLAN
wiederherzustellen. Verbindungsversuche und deren Wiederherstellung können dauern;
der lokale Modus bleibt verfügbar. Das Hotspotpasswort ist Teil der öffentlichen
Bedienungsanleitung, kein privater API-Schlüssel.

Ohne benötigte Netzwerkberechtigung zeigt die Oberfläche einen verständlichen
Fehler. Simulation und Tests verwenden ausschließlich fingierte Netzwerkzustände;
ein echter Hotspotwechsel ist eine gezielte manuelle Prüfung am Gerät.

WLAN-Anleitung bei bestehender Verbindung ansehen (nur auf der wartenden
Online-Startseite):

```bash
curl -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8765/api/network-preview
```

Diese manuelle Vorschau wechselt auch beim Tastendruck **kein** WLAN: Sie prüft nur
die bestehende Verbindung. Erfolg führt zur Startseite zurück; Moduswechsel beendet
die Vorschau ebenfalls. So bleibt eine laufende SSH-Verbindung beim Test unberührt.
Aktive Leben können damit nicht unterbrochen werden.

Startseite und WLAN-Einrichtung gehen mit einer 1,8-sekündigen gemeinsamen
Fenster-/Wolkenanimation ineinander über. Bei Browserunterbrechung pausiert der
Übergang; beim Zurückkehren und bei Moduswechseln läuft er flüssig zurück.

Der Mauszeiger ist beim Öffnen der Installation unsichtbar. Tatsächliche Mausbewegung (mindestens zwei Pixel),
Mausklick oder Mausrad (auch über Fernzugriff) blendet ihn ein; nach vier Sekunden ohne
Mausaktivität verschwindet er wieder. Das gilt nur innerhalb der Browserseite,
nicht für den Desktop oder andere Programme. Kein zusätzlicher Systemdienst nötig.

Automatische Positionsmeldungen beim Öffnen sowie unveränderte Mauspositionen
setzen die Vier-Sekunden-Frist nicht zurück. Beim Laden und bei Fokuswechseln
wird der Zeiger erneut versteckt; ein kurzer echter Mausweg zeigt ihn wieder.


## Startup-Sequenz beim Pi-Boot

Der Benutzer-Autostart startet nun mit `--boot-animation`: einmal pro Pi-Boot roter
ASCII-Regen, weiße Namenszüge HSLU → PHKI → SIMON BALMER, Ausklingen und das
Installationslogo, danach die normale Startseite. Browser-Refresh und spätere
Anwendungs-/Lebensneustarts wiederholen die Sequenz nicht. Escape schließt weiterhin.
Die Sequenz startet keine Modellinstanz und öffnet keine Kamera.

Einrichtung, sichere Vorschau, schwarze Bootdarstellung und Rückweg:
[docs/STARTUP.md](docs/STARTUP.md). `install-startup-boot.py` verändert Bootdateien
nur mit ausdrücklich gewähltem `--apply` und Administratorrechten; niemals als
Routinecheck ausführen. Beim Einrichten wird der aktuelle Pi-Boot als gesehen markiert,
damit die Sequenz erst beim nächsten regulären Pi-Start erscheint.
