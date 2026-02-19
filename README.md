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


