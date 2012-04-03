# coding=utf8
import webapp2
from urllib import urlopen
from xml.dom.minidom import parseString
from datetime import datetime, timedelta

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        hpl     = 81124     # LTH
        buss171 = (171,'D') # Mot Malmö
        buss169 = (169,'A') # Mot Malmö
        
        best={}
        best[buss171] = datetime.now() + timedelta(days=10)
        best[buss169] = datetime.now() + timedelta(days=10)

        url = 'http://www.labs.skanetrafiken.se/v2.2/stationresults.asp?selPointFrKey='+str(hpl)
        data = urlopen(url).read()
        xml = parseString(data)
        lines = xml.getElementsByTagName('Lines')[0]
        best={}
        for line in lines.getElementsByTagName('Line') :
            datestr = line.getElementsByTagName('JourneyDateTime')[0].firstChild.data
            date = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
            no   = int(line.getElementsByTagName('No')[0].firstChild.data)
            stop =     line.getElementsByTagName('StopPoint')[0].firstChild.data
            buss  = (no,stop)
            if not best.has_key(buss) :
                best[buss] = date
            elif date < best[buss] :
                best[buss] = date

        #----------------------------------        
        
        self.response.out.write('''
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>Mattebussen</title>
        <meta http-equiv="Content-Language" content="sv" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <script type="text/javascript" src="swfobject.js"></script>
        <style type="text/css">
        body {
            margin-left: 0px;
            margin-top: 0px;
            margin-right: 0px;
            margin-bottom: 0px;
        }

        html {
        height:100%
        }

        html,body {
        margin:0;padding:0;
        }

        body{
        text-align: center;
        min-width:650px;
        background-color: #000080;
        }

        #vertical{	
        position:absolute;
        top:50%;	
        margin-top:-130px;/* half flash height*/	
        left:0;
        width:100%;
        }

        #hoz {
        width:624px;/* flash width*/
        margin-left:auto;
        margin-right:auto;	
        height:395px;/* flash height*/
        }
        </style>
        </head>
        <body>
        <div id="vertical">   
        <div id="hoz">
        <div style="color: #9c6114; font-family: Arial; font-size: 220pt; line-height: 220pt; font-weight: bold;">
        ''')
        if best[buss171] - best[buss169] > timedelta(minutes=5) :
            self.response.out.write('169')
        else :
            self.response.out.write('171')   

        
        self.response.out.write('''
        </div>
        <div style="color: #333333; font-family: Arial; font-size: 8pt;">
        ''')
        self.response.out.write('Best 171 : ' +  str(best[buss171]) + '<br/>\n' )
        self.response.out.write('Best 169 : '+ str(best[buss169]) + '<br/>\n' )
        self.response.out.write('''
        </div>
        </div>
        </div>
        </body>
        </html>
        ''')
        

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
							  