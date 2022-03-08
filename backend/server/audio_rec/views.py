from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from audio_rec.audio_rec_script import detect
import pymongo
import os
import time


# Create your views here.
def index(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save("media/uploads/audio_rec/"+myfile.name, myfile)

        # connect to DB
        client = pymongo.MongoClient("mongodb+srv://root:root@cluster0.56jzb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client["Backend"]
        module_colleciton = db["module"]

        # Get module information from the request
        parkingLotName = ""
        modID = -1
        try:
            print("received post info")
            parkingLotName = request.POST["parkingLotName"]
            modID = request.POST["modNum"]
        except:
            print("No post info for parking lot")
            parkingLotName = "Kensington"
            modID = 0

        identifier = {"modID":int(modID), "parkingLotName":parkingLotName}
        mod = module_colleciton.find_one(identifier)

        lightColour = -1
        try:
            confidence, matches_found = detect(filename)
            if matches_found > 30 and confidence > 2:           
                #4 represents the colour blue, car alarm detected 
                lightColour = 4
                # Update module info on DB
                module_colleciton.update_one({"parkingLotName": parkingLotName,
                                "modID": modID},
                                {'$set': {
                                    "ledColour" : lightColour,
                                    }})
            else:
                #-1 represents keep previous lightColour
                lightColour = -1 
        except:
            lightColour = -1

        if os.path.exists("media/uploads/audio_rec/"+myfile.name):
            os.remove("media/uploads/audio_rec/"+myfile.name)
            print("file removed")
            time.sleep(5)
        else:
            print("file does not exist")

        client.close()
        return JsonResponse({'light_colour': lightColour})
    else:
        return render(request, 'audio_rec/index.html')