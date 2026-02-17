coolMATH Pro — README
Version 43 | Samsung FJM Edition
Entwickelt von Michael Schäpers, °coolsulting

Was ist coolMATH?
coolMATH ist ein interaktiver Kühllast-Rechner für bis zu 5 Zonen/Räume, der die Kühllast eines Gebäudes nach 6 verschiedenen Berechnungsmethoden simultan berechnet und automatisch passende Samsung FJM Wandgeräte sowie ein Außengerät vorschlägt. Exportierbar als JSON-Übergabedatei oder als PDF-Bericht (Kunden- und Technikerversion).

Eingabeparameter (pro Zone)
ParameterOptionenFlächem²BaustandardAltbau / Neubau / PassivhausVerglasungEinfach / Doppel / DreifachBeschattungKeine / Teilweise / VollständigAusrichtungN / NO / O / SO / S / SW / W / NWPersonenAnzahlTechnikWärmeleistung Geräte (W)Fensterflächem²Baumasseleicht / mittel / schwer

6 Berechnungsmethoden
MethodeBasisTypisches ErgebnisPraktikerHeuristik (Faustregel + Solar)konservativ / hochVDI 2078 ALTKlassische Norm (1996)mittel-hochVDI 6007 NEURC-Modell mit Einschwingung (96h)niedrig (physikalisch exakt)RecknagelStandard-abhängiges ΔTmittelKaltluftseeRecknagel × 1/1.3 (Quelllüftung)niedrigKI-HybridGewichteter Mix + Peak-Shavingausgewogen
Alle Methoden liefern ein 24-Stunden-Lastprofil (stündlich) und einen Peak-Wert in Watt.

Gerätedatenbank — nur Samsung S_FJM Wandgeräte
Echte Preise aus MTF-Datenbank (Stand 2026-02-02). Ausschließlich RAC|FJM Wandgeräte (kein BAC, kein S_RAC).
8 Serien — Innengeräte (IG):
SerieArt.-Nr. PrefixLeistungLP abWind-Free Standard (Default)AR60F…AWN2.0 – 5.0 kW693 EURAirise LivingAR50F…BHN2.0 – 6.5 kW554 EURWF ExklusivAR70F…C1AWN2.0 – 6.5 kW1.048 EURWF Exklusiv BlackAR70F…C1ABN2.0 – 3.5 kW1.178 EURWF Exklusiv-PremiereAR70H…C1AWN2.0 – 6.5 kW1.072 EURWF Exklusiv-Premiere BlackAR70H…C1ABN2.0 – 3.5 kW1.112 EURWF EliteAR70F…CAAWK2.0 – 3.5 kW1.347 EURWF Elite-Premiere PlusAR70H…CAAW2.0 – 3.5 kW1.296 EUR
Außengeräte (AG) — FJM Multi-Split:
Art.-Nr.LeistungZonenLPAJ040TXJ2KG/EU4.0 kW22.347 EURAJ050TXJ2KG/EU5.0 kW22.706 EURAJ052TXJ3KG/EU5.2 kW33.061 EURAJ068TXJ3KG/EU6.8 kW33.548 EURAJ080TXJ4KG/EU8.0 kW44.494 EURAJ100TXJ5KG/EU10.0 kW55.533 EUR

Geräteauswahl-Logik

Basis: Praktiker-Peak + 10% Sicherheitszuschlag
Vorschlag: kleinstes verfügbares IG ≥ Bedarf aus gewählter Serie
Außengerät: automatisch aus FJM_AG — kleinste AG ≥ Summe IG × 1.05
Gesamtpreis = Σ IG-Preise + AG-Preis (Listenpreis netto, excl. MwSt.)


Ausgabe & Diagramme

Methodenvergleich-Chart: alle 6 Methoden simultan (24h)
6 Einzelzonen-Charts (2×3 Raster): VDI Neu, VDI Alt, Recknagel, Praktiker, Kaltluftsee, KI-Hybrid
Ergebnismatrix: Tabelle aller Peaks je Zone und Methode


Exports
FormatInhaltJSONStrukturierter Übergabebericht für coolMATCH (alle Zonen, Kühllastwerte, Geräteauswahl)PDF KundenberichtProfessioneller Kundenbericht mit Ergebnissen und GeräteempfehlungPDF TechnikübergabeVollständiger technischer Bericht mit allen 6 Methoden und Diagrammen

Tech-Stack
Streamlit          UI Framework
Plotly             Interaktive Diagramme (24h-Kurven)
Matplotlib + Agg   Chart-Rendering für PDF-Export
fpdf               PDF-Generierung
openpyxl           Samsung-Datenbankimport (Excel)
NumPy / Pandas     Physik-Berechnungen

Starten
bashstreamlit run coolMATH.py
Alle Listenpreise netto, zzgl. MwSt. | Ohne Montage und Zubehör
Datenquelle: MTF Samsung WaWi-Import 2026-02-02
