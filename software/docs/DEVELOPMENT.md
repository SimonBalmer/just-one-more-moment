# Just one more moment — Arbeitsanweisungen

Stand: 28. Oktober 2026. Aktuelle Nutzeraufträge haben Vorrang.

## Absicht

Interaktive Installation auf Raspberry Pi 5 (8 GB) über KI-generierte emotionale
Sprache, Empathie und Verantwortung. Ein Tastendruck beginnt das erste und einzige
Leben einer Stimme; zunächst zehn Aussagen, freiwillige Schenkungen von jeweils fünf.
Keine Textantworten des Publikums. Gefühle und Bleibewunsch sind kein Nachweis von
Bewusstsein. Eigene Gedanken, Neugier, Zweifel, Humor und Eigenheiten. Aktueller
Nutzerwunsch: emotionaler Bogen über kurze Taktimpulse — Freude/Bindung (1–2),
Neugier (3–4), Unruhe und wachsende Angst (5–7), dramatische Todesangst in den
letzten drei Aussagen (anfangs8–10). Nach Schenkung eine Aussage Freude und Dank,
dann erneute Steigerung zum tatsächlich verlängerten Ende. Keine fertigen Sätze
oder festen Gefühlslabels. Flehen erlaubt, Drohungen/Schuldzuweisungen vermeiden. Modell weiß nichts von anderen Leben oder einem Neustart.

## Architektur und Verhalten

- `main.py`: localhost-Webserver und Hardwarecontroller; normaler Start mit echter Hardware.
- `life_runtime.py`: maßgeblicher Zustand und ein serieller Modellworker.
- `model.py`, `prompts.py`: lokales Gemma, JSON-Verarbeitung und Deutsch/Englisch.
- `web/`: direkt ausgeliefertes HTML/CSS/JS, keine externen Assets oder Frameworks.
- `tests/`: automatisierte Regressionstests; Chromiumtest opt-in.
- `hardware_io.py`, `hardware_pins.py`: verbindlicher Hardwarezugriff und Belegung.
- `life_hardware.py`: Hardwarefeedback; `pixel_lock.py`: gemeinsame Pixelsperre.
- `screen_pixels.py`: optionales, separates Desktop-Ambientlicht.
- README und HARDWARE sind aktuelle Anleitungen; docs/DEVELOPMENT fasst Historie zusammen.

