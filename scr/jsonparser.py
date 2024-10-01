import os
import json
import random
import math
import requests
import threading
import time
import numpy as np
from io import BytesIO
from pathlib import Path
from PIL import Image
import tkinter as tk

def listapis(foldername):
    """returns a list of the name key, path, and content of each json in the folder as a tuples of name and path"""
    # gets this file's parent's parent, aka the main folder, and add the string in the var "foldername" at the end of the path
    path = Path(__file__).parent.parent / foldername 
    
    fileslist = []
    # puts all the paths to json files in a list
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            fileslist.append(os.path.join(path, filename))
    
    apilist = []
    for file_path in fileslist:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                # adds the JSON object contains the key "name" to the list
                apiname = (data.get("ApiName"))
                
                # check if the current api was already listed so that there are no duplicates
                for api in apilist:
                    assert api[0] != apiname, "there are more than one file with the same api name"
                
                if "ApiName" in data:
                    apilist.append((apiname, file_path, data))
                else:
                    print(f"{file_path} doesn't have a 'ApiName' key")

            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {filename}")
    
    return apilist

def findjson(apiname:str, foldername:str="apis", outputtype="content"):
    """
    function that returns the path or the content of the json file that have a "name": that matches the given string input
    
    inputs:
        apiname: the name of the api to find
        path: the path to the folder in which the jsons are
        type : either "content" or "path" will define what will be outputed
    """
    
    if outputtype == "path":
        position = 1
    elif outputtype == "content":
        position = 2 
    else:
        print(f"{outputtype} is not a valid type, defaulting to content")
        position = 2
        
    
    apilist = listapis(foldername)
    matching_file = ""
    for e in apilist:
        if e[0] == apiname :
            matching_file = e[position]
    
    assert matching_file != "", "no matching file has been found"
    
    return matching_file

def getvarsfromurl(url:str):
    """returns the name/type of the variables in brackets"""
    variables = []
    for i in range(len(url)-2):
        before, current, after = url[i], url[i+1], url[i+2]
        if before == "[" and after == "]":
            variables.append(current)
    return(variables)

def generaterandom(stringtype:str, lenght):
    """generates a random string of letters or numbers using the inputs as settings"""
    string = ""
    if stringtype == "number":
        caracters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    else:
        caracters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        
    for i in range(lenght):
        string = f"{string}{random.choice(caracters)}"
    return string        

