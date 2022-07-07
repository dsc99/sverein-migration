#-----------  standard imports
from os.path import join as j, basename, dirname, exists as fexists
basedir = __file__.split("/bin")[0]
from os import makedirs

import sys
sys.path.append( basedir )    # to enable using: import lib.xxxx


#-----------  application imports
import subprocess
from datetime import datetime

import pandas as pd
import lib.ms_mdbtools as mdb

import lib.sverein_migration.beitraege as beitraege
import lib.sverein_migration.abteilungen as abteilungen
import lib.sverein_migration.zahlungsdaten as zahlungsdaten
import lib.sverein_migration.util as util

#-----------  setup directory structure and filenames
vardir = j(basedir, 'var')
makedirs( j(vardir, 'sverein'), exist_ok=True )
clouddir = j( dirname(basedir), 'dsc99-cloud')  # DSC99-Cloud "nebenan" (synced with Nextcloud)

verwaltungdir = j( clouddir, "DSC Verwaltung" )
db_filename = 'Mitgliederdatenbank_DSC99.mdb'

if not fexists( j(verwaltungdir, db_filename) ):
  print( "Datenbank-Datei aus DSC-Cloud nicht gefunden: ", j(verwaltungdir, db_filename))
  exit (-1)

#=====================================================
# Application start
#

# ------------------------------------------------------------------
# Einlesen und Anreichern der Quell-Daten:
#

# Read source table
table_name = "DSC99-Mitgliederdatenbank"
df = mdb.read_table(j(verwaltungdir,db_filename), table_name)

# Clean index and activate:
df = df.assign( mitnum_clean=df["Mitnum"].str.replace(' ', '', regex=False).str.replace('.', '-', regex=False) )
print("Check duplicate Mitglieds-Nr")
print( df[df['mitnum_clean'].duplicated(keep=False)] )
df.index = df['mitnum_clean']

# Zahlernr cleaning:
df = df.assign( zahlernr_clean=df["Zahlernr"].str.replace(' ', '', regex=False).str.replace('.', '-', regex=False) )

print( "====Anrede gesäubert:")
df = df.assign( anrede_clean=df["Anrede"].str.replace('An  ?die.*', 'An die Eltern von', regex=True) \
                                         .str.replace('Herr?n', 'Herr', regex=True) )
df.loc[(df['Geschlecht'].str.lower()=='w')
       &(df['anrede_clean'].str.lower()=='an die eltern von'), 'anrede_clean']="An die Eltern der"
df.loc[(df['Geschlecht'].str.lower()=='m')
       &(df['anrede_clean'].str.lower()=='an die eltern von'), 'anrede_clean']="An die Eltern vom"
print(df['anrede_clean'].value_counts())

# Dump the enriched full source data:
with open( j(vardir, table_name+".csv"), "w") as f:
  f.write( df.to_csv( sep=';') )

# Convert (string!) datetime values to actual datetime(s):
df['Mitseit_dt']  = util.to_datetime( df['Mitseit'] )
df['Geburt_dt']   = util.to_datetime( df['Geburt'] )
df['Austritt_dt'] = util.to_datetime_dmY( df['Austritt'] )