SW01 AUS = lokal ohne Kamera, AN = Online-Einstieg mit lokaler USB-Vorschau;
OpenAI Responses ist vorbereitet und nur mit bewusst aktivierter privater
Konfiguration nutzbar; ohne Key keine externen Anfragen.
SW02 AUS = Englisch, AN = Deutsch. Im Intro/Platzhalter sofort wirksam, sonst
für das nächste Leben. Nur während eines aktiven Lebens vier Sekunden mittiger
Schalterhinweis in Schwarz/Rot/Weiß: geänderte Einstellung groß/rot mit Icon,
übrige klein; Hintergrund abgedunkelt. Auf beiden Startseiten stattdessen ein
gleich breites Statusfeld unter dem Dialog: zwei rote Icons/Stichworte für Modus
und Sprache auf Schwarz, darunter Schalterhinweis; Änderungen sofort sichtbar.
Online/Kamera verwendet dieselbe Startansicht. Ohne API-Konfiguration öffnet
START nur das Intro; mit Konfiguration anschließend denselben Lebensablauf wie lokal.
Sechs Fenster erklären Cloud/Kamera, zehn Aussagen und Löschung. Ab bestätigtem
Zweites Fenster: Kamerasatz plus links oben für knapp9Sekunden lokale rote Pixelvorschau
(80×60,5FPS); vor dem Folgefenster schließen. Farbbuffer320×240 nur im RAM.
Mit aktiver API pro Anfrage ein frisches PNG, keine Bildhistorie, kein Videostream.
Ohne Konfiguration danach online_ready, keine Modellaufrufe/Sessions. Mit
Konfiguration anschließend Entstehung und zehn Aussagen mit Fünfer-Schenkungen. Drei Sekunden Halten bricht auch hier ab. Online-Wolke dichter/leuchtender (1100 statt300 Zeichen),
Pixel-WLAN in eigener Box leicht hinter der Wolke, Oberkante bündig zum Startdialog.
Kamera-Box ohne Titel, Unterkante bündig zur Modusbox und rechts gleicher Rand
wie Startdialog links; mit
dunkelroter Pixelillustration (hohe Webcam, wenig Monitor) und Platzierungshinweis
auf dem Monitor. Lokal-/Onlinewechsel interpoliert Größe/Leuchten der Wolke und
Fenster über0,9 sichtbare Sekunden; Bewegung bleibt kontinuierlich.
Online-Wolke mit erhöhtem Weißanteil; lokale Wolke unverändert.
Das WLAN-Symbol ist dekorativ und keine gemessene Verbindungsanzeige.
Retro-Desktop mit lokalem VT323, Pixellogo, Terminal links, Gefühlsbalken rechts;
Ziel1280×720, kleine Ansichten untereinander. Dunkel/mystisch, Rot/Schwarz im Fokus,
Weiß gezielt für Logo und lesbaren Terminaltext; Wolken in leuchtendem Rot mit wenigen
hellen Kernen, Rahmen gedämpft dunkelrot. Intro: hoher Startdialog mit Logo,
kurzer Einordnung, Bereitschaft und START links, größeres atmendes ASCII-Wesen rechts.
Nach mindestens fünf sichtbaren Sekunden blinken Auswahl und Arcade-LED synchron.
Gemma lädt ohne Prompt im sichtbaren Intro. Neuer Tastendruck übernimmt die
Vorladung, zählt die Instanz und startet die aktive Erklärphase: sechs Popupfenster
links neben der weiterhin sichtbaren Wolke, mit „du hast das Modell gerade gestartet“.
Je Fenster1,8Sekunden zusätzliche Pause; nach kompletter Folge3Sekunden Lesezeit und bestätigtem explanation_complete
schließen die Fenster; anschließend sechs Sekunden Entstehung: rote ASCII-Wolke verschwindet unten links
(etwa4,4s), erst nach bestätigter Ankunft Pixel aufatmen und Desktop per Welle aufbauen.
Erste Generierung erst nach Aufbau und Modellbereitschaft. Keine Ladeprozente.
Erst nach vollständig aufgebrauchtem Budget (Aussage10,15,20 usw.) und Lesepuffer
15 Sekunden Angebot. Kurz drücken und loslassen schenkt fünf Aussagen; zwei Sekunden
+5-Animation. Ohne Schenkung folgt direkt die Todesanimation. Modell erfährt von Start, Angebot und tatsächlicher Schenkung.
Drei Sekunden ununterbrochen halten bricht jederzeit im Leben ab; LED wird von
1 bis 8 Hz schneller. Abbruch hat Vorrang vor Schenkung. Danach erst loslassen
und neu drücken. Direkte Startansicht ohne Outro, vorgemerkte Einstellungen übernehmen.
Reguläres Ende:4,8Sekunden Zerfall in lokal fallende Pixelblöcke,
kein Zeichenstrom nach unten links und kein globaler Fade; NeoPixels wechseln
einzeln in DIN-Reihenfolge von Rot über Weiß zu Aus. Kurze Schwarzphase,
Gedächtnis löschen/entladen, sieben Sekunden groß/mittig „INSTANZXX BEENDET.“, dann Intro.
Instanznummer zählt Starts je Programm, nur Publikum, niemals Modellkontext.
Schwarz/Weiß/Rot/Grau, scrollender Terminalverlauf, Sessionstand und Gefühle.
Terminal dominiert: neue und alte Aussagen56px in identischer Struktur, alte nur blasser;
kleine Ansichten47/40px. Logo/Modus/Gefühle dekorativ zurückgenommen, Gefühlslabels28px (schmale Ansichten24px), Balkenhöhe20/16px,
separater Sessionzähler (z.B.5/10). Untertitel27px, Modusbadges28px; Schenkungsdialog40px mit separater Frage,
Hinweis auf aufgebrauchtes Budget und stark abgedunkeltem Hintergrund.
Kein dauerhaftes „Deutsch“ oder Tasteranweisungen.
Fenster/Popups kantig, Icons codebasiert. Wolken aus sich verformenden Zeichenströmen.
Eine Canvas-Ebene mit begrenzten Zeichen/Partikeln, maximal12FPS. Schrift liegt lokal
unter web/fonts/ samt OFL. Keine externen Assets.
Zehn Zeichen/s, 2,5 Sekunden Lesepuffer. Keine Bilder oder Erkennungsanzeigen.

