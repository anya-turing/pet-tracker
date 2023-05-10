import MySQLdb
import sys
import os
import serial
from datetime import datetime

username = input("Enter your username: ")
password = input("Enter your password: ")

try:
	con = MySQLdb.connect('antur90.us-east-1.rds.amazonaws.com', username, password, 'tracker')
	cur = con.cursor()
except MySQLdb.Error:
	print ("Error: ", MySQLdb.Error)
	sys.exit(1)

try:
	print ("Trying... serial port...")
	tracker = serial.Serial('COM3', 1200, timeout = 2) 
except: 
	print ("Failed to connect")
	sys.exit(1)

line = ""
lat = ""
lng = ""
age = 0
timelast = datetime.now()

print ("Listening:")	
while True:
	try:
		for b in tracker.read():
			timelast = datetime.now()
			if (b == ':'):
				if len(line)>0: ## clear old saved data for new data
					print("Fragmented Data: " + line)
					pieces = line.split(",")
					if len(pieces)==2:
						lat = pieces[0]
						lng = pieces[1]
						pieces = lng.split("#")
						if len(pieces)==2:
							lng = pieces[0]
							age = pieces[1]
				
					cur.execute("INSERT INTO evarate (raw,lat,lng,age) VALUES (%s,%s,%s,%s)", (line,lat,lng,age))
					con.commit() #commit the insert
					
					line = ""
					lat = ""
					lng = ""
					age = 0
			else:
				line+=b

		tdelta = datetime.now() - timelast
		tdelta = tdelta.total_seconds()
		if ((tdelta>3) & (len(line)>0)):
			timelast = datetime.now()
			print("")
			print("Recieved Data: " + line)
			pieces = line.split(",")
			if len(pieces)==2:
				lat = pieces[0]
				lng = pieces[1]
				pieces = lng.split("#")
				if len(pieces)==2:
					lng = pieces[0]
					age = pieces[1]
		
			cur.execute("INSERT INTO evarate (raw,lat,lng,age) VALUES (%s,%s,%s,%s)", (line,lat,lng,age))
			con.commit() #commit the insert
			
			line = ""
			lat = ""
			lng = ""
			age = 0
		else:
			print ("."),
	except:
		print ("Failed")
