# ------------------------------------
# Extract Abteilung from "Sportart"
#

def to_Abteilung_1( n ):
  if n == None or not isinstance( n, str ):
    return None
  return 'Hockey' if 'Hockey' in n[:10] or n.startswith("Passives ") \
                  else 'Tennis' if "Tennis" in n[:10] or "Tennnis"  in n  \
                  else 'Lacrosse' if "Lacrosse" in n[:10]  \
                  else 'DSC' if "Passive Mitgliedschaft" in n or "Anerkennung"  in n or "Ehrenmitglied"  in n \
                  else "??:"+n

def to_Abteilung_2( n ):
  if n == None or not isinstance( n, str ):
    return None
  if "+ Tennis" in n:
    return "Tennis"
  if "Hockey" in n[10:]:
    return "Hockey"
  return None  

