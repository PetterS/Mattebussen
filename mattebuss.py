# coding=utf8
import webapp2
from urllib import urlopen
from xml.dom.minidom import parseString
from datetime import datetime, timedelta, tzinfo
from google.appengine.api import urlfetch

# Helper class to fetchs URLs asyncronously
# Starts fetching when created; get_data() blocks 
# until done
class GetURL :
    def __init__(this, url) :
        this.rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(this.rpc, url)
    def get_data(this) :
        result = this.rpc.get_result()
        #result.status_code == 200
        return result.content
    
class MainPage(webapp2.RequestHandler):
    
    def get_bus(self, url_call, stop, no, delay) :
        try:
            # Difference from UTC.
            # This will not work in the winter!
            swedenoffset = timedelta(hours=2)
            now = datetime.now() + swedenoffset
            
            data = url_call.get_data()
            xml = parseString(data)
            lines = xml.getElementsByTagName('Lines')[0]
            best=None
            for line in lines.getElementsByTagName('Line') :
                datestr = line.getElementsByTagName('JourneyDateTime')[0].firstChild.data
                date = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
                this_no   = int(line.getElementsByTagName('No')[0].firstChild.data)
                this_stop =     line.getElementsByTagName('StopPoint')[0].firstChild.data
                
                #self.response.out.write(str((this_no,no)) + ' ' + str(this_stop) + ' ' + str(date - now ) + ' ---- ')
                #self.response.out.write( str(this_no == no) + ' ' + str(this_stop == stop) + ' ' + str(date - now > delay) + '\n')
                if this_no == no and this_stop == stop and date - now > delay :
                    # Rätt nummer, rätt läge och den går att hinna till
                    if best is None:
                        best = date
                    elif date < best:
                        best = date
                        
            return best
        except:
            return None
                    
                 

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        url = 'http://www.labs.skanetrafiken.se/v2.2/stationresults.asp?selPointFrKey='
        lth                       = 81124     
        professorsgatan = 81011
        
        # Start fetching both URLs
        prof_call = GetURL(url + str(professorsgatan))
        lth_call = GetURL(url + str(lth))
        
        best171 = self.get_bus(prof_call, 'A', 171,  timedelta(minutes=2) )
        best169 = self.get_bus(lth_call, 'A', 169,  timedelta(minutes=3))
        
        #----------------------------------        
        
        self.response.out.write('''
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>Mattebussen</title>
        <meta http-equiv="Content-Language" content="sv" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta http-equiv="refresh" content="5">
        <link rel="stylesheet" type="text/css" href="/stylesheets/style.css"/>
        </head>
        <body>
        <div id="vertical">   
        <div id="hoz">
        <div id="number">
        ''')
        if not best171 is None and not best169 is None :
            if best171- best169 > timedelta(minutes=3) :
                self.response.out.write('169')
            else :
                self.response.out.write('171')   
        elif not best171 is None :
            self.response.out.write('171')   
        elif not best169 is None :
            self.response.out.write('169')   
        else:
            self.response.out.write('?')  

        self.response.out.write('''
        </div>
        <div id="info">
        ''')
        self.response.out.write('Bästa 171 från professorsgatan : ' +  str(best171) + '<br/>\n' )
        self.response.out.write('Bästa 169 från LTH: '+ str(best169) + '<br/>\n' )
        self.response.out.write('''
        </div>
        </div>
        </div>
        </body>
        </html>
        ''')
        

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
							  