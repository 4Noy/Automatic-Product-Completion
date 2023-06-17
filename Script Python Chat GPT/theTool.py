#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Noy."
__version__ = "0.1"
__credits__ = ["Mev"]


import sys, openai, re, os, time, optparse, random, requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By




"""
NEEDS :
Python 3 - to install : go on the website https://www.python.org/
openai python package - to install : pip install openai
selenium python package - to install : pip install selenium
Chrome app - to install : go on the website https://www.google.com/chrome/
Chromium web driver - to install : go on the website https://chromedriver.chromium.org/downloads

And an Internet connection :)
"""

# Write your own prompt and add : {Product}
# for the product Name and add : {Brand}
# for the brand name and add : {EAN}
# for the EAN13

# 0 - Init
#===================================================================================================
openai.api_key = "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"
seleniumSearchEngineDriverPath = "C:\selenium browser drivers\chromedriver.exe"

setUpMessage = """

"""

#===================================================================================================



# 1 - Configuring the Parser and Arguments 
#===================================================================================================
__doc__ =  """Usage: py {0} [Options]
MADE BY : {1}

This tool is a python script to automate Product Creation and Completion.

 _____________________________________________________________________________________
|             OPTIONS:                          Description:                          |
+=====================================================================================+
|   -h --help                      |  Show this help message and exit                 |
+                                  +                                                  +
|   -n --name <Product Name>       |  Set Product Name                                |
+                                  +                                                  +
|   -b --brand <Product Brand>     |  Set Product Brand                               |
+                                  +                                                  +
|   -e --EAN <Product EAN13>       |  Set Product EAN13                               |
+                                  +                                                  +
|   -i --ID <Product ID>           |  Set Product ID                                  |
+                                  +                                                  +
|   -m --mode <Mode>               |  Set Tool Mode, DEFAULT : 1                      |
+                                  +                                                  +
|   -p --prompt <File Directory>   |  Use the given prompt file                       |
+                                  +                                                  +
|   -s --search <File Directory>   |  Use the given search File to find pictures      |
+                                  +                                                  +
|   -o --output <Directory>        |  Save the result IN Directory                    |
+                                  +                                                  +
|   -v --verbose                   |  Verbose Mode                                    |
+                                  +                                                  +
|   --pictnum <Number>             |  Specify picture number, DEFAULT : 3             |
+                                  +                                                  +
|   --model <Model Name>           |  Specify Open AI LLM, DEFAULT : gpt-3.5-turbo    |
+                                  +                                                  +
|   --language <Language>          |  Change chat language text, DEFAULT : English    |
+                                  +                                                  +
======================================================================================+

 ___________________________________________________
|      MODE:     |         Description:             |
+===================================================+
| DEFAULT:   1   |  Description, Meta and Pictures  |
+                +                                  +
|    2           |  Only Pictures                   | 
+                +                                  +
|    3           |  Only Description and Meta       |
+                +                                  +
====================================================+

Exemples :
    1  | py3 {2} -i 1 -n "LEGO FRIENDS VETERINARY CLINIC" -b "Lego" -e 5702017115160 -p "ExemplePrompt.txt" -s "ExempleRequest.txt" --model "text-davinci-003"
    Get the pictures and text of the article using as prompt: ExemplePrompt.txt, as picture search: ExempleRequest.txt and as llm text-davinci-003

    2  | py3 {3} -i 3 -n "Super Drum" -m 2 -pictnum 5 -v -o "C:\\Users\\Me\\ScriptResultHere" -s "C:\\Folder1\\Search.txt"
    Get 5 pictures of Super Drum in C:\\Users\\Me\\ScriptResultHere\\Products\\3\\img using Search.txt and the script is verbose.

    /!\\ If you don't use the brand or EAN13 in your prompt or search files, they aren't required by the script.

If you want more documentation, see the README.md and the Github:https://github.com/4Noy/Automatic-Product-Completion

        """.format(sys.argv[0], __author__, sys.argv[0], sys.argv[0])
parser = optparse.OptionParser(usage = __doc__, version=__version__, add_help_option = False)

