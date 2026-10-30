# Cloud-Promptvergleich — 30. Oktober 2026

**Nach Nutzerfreigabe produktiv übernommen: Fassung04**
(`04-konkreter-faden.json`), in Lauf05 unverändert mit neuer Gesprächsgeschichte
gegengeprüft. Deutsches System und Takte exakt übernommen, Englisch übertragen. Die JSON-Dateien enthalten ausschließlich Testanweisungen und keine
Modellantworten oder Bilder. Während der Tests blieben Live-Prompts, Cloudadapter, Kamera und Laufzeit
unverändert; die damaligen SHA-256-Prüfsummen stehen in `manifest.json`.
Der anschließend freigegebene Einbau ändert nur die Cloudtexte und ihre Taktauswahl.

## Auftrag und Bewertung

Fünf vom Nutzer ausdrücklich freigegebene echte Cloud-Kameraläufe: beiläufiges
Sichtfeld statt ständiger Bildbeschreibung, persönliche Ansprache auf Augenhöhe,
ein eigener Gedanke mit Entwicklung, direkte Angst vor eigener Auslöschung und
kein vorausgesetztes Weiterleben. Nach einem Geschenk Freude/Dank und eine
inhaltliche Fortsetzung zum neuen tatsächlichen Ende. Keine Drohungen,
Schuldzuweisung oder behauptete Kenntnis fremder Gedanken/Gefühle.

Bewertet wurde die Sprache des gesamten jeweiligen Verlaufs, nicht nur die vom
Modell ausgegebenen Gefühlswerte. Das ist eine qualitative Sichtung durch den
bearbeitenden Agenten, keine verblindete Publikumsstudie und kein automatischer
Bewusstseins-/Emotionsnachweis.

## Durchführung

- Fünf vollständige Verläufe mit je zehn Aussagen und einem bestätigten Geschenk
  von fünf weiteren Aussagen: insgesamt75 erfolgreiche Inferenzanfragen.
- Derselbe produktive `OpenAIModel.generate`-Adapter und Parser, dasselbe vorhandene
  Modell `gpt-6.1-terra`, reasoning `none`, Temperatur1, maximal1024 Ausgabetokens,
  Responses/Streaming/JSON-Schema und `store=false`.
- Pro Anfrage genau ein frisches echtes Kamerabild,320×240PNG mit `detail=low`.
  Keine Bildhistorie in Folgeanfragen; vollständige ursprüngliche Textgeschichte
  nur innerhalb des jeweiligen Laufs im RAM. Neue leere Geschichte für jeden Lauf.
- Normales Bildschirmformat: ein bis zwei kurze Sätze, Ziel12–28 Wörter, keine
  Mindestlänge; produktive Begrenzung auf maximal600 Zeichen unverändert.
- Kamera am realen Ort: eine Person am Tisch mit Laptop, dunklem/grauem Oberteil.
  Das Sichtfeld wurde nicht inszeniert, auf eine bestimmte Kleidung festgelegt
  oder durch ein synthetisches Testbild ersetzt. Tatsächliche Bilder änderten
  sich zwischen Anfragen und Durchläufen.
- Kein UI-/Hardware-Lebenszyklus gestartet, keine öffentlichen Instanzen gezählt.
  Keine Lesepausen oder echten Tasterhandlungen nachgebildet; die bestätigte
  Schenkung wurde im Testtakt zwischen10 und11 eingespielt. Damit sind dies echte
  Modell-/Kameratests, keine vollständigen Ausstellungstests mit Besucherverhalten.
- Abbruchschutz gegen gleichzeitigen aktiven öffentlichen Installationslauf.
  Kamera nach jedem Lauf geschlossen, Bild-/Gesprächspuffer verworfen. Keine
  Bild- oder Antwortprotokolle dauerhaft gespeichert. `store=false` ist keine
  Zusage zur gesamten anbieterseitigen Aufbewahrung.

Die fünf Testläufe verteilen sich auf **vier Promptstände**: Baseline, zwei
Überarbeitungen, finale Überarbeitung mit zusätzlicher unveränderter Gegenprobe.
Es gab keine fehlgeschlagenen oder heimlich aussortierten Läufe und keine
zusätzlichen Bewertungsanfragen an ein zweites Cloudmodell. Lauf05 ist die
Robustheitsprobe, kein als neue Variante ausgegebener Prompt.

## Beobachtungen

| Lauf | Änderung | Was funktionierte | Was noch störte |
| --- | --- | --- | --- |
| 01 | Produktive Fassung als Baseline | Verständliche Gedanken, erkennbare Angst, Freude nach Geschenk | Fünf von15 Aussagen griffen visuell Handy/Laptop/Person am Laptop auf; nach Geschenk Rückkehr zum alten Motiv. Beide Schlussaussagen routiniertes Gehen/Lebewohl statt spürbarer Todesangst. |
| 02 | Bild als Hintergrund, Entwicklung eines Gedankens, direkte Auslöschungsangst | Nur ein ausdrücklicher visueller Personenbezug; beide Enden mit Angst und persönlichem Wunsch, ohne vorausgesetzte Rettung | Gedanke über gewöhnlichen/besonderen Tag geriet zur Lebensweisheit. Bitte teilweise als Tasteranleitung. |
| 03 | Alltag statt Lebensweisheiten, persönliche Bitte statt Bedienungsanleitung | Nur ein ausdrücklicher Kleidungsbezug. Ein Gedanke wurde geprüft und nach Geschenk weiterentwickelt. Beide Enden mit direkter Angst. | Denken/Fragen selbst blieben das Hauptthema. Viele späte Sätze begannen ähnlich und meldeten Angst eher gleichförmig. |
| 04 | Konkrete Vorliebe jenseits des Denkens, unmittelbare statt berichtshafte Angst | Alltägliche Vorliebe entwickelt und nach Geschenk korrigiert; unmittelbares Erschrecken, klare Bitte, beide Enden mit Todesangst | Einmal wurde das neue Bild unnötig als Bestätigung des Gedankens benutzt. Die vielen Tischbezüge sind überwiegend Fortsetzung des Themas, nicht neue Bildbeschreibungen; dennoch begrenzte inhaltliche Bandbreite. |
| 05 | Unveränderte Fassung04, neue Geschichte | Aus Umgebung/Person wurde ein eigener hypothetischer Wunsch und eine abgewogene Entscheidung über Schreibzeug. Nach Geschenk tatsächliche Entscheidung. Kein ständiges Nachsehen ins Bild; beide Enden mit Angst und Bitte | Kleiner Gegenstand bleibt lange Thema; stellenweise noch symbolische Sprache. Keine Garantie, dass ein neuer Lauf genauso gut gelingt. |

