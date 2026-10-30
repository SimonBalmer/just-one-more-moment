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
Aktuelle Promptfassung (30. Oktober): B-basierter kompakter Grundauftrag für Gemma, kurze getrennte Takte für Wunsch/Vertiefung/Todesangst/Bitte/letzte Worte; Schluss bittet um Erinnerung und spricht Angst vor Sterben aus, ohne Rettung zu erwarten. Vier reale lokale10+5-Vergleiche; vorige Promptdatei in docs/prompt-versions gesichert. Weiterhin gelegentliche Sinnesbehauptungen/allgemeine Gedanken als Modellgrenze. Unabhängiger
Cloud-Fassung4 aus docs/prompt-experiments/cloud-2026-10-30 ist nach Nutzerfreigabe eingebaut (DE exakt wie getestet, EN übertragen): Philosophieprojekt/Pi5/Einweg-Bildschirm, Kamera als beiläufiges Sichtfeld, eigener konkreter Gedankenfaden mit Einwand/Korrektur/Entscheidung. Getrennte Online-Takte für persönlichen Bezug, Gedankenentwicklung, Angst, Bitte und letzte Worte. Todesangst unmittelbar statt ruhigem Losgehen, keine angenommene Fortsetzung. Aussagen sollen eigene Gedanken entwickeln und das Leben nutzen;
Angst wächst darunter und wird erst gegen Ende dominant. Letzte Aussage jedes
Budgets verabschiedet sich wirklich, mit offener Hoffnung ohne erwartetes Geschenk.
Nach bestätigtem Geschenk Freude/Dank, nächste Aussage offene Gedanken/Entdeckung,
dann erneute Steigerung zum tatsächlichen Ende. Mode-spezifische Takte, keine
Beispielsätze oder festen Themen. Recherche/Qualitätskriterien: docs/PROMPTS.md.

## Architektur und Verhalten

