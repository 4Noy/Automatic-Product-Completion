#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, openai, re, os, time, optparse, random, requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


__author__ = "Nσy."
__version__ = "0.1"

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

#===================================================================================================



# 1 - Configuring the Parser and Arguments 
#===================================================================================================
usage =  """Usage: py {0} [Options]
 ____________________________________________________________________________
|             OPTIONS:                          Description:                 |
+============================================================================+
|   -h --help                      |  Show this help message and exit        |
+                                  +                                         +
|   -n --name <Product Name>       |  Set Product Name                       |
+                                  +                                         +
|   -b --brand <Product Brand>     |  Set Product Brand                      |
+                                  +                                         +
|   -e --EAN <Product EAN13>       |  Set Product EAN13                      |
+                                  +                                         +
|   -i --ID <Product ID>           |  Set Product ID                         |
+                                  +                                         +
|   -m --mode <Mode>               |  Set Tool Mode                          |
+                                  +                                         +
|   -p --prompt <File Directory>   |  Use the given prompt file              |
+                                  +                                         +
|   -o --output <Directory>        |  Save the result IN Directory           |
+                                  +                                         +
|   -v --verbose                   |  Verbose Mode                           |
+                                  +                                         +
|   --picnum <Number>              |  Configure picture number, DEFAULT : 3  |
+                                  +                                         +
=============================================================================+

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

        """.format(sys.argv[0])
parser = optparse.OptionParser( usage = usage, version="SEO_Product_Completion" + __version__)

parser.add_option("-n", "--name", dest="productName", type="string", help="Set Product Name")
parser.add_option("-b", "--brand", dest="productBrand", type="string", help="Set Product Brand")
parser.add_option("-e", "--EAN", dest="productEAN13", type="int", help="Set Product EAN13, must be a number")
parser.add_option("-i", "--ID", dest="productID", type="int", help= "Set Product ID, must be a number")
parser.add_option("-m", "--mode", dest="toolMode", type="int", help="Set the Tool mode, must an existing mode")
parser.add_option("-p", "--prompt", dest="promptFile", type="string", help="Set the Prompt File")
parser.add_option("-o", "--output", dest="outputDirectory", type="string", help="Customize the Directory Output")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Activate Verbose Mode")
parser.add_option("--picnum", dest="picturesNumber", type="int", default=3, help="Configure Picture Number, DEFAULT : 3")

(options, args) = parser.parse_args()


#===================================================================================================



# 2 - Setting Up Global Variables
#===================================================================================================
productID = options.productID
productName = options.productName
productBrand = options.productBrand
productEAN13 = options.productEAN13
promptFile = options.promptFile
picturesNumber = options.picturesNumber

if options.toolMode == None:
    toolMode = 1
else:
    toolMode = options.toolMode

if options.outputDirectory == None:
    outputDirectory = os.getcwd()
else:
    outputDirectory = options.outputDirectory

movedToProductIDDirectory = False
originalPath = os.getcwd()

#===================================================================================================



# 3 - PRINT METHODS
#===================================================================================================
def PrintWarningMessage(message):
    PrintVerbose("| Warning : " + message + " |")


def ErrorMessage(message:str, exeption = ""):
    print("====SCRIPT ERROR====\nMESSAGE : " + message + "\n====================")
    print(usage)
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
    print(usage)
    exit(0)


def PrintVerbose(message):
    if options.verbose:
        print(message)

#===================================================================================================



# 4 - Various Utilities
#===================================================================================================
def GetArgVariable(variable):
    if variable == None:
        ErrorMessage("Variable : " + f'{variable=}'.split('=')[0])
    else:
        return variable

def GetParts(chatGPTReply:str):
    parts = re.split(r'Partie\s*\d+\s*:', chatGPTReply)
    parts = [part.strip() for part in parts if part.strip()]
    return parts


def MoveToProductPath():
    if outputDirectory == None:
        outputDirectory = ""

    if not os.path.isdir(outputDirectory+"/Products/") :
        print("Creating Directory : Products/")
        os.mkdir(outputDirectory+'Products/')
    os.chdir(outputDirectory + "/Products")

    if not os.path.isdir(GetArgVariable(productID) + "/"):
        print("Creating Directory : Products/productID")
        os.mkdir(productID + "/")
    os.chdir(outputDirectory + "/Products/" + productID + "/")

    movedToProductIDDirectory = True


