import http.client, urllib.request, urllib.parse, urllib.error, re

class Qis:
   def __init__(self):
      self.__notenspiegel = None 

   def update(self, qis_user, qis_password):
      conn = http.client.HTTPSConnection ('qis.hs-albsig.de')
      
      # Anmeldeseite aufrufen um die Sessionid rauszufinden 
      conn.request('GET', '/qisserver/rds?state=user&type=0&application=lsf')
      response = conn.getresponse()
      response.read ()
      
      params_anmeldung = urllib.parse.urlencode ({'username':"%s" % qis_user, 'password': "%s" % qis_password,'submit':'Ok'})
      headers_anmeldung = {"Content-type": "application/x-www-form-urlencoded", "Cookie" : "JSESSIONID=%s" % re.search (r'JSESSIONID=(.*?);', response.getheader ('Set-Cookie')).group (1)} 
         
      # Anmeldung durchfuehren 
      conn.request ('POST', "/qisserver/rds?state=user&type=1", params_anmeldung, headers_anmeldung)
      response = conn.getresponse ()
      # Sessionid aktualisieren
      header_cookie = {"Cookie" : "JSESSIONID=%s" % re.search (r'JSESSIONID=(.*?);', response.getheader ('Set-Cookie')).group (1)} 
      response.read ()
               
      # Menue abrufen
      conn.request ('GET', "/qisserver/rds?state=change&type=1&moduleParameter=studyPOSMenu&nextdir=change&next=menu.vm&subdir=applications&xml=menu&purge=y&navigationPosition=functions%2CstudyPOSMenu&breadcrumb=studyPOSMenu&topitem=functions&subitem=studyPOSMenu", None, header_cookie)
      response = conn.getresponse ()
      content = response.read ().decode('utf-8')
      asi = re.search (r';asi=(.*?)\"', content).group (1)
      
      # Notenspiegel abrufen
      # Master SE
      conn.request ('GET', "/qisserver/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=%s&expand=0&asi=%s" % ("auswahlBaum%7Cabschluss%3Aabschl%3D90%2Cstgnr%3D1", asi), None, header_cookie)
      # Bachelor TI
      # conn.request ('GET', "/qisserver/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=%s&expand=0&asi=%s" % ("auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1", asi), None, header_cookie)
      response = conn.getresponse ()
      self.__notenspiegel  = response.read ().decode('utf-8')
      
      # Abmeldung      
      conn.request ('GET', "/qisserver/rds?state=user&type=4&category=auth.logout&menuid=logout", None, header_cookie)
      response = conn.getresponse()
      response.read ()
            
      # Verbindung beenden
      conn.close ()

   def get_notenspiegel (self):
      if not self.__notenspiegel:
         return None
      pruefungen = []

      # Tabellenreihen
      trs = re.findall (r'<tr>(.*?)</tr>', self.__notenspiegel, re.S)

      # Tabellendaten
      for tr in trs:
         tds = re.findall (r'<td class="qis_records".*?>(.*?)</td>', tr, re.S)
         pruefung = []
         # Daten aufhuebschen
         for td in tds:
            bs = re.findall (r'<b>(.*?)</b>', td, re.S)
            for b in bs:
                  b = b.replace("&nbsp;", "" )
                  b = b.replace("&nbsp", "" )
                  pruefung.append(b)
         if pruefung != []:
            pruefungen.append(pruefung)
      return pruefungen

if __name__ == "__main__":
   qis = Qis()
   qis.update('<user>', '<passwd>')
   for pruefung in qis.get_notenspiegel ():
      print(pruefung)