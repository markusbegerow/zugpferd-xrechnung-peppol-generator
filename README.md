# ZUGFeRD/XRechnung/PEPPOL - E-Rechnung Generator 

Ein kostenloses, benutzerfreundliches Tool zur Erstellung von elektronischen Rechnungen nach ZUGFeRD- und XRechnung-Standard – inklusive PDF/A-3-Export, XML-Erstellung, grafischer Oberfläche (GUI) und Offline-Nutzung.

Kaffeespende: <a href="https://paypal.me/MarkusBegerow?country.x=DE&locale.x=de_DE">Spende mir einen Kaffee</a>

Die Nutzung dieses Tools erfolgt auf eigene Verantwortung. 
Es wird keine Haftung für Richtigkeit, Vollständigkeit oder rechtliche Konformität übernommen.
Keine Rechts- oder Steuerberatung. Keine Gewährleistung.

## Funktionen

- Erstellung von konformen ZUGFeRD-PDFs mit eingebetteter XML
- Export als XRechnung/PEPPOL-kompatibles UBL-XML
- Grafische Benutzeroberfläche
- Unterstützung von IBAN, MwSt, Zahlungsziel, Steuerbefreiung (§19 UStG)
- Export in PDF/A-3 mit eingebettetem ICC-Farbprofil (sRGB)
- 100 % offline-fähig, keine Cloud-Anbindung
- Kostenlos und quelloffen

## Screenshot

![image](https://github.com/user-attachments/assets/64c7ecc4-a003-4a03-abda-4c100c3a4cd5)

## Installation

### Voraussetzungen

- Python 3.10 oder höher
- Installation via `pip install pikepdf`
- ICC-Farbprofil: `sRGB.icc`  
  Download: [https://www.color.org/sRGB2014.icc](https://www.color.org/sRGB2014.icc)

### Projekt herunterladen und starten

```bash
git clone https://github.com/markusbegerow/zugpferd-xrechnung-peppol-generator.git
cd zugpferd-xrechnung-peppol-generator
python zugpferd-xrechnung-peppol-generator.py
```

## Unterstützte Felder

- Rechnungsnummer
- Rechnungsdatum und Leistungsdatum
- Verkäufer (Name, Adresse, USt-ID)
- Käufer (Name, Adresse)
- Leistungsbeschreibung
- Betrag Netto
- Mehrwertsteuer (MwSt)
- Gesamtbetrag Brutto
- IBAN
- Zahlungsziel
- Steuerbefreiung gemäß §19 UStG (optional)

## Exportformate

| Format           | Beschreibung                                                  |
|------------------|---------------------------------------------------------------|
| PDF/A-3          | Erstellt eine PDF mit eingebetteter XML (ZUGFeRD 1.0/2.1)     |
| XRechnung (UBL)  | Erstellt eine PEPPOL-kompatible XML-Datei im UBL 2.1-Format   |

## Erstellung einer ausführbaren .exe (optional)

Um das Tool ohne Python-Installation als `.exe` bereitzustellen:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "sRGB.icc;." zugpferd.py
```

Die fertige Anwendung liegt danach im Verzeichnis `dist/`.

## SHA256-Hash zur Verifikation

SHA256 557B490800650FF552827024A14F6C1D9179AF1DCE5F6AF31A4DD1993748EB99

[Jetzt herunterladen (Windows .exe)](https://github.com/markusbegerow/zugpferd-xrechnung-peppol-generator/releases/download/v1.0.0/zugpferd-xrechnung-peppol-generator.zip)


## Mitwirken

Dieses Projekt ist Open Source. Beiträge sind jederzeit willkommen!

- Bug melden: [Issues](https://github.com/markusbegerow/zugpferd-xrechnung-peppol-generator/issues)
- Funktionen vorschlagen oder verbessern: [Pull Requests](https://github.com/markusbegerow/zugpferd-xrechnung-peppol-generator/pulls)

## Autor

**Markus Begerow**  
Website & Links: [https://linktr.ee/markusbegerow](https://linktr.ee/markusbegerow)

## Lizenz

Dieses Projekt ist unter der GPL-Lizenz lizenziert. Siehe die LICENSE-Datei für Details.
