import pymongo
from twilio.rest import Client
import time

def connect_to_twilio():
# the following line needs your Twilio Account SID and Auth Token
    client = Client("AC65ed3fbbf3f60aa279985826f62a5653", "3350ac9038be92decb1cc5c53ebba665")
    return client

def connect_to_db():
    client = pymongo.MongoClient("mongodb+srv://root:root@cluster0.56jzb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client["Backend"]
    module_collection = db["module"]
    parking_lot = db["parking_lot"]
    return client, parking_lot, module_collection

def disconnect_from_db(client):
    client.close()

def list_of_parking_lots(module):
    list_of_parking_names = []
    for parking_lot_names in module.find():
        if parking_lot_names["parkingLotName"] not in list_of_parking_names:
            list_of_parking_names.append(parking_lot_names["parkingLotName"])
    return list_of_parking_names

def parking_density(module, list_of_parking_lots):
    list_of_density = []
    counter = 0
    for lot_names in list_of_parking_lots:
        query = {"parkingLotName" : lot_names}
        sumoccupiedspots = 0
        sumtotalspots = 0
        for documents in module.find(query): 
            totalspots = documents["totalSpots"]
            occupiedspots = documents["numSpotsFull"]
            sumtotalspots = int(totalspots) + sumtotalspots
            sumoccupiedspots = int(occupiedspots) + sumoccupiedspots

        density = sumoccupiedspots / sumtotalspots if totalspots != 0 else 0
        list_of_density.append(density)
        counter += 1
    return list_of_density

def plot_notify_list(parking_lot, density_parking):
    full = []
    three_quarters = []
    half = []
    for lot_name, density_lot in zip(parking_lot, density_parking):
        if density_lot == 1:
            full.append(lot_name)
        elif density_lot > 0.75:
            three_quarters.append(lot_name)
        elif density_lot > 0.5:
            half.append(lot_name)
    return full, three_quarters, half
    
def send_message(full_lot, three_quarters_lot, half_lot, twilio_client, parking_lot):

    for lots in parking_lot.find():
        phone_numbers = lots["phoneNumbers"]
        for full_lots in full_lot:
            if lots["parkingLotName"] == full_lots:
                for numbers in phone_numbers:
                    body_of_message = 'The Parking Lot: %s, is 100%% full, please try another parking lot.' % (full_lots)
                    twilio_client.messages.create(to=numbers, from_="+18457576276",
                                                  body=body_of_message)

        for three_quarter_lots in three_quarters_lot:
            if lots["parkingLotName"] == three_quarter_lots:
                for numbers in phone_numbers:
                    body_of_message = 'The Parking Lot: %s is 75%% full.' % (three_quarter_lots)
                    twilio_client.messages.create(to=numbers, from_="+18457576276",
                                                  body=body_of_message)
                
        for half_lots in half_lot:
            if lots["parkingLotName"] == half_lots:
                for numbers in phone_numbers:
                    body_of_message = 'The Parking Lot: %s is 50%% full.' % (half_lots)
                    print(body_of_message)
                    twilio_client.messages.create(to=numbers, from_="+18457576276",
                                    body=body_of_message)


twilio_client = connect_to_twilio()

while(1):
    client, parking_lot, module_collection = connect_to_db()
    list_plot_names = list_of_parking_lots(module_collection)
    list_parking_density = parking_density(module_collection, list_plot_names)

    full_lot, three_quarters_lot, half_lot = plot_notify_list(list_plot_names, list_parking_density)
    send_message(full_lot, three_quarters_lot, half_lot, twilio_client, parking_lot)
    time.sleep(900)

disconnect_from_db(client)