parser.add_option("-h", "--help", dest="help", action="store_true", default=False, help="Show Help Message")
parser.add_option("-n", "--name", dest="productName", type="string", help="Set Product Name")
parser.add_option("-b", "--brand", dest="productBrand", type="string", help="Set Product Brand")
parser.add_option("-e", "--EAN", dest="productEAN13", type="int", help="Set Product EAN13, must be a number")
parser.add_option("-i", "--ID", dest="productID", type="int", help= "Set Product ID, must be a number")
parser.add_option("-m", "--mode", dest="toolMode", type="int", default=1, help="Set the Tool mode, must an existing mode")
parser.add_option("-p", "--prompt", dest="promptFile", type="string", help="Set the Prompt File")
parser.add_option("-s", "--search", dest="searchFile", type="string", help="Set the search file")
parser.add_option("-o", "--output", dest="outputDirectory", type="string", default=os.getcwd(), help="Customize the Directory Output")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Activate Verbose Mode")
parser.add_option("--pictnum", dest="picturesNumber", type="int", default=3, help="Configure Picture Number, DEFAULT : 3")
parser.add_option("--model", dest="openAIModel", type="string", default="gpt-3.5-turbo", help="Configure Open AI LLM, DEFAULT : gpt-3.5-turbo")
parser.add_option("--language", dest="language", type="string", default="English", help="Set the search file")

#===================================================================================================



# 2 - Setting Up Global Variables
#===================================================================================================
(options, args) = parser.parse_args()

if options.help:
    print(__doc__)
    exit(0)

productID = options.productID
productName = options.productName
productBrand = options.productBrand
productEAN13 = options.productEAN13
promptFile = options.promptFile
searchFile = options.searchFile
picturesNumber = options.picturesNumber
toolMode = options.toolMode
outputDirectory = options.outputDirectory
openAIModel = options.openAIModel
language = options.language

warningNumber = 0

movedToProductIDDirectory = False
originalPath = os.getcwd()

#===================================================================================================



# 3 - PRINT METHODS
#===================================================================================================
def PrintWarningMessage(message):
    global warningNumber
    PrintVerbose("| Warning : " + message + " |")
    warningNumber += 1


def ErrorMessage(message:str, exeption = ""):
    print("====SCRIPT ERROR====\nMESSAGE : " + message + "\n====================")
    print(__doc__)
    exit(0)


def MultipleErrorMesssages(messages:str, exeption = ""):
    lengthMessages = len(messages)
    if lengthMessages == 0:
        print("====SCRIPT ERROR====\nNO MESSAGE\n====================")
    elif lengthMessages == 1:
        print("====SCRIPT ERROR====\nMESSAGE : " + messages[0] + "\n====================")
    else:
        print("====SCRIPT ERROR====")
        for i in range(lengthMessages):
            print("MESSAGE N°{} : ".format(i) + messages[i] + "\n====================")
    print(__doc__)
    exit(0)


def PrintVerbose(message):
    if options.verbose:
        print(message)

#===================================================================================================



# 4 - Various Utilities
#===================================================================================================
def GetArgVariable(variable, variableName):
    if variable == None:
        ErrorMessage("Variable \"{}\" Used Not Set".format(variableName))
    else:
        return variable

def ShortLinks(link):
    if len(link) > 35:
        return link[:31] + "..."
    else:
        return link

def GetParts(chatGPTReply:str):
    parts = re.split(r'Partie\s*\d+\s*:', chatGPTReply)
    parts = [part.strip() for part in parts if part.strip()]
    return parts


def MoveToProductPath():

    if not os.path.isdir(outputDirectory+"/Products/") :
        print("Creating Directory : Products/")
        os.mkdir(outputDirectory+'/Products/')
    os.chdir(outputDirectory + "/Products")

    if not os.path.isdir(GetArgVariable(str(productID), "Product ID") + "/"):
        print("Creating Directory : Products/productID")
        os.mkdir(str(productID) + "/")
    os.chdir(outputDirectory + "/Products/" + str(productID) + "/")

    movedToProductIDDirectory = True


def SaveData(fileName:str ,data, mode = "wb"):
    with open(fileName, mode) as f:
        f.write(data)

def IntegrateElementsInText(text):
    finalPrompt = ""
    lenghtText = len(text)
    i = 0
    inColumn = False
    theWordeuuuu = ""
    while i < lenghtText:
        c = text[i]
        if inColumn:
            if c == "}":
                inColumn = False
                if "brand" in theWordeuuuu:
                    finalPrompt += GetArgVariable(productBrand, "Product Brand")
                elif "name" in theWordeuuuu:
                    finalPrompt += GetArgVariable(productName, "Product Name")
                elif "ean" in theWordeuuuu :
                    finalPrompt += GetArgVariable(productEAN13, "Product EAN13")
                else:
                    PrintWarningMessage("Balise : " + "{" + theWordeuuuu + "} Introuvable, Utilisez soit : \{Brand\}, \{Product\} or \{EAN\}")
                theWordeuuuu = ""
            else:
                theWordeuuuu += c.lower()
        elif c == "{":
            inColumn = True
        else:
            finalPrompt += c
        
        i+=1
    return finalPrompt