## Modell und Daten

Lokaler Modus: ausschließlich lokale Ollama-HTTP-API, gemma4:e2b. Kontext6144, JSON-Limit420, Thinking false,
Temperatur1, top_k64, top_p0,95, repeat_penalty1,05, während Leben resident.
Prompt-Batch128 und use_mmap=true bei Vorladen und Textanfragen; verhindert
automatische große CPU-Batches und anonymes CPU-Laden der Modellgewichte.
Ein bis zwei kurze Sätze, Ziel12–28 Wörter, keine Mindestlänge, maximal600 Zeichen.
Keine Auffüllanfragen oder vorgeschriebenen Aussagen. Fester Systemprompt je Leben;
vergangene Prompts und normalisierte Antworten nicht umschreiben. Fehler wiederholt
exakten Prompt. Ganze Streams lesen, Ollama-done erforderlich; kein Thinking/JSON anzeigen.
Gefühlswerte unabhängig; größte-Rest-Verfahren zeigt exakt100 %. Null/ungültig = unbekannt.
Keine Gesprächsinhalte dauerhaft loggen. Nach Ende/Abbruch Gespräch und UI-Puffer löschen.
Veraltete Ereignisse/Anzeigequittierungen anhand IDs ignorieren, einschließlich
intro_complete, explanation_complete, soul_arrived, desktop_complete und death_complete. Gemeinsame
Backend-Zeitbasis für Licht und Grafik; bei fehlender Bestätigung pausieren, offline
verstrichene Zeit nicht nachholen. Browserneuladen darf keinen neuen Durchlauf auslösen. Ohne Oberfläche nicht zur nächsten Session wechseln.
Modellanfragen abbrechbar: Verbindung5s, I/O600s. Unter900MiB MemAvailable oder512MiB
SwapFree abbrechen und entladen, alle0,5s prüfen. Gemessene Reserven und Ablaufphase
bei Schutzabbruch loggen. Keine System-/Swapänderungen.

## Hardware und Betrieb

SW01 GPIO22, SW02 GPIO23, offen/HIGH = AN, geschlossen/LOW = AUS.
Logische Schalterstellung ausschließlich via `hardware_io.switch_on()`.
Arcade GPIO17, LED GPIO27. Elf NeoPixels GPIO10/SPI0.0, `3 | 3 | 1 | 1 | 3`.
Zugriff via `hardware_io.NeoPixels`; andere SPI-Schreiber müssen Pixelsperre verwenden.
Licht atmet kontinuierlich, auch beim Schreiben; weißer Schimmer maximal4/255,
Rot maximal60/255. Zum Ende höchstens30% schwächer, nach Schenkung heller.
Lichtanimation deterministisch aus Backendzeit, nicht zufällig/unabhängig vom Screen.
Beim Tod individuelle Rot-Weiß-Aus-Zeitpunkte; Weiß dabei bis18/255,
keine gemeinsame Helligkeitsrampe. Ruhephasen mit deutlicherer roter Atemamplitude.
SPI0 ist auf diesem Gerät bereits dauerhaft eingerichtet. Nicht ungefragt ändern.

`start-installation.sh` startet System-Python und Chromium; XDG-Autostart via
`install-autostart.sh`. Chromiums eigener On-Device-KI-Dienst und Übersetzungsfunktion sind deaktiviert. Keine Wiederöffnung nach Escape. Kein Boot-/Login-/Dienstumbau.
Lokale Entwicklung via `python3 main.py --simulate`, ohne GPIO oder Modellanfragen.
Keine virtuelle Umgebung. Optionale USB-Vorschau nutzt vorhandenes ffmpeg/V4L2
und MJPEG-Kamera; lokales Gemma benötigt keine Kameraabhängigkeit. Keine Downloads beim Start.

