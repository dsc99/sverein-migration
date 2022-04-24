


def to_Zahlungsdatensatz( mitnum, df, mitnum_feld='mitnum_clean' ):
  zahlungs_datum = dict()
  mitglied = df.loc[ (df[ mitnum_feld ]==mitnum)&df['Ktonr'].notnull() ]
  if mitglied.shape[0] != 1 and mitglied['Ktonr'].value_counts().shape[0] != 1:
    mitglied = df.loc[ (df[ mitnum_feld ]==mitnum)&df['Ktonr'].str.match(r"DE.{20}") ]
    if mitglied.shape[0] != 1 and mitglied['Ktonr'].value_counts().shape[0] != 1:
      raise Exception()
  for n in ['Ktonr', 'Blz', 'Bank', 'Ktoinhaber']:
    if mitglied[n].size == 0:
      raise Exception()
    zahlungs_datum[n] = mitglied[n].iloc[0]
  if not zahlungs_datum['Ktoinhaber']:
    zahlungs_datum['Ktoinhaber'] = ", ".join( [mitglied['Name'].iloc[0], mitglied['Vorname'].iloc[0]] )
  return zahlungs_datum

