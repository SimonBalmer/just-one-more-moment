# Startup: Just one more moment

Stand: 30. Oktober 2026. Auf ausdrücklichen Nutzerauftrag umgesetzt.

## Sichtbarer Ablauf

Die frühe Bootphase bleibt schwarz. Sobald die grafische Sitzung und der vorhandene
Installationslauncher bereit sind, beginnt die Sequenz. Es gibt keine künstliche
Verzögerung des Systemstarts oder neue Systemdienste.

| Sichtbare Zeit | Darstellung |
| --- | --- |
| 0–2,4 s | Dichtes rotes Zeichenfeld, unabhängig wechselnde Zeichen und weiße Aufheller |
| 2,4–4,5 s | HSLU als weiße Zeichen innerhalb desselben Rasters |
| 4,8–6,9 s | PHKI HS26 |
| 7,2–10,2 s | Simon Balmer |
| 10,2–11,8 s | Wieder freies Zeichenflackern |
| 11,8–13,4 s | Zeichenfeld klingt aus |
| 13,3–18,4 s | Installationslogo mit Credits, rotem Seitenstreifen und rotem Cursor; anschließend Ausblenden |
| Danach | Normale Startseite mit der am Gerät gewählten Sprache und Betriebsart |

Die Credits erscheinen nacheinander als nebeneinanderstehende Zeichen in exakt derselben Schrift und Größe wie das übrige Feld. Die Wörter erscheinen an unterschiedlichen Positionen im Raster. Die Umgebung flackert unverändert weiter; allein das reine Weiß kennzeichnet die Wörter. Weiße Zufallszeichen leuchten schwächer (48 % statt voller Deckkraft). Das Schlusslogo hat keine eigene schwarze Hintergrundfläche. Keine fallenden Zeichenströme oder großen Buchstabenmasken. Das Schlusslogo verwendet denselben
codebasierten Pixel-Schriftzug wie die Installation und die vom Nutzer gelieferte
Vorlage: `SIMON BALMER / PHKI / HSLU` und `AI / EMPATHY / RESPONSIBILITY`.

[Vorschau Namenszug](previews/startup-credits.png) · [Vorschau Logo](previews/startup-logo.png)

## Nur beim Pi-Boot

Der vorhandene XDG-Autostart ruft `start-installation.sh --boot-animation` auf.
`startup.py` vergleicht die Kernel-Boot-ID mit
`~/.local/state/just-one-more-moment/startup-boot-id` (bzw. `XDG_STATE_HOME`).
Die gesperrte Markerdatei speichert ausschließlich diese dekorative Boot-Kennung,
keine Instanznummer, Gesprächsinhalte oder Modellinformationen.

Pro Betriebssystem-Boot wird die Sequenz höchstens einmal beansprucht. Ein neuer
Login, ein Anwendungsneustart, Browser-Refresh oder ein reguläres Lebensende starten
sie nicht erneut. Ein Refresh während der Sequenz setzt die aktuelle serverseitige
Position fort. Escape schließt wie bisher die Anwendung; sie öffnet sich nicht selbst
wieder. Ein gewöhnlicher manueller Start ohne Boot-Flag zeigt direkt die Startseite.

`install-autostart.sh` markiert den aktuellen Boot bereits als gesehen. Eine
Installation oder Aktualisierung spielt deshalb keine neue Startup-Sequenz in der
laufenden Sitzung ab; sie ist für den nächsten Pi-Boot eingerichtet.

Die Sequenz zählt nur zusammenhängend bestätigte sichtbare Browserzeit. Hintergrund,
Verbindungsunterbruch und lange fehlende Heartbeats werden nicht nachgeholt. Eine
Canvas-Ebene mit maximal 12 FPS und begrenzter Zeichenanzahl; ausschließlich lokale
Schrift und codebasierte Grafik. Kein Zeichenfeld hinter einem laufenden Modellleben.

Während der Sequenz werden keine Intro-Anzeigequittierungen akzeptiert. Daher kann
auch der physische Taster kein Leben starten. Keine Instanz zählt hoch, keine
Modellanfrage, Vorladung oder Kameraaufnahme wird von der Sequenz ausgelöst. Erst
die normale, danach sichtbare Startseite übernimmt ihren bisherigen Ablauf.

## Bootlogo-Unterdrückung

Der separate Installer ist bewusst keine Routineprüfung:

```bash
python3 install-startup-boot.py            # zeigt nur den konkreten Plan
sudo python3 install-startup-boot.py --apply
```

Er verwendet die bereits installierten Werkzeuge, sichert Konfiguration und die
betroffenen ursprünglichen Initramfs unter `/var/backups/just-one-more-moment-boot-*`
und nimmt nur die folgenden Änderungen vor:

- `/boot/firmware/config.txt`: `disable_splash=1` in einem eigenen `[all]`-Block
  unterdrückt den Firmware-Regenbogen.
- `/boot/firmware/cmdline.txt`: `logo.nologo` unterdrückt das Kernel-Logo. Alle bisherigen
  Argumente, insbesondere Root-Partition und Konsolen, bleiben erhalten.
- Eigenes schwarzes Plymouth-Theme `moment-black` ersetzt den bisherigen Pi-Splash.
  Notwendige Passwort-/Frage-/Fehlermeldungen bleiben darstellbar.
- `update-initramfs -u -k all` bettet das Theme in beide vorhandenen Bootvarianten ein.

Keine Paketinstallation, SPI-Änderung, Login-/Dienstkonfiguration, EEPROM-Änderung,
Netzwerkunterbrechung oder automatischer Geräte-Neustart. Bei einem Installationsfehler
stellt das Skript die gesicherten Originaldateien einschließlich Initramfs wieder her.

Die [Raspberry-Pi-Dokumentation](https://www.raspberrypi.com/documentation/computers/configuration.html)
unterscheidet Firmware-/Kernel-Darstellung und Plymouth-Splash.
[`disable_splash`](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/config_txt/boot.adoc)
betrifft den Regenbogen. Ein angezeigter Bootloader-Diagnosebildschirm bei Fehlern ist
kein Teil der normalen Startup-Sequenz und wird nicht über EEPROM-Eingriffe versteckt.

Am Ausstellungs-Pi hat der Nutzer den Administratorbefehl selbst ausgeführt.
Geprüft wurden die aktive Auswahl `moment-black`, unveränderte übrige Bootparameter
und beide neu gebauten Firmware-Initramfs mit den eingebetteten Theme-Dateien.
Sicherung dieses Geräts:
`/var/backups/just-one-more-moment-boot-20261029T211804323421Z`.

Bootdarstellung dieses Geräts zurücksetzen:

```bash
sudo python3 install-startup-boot.py --restore /var/backups/just-one-more-moment-boot-20261029T211804323421Z
```

Das stellt auch die ursprünglichen Initramfs wieder her. Die Benutzer-Startsequenz
ist davon unabhängig. Sie lässt sich durch Entfernen von `--boot-animation` aus der
XDG-Desktop-Datei deaktivieren. Deren frühere Fassung liegt auf diesem Gerät unter
`~/.local/state/just-one-more-moment/autostart.before-startup.desktop`.

## Vorschau und Prüfung

```bash
python3 main.py --simulate --preview-startup --port 8766
# Im Browser http://127.0.0.1:8766/ öffnen; nach der Sequenz normale Simulation.
python3 -m unittest discover -q
MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_startup_browser tests.test_browser
```

Die Vorschau benötigt keine echte Kamera, GPIOs oder Modelle und beansprucht nicht
die reale Boot-Kennung. Der Preview-Schalter ist nur zusammen mit `--simulate` erlaubt.

Geprüft: konkurrierende Boot-Claims, neue Boot-ID, Pause bei versteckter Oberfläche
und Verbindungsunterbruch, veraltete Token, Sperre vor Intro-/Lebensstart, unveränderte
Kernel-/SPI-Konfiguration und idempotenter Installationsplan. Im echten isolierten
Chromium: alle Wortphasen und Logo, Refresh-Fortsetzung, vollständiger Übergang in die
Startseite und kein Replay nach erneutem Laden. Beide Chromiumtests sind bestanden;
die Regression umfasst 119 Tests (drei regulär übersprungen). Python- und Shell-Syntax
sind geprüft. Kein echter Modelllebenszyklus oder Kameratest wurde dafür gestartet.

Der Pi wurde nicht neu gestartet. Der vollständige physische Kaltstart einschließlich
der frühesten Firmwaredarstellung lässt sich erst beim nächsten regulären Start prüfen.

Abschluss: Anwendung einmalig regulär neu geöffnet und im Intro bereit bestätigt,
Aussage 0, kein Fehler. Die neue Startup-Sequenz ist beim laufenden Boot inaktiv;
sie bleibt wie vorgesehen für den nächsten Pi-Boot aktiviert. Boot-Konfiguration,
Autostart, Prüfstand und Rückweg sind vollständig gespeichert.

Anpassung vom 30. Oktober: stationäres Zeichenfeld statt Regen, Credits in normaler Zeichengröße. Fünf gezielte Startup-Tests einschließlich Chromium bestanden; Vorschauen aktualisiert.