def GetApiCallVariables(apiname:str):
    """Gives the values of each variable in the url associated to the apiname
    
    Args:
        apiname (string): the name of the api to check for
    
    output:
        a list of strings whichs content depending on their var type:
        
        query (q): Gets the query from the search bar on the top left of the titlebar
        toggle (t): shows a on/off button in the settings, this var type has a name, a string for the on state and a string for the off state
        random (r): gets a random string of either numbers or letters, with a defined length
        width (w) and height (h): gets the current size of the screen
        x and y: gets the current ratio of the screen as x/y, like 4/3 or 16/9
        api key (k): gets the value put in the entry box in settings
        
    """
    global query
    data = findjson(apiname,"apis", "content")
    apicall = data.get("ApiCall", {})
    url = str(apicall.get("Url"))
    variables = getvarsfromurl(url)
    
    values = []
    
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # Calculate the greatest common divisor
    gcd = math.gcd(screen_width, screen_height)
    
    for i in range(len(variables)):
        currentsetting = apicall.get(f"Setting{i+1}", {})
        e = variables[i]
        if e == "q":
            values.append(query)
        elif e == "t":
            assert currentsetting != {}, "missing settings"
            # from the imported ui.py
            print("toggle")
            values.append("toggle")
        elif e == "r":
            assert currentsetting != {}, "missing settings"
            stringtype, lenght = currentsetting.get("Type"), currentsetting.get("Length")
            values.append(generaterandom(stringtype, lenght))
        elif e == "w":
            values.append(screen_width)
        elif e == "h":
            values.append(screen_height)
        elif e == "x":
            values.append(screen_width // gcd)
        elif e == "y":
            values.append(screen_height // gcd)
        elif e == "k":
            # from the imported ui.py
            print("apikey")
            values.append("apikey")
    
    return url, values

def PutvarsintoUrl(url:str, values:list):
    """function that puts the fetched values where they're supposed to go in the

    Args:
        url (string): the url in which to put the variables
        values (list): a list of the values to add in the url string, in order

    Returns:
        string: the Url that can be used to make an api call
    """
    usedvar = 0
    ignore = 0
    finalstring = ""
    for i in range(len(url)-2):
        if ignore != 0:
            ignore -= 1
        else:
            before, after = url[i], url[i+2]
            if before == "[" and after == "]":
                finalstring = f"{finalstring}{values[usedvar]}"
                ignore = 2 #ignores the next 2 caracters
                usedvar += 1
            else:
                finalstring = f"{finalstring}{url[i]}"
    if ignore == 0:
        finalstring = f"{finalstring}{url[-2]}{url[-1]}"
    elif ignore == 1:
        finalstring = f"{finalstring}{url[-1]}"
        
    return finalstring

def apicallfetcher():
    """ a function that takes the name of an Api and gives the final string used to make the api call"""
    global selectedapi
    url, values = GetApiCallVariables(selectedapi)
    return PutvarsintoUrl(url, values)

def GetApiresponseVariables(which:str, response):
    """Api that gets the differerent variables from the response.json file

    Args:
        which (str): describes which response i am fetching, image, source or author
        response (dict): the response of the api GET from which to take the variables
    """
    global selectedapi
    currentapi = findjson(selectedapi)
    settings = currentapi.get(which)
    url = settings.get("Url")
    variables = getvarsfromurl(url)
    
    values = []
    
    for i in range(len(variables)):
        currentsetting = settings.get(f"Answer{i+1}", {})
        assert currentsetting != {}, "missing settings"
        position = currentsetting.split(":")
        variable  = response
        for e in position:
            variable = variable.get(e)
        values.append(variable)
    
    return url, values

def geturlfromresponse(response:dict, which):
    """function that gives the url of the current image
    """
    url, values = GetApiresponseVariables(which, response)
    return PutvarsintoUrl(url, values)

def downloadimage(url):
    """downloads the image, converts it to a .png and saves it as response/response.png"""
    filepath = Path(__file__).parent.parent / "response" / "response.jpg"
    filepath.parent.mkdir(parents=True, exist_ok=True) # make sure the path exists, if not, create it
    
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")  # converts image to PNG
        
        image.save(filepath, "JPEG", optimize=True)
        print(f"Image downloaded, converted to JPEG, and saved as {filepath}")
    else:
        print("Failed to download image. HTTP Status code:", response.status_code)

def Getinformations(response, which):
    """gets the name of the author or the source"""
    global selectedapi
    currentapi = findjson(selectedapi)
    authorpath = currentapi.get(which)
    assert authorpath != {}, "missing settings"
    
    authorpath = authorpath.split(":")
    authorname = response
    for e in authorpath:
        authorname = authorname.get(e)
        
    return authorname    

def reloadimage():
    """does all the logic for calling the api, once done, puts the image in /response/response.png and the "author" and the "source" in the global variable "response" """
    global response
    global selectedapi
    settings = findjson(selectedapi)
    callurl = apicallfetcher() 
    print(f"fetching {callurl}")

    response = {}
    
    if settings.get("Image") == None:
        downloadimage(callurl)
        response["Author"] = "unknown"
    else: 
        currentresponse = requests.get(callurl)
        if currentresponse.status_code != 200:
            return(currentresponse.status_code, currentresponse.content)# if the call has failed, give the code and the error back to be shown as an error message
        responsecontent = currentresponse.json()
        downloadimage(geturlfromresponse(responsecontent, "Image"))
        
        if settings.get("Source") != None:
            response["Source"] = geturlfromresponse(responsecontent, "Source")
        
        if settings.get("Author") != None:
            response["Author"] = Getinformations(responsecontent, "Author")
        else:
            response["Author"] = "unknown"
    return True

def getresponce():
    """returns the global response varible"""
    global response
    return response

def setquery(currentquery):
    """ sets the global query value"""
    global query
    query = currentquery
    return

def isqueryneeded():
    """checks for [q] in the current url"""
    global selectedapi
    data = findjson(selectedapi,"apis", "content")
    apicall = data.get("ApiCall", {})
    url = str(apicall.get("Url"))
    if "[q]" in url:
        return True
    else:
        return False

selectedapi = "unsplash"