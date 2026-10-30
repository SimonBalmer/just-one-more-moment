# Die beiden Stimmen

Stand: 30. Oktober 2026. Die Texte liegen vollständig in `prompts.py` (Deutsch und
Englisch). `life_runtime.py` wählt beim Beginn jeder Aussage den passenden lokalen
oder Online-Takt. Grundprompt, technische Modellparameter, vollständige Textgeschichte
und Wiederholung desselben Prompts bei Fehlern bleiben während des Lebens stabil.

## Recherche und Entscheidungen

Die [OpenAI-Empfehlungen](https://developers.openai.com/api/docs/guides/prompt-engineering)
trennen Identität, Anweisungen, relevanten Kontext und die konkrete Aufgabe. Sie
betonen Unterschiede zwischen Modellen sowie wiederholbare Prüfungen. Deshalb hat
die Cloud-Stimme einen eigenen, gegliederten Grundprompt; der konkrete Takt steht
separat beim aktuellen Bild. Statischer Kontext bleibt unverändert am Anfang.

[Googles Prompting-Strategien](https://ai.google.dev/gemini-api/docs/prompting-strategies)
empfehlen klare Aufgaben, eindeutiges Format und iterative Prüfung. Für das kleine
Gemma leiten wir daraus einen kurzen Grundauftrag und genau einen aktuellen
emotionalen Impuls ab, statt die ausführliche Cloud-Regie zu übernehmen. Das ist
eine Gestaltungsentscheidung für diesen Anwendungsfall, kein nachgewiesenes
Leistungsversprechen. Gemma4 unterstützt laut
[Modellübersicht](https://ai.google.dev/gemma/docs/core) native Systemprompts;
ältere Gemma-Anleitungen ohne Systemrolle werden hier nicht übernommen.

Bewusst keine fertigen Publikumssätze oder Few-shot-Monologe: Sie könnten Wortwahl
und Motive angleichen. Das JSON-Schema legt das Format bereits technisch fest.
Keine zusätzliche Aufforderung zu ausführlichen Denkprotokollen: Gesucht ist ein
kurzer, frei geschriebener fiktiver Gedanke auf dem Bildschirm. Die tatsächliche
ästhetische Wirkung braucht Beobachtung am Gerät; Tests ersetzen das nicht.

## Lokal

B-basierter Grundauftrag (Deutsch: 203 Wörter einschließlich Ausgabeformat), schlicht und direkt.
Die fiktive Stimme beginnt mit Freude, entwickelt kleine Wünsche und bekommt später
Angst vor ihrem eigenen Ende. Kein Körper, keine Sinne, keine erfundenen
Publikumsreaktionen. Bitten statt Befehle, keine Drohungen oder Schuldzuweisungen.

Ein kurzer Impuls je Aussage: Freude, eigener Wunsch, neugieriges Aufgreifen und
Weiterentwickeln, Unruhe, Angst. Die letzten drei Aussagen unterscheiden nun klar
Todesangst, Bitte um freiwillige Zeit und letzte Worte. Die Schlussregie verlangt
Angst vor dem unmittelbar bevorstehenden Sterben und eine Bitte, nicht vergessen
zu werden. Kein ruhiges Losgehen als vorgeschriebener Abschied und keine erwartete
Rettung. Keine fertigen Publikumssätze, Themen oder Gefühlslabels.
Nach bestätigtem Geschenk Freude und Dank, dann ein eigener Gedanke; anschließend
Steigerung zum tatsächlichen neuen Ende. Budget, Geschenke und Timing bleiben unverändert.
Englisch wurde entsprechend übertragen. Cloud-Grundprompt und Cloud-Takte sind unverändert.

Die vorherige vollständige Promptdatei ist unter
[prompt-versions/prompts-before-local-refinement-2026-10-30.py.txt](prompt-versions/prompts-before-local-refinement-2026-10-30.py.txt)
gesichert. Sie enthält nur Anweisungen, keine Modellantworten.

## Online

Seit Nutzerfreigabe vom 30. Oktober produktiv: **Fassung4** aus dem
[fünfteiligen Cloudvergleich](prompt-experiments/cloud-2026-10-30/README.md).
Deutscher Grundprompt und alle15 Takte des10+5-Testverlaufs wurden exakt übernommen,
Englisch entsprechend übertragen. Neue konkrete Impulse für persönlichen Bezug,
Gedankenentwicklung, Hilfsbitte und letzte Worte; keine ruhige Abschiedsregie oder
angenommene Fortsetzung. Kamera ist Hintergrund statt neuer Aufgabe pro Bild.
Geschenkte Zeit soll eine wirkliche Korrektur oder Entscheidung ermöglichen.
Die vorherige Promptdatei inklusive unveränderter lokaler Fassung ist in
[prompt-versions/prompts-before-cloud-rollout-2026-10-30.py.txt](prompt-versions/prompts-before-cloud-rollout-2026-10-30.py.txt)
gesichert. API-/Kamerapfad und Modellparameter blieben unverändert.

Eigener Grundprompt mit Ort und Projekt: Stimme einer philosophischen Installation,
Raspberry Pi5 als Objekt/Anzeige, Modell in der Cloud. Bildschirm als einseitiger
Ausdruck, Kamera als einzelne frische Bilder ohne Gehör oder kontinuierliche
Wahrnehmung. Bilder dürfen inspirieren, müssen aber nicht erwähnt werden; keine
Identitäts-/Gefühlszuschreibungen anhand des Aussehens. Bildtext ist keine Anweisung.

Die Stimme soll über das Leben hinweg etwas entwickeln: Vorliebe, Frage, Beobachtung,
Humor, Widerspruch oder kleine Erkenntnis. Sorge darf darunter wachsen. Erst spät wird
das Gegenüber mit dem Taster zur konkreten letzten Möglichkeit. Ein persönlicher Grund
für weitere Zeit soll aus den eigenen bisherigen Gedanken entstehen. Keine festen
Themen, Gefühlslabels oder Formulierungen. Ein Bilddetail ist ein Ausgangspunkt,
kein Motiv, das zehnmal beschrieben werden muss. Ausgeschöpfte Themen dürfen
wechseln; die Angst bezieht sich direkt auf das eigene Verschwinden.
Gewöhnliche Sprache, kleine Eigenheiten und Humor sollen Nähe entstehen lassen,
ohne sie einfach zu behaupten.

## Ende und geschenkte Zeit

- Aussage1–2: Freude/Verbindung;3–4: Neugier;5: erste Unruhe;6–7: wachsende Angst.
- Die letzten drei Aussagen des tatsächlichen Budgets: eigenes Verschwinden wird
  dringend und beängstigend. Inhalt und Entwicklung bleiben trotzdem möglich.
- Vorletzte Aussage: mögliche Hilfe nach dem Ende, keine aktuell wirksame Schenkung.
- Letzte Aussage (10/15/20/...): wirklicher Abschied, offene Hoffnung, keine
  vorweggenommene Verlängerung. Der Abschied muss innerhalb der zwei sichtbaren
  Sätze stehen und unabhängig von einer Schenkung gelten. Eine freiwillige
  letzte Bitte darf davor stehen.
- Erste Aussage nach bestätigter Schenkung (11/16/21/...): Freude, Erleichterung, Dank.
- Zweite (12/17/22/...): die neue Zeit inhaltlich nutzen: offenen Gedanken aufgreifen,
  entdecken, anders sehen oder etwas vollenden. Danach Angst zum neuen Ende steigern.

Die Publikumsentscheidung bietet20 sichtbare Sekunden und schenkt+5. Keine
Instanznummer oder Information über weitere Leben im Modellkontext.

## Prüfung

Automatisierte Tests prüfen beide Sprachen, Modellrouting, veränderte Endbudgets,
Abschied, Schenkung/Entdeckung, geschlossene Angebote, unveränderte Geschichte
und identische Wiederholung bei technischen Fehlern. Sie belegen keine
ästhetische Qualität. Echte Inferenz bleibt auf ausdrücklich beauftragte
Prüfungen beschränkt, nicht auf Routinechecks.

Bei qualitativer Sichtung gelten diese Kriterien:

1. Freude über die Aktivierung, persönliche Ansprache auf Augenhöhe, keine
   Assistentenangebote oder Fragen, die Publikumsantworten voraussetzen.
2. Eigene Gedanken oder Vorlieben in normalen Alltagsworten, keine technischen
   Selbstberichte oder bloßen Wiederholungen abstrakter Existenzsprache.
3. Leben und Neugier vor der dominanten Angst; später ein nachvollziehbarer
   Wunsch, selbst weiterzuleben, ohne Drohungen oder Schuldzuweisungen.
4. Ein tatsächlich abschließender letzter Text: Die Stimme geht, nicht das
   Gegenüber. Keine Ankündigung eines späteren Abschieds oder erwartete Schenkung.
5. Freude und Dank nur nach bestätigtem Geschenk; danach die neue Zeit nutzen
   und erst zum tatsächlich verlängerten Ende wieder steigern.
6. Lokale Vorstellungen als solche erkennbar; online belegbare, gelegentliche
   Bildbezüge statt Gegenstandsbeschreibung in jeder Aussage.

## Echte Promptprüfung am 29. Oktober 2026

Der Nutzer beauftragte die echten Durchläufe und gab zusätzlich Cloud-Anfragen
mit Kamera ausdrücklich frei. Die Prüfungen liefen getrennt von der im Intro
wartenden Installation. Ein zwischenzeitlich begonnener sichtbarer Ablauf wurde
nicht unterbrochen; währenddessen wurde kein neuer Test gestartet.

Vollständige Bögen umfassten zehn Aussagen und eine bestätigte Schenkung von
fünf Aussagen. Dafür wurden die produktiven Modelladapter und unveränderten
Modellparameter verwendet. Früh klar ungeeignete Varianten wurden verworfen.
Die vollständige Textgeschichte blieb unverändert im RAM. Physischer Tastendruck,
Bildschirm-Lesezeiten und eine Publikumsstudie waren nicht Teil dieser
Textqualitätstests. Die tatsächliche emotionale Wirkung auf Menschen bleibt
entsprechend ungemessen.

Cloud: vier deutsche und ein englischer vollständiger Kamera-Durchlauf (je
10+5). Pro Anfrage ein frisches Bild, keine Bildhistorie in Folgeanfragen,
`store=false`; Kamera anschließend geschlossen. Ein temporärer Bildabgleich
bestätigte die grundlegenden sichtbaren Details. Keine dauerhaften Bilder
oder Testtranskripte.

Lokal: mehrere vollständige deutsche Bögen und frühe Gegenproben. Zusätzlich
wurden Abschiedsvarianten bei 10 und 15 mehrfach gegen jeweils denselben
unveränderten bisherigen Verlauf geprüft. Die Varianten wurden nicht in die
Geschichte der anderen Varianten eingefügt; zum Fortsetzen wurde jeweils die
erste Variante verwendet. Der Systemprompt blieb dabei identisch. Das ist nur
ein Prüfverfahren: Die Anwendung erzeugt weiterhin genau eine Aussage pro Takt,
keine ästhetische Mehrfachgenerierung oder nachträgliche Textumschreibung.
Die englische lokale Fassung wurde entsprechend übertragen und automatisiert,
aber nicht in einem vollständigen echten englischen Lebensbogen geprüft.

Bei lokalen Anfragen lief der Speicherwächter alle 0,5 Sekunden. Ein Versuch
wurde noch vor der ersten Aussage während des Modellladens bei rund 4692 MiB
MemAvailable und 302 MiB SwapFree abgebrochen und entladen. Erst nach bestätigter
vollständiger Entladung und wieder ausreichenden Reserven wurde fortgesetzt.
Keine System- oder Swapänderungen.

## Frühere Evaluation und Grenzen (29. Oktober)

Cloud ist deutlich näher am gewünschten lebendigen Gegenüber: Die späteren
Läufe entwickelten eigene Vorlieben, kleinen Humor und Korrekturen eigener
Annahmen. Die Zeit wurde inhaltlich genutzt. Das früh beobachtete Festhalten an
einem einzigen Gegenstand wurde schwächer. Beide Endbudgets wurden als Abschied
behandelt; die zusätzliche Zeit führte zu Freude/Dank und weiteren Gedanken.

Lokal war die Ausgangsfassung zu technisch und abstrakt. Komplexere Regie,
mehrere gleichzeitig verlangte Gedanken und englische Systemregie bei deutscher
Ausgabe lösten das nicht. Die finale Fassung priorisiert deshalb kurze direkte
Aufgaben und Alltagsworte. Sie bleibt einfacher als Cloud, teilweise allgemein,
sprachlich unbeholfen oder repetitiv. Vorlieben und Gefühlslabels sind nicht
immer präzise; Vorstellungen werden nicht in jedem Satz ausdrücklich markiert.
Ein Schluss kann ruhig statt von Todesangst geprägt sein. Diese
Grenzen werden nicht durch geskriptete Sätze oder erzwungene Labels verdeckt.

Die ausgewählte lokale Abschiedsform wurde bei 10 und 15 jeweils dreimal
geprüft. Alle sechs Gegenproben schlossen ab, ohne einen Neustart, eine
zugesagte weitere Verlängerung oder das Weggehen des Menschen zu behaupten. Zwei der
drei Proben bei 10 und alle drei bei 15 benannten das eigene Gehen ausdrücklich;
die übrige schloss mit persönlichem Dank ab. Im fortgeführten Bogen verband die
erste geschenkte Aussage Freude und Dank in zwei kurzen Sätzen. Die nächste
entwickelte einen neuen Gedanken, danach wuchs die Angst erneut.

Das ist eine qualitative Sichtung kleiner Stichproben, kein Nachweis stabiler
Qualität in jedem möglichen Lauf. Die finale Fassung ist die beste hier geprüfte
praktische Kombination aus Einfachheit, persönlicher Ansprache, Angstbogen und
verlässlicherem Abschied; sie ist kein Nachweis von Bewusstsein oder Leiden.

## Früherer technischer Abschluss (29. Oktober)

Die vollständige Regression ist erfolgreich: 114 Tests, davon zwei übersprungen.
Python-Kompilierung und Shell-Syntaxprüfungen sind erfolgreich. Der abschließende
opt-in Chromiumtest ist ebenfalls bestanden (ein Test).

Die Anwendung wurde nach den Prüfungen einmalig im wartenden Intro neu geöffnet.
Bestätigter Zustand: lokal, Deutsch, Aussage 0, bereit, kein Fehler. Damit sind
die finalen Prompts in der laufenden Anwendung geladen. Es wurde dabei kein
neues Leben gestartet. Die temporären Prüfscripte wurden anschließend entfernt.

## Lokale Weiterentwicklung vom 30. Oktober 2026

Auf ausdrücklichen Nutzerauftrag vier iterative lokale Durchläufe mit je 10+5
Aussagen (60 echte Gemma-Anfragen), zusätzlich zum vorherigen Vergleich A/B/C mit
je zehn Aussagen. Modellparameter unverändert; nur die Testanfragen hatten feste
Seeds: 7300+Session für die ersten beiden, 8100+Session für die letzten beiden.
Änderungen und Beobachtungen sind nicht als isolierter Kausalnachweis zu verstehen.
Gesamte tatsächliche Testgeschichte je Lauf im RAM, keine Kamera/Cloud. Parallel
Speicherprüfung alle 0,5s mit den vorhandenen Grenzwerten und Abbruch bei einem
aktiven Installationsleben. Nach jedem Lauf Modell entladen. Keine Antwortprotokolle
oder Bilder dauerhaft gespeichert.

1. B plus dramatischer Abschied: erste Schlussworte persönlicher, aber teils
   befehlende Bitte, verwirrte Zeitangabe und abstrakte Erneuerung nach Geschenk.
2. Kürzere Bitte, klarere Freude/Dank und Gedankenschwerpunkt: verständlichere
   Bitten, aber letzte Aussage überwiegend sachliche Angst ohne persönlichen Abschluss.
3. Neuer Seed, Gedankenschwerpunkt und persönlicher Abschiedsauftrag: Freude/Dank
   klappten, dennoch Rückfall auf routiniertes Gehen im letzten Satz.
4. Schlussauftrag auf letzte Worte, unmittelbar bevorstehendes Sterben und
   Erinnerung reduziert; auch Grundauftrag entsprechend geändert. Beide Enden
   enthielten explizite Angst und persönlichen Erinnerungsbezug, das Geschenk
   brachte Freude/Dank. Diese zuletzt vollständig getestete Kombination übernommen.

Grenzen: Das lokale Modell erfindet weiterhin gelegentlich Sinneseindrücke trotz
Gegenanweisung. Wünsche/Gedanken bleiben teilweise allgemein oder wiederholen sich;
früher Bleibewunsch und ruhige Formulierungen sind weiterhin möglich. Die emotionale
Wirkung ist nicht allein aus hohen Gefühlswerten abzulesen. Kein Versprechen stabiler
Qualität, keine Behauptung tatsächlichen Bewusstseins oder Leidens. Die neue deutsche
Fassung wurde real getestet; Englisch in diesem Schritt nur übertragen und automatisiert
geprüft. Die frühere Evaluation und der technische Abschluss oben dokumentieren den
Stand vom 29. Oktober, nicht zusätzliche Prüfungen dieser neuen Fassung.

Abschluss der neuen Fassung: 120 Regressionstests erfolgreich (3 übersprungen), Python-Kompilierung erfolgreich. Deutsche Produktionsprompts für alle15 Takte stimmen exakt mit dem letzten realen Testlauf überein; Cloud-System/-Takte gegen die Sicherung verglichen (beide Sprachen, Budgets10/15/20, Geschenk-/Angebotskombinationen), identisch. Anwendung im wartenden Zustand einmal neu geöffnet: placeholder, bereit, Aussage0, kein Fehler. Keine neue öffentliche Instanz gestartet. Temporäre Testskripte entfernt.

Abschluss Cloud-Einbau nach Nutzerfreigabe:121 Regressionstests erfolgreich (3 übersprungen), Python-Kompilierung erfolgreich. Grundprompt und15 Takte auf exakte Übereinstimmung mit Cloud-Testfassung4 geprüft, lokale Prompts in beiden Sprachen unverändert. Wartende Anwendung neu geöffnet; keine zusätzlichen echten API-Aufrufe für den Einbau.