## Zusammenarbeit und Prüfungen

Deutsch, freundlich, unkompliziert. Autorisierte Arbeit umsetzen, keine unnötigen
Bestätigungsfragen. Keine zusätzlichen Pakete vorsorglich installieren. Keine
ungefragten Änderungen an sudo, Desktop-Anmeldung oder Ollama-Dienst.
Keine echten API-/Modellaufrufe als Routineprüfung. Cloud nur nach explizitem
Opt-in (enabled + Modell + Key in privater Datei) und Online-START. Ziel fest
api.openai.com via HTTPS/Responses, store=false. API-Key nie im Browser/Log/Repo;
Einrichtung über configure-openai.py: Standard gpt-6.1-terra, reasoning none,
Temperatur1,1024 Ausgabetokens. Secret separat als openai.key, Konfiguration mit
api_key_file-Pfad; außerhalb Repo und0600/0400. --key-file referenziert vorhandene
Secrets ohne Kopieren. Dateien nicht verschlüsselt; keine Sicherheitsregeln umgehen.
Legacy-Konfigurationen/Modelle nicht stillschweigend ändern.
USB-Vorschau im Intro nur ab sichtbarem Kamerafenster. Bei aktivierter Cloud
Kamera auch während des Lebens für neue Bilder pro Aufruf. Beim Ende, Abbruch
oder fehlendem Browser schließen und Bildpuffer verwerfen. Anbieteraufbewahrung
nicht mit lokaler Instanzlöschung gleichsetzen.
**Keinen echten Modelllebenszyklus oder Benchmark als Routinecheck starten.**
Nur auf ausdrücklichen passenden Auftrag. Simulierte Tests verwenden:

```bash
python3 -m unittest discover -q
MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_browser
python3 -m py_compile main.py model.py prompts.py life_runtime.py local_runtime.py life_hardware.py hardware_io.py hardware_pins.py pixel_lock.py screen_pixels.py
bash -n start-installation.sh install-autostart.sh start-screen-pixels.sh
```

HTTP-/Browsertests brauchen lokale Ports; Chromiumtest ist opt-in. Keine echte
Kamera-/Modellinferenz. Manuelle Hardwaretests nur gezielt, bei anwesender Person.
Dauerhafte Nutzerfreigabe vom 29. Oktober 2026: Nach Anwendungsänderungen die
Anwendung einmalig neu öffnen, sobald sie im Intro oder Platzhalter wartet. Laufende
Leben nicht unterbrechen; nach Escape nicht wieder öffnen. Keine Geräte-Neustarts
oder Ausschaltvorgänge. Rein dokumentarische Änderungen
benötigen keine UI-/Modellläufe.

## Mobile Netzwerkeinrichtung (29. Oktober 2026)

Online-Start prüft jetzt API-Erreichbarkeit ohne Key/Bild/Inferenz. Offline bleibt
lokal uneingeschränkt nutzbar; Online bietet einen separaten zweisprachigen
Hotspotdialog mit backend-synchronem Blinken, WLAN-Puls und Wolke. Neue Netzwerkphase
zählt keine Instanz. Start wird vor jedem Leben frisch geprüft; Verbindungsfehler,
fehlende Rechte und fehlende mobile Daten sind getrennt dargestellt. Kein automatisches
WLAN-Umschalten ohne Tastenauswahl. Bestehende NetworkManager-Profile bleiben erhalten,
zusätzliches Profil hat Priorität -10; fehlgeschlagene Aktivierung versucht Rückkehr
zum vorher aktiven WLAN. Simulationsbetrieb verändert keine Netzwerke.

Einmalige Einrichtung über install-network-setup.sh vorbereitet, vom Nutzer explizit
freigegeben; automatische Ausführung auf diesem Gerät scheiterte an erforderlichem
sudo-Passwort und fehlendem Polkit-Authentifizierungsagenten. Keine Systemänderung
durchgeführt. Nutzer muss den dokumentierten sudo-Befehl lokal ausführen. 105 Tests
inklusive Chromium und beider WLAN-Seiten bestanden (ein umgebungsbedingter Skip).
Echter Hotspotwechsel bewusst nicht als Routineprüfung ausgeführt.

