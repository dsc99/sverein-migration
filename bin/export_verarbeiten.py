#-----------  standard imports
from os.path import join as j, basename, dirname, exists as fexists
import tempfile
basedir = __file__.split("/bin")[0]
import sys
sys.path.append( basedir )    # to enable using: import lib.xxxx


#-----------  application imports
import pandas as pd
from numpy import float64
import lib.ms_mdbtools as mdb

from datetime import datetime, date


#-----------  setup directory structure and filenames
vardir = j(basedir, 'var')
clouddir = j( dirname(basedir), 'dsc99-cloud')  # DSC99-Cloud "nebenan"

verwaltungdir = j( clouddir, "DSC Verwaltung" )
db_filename = 'Mitgliederdatenbank_DSC99.mdb'

technik_sverein_dir = j( verwaltungdir, 'Technik', 'S-Verein')
export_filename = 'ExportList_20221227-0606.csv'


# This function converts given date to age
today = date.today()
def age(dob):
    return today.year - dob.year - ((today.month, today.day)
                                       < (dob.month, dob.day))

altersgruppen = {
    "0-6": (0,6),
    "7-14": (7,14),
    "15-18": (15,18),
    "19-26": (19,26),
    "27-40": (27, 40),
    "41-60": (41,60),
    "61-99": (61,99),
    "99+": (100, 200)
}
altersgruppen_by_age = {
    a: [ag for ag in altersgruppen if altersgruppen[ag][0] <= a <= altersgruppen[ag][1]][0]  
    for a in range(0,200)
}

def split_emails_0(email:str):
    return split_emails(email, 0)
def split_emails_1(email:str):
    return split_emails(email, 1)

def split_emails( email: str, index:int ):
    email2 = None
    if isinstance(email, str):
        email2 = (email+",").split(",")[index].strip() or None
    return email2

export_filename_json = j(vardir, export_filename.replace('.csv', '.json') )
if fexists( export_filename_json ):
    export_data = pd.read_json( export_filename_json, orient='table' )
else:
    # Upon first read, coerce everything into a str --> PLZ, IBAN, Kto-Nr etc.
    export_data = pd.read_csv(  j(technik_sverein_dir, export_filename), sep=';', dtype=str )

    # Now do some cleansing of the str-data:
    #  - convert datum (dd.mm.yyyy) into actual datetime objects
    #  - Remove empty columns entirely
    for s in export_data:
        if export_data[s].value_counts().size == 0:
            print( "Removing empty colum", s, "...")
            del export_data[s]
            continue
        if "DFB" in s:
            print( "Removing useless 'DFB' colum", s, "...")
            del export_data[s]
            continue

        if len(s)==2 and s[0]=="_" and s[1].isdigit():
            export_data.rename(columns={s:"Abteilungseintritt"+s}, inplace=True)
            s="Abteilungseintritt"+s
        
        if s.startswith("Betrag"):
            export_data[s] = pd.to_numeric( export_data[s].str.replace(r",", ".") )
        if s in ['Guthaben', "Kontostand"]:
            export_data[s] = pd.to_numeric( export_data[s].str.replace(r"\+", "").str.replace(r",", ".") )

        if "datum" in s.lower() \
            or "eintritt_" in s.lower() or "austritt_" in s.lower() \
            or "start_" in s.lower() or "ende_" in s.lower() or "bis_" in s.lower():

            print( "Converting colum", s, ' to datetime ...')
            export_data[s] = pd.to_datetime( export_data[s], dayfirst=True, infer_datetime_format=True )
    # Save a copy to use save some time on the next run:
    export_data.to_json( export_filename_json, orient='table' )


mitgliedsfelder = ["Mitglieds-Nr","Vorname","Nachname", "Familien-Nr", "Austritt", "Notizen"]
persoenlichefelder = ["Straße","PLZ","Ort","Land","Titel","Anrede","Geschlecht","Familienstand","Geburtsdatum","Eintrittsdatum","Austrittsdatum","Vereinsaustrittsgrund","Status"]
#kommunikationsfelder = ["Notfallnummer", "Notfallkontakt", "KommE-Mail_G1", "KommMobil_G1", "KommE-Mail_P1", "KommMobil_P1", "KommTelefon_P1", "KommE-Mail_P2", "KommMobil_P2"]
kommunikationsfelder = ["E-Mail", "E-Mail2", "Mobil", "Telefon"]
zahlungsfelder = ["Zahlungsart", "IBAN", "BIC", "Kontonummer", "Bankleitzahl", "Kreditinstitut", "Kontoinhaber", "Eingabe Bankdaten", "Guthaben", "Kontostand", "Rechnungsstatus"]

#export_data["Alter"] = export_data["Geburtsdatum"].apply( age )
export_data["Alter"] = pd.to_numeric(export_data["Alter"])
export_data["Jahresalter"] = pd.to_numeric(export_data["Jahresalter"])
export_data["Altersgruppe"] = export_data[export_data["Alter"].notnull()]["Alter"].apply( lambda a: altersgruppen_by_age[a] )

export_data["E-Mail2"] = export_data["E-Mail"].apply(split_emails_1)
export_data["E-Mail"]  = export_data["E-Mail"].apply(split_emails_0)

export_data["Austritt"] = export_data["Mitglieds-Nr"].str.startswith("*")
export_data["Mitglieds-Nr"] = export_data["Mitglieds-Nr"].str.replace(r"\* ", '')

mitglieder_daten = export_data[mitgliedsfelder+persoenlichefelder+["Alter", "Altersgruppe", "Jahresalter"]]
telefonliste_daten = export_data[mitgliedsfelder+kommunikationsfelder]

with pd.ExcelWriter(j(technik_sverein_dir, export_filename.replace('.csv', '.xlsx'))) as writer:
    mitglieder_daten.to_excel( writer, sheet_name="Mitglieder", index=False, freeze_panes=(1,1) )
    telefonliste_daten.to_excel( writer, sheet_name="Telefonliste", index=False, freeze_panes=(1,1) )
    export_data[mitgliedsfelder+zahlungsfelder].to_excel( writer, sheet_name="Bankdaten", index=False, freeze_panes=(1,1) )
    export_data.to_excel( writer, sheet_name="Alle Daten", index=False )
    export_data.dtypes.to_excel( writer, sheet_name="Datenfelder")


print("Done.")