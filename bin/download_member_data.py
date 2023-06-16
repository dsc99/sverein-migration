import requests as r


loginscreen_url = "https://verwaltung.s-verein.de/login.php?strShortKey=d17"
login_url = "https://verwaltung.s-verein.de/login/d17?"
session = r.Session()
res = session.get( loginscreen_url )
login_data = {"strUserName":"michaelhwalthergmailcom", "strPass":"wbn2jlia"}
res2 = session.post(login_url)

# Adressdaten exportiern - Mitglieder
exportieren_mitglieder_screenurl = "https://verwaltung.s-verein.de/mio/admin/tools_export.php?iTypeAdr=2&iExportTyp=6&iStep=5&strExportType=Mitglieder&OphId=396c6a&ophinex=00e33b"
#res_exportieren = session.get( exportieren_mitglieder_screenurl )

exportieren_mitgliederlisten_screenurl ="https://verwaltung.s-verein.de/mio/adressen/mitglieder_listen.php?ModePage=17&OphId=396c6a&ophinex=e13563"
res_mitgliederlisten = session.get( exportieren_mitgliederlisten_screenurl )

exportieren_allemitglieder_url = "https://verwaltung.s-verein.de/mio/adressen/exportfile.php?iBenutzerId=14891&iKundeId=13255&ModePage=17&iListExportMode=5&strCat=13416&Mode=&OrderBy=&iAdrIdFirKon=&iTypeAdrNot=&Operation=&UseListen=&iSucheListeId=-1&OphId=396c6a"
res_export = session.get( exportieren_allemitglieder_url )

print( "Done" )