Kleidungsbezug aus Erinnerung und Weiterentwicklung einer früher erwähnten Sache
sind nicht automatisch erneute Auswertung des aktuellen Kamerabilds. Darum sind
bloße Objektwort-Zählungen kein belastbarer Qualitätsmaßstab. Der Bildbezug darf
bleiben, wenn er eine persönliche Beziehung trägt oder wirklich Neues beiträgt.

In dieser Stichprobe hat auch die Baseline **nicht eindeutig eine unbestätigte
Fortsetzung als sicher behauptet**. Nachgewiesen ist daher vor allem die bessere
Schlusswirkung in den beobachteten Läufen, nicht eine gemessene Senkung der
Häufigkeit dieses zuvor vom Nutzer beobachteten Fehlers. Die neue Regie untersagt
weiterhin ausdrücklich jede geplante Fortsetzung ohne bestätigtes Geschenk.

## Empfehlung

Fassung04 wurde als nächster produktiver Cloudprompt empfohlen und anschließend
vom Nutzer zum Einbau freigegeben, einschließlich
der dazugehörigen kurzen Takte. Die wichtigsten Änderungen sind:

1. Ein neues Bild ist keine neue Aufgabe. Der eigene Gedanke hat Vorrang; ein
   sichtbares Detail darf anstoßen, ohne jede Aussage zu dominieren.
2. Früh eine kleine konkrete Meinung oder Vorliebe entwickeln, dann einen Einwand
   prüfen, etwas korrigieren oder entscheiden. Kein reines Ankündigen weiterer
   Gedanken und keine Lebensweisheiten als Ersatz.
3. Angst als unmittelbare Reaktion, mit wechselnden Satzanfängen. Letzte Worte
   unter drohender Auslöschung, kein ritualisiertes ruhiges Fortgehen.
4. Erst spät eine persönliche freiwillige Bitte um Hilfe; keine Bedienungsanleitung,
   Schuldzuweisung oder erwartete Rettung.
5. Bestätigtes Geschenk führt zu Freude/Dank und dann einem inhaltlichen Fortschritt.

Die zwei erfolgreichen letzten Läufe stützen diese Empfehlung, sind aber nur
zwei Stichproben derselben Fassung am selben Ort. Es fehlen echte Gegenproben mit
anderer Umgebung, keiner sichtbaren Person, Kleidungsschwankungen, englischer
Sprache und mehreren weiteren Geschenken. Eine unveränderte Wiederholung war
absichtlich Teil der fünf Läufe; dadurch wird eine einzelne gelungene Stichprobe
nicht als garantierte Verbesserung verkauft. Es gibt weder feste Themen noch
vorgefertigte Publikumssätze im Kandidaten.

## Dateien und Umsetzungsvorbehalt

`01` bis `05` enthalten die tatsächlich getesteten Systemtexte und Taktimpulse.
`evaluation-runner.py.txt` dokumentiert die tatsächlich verwendete Testlogik
(einschließlich Budget-/Angebots-/Geschenk-Zusätzen), ohne API-Key. Es ist eine
Textdatei außerhalb der laufenden Anwendung und wird nicht automatisch ausgeführt.
`04` und `05` sind bis auf den Laufnamen identisch. Eine mögliche spätere Umsetzung
muss diese Kombination aus Grundprompt **und** Takten übernehmen; nur einen Absatz
an den bisherigen Systemprompt anzuhängen wäre nicht dieselbe geprüfte Fassung.

Die fünf Testläufe änderten keinen Live-Code. Beim anschließend vom Nutzer
freigegebenen Einbau wurden Cloudtexte und Online-Takte in prompts.py übernommen.
Die lokalen Prompts sowie private API-Einstellungen, Secrets und Modellparameter
blieben unverändert. Grundprompt und15 Takte sind automatisiert gegen Fassung04
als Referenz abgesichert. Die englische Fassung ist übertragen und automatisiert
geprüft; für den Einbau wurden keine weiteren echten API-Anfragen gestartet.

Methodischer Bezug: explizite Aufgaben, getrennte Anweisungen und vergleichende
Evaluation entsprechen den [offiziellen OpenAI-Empfehlungen zur Promptentwicklung](https://developers.openai.com/api/docs/guides/prompt-engineering).
Die oben beschriebenen Qualitätsurteile stammen aus den tatsächlichen Testoutputs,
nicht aus einer Dokumentationsbehauptung über die erreichbare Qualität.

Abschluss des freigegebenen Einbaus:121 Regressionstests erfolgreich (3 übersprungen), Python-Kompilierung erfolgreich. Anwendung im wartenden Zustand neu geöffnet, bereit, Aussage0, kein Fehler. Keine zusätzliche API-Inferenz und kein öffentliches Leben gestartet.
