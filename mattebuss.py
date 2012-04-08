# coding=utf8
import webapp2
from urllib import urlopen
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
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
      	
    def add_buses(self, buses, url_call, hpl_name, buss_no, stop_point) :	
        data = url_call.get_data()

        xml = parseString(data)
        lines = xml.getElementsByTagName('Lines')[0]
        for line in lines.getElementsByTagName('Line') :
            datestr = line.getElementsByTagName('JourneyDateTime')[0].firstChild.data
            date = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S')
            no   = int(line.getElementsByTagName('No')[0].firstChild.data)
            stop =     line.getElementsByTagName('StopPoint')[0].firstChild.data
      	    towards = line.getElementsByTagName('Towards')[0].firstChild.data;

	    if (stop == stop_point) and (no == buss_no) :
			buses.append([hpl_name, no,date,date]);
	return buses;		

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
           
   	swedenoffset = timedelta(hours=2);
    	now = datetime.now() + swedenoffset;

 	# Many settings, oh fun.
	show_num_options = 3; # How many alternatives should be presented?

	time_margin = timedelta(seconds=30);
    	time_exit = timedelta(seconds=50); # From office to entrance
	time_lth = timedelta(seconds=180); # From entrance to lth.
	time_pro = timedelta(seconds=180); # From entrance to professorsgatan
	
	time_tease = timedelta(seconds = 60); # Show buses that it's esimtaed you wont catch.

        hpl_lth     = 81124;     # Kårhuset
        hpl_pro     = 81011;    # Professorsgatan
	url = 'http://www.labs.skanetrafiken.se/v2.2/stationresults.asp?selPointFrKey='
        prof_call = GetURL(url + str(hpl_pro))
        lth_call = GetURL(url + str(hpl_lth))

	buses =[];
	buses = self.add_buses(buses, lth_call, 'lth', 169, 'A');
	buses = self.add_buses(buses, lth_call, 'lth', 171, 'D');
	buses = self.add_buses(buses, prof_call, 'pro', 171, 'A');
	       
        # Remove transportation time
	for item in buses :
		item[3] -= (time_margin+time_exit);
		
		if item[0] == 'lth' :
			item[3] -= time_lth;
		if item[0] == 'pro' :
			item[3] -= time_pro;

 	# Sort on  modified time
	buses.sort(key=lambda x: x[3]); 
    
	# Remove uncatchable buses
	def catchable(x):
    		if (now - x[3]) > time_tease:
      			return False
    		else:
			return True

	buses = filter(catchable, buses);

        #----------------------------------        
        
        self.response.out.write('''
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>Mattebusen</title>
        <meta http-equiv="Content-Language" content="sv" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" type="text/css" href="/stylesheets/style.css"/>
        </head>
        <body>
        <div id="vertical">   
        <div id="hoz">
	<div style="color: #DDDDDD; font-family: Arial; font-size: 20pt; line-height: 20pt; text-align:left"> 
	''')
	
	self.response.out.write('Current time: ' + str(now.strftime('%H:%M')) + '<br/><hr/> ');	
	
	for num in range(0,min(show_num_options,len(buses))):	

		
		bus = buses[num];
		self.response.out.write('''<div style="color: #FFFFFF; font-family: Arial; font-size: 20pt; line-height: 20pt; text-align:left">''')

		if bus[0] == 'lth' :
			bus_stop =  'Kårhuset';
		if bus[0] == 'pro' :
			bus_stop = 'Professorsgatan';
	
		self.response.out.write('From <b>' + bus_stop + '</b> at ' + str(bus[2].strftime('%H:%M')) + ' take bus:');		
		self.response.out.write(''' <div style="color: #9c6114; font-family: Arial; font-size: 80pt; line-height: 80pt; font-weight: bold;">''');
		self.response.out.write(bus[1]);	
		self.response.out.write('''</div>''') 
		
        
       		self.response.out.write('''</div><div style="color: #AAAAAA; font-family: Arial; font-size: 12pt;">''')
	
		marginal = bus[3]-now;
		
		
		self.response.out.write('Estimated marginal is: ' + str(round(marginal.total_seconds(),0)) + ' seconds' ' <br /><br />');			
		self.response.out.write('</div>');		
		
       	self.response.out.write('''
        </div>
        </div>
        </div>
        </body>
        </html>
        ''')

        

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
							  
