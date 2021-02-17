import wss
import asyncio
import json
import escpos.printer
import time
import datetime
import pymsteams

loop = asyncio.get_event_loop()
## Update for SSL with Cert and Keys.
server =  wss.Server(port=7351, useSsl=False, sslCert="cert.crt", 
                     sslKey="server.key")

## Parse the message of strings and prepare variables
def parseIncommingMessage(msg, client):
	order = json.loads(msg)
	orderFood = order['items']
	orderDelivery = order['deliveryInformation']
	for question in orderDelivery: ## Grab the Questions from the JSON list.
		if question['question'].find ("Which bay number are you in?") != -1:
			carBay = question['answerString']
		if question['question'].find ("What's your license plate?") != -1:
			carReg = question['answerString']
	printOrder(order['orderSubmittedTime'],order['poeple'],carBay,carReg,orderFood,order['id'])

## Print Order
def printOrder(orderTime,orderName,orderBay,orderReg, orderFoodList, orderID):
	try:
		kitchen = escpos.printer.Network("10.0.0.245",timeout=5) #Touch the Kitchen Printer, make sure its alive.
	except:
		print("Printer is up the Ducking creak")
		sendAlert("Kitchen Printer Failed to respond.","Bentleys Kitchen Printer")
	finally:
		x = datetime.datetime.now()
		kitchen.set(font='c', align='center',width=1, height=2)
		kitchen.text("Tulleys Drive In Movies\n")
		kitchen.text("Bentleys Diner\n")
		kitchen.text("\n\n")
		kitchen.set(align='center')
		kitchen.text("Time: ")
		kitchen.text(x.strftime("%c"))
		kitchen.set(font='c', align='center',width=1, height=2)
		kitchen.text("\nCar Reg: ")
		kitchen.text(orderReg)
		kitchen.text("\n")
		kitchen.set(font='c', align='center',width=2, height=4)
		kitchen.text(orderBay)
		kitchen.set(font='c', align='center',width=1, height=2)
		kitchen.text("\n")
		kitchen.text(orderName)
		kitchen.text("\n\n\n")
		kitchen.set(font='c', align='center',width=1, height=1)
		for stuff in orderFoodList: 
			kitchen.text(stuff['name'])
		kitchen.text("\n\n")
		kitchen.barcode(orderID, 'EAN13', 64, 2, '', '')
		kitchen.cashdraw(5)
		kitchen.cashdraw(2)
		kitchen.cut()

## Send alert via Teams Message		
def sendAlert(message,title):
	myTeamsMessage = pymsteams.connectorcard("https://tulleysfarm.webhook.office.com/webhookb2/1183fae8-d4f6-4ce4-a2ba-35d9a3fb0518@01f9cc04-ca42-4456-b30d-a82d9f753bef/IncomingWebhook/e6ee31e9481b45bbbb297b5ff3358eaf/5599784b-e7d2-45a6-8c47-eaa84431383e")
	myTeamsMessage.text(" ")
	myTeamsMessage.title(title)

	# create the section
	myMessageSection = pymsteams.cardsection()

	# Section Title
	#myMessageSection.title(title)

	# Activity Elements
	myMessageSection.activityImage("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.visualpharm.com%2Ffree-icons%2Freceipt-595b40b65ba036ed117d15cc&psig=AOvVaw00M_1mRyJmyg5FWkJpNSjd&ust=1613289318469000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCOC1i5qx5u4CFQAAAAAdAAAAABAE")
	myMessageSection.activityText(message)

	# Add your section to the connector card object before sending
	myTeamsMessage.addSection(myMessageSection)
	myTeamsMessage.send()

	last_status_code = myTeamsMessage.last_http_status.status_code

server.setTextHandler(parseIncommingMessage)
sendAlert("TEST, APP ONLINE","Kitchen Printer")
server.start()
loop.run_forever()
