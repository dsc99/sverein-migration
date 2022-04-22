
beitraege = {
  'Hockey': {
    598.5: 'Hockey-Mitgliedschaft (mtl)',
    462: 'Hockey-Mitgliedschaft (mtl)',
    241.5: 'Hockey-Mitgliedschaft (mtl)',
    570: 'Hockey-Mitgliedschaft',
    440: 'Hockey-Mitgliedschaft',
    230: 'Hockey-Mitgliedschaft',
    400: 'Hockey-Mitgliedschaft (Ausbildung)',
    420: 'Hockey-Mitgliedschaft (Ausbildung-mtl)',
    150: 'Passive Eltern-Fördermitgliedschaft',
    157.5: 'Passive Eltern-Fördermitgliedschaft (mtl)',
    135: 'Passive Mitgliedschaft',
    410: 'Elternhockey',
    430.5: 'Elternhockey (mtl)',
    270: 'Ü35 Hobbymannschaft',
    283.5: 'Ü35 Hobbymannschaft (mtl)',
    142.5: 'Hockey - Erwachsene 3. Damen',
  },
  'Tennis': {
    350: 'Tennis-Mitgliedschaft',
    367.5: 'Tennis-Mitgliedschaft (mtl)',
  },
  'Lacrosse': {
    499: 'Lacrosse-Mitgliedschaft',
    219: 'Lacrosse-Mitgliedschaft',
    105: 'Lacrosse-Mitgliedschaft (Schnupper-mtl)',
    320: 'Lacrosse-Mitgliedschaft (Ausbildung)',
    524: 'Lacrosse-Mitgliedschaft (mtl)',
    230: 'Lacrosse-Mitgliedschaft (mtl)',
    336: 'Lacrosse-Mitgliedschaft (Ausbildung-mtl)',
    157.5: 'Lacrosse-Mitgliedschaft (Ausbildung-Schnupper-mtl)',
  },
  'DSC': {
    135: 'Passive Mitgliedschaft',
    42: 'Anerkennung',
  },

}

def to_Beitrag(Abteilung, Beitrag, Sportart):
  res= beitraege.get(Abteilung, {}).get(Beitrag, None)

  if not res and Abteilung=="Hockey":
    if Beitrag==510 and "35" in Sportart:
      return "Hockey - Ü35 Hobby + Tennis"
    elif Beitrag==510:
      return "Elternhockey + Tennis"
    elif Beitrag==535.5 and "35" in Sportart:
      return "Hockey - Ü35 Hobby + Tennis (mtl)"
    elif Beitrag==535.5:
      return "Elternhockey + Tennis (mtl)"

  if not res and Abteilung=="Tennis":
    if Beitrag==219 and "27" in Sportart:
      return "Tennis-Mitgliedschaft (Ausbildung)"
    elif Beitrag==219:
      return "Tennis-Mitgliedschaft"
    elif Beitrag==230 and "27" in Sportart:
      return "Tennis-Mitgliedschaft (Ausbildung-mtl)"
    elif Beitrag==230:
      return "Tennis-Mitgliedschaft (mtl)"

  if not res and Abteilung=="DSC":
    if Beitrag==0 and "Ehrenmitglied" in Sportart:
      return "Ehrenmitgliedschaft"

  return res


def to_Umlagen( mitglied, art ):
  if art == "Spind":
    if mitglied['Spindbeitrag'] == 30:
      return "Spindbeitrag"
    if mitglied['Spindbeitrag'] == 0:
      return None
    return "Unbekannter Spindbeitrag: "+str(mitglied['Spindbeitrag'])
  if 'assiv' in str(mitglied['Sportart']):
    return "Umlage (%s-Passive Mitglieder)"%(art,)
  if mitglied['Umlage'] in [15, 25, 50]:
    return 'Umlage (%s)'%(art,)
  if mitglied['Umlage'] in [65, 125]:
    return "Umlage (%s-Familienhöchstbeitrag)"%(art,)
  if mitglied['Umlage'] > 0:
    return "Unbekannt: "+str(mitglied['Umlage'])
  return None