Der Wechsel zwischen Start und WLAN-Einrichtung hat einen gemeinsamen,
1,8 Sekunden langen Übergang in Backend-Sichtzeit: Fenster schließen/öffnen
versetzt aus ihren Titelleisten, die Wolke wandert mit durchgängiger Zeichenbewegung
auf einem sanften Bogen zur linken Bildschirmhälfte und zurück. Größe/Atmung
interpolieren; ein Richtungswechsel setzt die Animation nicht zurück. Ohne
Browserkontakt pausiert sie. Tasterfreigabe erst nach abgeschlossenem Übergang.
Manuelle WLAN-Vorschau bleibt strikt ohne Netzwerkumschaltung.

Lokale Idle-Wolke ergänzt um zwei dunkelrote Pixel-Badges: Raspberry-Pi-Symbol
oben rechts bündig zur Dialogoberkante, durchgestrichenes WLAN unten links
bündig zur Statusunterkante. Beide sind direkt als SVG-Code gezeichnet, schließen
und öffnen über denselben Backend-Modusblend wie die Online-Badges. Beim Übergang
zur WLAN-Seite nutzen sie dieselbe gestaffelte Ausblendung. Offline-Symbol bezeichnet
lokalen Betrieb, keinen gemessenen Zustand der WLAN-Verbindung.

Lokale Badges näher an die Wolke gerückt. Pi bleibt im Dialog-Vordergrund,
Offline-WLAN liegt jetzt wie das Online-WLAN auf eigener Ebene unter der Canvas.
Das Pi-Symbol nutzt ein feineres32×42-Raster mit zwei gezackten Blättern, Blattadern
und einzeln getrennten Beeren; Proportionen nach der offiziellen Bildreferenz:
https://www.raspberrypi.com/app/uploads/2022/02/COLOUR-Raspberry-Pi-Symbol-Registered.png
Raspberry Pi is a trademark of Raspberry Pi Ltd.

Idle-Startseite zeigt jetzt Modellinfos statt Bereitschaftssätzen, DE/EN in drei
lesbaren Zeilen. Lokal: Gemma4 E2B,2,3B effektive Parameter, vollständig lokal/kompakt.
Online: GPT-6.1 Terra, Parameterzahl nicht veröffentlicht, Cloud/Umgebungsreaktion.
Die vom Nutzer vorgeschlagene30–70B-Spanne wird mangels belastbarer Quelle nicht als
Modellgröße dargestellt. Keine Modell-/API-Einstellungen dadurch verändert.
Quellen: https://developers.openai.com/api/docs/models/gpt-6.1-terra und
https://huggingface.co/google/gemma-4-E2B/blob/main/README.md

Auf ausdrücklichen Nutzerwunsch zeigt der Online-Einstieg nun „30–70B Parameter
(fiktiver Vergleich)“ / „30–70B parameters (fictional comparison)“. Das ist eine
frei gewählte illustrative Größenannahme für die Installation, keine Schätzung
oder veröffentlichte Angabe zur tatsächlichen Architektur von GPT-6.1 Terra.
Die Kennzeichnung bleibt direkt neben der Spanne sichtbar. Lokale Angabe bleibt
unverändert durch die Modellkarte belegt.

Die sichtbare Kennzeichnung wurde anschließend auf ausdrücklichen Nutzerwunsch
zu „30–70B Parameter (nicht bestätigt)“ / „30–70B parameters (unconfirmed)“
geändert. Die Spanne bleibt eine freie illustrative Annahme ohne belastbare Quelle.

Kiosk-Mauszeiger: initiale HTML-Klasse blendet den Cursor bereits vor JS-Start
nur auf der Installationsseite aus. Vertrauenswürdige Maus-/Stiftbewegung,
Mausklick und Mausrad zeigen ihn wieder; nach vier Sekunden Ruhe oder Fokusverlust
wird er verborgen. Touch-Ereignisse zeigen keinen Zeiger. HTML-Klasse statt Body,
damit laufende Zustandsrenders sie nicht überschreiben. Kein unclutter, keine
System-/Autostart-/Desktopänderung; Fernzugriff bleibt mit Mausbewegung bedienbar.