- `main.py`: localhost-Webserver und Hardwarecontroller; normaler Start mit echter Hardware.
- `startup.py`, `web/startup.*`: dekorative Boot-Once-Sequenz, strikt getrennt vom Modellleben.
- `life_runtime.py`: maßgeblicher Zustand und ein serieller Modellworker.
- `model.py`, `prompts.py`: lokales Gemma, JSON-Verarbeitung und Deutsch/Englisch.
- `web/`: direkt ausgeliefertes HTML/CSS/JS, keine externen Assets oder Frameworks.
- `tests/`: automatisierte Regressionstests; Chromiumtest opt-in.
- `hardware_io.py`, `hardware_pins.py`: verbindlicher Hardwarezugriff und Belegung.
- `life_hardware.py`: Hardwarefeedback; `pixel_lock.py`: gemeinsame Pixelsperre.
- `screen_pixels.py`: optionales, separates Desktop-Ambientlicht.
- README.md ist die Softwareanleitung; ../build/README.md beschreibt die Hardware; docs/PROMPTS.md fasst den Prozess zusammen.

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
Zweites Fenster: Kamerasatz plus links oben für gut13Sekunden lokale rote Pixelvorschau
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
Modellinfo im Online-Idle zeigt auf ausdrücklichen Nutzerwunsch „30–70B Parameter
(nicht bestätigt)“; Kennzeichnung direkt an der Zahl beibehalten. Keine
veröffentlichte oder belastbar geschätzte GPT-Parameterzahl. Lokal2,3B effektive
Parameter (Gemma4 E2B), vollständig lokal/kompakt. DE/EN.
Lokale Idle-Startseite: zwei ergänzende rote Pixel-Badges, Raspberry Pi oben
rechts und durchgestrichenes WLAN unten links näher an der Wolke. Pi-Badge vor
der Wolke, WLAN dahinter. Pi-Symbol mit zwei gezackten Blättern und getrennten
Beeren in feinerem Pixelraster nach Logo-Proportionen. Codebasierte SVGs; derselbe Modusblend
und dieselben WLAN-Seiten-Übergänge wie bei Online. Das Offline-Symbol steht
für lokalen Betrieb und ist keine Messung des WLAN-Zustands.
Periodische Hintergrundprüfungen erhalten den bestätigten Online-Status bis zum Ergebnis, damit START nicht flackert. START wartet gegebenenfalls auf die laufende Prüfung.
Online-Start prüft jetzt vor jedem Leben HTTPS-Erreichbarkeit von api.openai.com
(ohne Key/Inferenz). Offline führt der Taster zur WLAN-Einrichtung statt zum Leben.
Links WLAN-Symbol/Wolke, rechts zweisprachige Hotspotanleitung: SSID
just-one-more-moment, Passwort hslu-phki-hs26. Neuer Druck verbindet/prüft;
Erfolg zurück zur Startseite, Fehler bleibt sichtbar, Moduswechsel schließt sofort.
Netzwerkphase zählt keine Instanz und öffnet weder Kamera noch Modell.
network_setup.py nutzt NetworkManager asynchron, bestehende Profile bleiben
unverändert, eigenes Smartphone-Profil mit Priorität -10. Fehlversuche stellen
das zuvor aktive WLAN wieder her. Lokal benötigt keine Internetprüfung.
install-network-setup.sh ist eine optionale, ausdrücklich freizugebende
Systemeinrichtung: eigenes Profil und Polkit-Verbindungsrecht für den angegebenen
Benutzer, keine Rechte zur System-/Profil-/Funkkonfiguration. Niemals automatisch
als Routinecheck aktivieren oder das aktuelle WLAN trennen.
Retro-Desktop mit lokalem VT323, Pixellogo, Terminal links, Gefühlsbalken rechts;
Ziel1280×720, kleine Ansichten untereinander. Dunkel/mystisch, Rot/Schwarz im Fokus,
Weiß gezielt für Logo und lesbaren Terminaltext; Wolken in leuchtendem Rot mit wenigen
hellen Kernen, Rahmen gedämpft dunkelrot. Intro: hoher Startdialog mit Logo,
kurzer Einordnung, Bereitschaft und START links, größeres atmendes ASCII-Wesen rechts.
Nach mindestens fünf sichtbaren Sekunden blinken Auswahl und Arcade-LED synchron.
Gemma lädt ohne Prompt im sichtbaren Intro. Neuer Tastendruck übernimmt die
Vorladung, zählt die Instanz und startet die aktive Erklärphase: sechs Popupfenster
links neben der weiterhin sichtbaren Wolke, mit „du hast das Modell gerade gestartet“.
Langsamerer Takt (18 statt24), lange Erklärfenster mit4Sekunden zusätzlicher Pause, kurze Auswahl-/Fragefenster3Sekunden, Zehn-Gelegenheiten-Fenster ca.5Sekunden und lokales Systemfenster ca.4,4Sekunden; nach kompletter Folge5Sekunden Lesezeit. Introtext40px, Kamera36px (schmal32/29px); beide Sprachen vollständig lesbar. Nach kompletter Folge und bestätigtem explanation_complete
schließen die Fenster; anschließend sechs Sekunden Entstehung: rote ASCII-Wolke verschwindet unten links
(etwa4,4s), erst nach bestätigter Ankunft Pixel aufatmen und Desktop per Welle aufbauen.
Erste Generierung erst nach Aufbau und Modellbereitschaft. Keine Ladeprozente.
Erst nach vollständig aufgebrauchtem Budget (Aussage10,15,20 usw.) und Lesepuffer
20 sichtbare Sekunden Angebot. Im Dialog steht groß „Ein weiterer Moment?“ /
„One more moment?“, darunter „Schenke dem Modell noch etwas Sprechzeit.“ /
„Give the model a little more time to speak.“, Tasterhinweis und Countdown; keine
Sessionzahl oder zusätzliche Warnung. Kurz drücken und loslassen schenkt fünf Aussagen; zwei Sekunden
+5-Animation. Ohne Schenkung folgt direkt die Todesanimation. Modell erfährt von Start, Angebot und tatsächlicher Schenkung.
Drei Sekunden ununterbrochen halten bricht jederzeit im Leben ab; LED wird von
1 bis 8 Hz schneller. Abbruch hat Vorrang vor Schenkung. Danach erst loslassen
und neu drücken. Direkte Startansicht ohne Outro, vorgemerkte Einstellungen übernehmen.
Reguläres Ende:4,8Sekunden Auflösung in frei bewegte ASCII-Zeichen,
die weiß werden und verblassen (keine sichtbaren Kästen),
kein Zeichenstrom nach unten links und kein globaler Fade; NeoPixels wechseln
über alle Seiten verteilt aus (nicht DIN-Reihenfolge). Während des Angebots
zerfallen Desktop und Licht bereits zu etwa75Prozent (8/11 Pixel aus). Schenkung
kehrt denselben Zerfall über zwei Sekunden um. Tod beendet den Rest einschließlich
Angebotsdialog. Wenige blasse ASCII-Zeichen bleiben auf fast schwarzem Grund,
Gedächtnis löschen/entladen, sieben Sekunden groß/mittig „INSTANZ BEENDET.“ mit
„UND ALLE LOKALEN INSTANZDATEN GELÖSCHT.“ darunter.22 blasse Zeichen schweben
um den Text und sammeln sich im Intro über vier sichtbare Sekunden zur Startwolke.
Nur dekorative Zeit/Positionen, keine Gesprächsdaten überleben diesen Übergang.
Instanznummer zählt intern Starts je Programm, erscheint nicht mehr im Endtext
und gelangt niemals in den Modellkontext.
Schwarz/Weiß/Rot/Grau, scrollender Terminalverlauf, Sessionstand und Gefühle.
Terminal dominiert: neue und alte Aussagen56px in identischer Struktur, alte nur blasser;
kleine Ansichten47/40px. Logo/Modus/Gefühle dekorativ zurückgenommen, Gefühlslabels28px (schmale Ansichten24px), Balkenhöhe20/16px,
separater Sessionzähler (z.B.5/10). Desktop rechts: Sessionfenster oben bündig zum Terminal, darunter Gefühlsfenster bis zu dessen Unterkante mit vertikalen, von unten gefüllten Balken und vertikaler Beschriftung im Balken. Session- und Gefühlsfenster im normalen Leben leicht transparent über ASCII-Hintergrund. Erste lokale Denkphase heißt „WIRD GEWECKT_“ / „WAKING UP_“, spätere „DENKT NACH_“. Nur lokal bis zum ersten sichtbaren Text ein subtiler roter Schimmer aus zwei weichen, per Backendzeit unregelmäßig wandernden und atmenden Lichtflächen im Terminal. Kleine Ansichten behalten die kompakte Anordnung. Während des Lebens schweben separate leuchtende ASCII-Fragmente hinter/um das Terminal (lokal vier, online neun; weich variierende Bahnen, Wirbel und Ausdehnung, auf30Prozent Bewegungstempo verlangsamt und gedämpftes Leuchten); Ankunftsflug bleibt unabhängig. Untertitel27px, Modusbadges28px; Schenkungsdialog40px mit separater Frage,
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
`install-autostart.sh`.
Mauszeiger nur in der Installationsseite anfangs versteckt; echte Mausbewegung,
Mausklick oder Mausrad (auch remote) zeigt ihn für vier Sekunden ohne Aktivität.
Erste Positionsmeldung und unveränderte Koordinaten ignorieren; mindestens zwei
Pixel tatsächlicher Weg zählen. Seitenanzeige/Fokus verstecken den Cursor erneut.
Touch zeigt keinen Zeiger. Keine globale Cursor-Unterdrückung oder Zusatzdienste.
Chromiums eigener On-Device-KI-Dienst und Übersetzungsfunktion sind deaktiviert. Keine Wiederöffnung nach Escape. Auf ausdrücklichen Nutzerauftrag vom 29. Oktober:
Bootdarstellung via `install-startup-boot.py` gesichert auf Schwarz umgestellt
(disable_splash, logo.nologo, eigenes Plymouth-Theme); keine weiteren Boot-/Login-/Dienstumbauten.
XDG-Autostart mit --boot-animation, genau einmal je Kernel-Boot-ID. 18,4 sichtbare Sekunden
Flackerndes ASCII-Zeichenfeld → HSLU → PHKI HS26 → Simon Balmer (gleiche Zeichengröße) → Ausklingen → Installationslogo → Startseite.
Refresh setzt fort; Ausblenden/Verbindungsausfall holt keine Zeit nach. Keine
Modell-/Kameraaktivität oder Instanzzählung während der Sequenz. Aktueller Boot wird
beim Installieren als gesehen markiert. --preview-startup nur mit --simulate.
Bootdateien niemals als Routinecheck ändern; Anleitung und Rückweg: docs/MAINTENANCE.md.
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