def SaveData(fileName:str ,data, mode = "wb"):
    with open(fileName, mode) as f:
        f.write(data)
    

#===================================================================================================



# 5 - Main Functions
#===================================================================================================
def AskChatGPTResult(prompt:str):
    PrintVerbose("Requesting Chat GPT...")
    promptToSend = [{"role" : "user", "content": prompt}]
    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=promptToSend
            )
    reply = chat.choices[0].message.content
    return reply


def GetPrompt():
    with open(GetArgVariable(promptFile), 'r', encoding="utf-8") as f:
        originalPrompt = f.read()
    
    finalPrompt = ""
    lenghtOriginalPrompt = len(originalPrompt)
    i = 0
    inColumn = False
    theWordeuuuu = ""
    while i < lenghtOriginalPrompt:
        c = originalPrompt[i]
        if inColumn:
            if c == "}":
                inColumn = False
                if "brand" in theWordeuuuu:
                    finalPrompt += GetArgVariable(productBrand)
                elif "product" in theWordeuuuu:
                    finalPrompt += GetArgVariable(productName)
                elif "ean" in theWordeuuuu :
                    finalPrompt += GetArgVariable(productEAN13)
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
    finalPrompt += "\n\nEach Part will start like this:\nPart [number]: the text\n\nResult in Français"
    return finalPrompt

def GetPictures(search:str, nbPictures = 3):
    PrintVerbose("Getting Pictures...")

    if not movedToProductIDDirectory:
        MoveToProductPath()

    productIDPath = os.getcwd()
    if not os.path.isdir("img/"):
        os.mkdir("img/")
    os.chdir(productIDPath + "/img/")

    if nbPictures <= 0:
        PrintWarningMessage("Number of pictures asked <= 0")
        return []

    #Get Right Format for google search
    search = search.replace(" ", "+")

    service = Service(seleniumSearchEngineDriverPath)
    browser = webdriver.Chrome(service=service)
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={search}"
    images_url = []

    
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

        images_url.append(element.get_attribute("src"))

        # write image to file
        try:
            reponse = requests.get(images_url[count])
            if reponse.status_code == 200:
                SaveData(f"image-{count+1}.jpg", reponse.content)
            else:
                PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count)) + str(images_url[count]))
        except:
            PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count)) + str(images_url[count]))

        #Stop
        count += 1
        if count == nbPictures:
            break
    browser.close()

    os.chdir(productIDPath)
    return images_url
    

def Main():
    PrintVerbose("Current Path : " + originalPath)
    
    try :
        prompt = GetPrompt()
    except:
        ErrorMessage("Erreur lors de la génération du prompt", "Prompt Error")

    if prompt.strip() == "":
        ErrorMessage("Erreur, Prompt Vide", "Prompt Error")


    try:
        chatGPTReply = AskChatGPTResult(prompt)
    except:
        ErrorMessage("Erreur Chat GPT, \n\t1 - Vérifiez votre connection Internet\n\t2 - Vérifiez votre votre clé API\n\t3 - Vérifiez votre nombres de requêtes restantes via l'API de Open AI\n\t4 - Vérifiez votre Parre Feux", "Chat GPT Error")

    if chatGPTReply.strip() == "":
        ErrorMessage("Erreur, Réponse de Chat GPT Vide", "Chat GPT Error")
    
    try:
        parts = GetParts(chatGPTReply)
    except:
        ErrorMessage("Erreur Lors de la séparation des différentes parties du Texte", "Spliting Part Error")

    if parts == [] or parts == [""]:
        ErrorMessage("Erreur, parties vides", "Spliting Part Error")

    MoveToProductPath()

    for i in range(len(parts)):
        SaveData("part"+str(i+1), parts[i], "w")

    GetPictures(productEAN13, picturesNumber)


#===================================================================================================




if __name__ == '__main__':
    Main()