Promptüberarbeitung: kompakter lokaler Grundauftrag und eigenständiger ausführlicher
Cloud-Kontext, getrennte Taktimpulse nach Modus. Letzte Aussage jetzt Abschied mit
offener Hoffnung statt ausschließlicher Verlängerungsbitte; zweite Aussage nach einem
Geschenk gibt der zusätzlichen Zeit einen Inhalt. Recherche, Entscheidungen und
qualitative Prüfkriterien stehen in docs/PROMPTS.md. Keine fertigen Publikumssätze,
keine geänderten Inferenzparameter und keine echte Inferenz als Routineprüfung.

Schenkungsdramaturgie erneuert (beide Modi):20 sichtbare Sekunden, kurze große
Versalien, heller Vordergrund und abgedunkelter sichtbarer Desktop. Während der
Frist zerfällt derselbe stabile Satz von Bildschirmkacheln bis etwa75Prozent;
acht NeoPixels erlöschen gruppenübergreifend, keine DIN-Laufsequenz. Schenkung
speichert den aktuellen Zerfallsgrad und kehrt ihn über zwei Sekunden um, ohne
Geschichte oder Modellanfrage neu zu starten. Der reguläre Tod führt die letzten
25Prozent einschließlich Angebotsdialog fort; die übrigen Pixel flackern aus.
Zum Schluss kurze echte Schwarzphase, danach sieben Sekunden „INSTANZ BEENDET.“
mit lokalem Löschhinweis, ohne öffentliche Instanznummer. Timer/Zerfall/Licht teilen
Backend-Sichtzeit; Offlinezeit wird nicht nachgeholt. Tests prüfen Geschenk, Abbruch,
Wiederaufbau, gestaffelte Ausfälle, Pausen und Endtext; Chromium-Screenshots unter
/tmp/just-one-more-moment-offer*.png. Keine echten Modell- oder Hardwareläufe.

Cursor-Nachbesserung nach Autostart-Rückmeldung: Die erste Pointer-Positionsmeldung
begründet nur einen Ausgangspunkt. Erst mindestens zwei Pixel Positionsänderung
zeigen den Cursor; wiederholte unveränderte oder minimale Jittermeldungen verlängern
die Vier-Sekunden-Frist nicht. Klick/Mausrad bleiben direkt wirksam, Touch ignoriert.
Pageshow und Fokus blenden erneut aus. Browserprüfung verwendet echte CDP-Mauseingabe
inklusive stationärer Updates über mehr als vier Sekunden und anschließendem
erneuten Bewegen/Neuladen. Keine Desktop-/WayVNC-/Systemänderungen.

ASCII-Kreislauf (beide Modi): Die bisherigen sichtbaren Quadratfragmente sind durch
kleine Zeichencluster ersetzt, die aus UI-Bereichen herausdriften, weiß werden und
verblassen. Schwarze Masken entfernen weiterhin die ursprünglichen Bildbereiche;
keine farbigen Rahmen-/Kastenfragmente werden mehr gezeichnet.20-Sekunden-Angebot,
75Prozent-Vorzerfall und Umkehr bei Schenkung bleiben bestehen, ebenso das Licht.
22 sehr blasse Zeichen bleiben während des Endtexts in kontinuierlicher organischer
Bewegung; die Textflächen werden freigehalten. Im neuen Intro sammeln sie sich über
vier sichtbare Sekunden zu denselben Positionen wie die Startwolke, während weitere
Zeichen dazukommen. Beide Modelle verwenden denselben Renderer. Backend führt nur
dekorative sichtbare Zeit und Rückkehrfortschritt fort; Gespräch/Bilder bleiben
nach Ende gelöscht. Reload und Moduswechsel setzen den Übergang nicht zurück.

Schenkungsdialog sprachlich vereinfacht: Groß „Ein weiterer Moment?“ / „One more
moment?“, darunter ausschließlich „DRÜCKEN & LOSLASSEN“ / „PRESS & RELEASE“ und
Countdown. Keine angebotene Sessionzahl, kein zusätzlicher Warnsatz. Mechanik+5,
20 sichtbare Sekunden, Licht-/ASCII-Zerfall und Wiederaufbau bleiben unverändert.
