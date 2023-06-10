# imports
from datetime import datetime, timedelta, timezone
from icalendar import Calendar
import requests
import pytz
import time

tz_SG = pytz.timezone('Asia/Singapore')
url = "https://p203-caldav.icloud.com.cn/published/2/MjAxMjcyMTk2NTEyMDEyN8GBwm1FlgKQX286ky2MJ-uEC_7MKsK7VyDrT3PvH58fioQWPcWeTrDOzzAl3u7aRBDVjYfABltR4_kJ28513Hw"

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix

def fuckswap(a, b):
	dtendtemp = dtend[a]
	dtend[a] = dtend[b]
	dtend[b] = dtendtemp
	dtstarttemp = dtstart[a]
	dtstart[a] = dtstart[b]
	dtstart[b] = dtstarttemp
	prioritytemp = priority[a]
	priority[a] = priority[b]
	priority[b] = prioritytemp
	statustemp = status[a]
	status[a] = status[b]
	status[b] = statustemp
	locationtemp = location[a]
	location[a] = location[b]
	location[b] = locationtemp
	nametemp = name[a]
	name[a] = name[b]
	name[b] = nametemp

while(True):

	r = requests.get(url, allow_redirects=True, timeout = 10)
	open('data.ics', 'wb').write(r.content)

	e = open('data.ics', 'rb')
	ecal = Calendar.from_ical(e.read())
	#print ("{:<4} {:<15} {:<4} {:<40} {:<8}".format('Pos', 'Time', 'Pri', 'Name', 'Status'))
	now = datetime.now(tz_SG)
	#now = datetime(2023, 6, 9)

	dtend = []
	dtstart = []
	priority = []
	status = []
	location = []
	name = []

	count = 0 # Count is only for debug and display purposes.

	for component in ecal.walk():
		if component.name == "VEVENT":

			count = count + 1

			format_datetime = True # For End Times
			format_datetime2 = True # For Start Times
			today_done = False
			ongoing = False

			timeend = component.decoded("dtend")
			if (str(timeend) == "None"):
				timeend = component.decoded("dtstart")

			combine_end = datetime.combine(timeend, datetime.min.time(), tz_SG)

			try:
				delta:timedelta = timeend - now
			except TypeError:
				format_datetime = False
				delta:timedelta = combine_end - now

			if (format_datetime):
				delta:timedelta = timeend.astimezone(tz_SG) - now
				realenddate = timeend.astimezone(tz_SG)
			else:
				delta:timedelta = combine_end.astimezone(tz_SG) - now
				realenddate = combine_end.astimezone(tz_SG)

			#print (realenddate, combine_end, now)
			#print (delta)

			if (delta.days < -1 or (delta.days == -1 and realenddate.day != now.day)):
				#print (component.get("summary"))
				#print ("Invalid.\n\n")
				continue
			elif (delta.days == -1 and realenddate.day == now.day):
				#print (component.get("summary"))
				#print ("Already happened, but today. output anyways.\n\n")
				today_done = True
			#else:
				#print (component.get("summary"))
				#print ("Normal.\n\n")

			timestart = component.decoded("dtstart")

			combine_start = datetime.combine(timestart, datetime.min.time(), tz_SG)

			try:
				delta2:timedelta = timestart - now
			except TypeError:
				format_datetime2 = False
				delta2:timedelta = combine_start - now

			if (format_datetime2):
				delta2:timedelta = timestart.astimezone(tz_SG) - now
				realstartdate = timestart.astimezone(tz_SG)
			else:
				delta:timedelta = combine_start.astimezone(tz_SG) - now
				realstartdate = combine_start.astimezone(tz_SG)

			if (delta2.days <= 0 and (not today_done)):
				ongoing = True

			dtend.append ( realenddate )
			dtstart.append ( realstartdate )

			'''if (format_datetime):
				dtend.append( timeend )
			else:
				dtend.append( combine_end )

			if (format_datetime2):
				dtstart.append( timestart )
			else:
				dtstart.append( combine_start )'''

			name.append( component.get("summary") )

			if (component.get("priority") == 1):
				priority.append( "HIGH" )
			elif (component.get("priority") == 5):
				priority.append( "MID" )
			elif (component.get("priority") == 9):
				priority.append( "LOW" )
			else:
				priority.append( "N/A" )

			if (ongoing and str(component.get("status")) != "CANCELLED"):
				status.append( "Departed" )
			elif (today_done and str(component.get("status")) != "CANCELLED"):
				status.append( "Arrived" )
			elif (str(component.get("status")) == "CONFIRMED"):
				status.append( "On Time" )
			elif (str(component.get("status")) == "TENTATIVE"):
				status.append( "Unknown" )
			elif (str(component.get("status")) == "CANCELLED"):
				status.append( "Cancelled" )
			else:
				status.append( "Unspecified" )

			location.append( component.get("location") )

	for i in range(len(name)-1):
		mark = False
		for j in range(len(name)-i-1):
			if (dtend[j+1] < dtend[j]):
				fuckswap(j, j+1)
				mark = True
		if(not mark):
			break

	#for i in range(len(name)):
		#print ("{:<4} {:<15} {:<4} {:<40} {:<8}".format(ordinal(i+1), str(dtstart[i].strftime('%d/%b/%y %H:%M')), str(priority[i]), str(name[i]), str(status[i])))

	f = open("index.html", "w")

	f.write("""<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<head>
<meta http-equiv="refresh" content="30" />
<meta charset="UTF-8">
<title>Test</title>
<link rel="stylesheet" href="style.css" />
</head>
<body>
<br/>
<table align="center">
<tr>
<td>POS&nbsp;&nbsp;&nbsp; </td>
<td>Time&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </td>
<td>PRI&nbsp;&nbsp;&nbsp; </td>
<td>Name&nbsp;&nbsp;&nbsp; </td>
<td>Status&nbsp;&nbsp;&nbsp; </td>
</tr>\n\n""")

	for i in range(len(name)):
		f.write("<tr>\n<td>" + str(ordinal(i+1)) + "</td>\n<td>" + str(dtstart[i].strftime('%d/%b/%y %H:%M')) + "</td>\n<td>" + str(priority[i]) + "</td>\n<td>" + str(name[i]) + "</td>\n")

		if (str(status[i]) == "Departed"):
			f.write("<td style=\"color: #00d619\">Departed</td>\n</tr>\n\n")
		elif (str(status[i]) == "Arrived"):
			f.write("<td style=\"color: #c842f5\">Arrived</td>\n</tr>\n\n")
		elif (str(status[i]) == "On Time"):
			f.write("<td style=\"color: #00d619\">On Time</td>\n</tr>\n\n")
		elif (str(status[i]) == "Cancelled"):
			f.write("<td style=\"color: #ff1f1f\">Cancelled</td>\n</tr>\n\n")
		else:
			f.write("<td>" + str(status[i]) + "</td>\n</tr>\n\n")

		if (i == 0):
			f.write("<tr>\n<td></td>\n<td style=\"color: #ff1f1f\">Calling at:</td>\n<td></td>\n<td>" + str(location[i]) + "</td>\n<td></td>\n</tr>\n\n")

	f.write("""</table>
<div id="scroll-container">
<div id="scroll-text">If you see something that doesn't look right, speak to a member of staff. See it, say it, sorted.</div>
</div>
<div id="scroll-container">
<div id="scroll-text-2">Last Updated: """)
	f.write(str(now.strftime('%Y-%m-%d %H:%M:%S.%f')))
	f.write("""</div>
</div>
<br/>
</body>
</html>
""")

	f.close()
	print("\nRefreshed successfully at " + str(now.strftime('%Y-%m-%d %H:%M:%S.%f')) + ".\nRendered " + str(len(name)) + " events out of " + str(count) + " fetched.\n")
	time.sleep(30) # Everyday use: 5min/300; Testing purposes: 30
