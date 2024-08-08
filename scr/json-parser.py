import os
import json
import random
import math
from pathlib import Path
from PIL import ImageGrab

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

def findjson(apiname:str, foldername:str, outputtype="path"):
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
        print(f"{outputtype} is not a valid type, defaulting to path")
        position = 1
        
    
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
    data = findjson(apiname,"apis", "content")
    apicall = data.get("ApiCall", {})
    url = str(apicall.get("Url"))
    variables = getvarsfromurl(url)
    
    values = []
    
    
    # Grab the screen (entire screen)
    screen = ImageGrab.grab()
    # Get the screen width and height
    screen_width, screen_height = screen.size
    # Calculate the greatest common divisor
    gcd = math.gcd(screen_width, screen_height)
    
    for i in range(len(variables)):
        currentsetting = apicall.get(f"Setting{i+1}", {})
        e = variables[i]
        if e == "q":
            # from the imported ui.py
            print("query")
            values.append("query")
        elif e == "t":
            # from the imported ui.py
            print("toggle")
            values.append("toggle")
        elif e == "r":
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
    return finalstring

def apicallfetcher(apiname:str):
    """ a function that takes the name of an Api and gives the final string used to make the api call"""
    url, values = GetApiCallVariables(apiname)
    return PutvarsintoUrl(url, values)