# ------------------------------------------------------------------
# Übertragen der (meisten) Grunddaten:
#
sverein_df = pd.DataFrame({
  'Mitglieds-Nr': df['mitnum_clean'],
  'Freifeldname_1': 'Familien-Nr',
  'Freifeldwert_1': df['Fanum'],
  'Anrede': df['anrede_clean'],
  'Vorname': df['Vorname'],
  'Nachname': df['Name'],
  'Straße': df['Strasse'],
  'PLZ': df['Plz'],
  'Ort': df['Ort'],
  'Geschlecht': [ 'männlich' if v=='M' else 'weiblich' for v in df['Geschlecht']],
  'Geburtsdatum': df['Geburt_dt'],
  'Eintrittsdatum': df['Mitseit_dt'],
  'Austrittsdatum': df['Austritt_dt'],
  'KommE-Mail_P1': df['Email'],
  'KommE-Mail_P2': df['Email2'],
  'KommTelefon_P1': df['Telefon'],
  'KommMobil_P1': df['Telefon2'],

  'Freifeldname_2': 'Spind',
  'Freifeldwert_2': df['Spind'],

  'Status': "Aktiv",

  'Abteilung_1': "DSC",
  'Abteilungseintritt_1': df['Mitseit_dt'],
  'Abteilungsstatus_1': "Aktiv",

  'Abteilung_2': [abteilungen.to_Abteilung_1(n)
                  for n in df['Sportart'] ],
  'Abteilungseintritt_2': df['Mitseit_dt'],
  'Abteilungsstatus_2': 'Aktiv',

  'Abteilung_3': [abteilungen.to_Abteilung_2(n)
                  for n in df['Sportart'] ],
  'Abteilungseintritt_3': df['Mitseit_dt'],
  'Abteilungsstatus_3': 'Aktiv',

  'Zahlungsart': [ 'Überweisung' if v=='Überweisung' else
                   'Lastschrift' if v=='Bankeinzug' else
                   'Bar'
                   for v in df['Zahlart']],


  'Beitrag': df['Beitrag'],   # Helper column
  'Sportart': df['Sportart'], # Helper column
}, index=df.index)
sverein_df['Abteilungseintritt_3']=pd.Series( [df['Mitseit_dt'].at[a] if b else None for a,b in sverein_df['Abteilung_3'].items()], index=df.index )
sverein_df['Abteilungsstatus_3']=pd.Series( ['Aktiv' if b else None for a,b in sverein_df['Abteilung_3'].items()], index=df.index )


# ------------------------------------------------------------------
# Grunddaten-Reports
print("====Check duplicate Mitglieds-Nr")
print( sverein_df[sverein_df['Mitglieds-Nr'].duplicated(keep=False)] )

print("====Fehlendes Geburtsdatum")
print( df[df['Geburt'].isnull() & df['Sportart'].ne('Passives Eltern-Fördermitglied')] )
sverein_df.loc[df['Geburt'].isnull() & df['Sportart'].ne('Passives Eltern-Fördermitglied'), ['Geburtsdatum']] = datetime(1970,1,1)
sverein_df.loc[df['Geburt'].isnull() & df['Sportart'].ne('Passives Eltern-Fördermitglied'), ['Freifeldwert_3']] = "Geburtsdatum auf 1.1.1970 gesetzt"
sverein_df.loc[df['Geburt'].isnull() & df['Sportart'].ne('Passives Eltern-Fördermitglied'), ['Freifeldname_3']] = 'Import-Meldung'

print("====Abteilungszuordnung")
print( sverein_df['Abteilung_1'].value_counts() )


# ------------------------------------------------------------------
# DSC-weite Beiträge:
sverein_df['Beitragsbezeichnung_1_1']=pd.Series( [beitraege.to_Umlagen(b, 'Investitionen') for a,b in df.iterrows()], index=df.index )
sverein_df['Beitragsbezeichnung_1_2']=pd.Series( [beitraege.to_Umlagen(b, 'Gastro') for a,b in df.iterrows()], index=df.index )
sverein_df['Beitragsbezeichnung_1_3']=pd.Series( [beitraege.to_Umlagen(b, 'Spind') for a,b in df.iterrows()], index=df.index )
# Haupt-Fachbeitrag:
sverein_df['Beitragsbezeichnung_2_1']=pd.Series( [beitraege.to_Beitrag(b.iloc[0], b.iloc[1], b.iloc[2])
                                                  for a,b in sverein_df[['Abteilung_2', 'Beitrag', 'Sportart']].iterrows()],
                                                 index=df.index )
