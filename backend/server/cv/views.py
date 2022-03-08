from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import pymongo
import os
import yaml
import time
from cv.cv_script import detect
from cv.models import Module, Spot


@csrf_exempt
def index(request):
    if request.method == 'POST' and request.FILES['myfile']:
        # Get and save image file
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save("media/uploads/cv/"+myfile.name, myfile)
        print(filename)
        img_file = fs.url(filename)

        # connect to DB
        client = pymongo.MongoClient("mongodb+srv://root:root@cluster0.56jzb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client["Backend"]
        module_colleciton = db["module"]
        bbox_ref_collection = db["bbox_ref"]
        spot_collection = db["spots"]

        # Get module information from the request
        parkingLotName = ""
        modID = -1
        try:
            print("received post info")
            parkingLotName = request.POST["parkingLotName"]
            modID = int(request.POST["modNum"])
        except:
            print("No post info for parking lot")
            parkingLotName = "polygons"
            modID = 0

        identifier = {"modID":int(modID), "parkingLotName":parkingLotName}

        # Get the rest of the information from DB
        mod = module_colleciton.find_one(identifier)
        numSpotsFull = mod["numSpotsFull"]
        totalSpots = mod["totalSpots"]
        # print(totalSpots)

        module = Module(modNumber=modID, parkingLotName = parkingLotName, 
                        numSpotsFilled=numSpotsFull, numTotalSpots=totalSpots)

        # Load the bounding boxes from db
        bbox_dic = bbox_ref_collection.find_one(identifier)
        bbox = bbox_dic["mapping"]
        refSpots = []
        for idx, box in enumerate(bbox):
            combBox = []
            combBox.append(tuple(box[3]))
            combBox.append(tuple(box[0]))
            combBox.append(tuple(box[1]))
            combBox.append(tuple(box[2]))
            refSpots.append(Spot(box=combBox, spotNum=idx))

        # TODO: turn the CV into an API call
        t_start = time.process_time()
        updatedSpots = detect(filename, module, refSpots)
        print(time.process_time() - t_start)

        # count the number of occupied spots and update spot information
        numOccupied = 0
        occupiedIDs = []
        unoccupiedIDs = []
        for i, spot in enumerate(updatedSpots):
            print("Printing updated spot info:")
            print(spot.getID())
            print(spot.isOccupied())
            if spot.isOccupied():
                occupiedIDs.append(spot.getID())
                numOccupied += 1
            else:
                unoccupiedIDs.append(spot.getID())

        # divide total by num occupied to get %
        percentOccupied = numOccupied / module.getTotalSpots() if module.getTotalSpots()  != 0 else 0


        # bracket for each light colour
        # FIXME:TODO: Tweak bounds
        lightColour = 0                 # 0 represents off
        if percentOccupied >= 0.80:
            lightColour = 1             # 1 represents red
        elif percentOccupied >= 0.5:
            lightColour = 2             # 2 represents yellow
        elif percentOccupied < 0.5:
            lightColour = 3             # 3 represents green

        # Update the database information for the module
        module_colleciton.update_one({"parkingLotName": parkingLotName,
                                     "modID": modID},
                                     {'$set': {
                                         "ledColour" : lightColour,
                                         "numSpotsFull": numOccupied
                                     }})
        
        # Update spot specific information
        # Update occupied spots status to true
        spot_collection.update_many({"parkingLotName": parkingLotName,      # filter
                                     "modID": modID, 
                                     "spotNum": {"$in": occupiedIDs}},
                                     {'$set': {
                                         "occupied": True}})
        # Update unoccupied spots status to false
        spot_collection.update_many({"parkingLotName": parkingLotName,      # filter
                                    "modID": modID, 
                                    "spotNum": {"$in": unoccupiedIDs}}, 
                                    {'$set': {
                                        "occupied": False}})
                    
        if os.path.exists("media/uploads/cv/"+myfile.name):
            os.remove("media/uploads/cv/"+myfile.name)
            print("file removed")
            time.sleep(5)
        else:
            print("file does not exist")

        client.close()
        return JsonResponse({'light_colour': lightColour})
    
    # default response
    else:
        return render(request, 'cv/index.html')
