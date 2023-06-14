from datetime import datetime, timedelta
from configparser import ConfigParser
import time
from icalendar import Calendar
import requests
import pytz

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix

dtend = []
dtstart = []
priority = []
status = []
location = []
name = []

def fuckswap(a, b):
	dtstart[a], dtstart[b] = dtstart[b], dtstart[a]
	dtend[a], dtend[b] = dtend[b], dtend[a]
	priority[a], priority[b] = priority[b], priority[a]
	status[a], status[b] = status[b], status[a]
	location[a], location[b] = location[b], location[a]
	name[a], name[b] = name[b], name[a]

while(True):

	config_object = ConfigParser()
	config_object.read("config.ini")

	readinfo = config_object["USERINFO"]
	url = str(readinfo["url"])
	tz_user = pytz.timezone(readinfo["timezone"])
	regenerate_interval = int(readinfo["regenerate_interval"])

	readinfo2 = config_object["SITE"]
	if (str(readinfo2["no_unknown"]) == "True"):
		no_unknown = True
	else:
		no_unknown = False
	started_text = str(readinfo2["started_text"])
	ended_text = str(readinfo2["ended_text"])
	confirmed_text = str(readinfo2["confirmed_text"])
	cancelled_text = str(readinfo2["cancelled_text"])
	tentative_text = str(readinfo2["tentative_text"])
	unspecified_text = str(readinfo2["unspecified_text"])
	display_location = str(readinfo2["display_location"])
	refresh_interval = int(readinfo2["refresh_interval"])
	scrolltext = str(readinfo2["scrolltext"])

	r = requests.get(url, allow_redirects=True, timeout = 10)
	open('data.ics', 'wb').write(r.content)

	e = open('data.ics', 'rb')
	ecal = Calendar.from_ical(e.read())
	now = datetime.now(tz_user)

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

			combine_end = datetime.combine(timeend, datetime.min.time(), tz_user)

			try:
				delta:timedelta = timeend - now
			except TypeError:
				format_datetime = False
				delta:timedelta = combine_end - now

			if (format_datetime):
				delta:timedelta = timeend.astimezone(tz_user) - now
				realenddate = timeend.astimezone(tz_user)
			else:
				delta:timedelta = combine_end.astimezone(tz_user) - now
				realenddate = combine_end.astimezone(tz_user)

			if (delta.days < -1 or (delta.days == -1 and realenddate.day != now.day)):
				continue
			elif (delta.days == -1 and realenddate.day == now.day):
				today_done = True

			timestart = component.decoded("dtstart")

			combine_start = datetime.combine(timestart, datetime.min.time(), tz_user)

			try:
				delta2:timedelta = timestart - now
			except TypeError:
				format_datetime2 = False
				delta2:timedelta = combine_start - now

			if (format_datetime2):
				delta2:timedelta = timestart.astimezone(tz_user) - now
				realstartdate = timestart.astimezone(tz_user)
			else:
				delta:timedelta = combine_start.astimezone(tz_user) - now
				realstartdate = combine_start.astimezone(tz_user)

			if (delta2.days < 0 and (not today_done)):
				ongoing = True

			dtend.append ( realenddate )
			dtstart.append ( realstartdate )

			name.append( component.get("summary") )

			if (component.get("priority") == 1):
				priority.append( "HIGH" )
			elif (component.get("priority") == 9):
				priority.append( "LOW" )
			elif (component.get("priority") == 5 or no_unknown):
				priority.append( "MID" )
			else:
				priority.append( "N/A" )

			if (ongoing and str(component.get("status")) != "CANCELLED"):
				status.append( "Departed" )
			elif (today_done and str(component.get("status")) != "CANCELLED"):
				status.append( "Arrived" )
			elif (str(component.get("status")) == "TENTATIVE"):
				status.append( "Unknown" )
			elif (str(component.get("status")) == "CANCELLED"):
				status.append( "Cancelled" )
			elif (str(component.get("status")) == "CONFIRMED" or no_unknown):
				status.append( "On Time" )
			else:
				status.append( "Unspecified" )

			location.append( component.get("location") )

	for i in range(len(name)-1):
		mark = False
		for j in range(len(name)-i-1):
			if (dtstart[j+1] < dtstart[j]):
				fuckswap(j, j+1)
				mark = True
		if(not mark):
			break

	f = open("index.html", "w")

	f.write("""<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<head>
<meta http-equiv="refresh" content=\"""" + str(refresh_interval) + """\" />
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
			f.write("<td style=\"color: #00d619\">" + started_text + "</td>\n</tr>\n\n")
		elif (str(status[i]) == "Arrived"):
			f.write("<td style=\"color: #c842f5\">" + ended_text + "</td>\n</tr>\n\n")
		elif (str(status[i]) == "On Time"):
			f.write("<td style=\"color: #00d619\">" + confirmed_text + "</td>\n</tr>\n\n")
		elif (str(status[i]) == "Cancelled"):
			f.write("<td style=\"color: #ff1f1f\">" + cancelled_text + "</td>\n</tr>\n\n")
		elif (str(status[i]) == "Unknown"):
			f.write("<td>" + tentative_text + "</td>\n</tr>\n\n")
		elif (str(status[i]) == "Unspecified"):
			f.write("<td>" + unspecified_text + "</td>\n</tr>\n\n")
		else:
			f.write("<td>" + str(status[i]) + "</td>\n</tr>\n\n")

		if ((display_location == "First" and i == 0) or display_location == "All" or (display_location == "Auto" and str(location[i]) != "None")):
			f.write("<tr>\n<td></td>\n<td style=\"color: #ff1f1f\">Calling at:</td>\n<td></td>\n<td>" + str(location[i]) + "</td>\n<td></td>\n</tr>\n\n")

	f.write("""</table>
<div id="scroll-container">
<div id="scroll-text">""" + scrolltext + """</div>
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
	time.sleep(regenerate_interval)
