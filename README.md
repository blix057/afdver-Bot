# AfD-Twitter-Monitoring-Bot

Ein automatisiertes System zur Beobachtung öffentlicher Inhalte der Alternative für Deutschland (AfD) auf X/Twitter. Es analysiert Tweets auf mögliche verfassungsrelevante Hinweise im Sinne von Art. 21 Abs. 2 Grundgesetz (GG) und erstellt strukturierte Berichte mit Links und Kurzsummaries. Optional werden gefundene Links (Quellen) in einer MongoDB gespeichert, um sie über mehrere Nutzer hinweg zu deduplizieren.

## Überblick

Der Bot überwacht offizielle AfD-Accounts auf Bundes- und Landesebene und durchsucht deren öffentliche Tweets nach Schlagwörtern und Mustern, die auf verfassungsrechtlich relevante Aspekte hindeuten könnten. Die Kriterien orientieren sich am rechtlichen Rahmen für Parteiverbote in Deutschland. Ergebnisse werden in einem Textbericht zusammengefasst; optional werden erkannte Links in einer Datenbank festgehalten (ohne Duplikate).

## Rechtlicher Hinweis

⚠️ WICHTIG: Dieses Projekt ist ein automatisiertes Analyse- und Forschungswerkzeug. Es ist weder eine juristische Begutachtung noch ein Beweismittel. Eine verfassungsrechtliche Bewertung von Parteien obliegt ausschließlich dem Bundesverfassungsgericht. Ergebnisse sollten unabhängig geprüft und stets im Kontext betrachtet werden.

## Funktionen

- Account-Monitoring: Überwachung offizieller AfD-Accounts (Bund/Länder)
- Schlagwort-Analyse: Suche nach verfassungsrelevanten Begriffen und Phrasen
- Schweregrad-Scoring: 0–10 basierend auf Trefferanzahl und Kategoriegewichtung
- Inhaltskategorien: Einordnung u. a. in anti-demokratisch, Gewaltbefürwortung, u. a.
- Berichte: Ausführliche Textberichte mit Links, Kategorien, Metriken und Kurzsummary
- Ratenbegrenzung: Beachtung der API-Limits von X/Twitter
- Optionale MongoDB-Anbindung: Kollaboratives, dedupliziertes Link-Repository

## Voraussetzungen

- Python 3.8 oder höher
- Zugang zu Twitter/X API v2 (Bearer Token + OAuth 1.0a)
- Python-Abhängigkeiten (siehe `requirements.txt`)
- Optional: MongoDB (z. B. MongoDB Atlas) für gemeinsame, deduplizierte Link-Speicherung

## Einrichtung

### 1) Twitter/X API-Zugang beschaffen

So erhältst du API-Schlüssel:
1. Auf https://developer.twitter.com anmelden
2. Entwicklerzugang beantragen und ein Project + App anlegen
3. In der App generieren:
   - API Key und API Secret
   - Bearer Token
   - Access Token und Access Token Secret
4. Diese Werte in die `.env` eintragen (siehe unten)

### 2) Abhängigkeiten installieren

Virtuelle Umgebung (empfohlen):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Dann Pakete installieren:

```bash
pip install -r requirements.txt
```

### 3) Umgebungsvariablen konfigurieren

1. Vorlage kopieren:
```bash
cp .env.template .env
```

2. `.env` bearbeiten und Twitter/X-API-Daten (und optional MongoDB) setzen:
```env
# Twitter/X
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# MongoDB (optional, empfohlen für gemeinsame Deduplizierung)
# Beispiel (MongoDB Atlas): mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority
MONGODB_URI=your_mongodb_connection_uri_here
```

## Nutzung

Wenn `MONGODB_URI` gesetzt ist, werden aus den markierten Tweets alle erkannten URLs extrahiert und dedupliziert in der Datenbank gespeichert. Ohne MongoDB läuft der Bot weiterhin und erzeugt lokale Berichte.

### Basisbeispiele

Vollständige Analyse (Accounts + Schlagwörter):
```bash
python main.py
```

### Kommandozeilen-Optionen

- `--accounts-only`: Nur AfD-Accounts durchsuchen (ohne Schlagwortsuche)
- `--keywords-only`: Nur per Schlagwörtern suchen (ohne Accountsuche)
- `--output-dir PATH`: Verzeichnis für Berichte (Standard: `./reports`)
- `--verbose`: Ausführliches Logging aktivieren
- `--dry-run`: Analyse ohne Berichtserzeugung

MongoDB wird automatisch über `MONGODB_URI` erkannt – keine zusätzlichen Flags nötig.

### Beispiele

```bash
# Vollanalyse mit ausführlichem Logging
python main.py --verbose

# Nur AfD-Accounts durchsuchen
python main.py --accounts-only

# Nur nach Schlagwörtern suchen
python main.py --keywords-only

# Testlauf ohne Bericht
python main.py --dry-run

# Berichte in benutzerdefiniertem Pfad speichern
python main.py --output-dir /pfad/zu/reports
```