sverein_df['Beitragsstart_2_1']=pd.Series( [df['Mitseit_dt'].at[a] if b else None for a,b in sverein_df['Beitragsbezeichnung_2_1'].items()], index=df.index )

print('====Umlagen-Zuordnung (Investitionen)')
print(sverein_df['Beitragsbezeichnung_1_1'].value_counts())
print('====Umlagen-Zuordnung (Gastro)')
print(sverein_df['Beitragsbezeichnung_1_2'].value_counts())
print('====Umlagen-Zuordnung (Spind)')
print(sverein_df['Beitragsbezeichnung_1_3'].value_counts())

with open( j(vardir, table_name+"-UmlagenOffen.csv"), "w") as f:
  umlagen_offen_df = df.loc[sverein_df['Beitragsbezeichnung_1_1'].str.startswith("Unbekannt")==True, ['Mitnum', 'Fanum', 'Vorname', 'Name', 'Sportart', 'Umlage']]
  f.write( umlagen_offen_df.to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_1'].str.startswith("Unbekannt")==True, ['Freifeldwert_3']] = sverein_df.loc[sverein_df['Beitragsbezeichnung_1_1'].str.startswith("Unbekannt")==True, ['Beitragsbezeichnung_1_1']]
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_2'].str.startswith("Unbekannt")==True, ['Freifeldwert_3']] = sverein_df.loc[sverein_df['Beitragsbezeichnung_1_2'].str.startswith("Unbekannt")==True, ['Beitragsbezeichnung_1_2']]
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_1'].str.startswith("Unbekannt")==True, ['Freifeldname_3']] = 'Import-Meldung'
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_2'].str.startswith("Unbekannt")==True, ['Freifeldname_3']] = 'Import-Meldung'
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_1'].str.startswith("Unbekannt")==True, ['Beitragsbezeichnung_1_1']] = None
sverein_df.loc[sverein_df['Beitragsbezeichnung_1_2'].str.startswith("Unbekannt")==True, ['Beitragsbezeichnung_1_2']] = None

# Beitragsstart ist jeweils der Vereinseintritt
sverein_df['Beitragsstart_1_1']=pd.Series( [df['Mitseit_dt'].at[a] if b else None for a,b in sverein_df['Beitragsbezeichnung_1_1'].items()], index=df.index )
sverein_df['Beitragsstart_1_2']=pd.Series( [df['Mitseit_dt'].at[a] if b else None for a,b in sverein_df['Beitragsbezeichnung_1_2'].items()], index=df.index )
sverein_df['Beitragsstart_1_3']=pd.Series( [df['Mitseit_dt'].at[a] if b else None for a,b in sverein_df['Beitragsbezeichnung_1_3'].items()], index=df.index )

print( "====Beitrags-Zuordnung:")
print( sverein_df['Beitragsbezeichnung_2_1'].value_counts() )

print( "====Offene Beitrags-Zuordnung:")
print( sverein_df[sverein_df['Beitragsbezeichnung_2_1'].isnull()]['Beitrag'].value_counts() )

with open( j(vardir, table_name+"-BeitraegeOffen.csv"), "w") as f:
  beitraege_offen_df = df.loc[sverein_df['Beitragsbezeichnung_2_1'].isnull(),['Mitnum', 'Fanum', 'Zahlernr', 'Vorname', 'Name','Beitrag','Sportart']].sort_values(['Fanum','Beitrag'])
  f.write( beitraege_offen_df.to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )

with open( j(vardir, table_name+"-beitraege.csv"), "w") as f:
  f.write( df[['Beitrag', 'Sportart']].value_counts().sort_index(ascending=False).to_csv( sep=';' ) )


# ------------------------------------------------------------------
# Zahlungsdaten

zahlungs_daten = {}   # Merke alle Zahlungsdaten, indiziert nach DSC-Mitgliedsnr

# Zunächst alle Zahlungsdaten, die direkt bei den Mitgliedern stehen, merken:
for mitnum in df.loc[ df['Ktonr'].notnull(), 'mitnum_clean' ]:
    zahlungs_daten[mitnum] = zahlungsdaten.to_Zahlungsdatensatz(mitnum, df)

# Jetzt noch von allen Familien-Nummern die Zahlungs-Daten extrahieren:
for fanum in df.loc[ df['Ktonr'].notnull() & df['Fanum'].notnull(), 'Fanum']:
  if fanum in zahlungs_daten:
    continue
  zahlungs_daten[fanum] = zahlungsdaten.to_Zahlungsdatensatz(fanum, df, 'Fanum')

# Jetzt alle extrahierten Zahlungsdaten übertragen:
for mitnum in zahlungs_daten:
  if zahlungs_daten[mitnum]['Ktonr'].startswith('DE'):
    sverein_df.loc[mitnum, 'IBAN']            = zahlungs_daten[mitnum]['Ktonr']
    sverein_df.loc[sverein_df['Freifeldwert_1']==mitnum, 'IBAN']     = zahlungs_daten[mitnum]['Ktonr']
  else:
    sverein_df.loc[mitnum, 'Kontonummer']     = zahlungs_daten[mitnum]['Ktonr']
    sverein_df.loc[mitnum, 'Bankleitzahl']    = zahlungs_daten[mitnum]['Blz']
    sverein_df.loc[mitnum, 'Kreditinstitut']  = zahlungs_daten[mitnum]['Bank']
    sverein_df.loc[sverein_df['Freifeldwert_1']==mitnum, 'Kontonummer']     = zahlungs_daten[mitnum]['Ktonr']
    sverein_df.loc[sverein_df['Freifeldwert_1']==mitnum, 'Bankleitzahl']    = zahlungs_daten[mitnum]['Blz']
    sverein_df.loc[sverein_df['Freifeldwert_1']==mitnum, 'Kreditinstitut']  = zahlungs_daten[mitnum]['Bank']
  
  sverein_df.loc[mitnum, 'Kontoinhaber']      = zahlungs_daten[mitnum]['Ktoinhaber']
  sverein_df.loc[sverein_df['Freifeldwert_1']==mitnum, 'Kontoinhaber']    = zahlungs_daten[mitnum]['Ktoinhaber']

lastschrift_ohne_zahlungsdaten_df = sverein_df[ (sverein_df['Zahlungsart']=='Lastschrift') & (sverein_df['Kontonummer'].isnull())  & (sverein_df['IBAN'].isnull())]
print("==== Lastschrift ohne Bankdaten:", lastschrift_ohne_zahlungsdaten_df.shape[0] )
if lastschrift_ohne_zahlungsdaten_df.shape[0] > 0:
  print(lastschrift_ohne_zahlungsdaten_df)
  with open( j(vardir, table_name+"-LastschriftOhneZahlungsdaten.csv"), "w") as f:
    f.write( lastschrift_ohne_zahlungsdaten_df.to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )



# ------------------------------------------------------------------
# Ausgabe der Import-Dateien:
#
with open( j(vardir, "sverein", table_name+"-sverein.csv"), "w") as f:
  f.write( sverein_df.to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )

# Clean any records without a Mitglieds-Nr.: (includes Sascha Heinrich...)
sverein_df = sverein_df.loc[ sverein_df['Mitglieds-Nr'].notnull() ]

with open( j(vardir, "sverein", table_name+"-sverein-1.csv"), "w") as f:
  f.write( sverein_df[:999].to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )
with open( j(vardir, "sverein", table_name+"-sverein-2.csv"), "w") as f:
  f.write( sverein_df[1000:].to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )
with open( j(vardir, "sverein", table_name+"-sverein-test.csv"), "w") as f:
  f.write( sverein_df[sverein_df['Beitragsbezeichnung_1_1'].str.match(r"Umlage.*", na=False)][:100].to_csv( sep=';', index=False, date_format='%d.%m.%Y' ) )



pass