
#-----------  standard imports
from os.path import join as j, basename, dirname
basedir = __file__.split("/bin")[0]
import sys
sys.path.append( basedir )    # to enable using: import lib.xxxx


#-----------  application imports
import pandas as pd
import lib.ms_mdbtools as mdb


#-----------  setup directory structure and filenames
vardir = j(basedir, 'var')
clouddir = j( dirname(basedir), 'dsc99-cloud')  # DSC99-Cloud "nebenan"

verwaltungdir = j( clouddir, "DSC Kompetenzteams Jugendhockey", "Verwaltung" )
db_filename = 'Mitgliederdatenbank_DSC99.mdb'

#=====================================================
# Application start
#

# Listing the tables.
for table_name in mdb.list_tables(j(verwaltungdir,db_filename), encoding="UTF-8"):
  try:
    df = mdb.read_table(j(verwaltungdir,db_filename), table_name)
    print(df.info())
  except Exception as e:
    print("Exception reading", table_name, str(e))
#  print(df.shape)

pass