## Ausgabe

Der Bot erzeugt strukturierte Textberichte mit:

- Executive Summary: Überblick über Treffer und Statistiken
- Detaillierte Befunde: Einzelne Tweets mit URL, Kategorien, Keywords, Metriken
- Statistische Auswertung: Such- und Sammlungsmetriken, Verteilungen
- Methodik: Beschreibung des Analyseverfahrens
- Rechtlicher Kontext: Hinweise zu Art. 21 Abs. 2 GG

Berichte werden mit Zeitstempel im Verzeichnis `reports/` gespeichert.

## Konfiguration

Wichtige Dateien:

- `config.py`: Liste der AfD-Accounts, Schlagwörter, Sucheinstellungen
- `requirements.txt`: Python-Abhängigkeiten
- `.env`: API-Zugangsdaten (aus Vorlage erstellen)

### Beobachtete Accounts

Der Bot enthält eine Auswahl offizieller AfD-Accounts (Bund/Länder). Diese Liste kann in `config.py` erweitert oder angepasst werden.

### Analyse-Schlagwörter

Die Schlagwörter sind an verfassungsrelevanten Aspekten (Art. 21 Abs. 2 GG) orientiert, u. a.:
- Angriffe auf die freiheitlich-demokratische Grundordnung
- Anti-verfassungsrechtliche Rhetorik
- Geschichtsrevisionismus
- Befürwortung von Gewalt
- Muster von Hassrede

## Technische Details

### Deduplizierung & Zusammenarbeit

- Mit MongoDB werden alle in markierten Tweets erkannten URLs einmalig gespeichert
- Ein eindeutiger Index auf `url` verhindert Duplikate – auch über mehrere Nutzer/Maschinen
- So können viele Nutzer parallel beitragen, ohne doppelte Quellen zu sammeln
- Ohne MongoDB arbeitet der Bot lokal weiter (nur Berichtsausgabe)

### Architektur

- `twitter_client.py`: API-Client inkl. Rate-Limits
- `content_analyzer.py`: Schlagworterkennung, Kategorisierung, Schweregrad
- `tweet_collector.py`: Datensammlung aus Accounts/Schlagworten
- `report_generator.py`: Berichtsgenerierung (.txt)
- `main.py`: CLI und Orchestrierung
- `config.py`: Einstellungen (Accounts, Keywords, Parameter)

### Ratenbegrenzung

- Automatisches Warten bei Limits (API-konform)
- Konfigurierbare Pausen zwischen Anfragen
- Beachtung von Quoten und Grenzwerten

### Ethische Hinweise

- Analyse ausschließlich öffentlicher Inhalte
- Transparente Methodik und Limitierungen
- Deutliche Hinweise auf den nicht-juristischen Charakter
- Beachtung der Plattform-AGB

## Logging

Logs werden im Verzeichnis `logs/` mit Zeitstempel abgelegt. Mit `--verbose` erhältst du detaillierte Debug-Informationen.

## Troubleshooting

Häufige Probleme:
1. "Missing Twitter API credentials"
   - Prüfe, ob `.env` existiert und gültige Werte enthält
   - Stelle sicher, dass alle benötigten Variablen gesetzt sind
2. Rate-Limit-Fehler
   - Der Bot geht automatisch damit um
   - Ggf. Suchparameter reduzieren
3. Keine Tweets gefunden
   - Prüfen, ob Accounts aktiv sind und API-Zugriff korrekt ist

## Rechtlicher Rahmen

Art. 21 Abs. 2 GG (Auszug):

> "Parteien, die nach ihren Zielen oder nach dem Verhalten ihrer Anhänger darauf ausgehen, die freiheitliche demokratische Grundordnung zu beeinträchtigen oder zu beseitigen oder den Bestand der Bundesrepublik Deutschland zu gefährden, sind verfassungswidrig."

Die Analyse zielt darauf ab, Inhalte zu identifizieren, die möglichweise auf:
1. aktive Gegnerschaft zur FDGO,
2. Pläne zur Unterminierung der Verfassungsordnung oder
3. ausreichende Bedeutung zur tatsächlichen Gefährdung
hindeuten könnten.

## Disclaimer

Dieses Tool dient Forschungs- und Demonstrationszwecken. Nutzer sind verantwortlich für:
- Einhaltung geltender Gesetze und Vorschriften
- Sorgfältige Einordnung automatisierter Ergebnisse
- Unabhängige Verifikation der Befunde über geeignete Kanäle
- Beachtung von Datenschutz und Persönlichkeitsrechten

Automatisierte Analysen können Fehlklassifikationen enthalten und dürfen nicht alleinige Grundlage rechtlicher oder politischer Entscheidungen sein.