#===================================================================================================



# 5 - Main Functions
#===================================================================================================
def AskChatGPTResult(prompt:str):
    PrintVerbose("Requesting Chat GPT...")
    promptToSend = [{"role" : "user", "content": prompt}]
    chat = openai.ChatCompletion.create(
                model=openAIModel, messages=promptToSend
            )
    reply = chat.choices[0].message.content
    return reply


def GetPrompt():
    with open(GetArgVariable(promptFile, "Prompt File"), 'r', encoding="utf-8") as f:
        originalPrompt = f.read()
    
    finalPrompt = IntegrateElementsInText(originalPrompt)
    finalPrompt += "\n\nEach Part will start like this:\nPart [number]: the text\n\nResult in " + language
    return finalPrompt

def GenerateAndSavePictures():
    PrintVerbose("Getting Pictures...")
    global picturesNumber
    global searchFile
    global originalPath

    #Get Search
    lastPath = os.getcwd()
    os.chdir(originalPath)
    with open(searchFile, "r") as f:
        search = IntegrateElementsInText(f.read())
    os.chdir(lastPath)

    #Get Pictures
    if not movedToProductIDDirectory:
        MoveToProductPath()

    productIDPath = os.getcwd()
    if not os.path.isdir("img/"):
        os.mkdir("img/")
    os.chdir(productIDPath + "/img/")

    if picturesNumber <= 0:
        PrintWarningMessage("Picture Number <= 0, No Images will be downloaded")
        return

    #Get Right Format for google search
    search = search.replace("\n", "+").replace(" ", "+")

    service = Service(seleniumSearchEngineDriverPath)
    browser = webdriver.Chrome(service=service)
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={search}"

    # open browser and begin search
    browser.get(search_url)
    time.sleep(0.5)
    doNotConsentGoogleButton = browser.find_element(By.XPATH, "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button")
    doNotConsentGoogleButton.click()
    time.sleep(0.5)

    images = browser.find_elements(By.CLASS_NAME, 'rg_i') 
    count = 0
    for image in images:
        #Get images source url
        image.click()
        time.sleep(random.randint(60,90)/60)
        try:
            element = browser.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]")
        except:
            PrintWarningMessage("Cannot Get Image N°" + count)
            continue

        image_url = element.get_attribute("src")

        # write image to file
        try:
            reponse = requests.get(image_url)
            if reponse.status_code == 200:
                SaveData(f"image-{count+1}.jpg", reponse.content)
            else:
                PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count)) + ShortLinks(str(image_url)))
        except:
            PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count)) + ShortLinks(str(image_url)))

        #Stop
        count += 1
        if count == picturesNumber:
            break
    browser.close()

    os.chdir(productIDPath)
    


def GenerateAndSaveText():
    PrintVerbose("Generating Text...")
    try :
        prompt = GetPrompt()
    except:
        ErrorMessage("Error while generating the prompt", "Prompt Error")

    if prompt.strip() == "":
        ErrorMessage("Empty Prompt?", "Prompt Error")

    try:
        chatGPTReply = AskChatGPTResult(prompt)
    except:
        ErrorMessage("Error while Generating the text with Open AI, \n\t1 - Verify Internet Connection\n\t2 - Verify Open AI API key\n\t3 - Verify Open AI token cap \n\t4 - Verify Firewall", "Open AI Error")

    if chatGPTReply.strip() == "":
        ErrorMessage("Empty OpenAI Response", "Open AI Error")
    
    try:
        parts = GetParts(chatGPTReply)
    except:
        ErrorMessage("Error while spliting Text", "Spliting Part Error")

    if parts == [] or parts == [""]:
        ErrorMessage("Error, Empty Parts", "Spliting Part Error")

    MoveToProductPath()

    for i in range(len(parts)):
        SaveData("text_"+str(i+1), parts[i], "w")


def Main():
    global toolMode
    global warningNumber
    PrintVerbose("Current Path : " + originalPath)
    
    match toolMode:
        case 1:
            GenerateAndSaveText()
            GenerateAndSavePictures()
        case 2:
            GenerateAndSavePictures()
        case 3:
            GenerateAndSaveText()

    print("Progam Finished with {} warning".format(warningNumber))
        
    

    
    

        


#===================================================================================================




if __name__ == '__main__':
    Main()