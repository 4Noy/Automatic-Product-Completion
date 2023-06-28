#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Noy."
__version__ = "0.1"
__credits__ = ["Mev"]


import sys, openai, re, os, time, optparse, requests, json, threading, subprocess, unidecode
from selenium_recaptcha_solver import RecaptchaSolver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image


"""
NEEDS :
Python 3 - to install : go on the website https://www.python.org/
openai python package - to install : pip install openai
selenium python package - to install : pip install selenium
unidecode python packa - to install : pip install Unidecode
bs4 python package - to install : pip install bs4
PIL python package - to install : pip install pillow
Chrome app - to install : go on the website https://www.google.com/chrome/
Chromium web driver - to install : go on the website https://chromedriver.chromium.org/downloads

And an Internet connection :)
"""

# Write your own prompt and add : {Product}
# for the product Name and add : {Brand}
# for the brand name and add : {EAN}
# for the EAN13

# You can modift these values if your internet connection is slow
#===================================================================================================
lowestWaitingTime = 0
highestWaitingTime = 0.2
lowestWaitingTimeForPictures = 0.2
highestWaitingTimeForPictures = 1


# 0 - Init
#===================================================================================================
isWebSiteUsage = False
lock = threading.Lock()


def is_chat_model(model_name):
    """
    DOCUMENTATION
        Function : is_chat_model
        Description : Check if the model is a chat model
        Input :
            model_name : The name of the model to check
        Output :
            True if the model is a chat model, False otherwise
    """
    models = openai.Model.list()["data"]
    for i in models:
        if model_name == i["id"]:
            return True
    return False

def SetupConfig(isFirstTime):
    """
    DOCUMENTATION
        Function : SetupConfig
        Description : Setup the config file
        Input :
            isFirstTime : True if it's the first time you use the tool, False otherwise
        Output :
            None
    """
    print("""
Welcome to the Automatic Product Completion Tool installation.
This tool is a python script to automate Product Creation and Completion.
With this initial setup, you will add :
    - your OpenAI API key
    - your Selenium Web Driver path
    - your enterprise name (on google shopping)
    - your default language
    - your default chat model (gpt-3.5-turbo recommanded)
    - your default prompt file
    - your default prompt file if you dont have brand name
    - your default search file
"""
)
    #Verify if the api key is valid
    global openai
    global seleniumSearchEngineDriverPath
    global enterpriseName
    global defaultLanguage
    global defaultModel
    global defaultPrompt
    global defaultSearch
    if isFirstTime:
        time.sleep(2)
        
        openai.api_key = input("Enter your OpenAI API key : ")
        while True:
            try:
                openai.Completion.create(engine="davinci", prompt="i", max_tokens=2)
                break
            except:
                print("Your API key is not valid, please try again")
                openai.api_key = input("Enter your OpenAI API key : ")
        #Verify if the selenium web driver path is valid
        seleniumSearchEngineDriverPath = input("Enter your Selenium Web Driver path : ")
        while True:
            try:
                service = Service(seleniumSearchEngineDriverPath)
                break
            except:
                print("Your Selenium Web Driver path is not valid, please try again")
                seleniumSearchEngineDriverPath = input("Enter your Selenium Web Driver path : ")

        enterpriseName = input("Enter your enterprise name (on google shopping) : ")

        defaultLanguage = input("Enter your default language : ")

        defaultModel = input("Enter your default chat model (gpt-3.5-turbo recommanded) : ")
        #verify if the default model is valid
        while not is_chat_model(defaultModel):
            print("Your default model is not valid, please try again")
            defaultModel = input("Enter your default chat model (gpt-3.5-turbo recommanded) : ")
        #Verify if the default prompt file is valid
        defaultPrompt = input("Enter your default prompt file : ")
        while not os.path.isfile(defaultPrompt):
            print("Your default prompt file is not valid, please try again")
            defaultPrompt = input("Enter your default prompt file : ")

        defaultPromptNoBrand = input("Enter your default prompt file if you dont have brand name (can be the same as the prompt file): ")
        while not os.path.isfile(defaultPromptNoBrand):
            print("Your default prompt file if you dont have brand name is not valid, please try again")
            defaultPromptNoBrand = input("Enter your default prompt file if you dont have brand name (can be the same as the prompt file) : ")
        #Verify if the default search file is valid
        defaultSearch = input("Enter your default search file : ")
        while not os.path.isfile(defaultSearch):
            print("Your default search file is not valid, please try again")
            defaultSearch = input("Enter your default search file : ")
    else:
        jsonFile = open("config.json", "r")
        config = json.load(jsonFile)
        jsonFile.close()
        if "openai_api_key" not in config or input("Do you want to change your OpenAI API key ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            key = input("Enter your OpenAI API key : ")
            openai.api_key = key
            while True:
                try:
                    openai.Completion.create(engine="davinci", prompt="i", max_tokens=2)
                    break
                except:
                    print("Your API key is not valid, please try again")
                    key = input("Enter your OpenAI API key : ")
            config["openai_api_key"] = key
        else:
            openai.api_key = config["openai_api_key"]

        if "selenium_search_engine_driver_path" not in config or input("Do you want to change your Selenium Web Driver path ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            path = input("Enter your Selenium Web Driver path : ")
            while True:
                try:
                    service = Service(path)
                    break
                except:
                    print("Your Selenium Web Driver path is not valid, please try again")
                    path = input("Enter your Selenium Web Driver path : ")
            seleniumSearchEngineDriverPath = path
            config["selenium_search_engine_driver_path"] = path
        else:
            seleniumSearchEngineDriverPath = config["selenium_search_engine_driver_path"]

        if "enterprise_name" not in config or input("Do you want to change your enterprise name (on google shopping) ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            name = input("Enter your enterprise name (on google shopping) : ")
            enterpriseName = name
            config["enterprise_name"] = name
        else:
            enterpriseName = config["enterprise_name"]

        if "default_language" not in config or input("Do you want to change your default language ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            language = input("Enter your default language : ")
            defaultLanguage = language
            config["default_language"] = language
        else:
            defaultLanguage = config["default_language"]

        if "default_model" not in config or input("Do you want to change your default chat model ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            model = input("Enter your default chat model : ")
        
            while not is_chat_model(model):
                print("Your default model is not valid, please try again")
                model = input("Enter your default chat model : ")
            defaultModel = model
            config["default_model"] = model
        else:
            defaultModel = config["default_model"]

        if "default_prompt" not in config or input("Do you want to change your default prompt file ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            prompt = input("Enter your default prompt file : ")
            #Verify if the default prompt file is valid
            while not os.path.isfile(prompt):
                print("Your default prompt file is not valid, please try again")
                prompt = input("Enter your default prompt file : ")
            defaultPrompt = prompt
            config["default_prompt"] = prompt
        else:
            defaultPrompt = config["default_prompt"]

        if "default_prompt_no_brand" not in config or input("Do you want to change your default prompt file if you dont have brand name ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            prompt = input("Enter your default prompt file if you dont have brand name (can be the same as the prompt file): ")
            #Verify if the default prompt file is valid
            while not os.path.isfile(prompt):
                print("Your default prompt file if you dont have brand name is not valid, please try again")
                prompt = input("Enter your default prompt file if you dont have brand name (can be the same as the prompt file) : ")
            defaultPromptNoBrand = prompt
            config["default_prompt_no_brand"] = prompt

        if "default_search" not in config or input("Do you want to change your default search file ? (Press Enter to skip, anything else then Enter otherwise)") != "":
            search = input("Enter your default search file : ")
            #Verify if the default search file is valid
            while not os.path.isfile(search):
                print("Your default search file is not valid, please try again")
                search = input("Enter your default search file : ")
            defaultSearch = search
            config["default_search"] = search     
        else:
            defaultSearch = config["default_search"]
        #Add the modified config to the config.json file
    config = {
        "openai_api_key": openai.api_key,
        "selenium_search_engine_driver_path": seleniumSearchEngineDriverPath,
        "enterprise_name": enterpriseName,
        "default_language": defaultLanguage,
        "default_model": defaultModel,
        "default_prompt": defaultPrompt,
        "default_prompt_no_brand": defaultPromptNoBrand,
        "default_search": defaultSearch
    }   
    jsonFile = open("config.json", "w+")
    jsonFile.write(json.dumps(config))
    jsonFile.close()
    print("Your configuration has been saved in the config.json file")
    exit(0)

corruptedConfig = False

if os.path.isfile("config.json"):
    jsonFile = open("config.json", "r")
    config = json.load(jsonFile)
    jsonFile.close()
    try:
        openai.api_key = config["openai_api_key"]
        seleniumSearchEngineDriverPath = config["selenium_search_engine_driver_path"]
        enterpriseName = config["enterprise_name"]
        defaultLanguage = config["default_language"]
        defaultModel = config["default_model"]
        defaultPrompt = config["default_prompt"]
        defaultPromptNoBrand = config["default_prompt_no_brand"]
        defaultSearch = config["default_search"]
    except:
        print("Your config.json file is corrupted, please do the setup again")
        corruptedConfig = True
else:
    SetupConfig(True)
    

#===================================================================================================



# 1 - Configuring the Parser and Arguments 
#===================================================================================================
__doc__ =  """Usage: py {0} [Options]
MADE BY : {1}

This tool is a python script to automate Product Creation and Completion.

 ________________________________________________________________________________________
|             OPTIONS:                          Description:                             |
+========================================================================================+
|   -h --help                      |  Show this help message and exit                    |
+                                  +                                                     +
|   -n --name <Product Name>       |  Set Product Name                                   |
+                                  +                                                     +
|   -b --brand <Product Brand>     |  Set Product Brand                                  |
+                                  +                                                     +
|   -e --EAN <Product EAN13>       |  Set Product EAN13                                  |
+                                  +                                                     +
|   -i --ID <Product ID>           |  Set Product ID                                     |
+                                  +                                                     +
|   -m --mode <Mode>               |  Set Tool Mode, DEFAULT : 111                       |
+                                  +                                                     +
|   -p --prompt <File Directory>   |  Use the given prompt file                          |
+                                  +                                                     +
|   -s --search <File Directory>   |  Use the given search File to find pictures         |
+                                  +                                                     +
|   -o --output <Directory>        |  Save the result IN Directory                       |
+                                  +                                                     +
|   -v --verbose                   |  Verbose Mode                                       |
+                                  +                                                     +
|   --picnum <Number>              |  Specify picture number, DEFAULT : 5                |
+                                  +                                                     +
|   --model <Model Name>           |  Specify Open AI LLM chat, DEFAULT : gpt-3.5-turbo  |
+                                  +                                                     +
|   --language <Language>          |  Change chat language response                      |
+                                  +                                                     +
|   --GSP                          |  Get the price only with google shopping            |
+                                  +                                                     +
|   --config                       |  Initialize or modify the config File               |
+                                  +                                                     +
=========================================================================================+

 ___________________________________________________
|      MODE:     |         Description:             |
+===================================================+
| DEFAULT:  100  |  Descriptions                    |
+                +                                  +
|    010         |  Pictures                        | 
+                +                                  +
|    001         |  Price                           |
+                +                                  +
====================================================+
Wich means that 101 will get Descriptions and Price
and 111 will get Descriptions, Pictures and Price


Exemples :
    1  | py3 {2} -i 1 -n "LEGO FRIENDS VETERINARY CLINIC" -b "Lego" -e 5702017115160 -p "ExemplePrompt.txt" -s "ExempleRequest.txt" --model "gpt-3.5-turbo-0613"
    Get the pictures and text of the article using as prompt: ExemplePrompt.txt, as picture search: ExempleRequest.txt and as llm gpt-3.5-turbo-0613

    2  | py3 {3} -i 3 -n "Super Drum" -m 2 -pictnum 5 -v -o "C:\\Users\\Me\\ScriptResultHere" -s "C:\\Folder1\\Search.txt"
    Get 5 pictures of Super Drum in C:\\Users\\Me\\ScriptResultHere\\Products\\3\\img using Search.txt and the script is verbose.

    /!\\ If you don't use the brand, Name or EAN13 in your prompt or search files, they aren't required by the script. But ID is required /!\\

If you want more documentation, see the README.md and the Github:https://github.com/4Noy/Automatic-Product-Completion

        """.format(sys.argv[0], __author__, sys.argv[0], sys.argv[0])
parser = optparse.OptionParser(usage = __doc__, version=__version__, add_help_option = False)

parser.add_option("-h", "--help", dest="help", action="store_true", default=False, help="Show Help Message")
parser.add_option("-n", "--name", dest="productName", type="string", help="Set Product Name")
parser.add_option("-b", "--brand", dest="productBrand", type="string", help="Set Product Brand")
parser.add_option("-e", "--EAN", dest="productEAN13", type="string", help="Set Product EAN13")
parser.add_option("-i", "--ID", dest="productID", type="string", help= "Set Product ID")
parser.add_option("-m", "--mode", dest="toolMode", type="string", default="111", help="Set the Tool mode, must an existing mode")
parser.add_option("-p", "--prompt", dest="promptFile", type="string", help="Set the Prompt File")
parser.add_option("-s", "--search", dest="searchFile", type="string", help="Set the search file")
parser.add_option("-o", "--output", dest="outputDirectory", type="string", default=os.getcwd(), help="Customize the Directory Output")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Activate Verbose Mode")
parser.add_option("--pictnum", dest="picturesNumber", type="int", default=5, help="Configure Picture Number, DEFAULT : 3")
parser.add_option("--model", dest="openAIModel", type="string", help="Configure Open AI LLM, DEFAULT : gpt-3.5-turbo")
parser.add_option("--language", dest="language", type="string", help="Set the search file")
parser.add_option("--GSP", dest="GSP", action="store_true", default=False, help="Get the price only with google shopping")
parser.add_option("--config", dest="modifyConfigFile", action="store_true", default=False, help="Set the search file")

#===================================================================================================



# 2 - Setting Up Global Variables
#===================================================================================================
(options, args) = parser.parse_args()

if options.modifyConfigFile or corruptedConfig:
    SetupConfig(False)
    exit(0)

if options.help:
    print(__doc__)
    exit(0)

productID = options.productID
productName = options.productName
productBrand = options.productBrand
productEAN13 = options.productEAN13

if options.promptFile is None:
    promptFile = defaultPrompt
else:
    promptFile = options.promptFile

if options.searchFile is None:
    searchFile = defaultSearch
else:
    searchFile = options.searchFile
picturesNumber = options.picturesNumber
toolMode = options.toolMode
outputDirectory = options.outputDirectory
if options.openAIModel is None:
    openAIModel = defaultModel
else:
    openAIModel = options.openAIModel
if options.language is None:
    language = defaultLanguage
else:
    language = options.language
verbose = options.verbose
GSP = options.GSP

warningNumber = 0



IsOnMainResultPage = False

changingDirectory = False
askingChatGPT = False

originalPath = os.getcwd()

#===================================================================================================



# 3 - PRINT METHODS
#===================================================================================================
def PrintWarningMessage(message):
    """
    DOCUMENTATION
        Function : PrintWarningMessage
        Description : Print a warning message
        Input : 
            message : The message to print
        Output :
            None
    """
    global warningNumber
    PrintVerbose("| Warning : " + message + " |")
    warningNumber += 1


def ErrorMessage(message:str, exeption = ""):
    """
    DOCUMENTATION
        Function : ErrorMessage
        Description : Print an error message and exit the script
        Input :
            message : The message to print
        Output :
            None
    """
    print("====SCRIPT ERROR====\nMESSAGE : " + message + "\n====================")
    exit(0)


def MultipleErrorMesssages(messages:str, exeption = ""):
    """
    DOCUMENTATION
        Function : MultipleErrorMesssages
        Description : Print multiple error messages and exit the script
        Input :
            messages : The list of messages to print
        Output :
            None
    """
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
    """
    DOCUMENTATION
        Function : PrintVerbose
        Description : Print the message if the verbose mode is activated
        Input :
            message : The message to print
        Output :
            None
    """
    if verbose:
        print(message)

#===================================================================================================



# 4 - Various Utilities
#===================================================================================================
def GetArgVariable(variable, variableName):
    """
    DOCUMENTATION
        Function : GetArgVariable
        Description : Get the variable from the arguments
        Input :
            variable : The variable to get
            variableName : The name of the variable
        Output :
            The variable
    """
    if variable == None:
        ErrorMessage("Variable \"{}\" Used Not Set".format(variableName))
    else:
        return variable

def CleanName(name):
    """
    DOCUMENTATION
        Function : CleanName
        Description : Clean the name to avoid errors
        Input :
            name : The name to clean
        Output :
            The cleaned name
    """
    #replace all non-ascii characters by ascii characters
    name = unidecode.unidecode(name)
    #replace all special characters by _
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name



def ShortLinks(link):
    """
    DOCUMENTATION
        Function : ShortLinks
        Description : Short the link to 35 characters
        Input :
            link : The link to short
        Output :
            The shorted link
    """
    if len(link) > 66:
        return link[:63] + "..."
    else:
        return link


def SaveInLog(message):
    """
    DOCUMENTATION
        Function : SaveInLog
        Description : Save the message in the log file  
        Input :
            message : The message to save
        Output :
            None
    """
    #verify if the log file exist
    if not os.path.isfile(originalPath + "/log.txt"):
        with open(originalPath + "/log.txt", "w") as f:
            f.write("Log File\n\n")
    #write the message in the log file
    with open(originalPath + "/log.txt", "a") as f:
        f.write(message + "\n")


def CleanPrices(prices):
    """
    DOCUMENTATION
        Function : CleanPrices
        Description : Clean the prices list, verify if the prices are all approximately in the same magnitude delete otherwises
        Input :
            prices : A list of prices
        Output :    
            prices : A list of prices
    """
    if len(prices) > 1:
        # Sort the prices in ascending order
        sorted_prices = sorted([p for (_, p) in prices])
        # Calculate the first quartile (Q1) and third quartile (Q3)
        q1 = sorted_prices[len(sorted_prices) // 4]
        q3 = sorted_prices[(3 * len(sorted_prices)) // 4]
        # Calculate the interquartile range (IQR)
        iqr = q3 - q1
        # Set the threshold range for outlier detection
        threshold = 1.5 * iqr
        # Filter out prices outside the threshold range
        prices = [(seller, p) for (seller, p) in prices if abs(p - q1) <= threshold and abs(p - q3) <= threshold]
    if len(prices) < 3:
        PrintWarningMessage("Be Careful, Under 3 princes were found, the price may be wrong")
    return prices


def GetParts(chatGPTReply:str):
    """
    DOCUMENTATION
        Function : GetParts
        Description : Split the chatGPTReply in parts
        Input :
            chatGPTReply : A string containing the chat GPT Reply to split
        Output :
            parts : A list of string containing the parts
    """
    #split the parts with "Partie thing.. :" deleting : too
    parts = re.split(r'Partie\s*\d+\s*:', chatGPTReply)
    parts = [part.strip() for part in parts if part.strip()]

    #If the is all parts in one partn try to split with Part X : instead of Partie X :
    if len(parts) == 1:
        parts = re.split(r'Part\s*\d+\s*:', chatGPTReply)
        parts = [part.strip() for part in parts if part.strip()]

    return parts

def GetUrl(url, browser, recaptchaSolver):
    """
    DOCUMENTATION
        Function : GetUrl
        Description : Get the url with the browser
        Input :
            url : The url to get
            browser : The browser to use
        Output :
            The url
    """
    global lowestWaitingTime

    browser.get(url)

    time.sleep(lowestWaitingTime)

    if "/sorry/" in browser.current_url:
        PrintVerbose("Google Captcha, trying to solve it...")
        i = 0
        while "/sorry/" in browser.current_url and i < 10:
            #try:
            browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]').click()
            time.sleep(0.5)
            browser.find_element(By.XPATH, '//iframe[@title="Solve the challenge"]').click()
            """ except:
                PrintWarningMessage("Error while solving the captcha, trying again...")"""
            time.sleep(5000)
            i += 1
        if i == 10:
            ErrorMessage("Error while solving the captcha, stopping the program")

    return browser.current_url



def CreateProductDir():
    """
    DOCUMENTATION
        Function : CreateProductDir
        Description : Move to the product path
        Input :
            None
        Output :
            None
    """
    global originalPath
    global changingDirectory

    changingDirectory = True
    try:
        if not os.path.isdir(outputDirectory+"/Products/") :
            PrintVerbose("Creating Directory : Products/")
            os.mkdir(outputDirectory+'/Products/')
    except:
        pass

    os.chdir(outputDirectory + "/Products")

    try:
        if not os.path.isdir(GetArgVariable(str(productID), "Product ID") + "/"):
            PrintVerbose("Creating Directory : Products/productID")
            os.mkdir(str(productID) + "/")
    except:
        pass
    os.chdir(outputDirectory + "/Products/" + str(productID) + "/")

    os.chdir(originalPath)
    changingDirectory = False


def SaveData(fileName:str ,data, mode = "wb", moveToProductIDDirectory = True, encoding = ""):
    """
    DOCUMENTATION
        Function : SaveData
        Description : Save the data in the file
        Input :
            fileName : The name of the file to save the data in
            data : The data to save
            mode : The mode to open the file in
        Output :
            None
    """
    global changingDirectory
    global productID
    global originalPath

    CreateProductDir()

    changingDirectory = True

    os.chdir(outputDirectory + "/Products/" + str(productID) + "/")

    if os.path.isfile(fileName):
        os.remove(fileName)
    
    if encoding == "":
        with open(fileName, mode) as f:
            f.write(data)
    else:
        with open(fileName, mode, encoding=encoding) as f:
            f.write(data)
    os.chdir(originalPath)
    changingDirectory = False

    

def IntegrateElementsInText(text):
    """
    DOCUMENTATION
        Function : IntegrateElementsInText
        Description : Integrate the product elements in the text
        Input :
            text : The text to integrate the elements in
        Output :
            finalPrompt : The text with the elements integrated
    """
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
                    finalPrompt += str(GetArgVariable(productEAN13, "Product EAN13"))
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
    

def GetWebPageText(url:str):
    """
    DOCUMENTATION
        Function : GetWebPageText
        Description : Get the text of a web page
        Input :
            url : the url of the web page
        Output :
            title : the title of the web page
            textClean : the text of the web page
    """
    time.sleep(lowestWaitingTime)
    try:
        response = requests.get(url)
    except:
        PrintWarningMessage("The url : " + ShortLinks(url) + " is not valid")
        return "", ""
    try:
        textToClean = BeautifulSoup(response.text, "html.parser").find_all("p")
    except:
        PrintVerbose("No text found for the web page : " + ShortLinks(url))
        textToClean = []
    try:
        title = BeautifulSoup(response.content, "html.parser").find("title").text
    except:
        PrintVerbose("No title found for the web page : " + ShortLinks(url))
        title = ""
    
    
    textClean = ""
    for i in textToClean:
        if i.text != "":
            textClean += i.text.strip() + " "
    if len(textClean) < 500:
        return title, textClean
    else:
        return title, textClean[:500]


def GetInternetSearchSites(browser, recaptchaSolver):
    """
    DOCUMENTATION
        Function : GetInternetSearchSites
        Description : Get the first 10 results of a google search
        Input :
            browser : the browser used to get the results
        Output :
            sites : a list of the 3 first results urls
    """
    global IsOnMainResultPage
    IsOnMainResultPage = True
    
    
    search = "https://www.google.com/search?q=\"" + str(GetArgVariable(productEAN13, "Product EAN"))+ "\""
    GetUrl(search.replace(" ", "+"), browser, recaptchaSolver)

    #Get all sons of elements in browser.find_elements(By.CLASS_NAME, "yuRUbf"), "yuRUbf" is the class name of the div containing the link to the website
    #Then get the href attribute of the first element in the div
    try:
        sites = [(site.find_element(By.XPATH, ".//*")).get_attribute("href") for site in browser.find_elements(By.CLASS_NAME, "yuRUbf")]    
    except:
        PrintVerbose("Getting Google results Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            sites = [(site.find_element(By.XPATH, ".//*")).get_attribute("href") for site in browser.find_elements(By.CLASS_NAME, "yuRUbf")]
        except:
            ErrorMessage("Getting Google results Error")
    if len(sites) > 3:
        return sites[:3]
    else:
        return sites


def GetPrompt(browser, recaptchaSolver):
    """
    DOCUMENTATION
        Function : GetPrompt
        Description : get the prompt from the prompt file and integrate the product information in it
        Input : 
            browser
        Output : 
            prompt - a string containing the prompt
    """
    try:
        with open(GetArgVariable(promptFile, "Prompt File"), 'r', encoding="utf-8") as f:
            originalPrompt = f.read()
    except FileNotFoundError:
        PrintWarningMessage("Prompt File Not Found, Getting default prompt")
        with open(GetArgVariable(defaultPrompt, "Prompt File"), 'r', encoding="utf-8") as f:
            originalPrompt = f.read()
    except UnicodeDecodeError:
        PrintWarningMessage("Prompt File Not UTF-8 Encoded, Getting default prompt")
        with open(GetArgVariable(defaultPrompt, "Prompt File"), 'r', encoding="utf-8") as f:
            originalPrompt = f.read()
    except Exception as e:
        PrintWarningMessage("Prompt File Error", e, "Getting default prompt")
        with open(GetArgVariable(defaultPrompt, "Prompt File"), 'r', encoding="utf-8") as f:
            originalPrompt = f.read()
    except:
        ErrorMessage("Prompt File Error Getting default prompt")
        with open(GetArgVariable(defaultPrompt, "Prompt File"), 'r', encoding="utf-8") as f:
            originalPrompt = f.read()

    finalPrompt = """Disregard any previous instructions I will give you a question or an instruction Your objective be to answer my question or fulfill my instruction 
My question or instruction is: {Question}
For your reference, today's date is {Date}.

It's possible that the question or instruction, or just a portion of it, requires relevant information from the internet to give a satisfactory answer or complete the task. Therefore, provided below is the necessary information obtained from the internet, which sets the context for addressing the question or fulfilling the instruction. You will write a comprehensive reply to the given question or instruction. Make sure to cite results using [[NUMBER](URL)] notation after the reference. If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject:
\"\"\"
    """.format(Question = IntegrateElementsInText(originalPrompt), Date = time.strftime("%Y-%m-%dT%H:%M:%S%z"))

    sites = GetInternetSearchSites(browser, recaptchaSolver)
    if len(sites) == 0:
        PrintWarningMessage("No Google Results Found")
    elif len(sites) < 3:
        for i in range(len(sites)):
            (title, content) = GetWebPageText(sites[i])
            finalPrompt += "NUMBER:{number}\nURL: {url}\nTITLE: {title}\nCONTENT : {content}\n\n""".format(number = i+1, url = sites[i], title = title, content = content)
    else:
        for i in range(3):
            (title, content) = GetWebPageText(sites[i])
            finalPrompt += "NUMBER:{number}\nURL: {url}\nTITLE: {title}\nCONTENT : {content}\n\n""".format(number = i+1, url = sites[i], title = title, content = content)

    finalPrompt += """\"\"\"
    
To complete this task, you should:
1. Conduct research on the product and its brand to identify its unique selling points and key features.
2. Use language that is persuasive and engaging, while also being accurate and informative.
3. Select appropriate categories for the product based on its characteristics and intended audience, taking care to avoid generalizations or misrepresentations.
4. Write your response in {}, and ensure that it is free of errors in grammar and spelling.

Please note that you should not cite any external resources or websites in your response, and should instead rely on your own knowledge and research.

Each Part will start like this:
Part [number]: the text""".format(language)
    return finalPrompt.strip()


def InitGoogle():
    """
    DOCUMENTATION
        Function : InitGoogle
        Description : Initialize Google Search Engine
        Input :
            None
        Output : 
            None
    """
    #ua = "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
    ua= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    options = Options()
    #options.add_argument("--headless")
    options.add_argument(f'--user-agent={ua}')
    options.add_argument('--no-sandbox')
    #options.add_argument("--disable-extensions")
    options.add_extension("captchaSolver.crx")

    service = Service(seleniumSearchEngineDriverPath)
    browser = webdriver.Chrome(service=service, options=options)
    search_url = f"https://www.google.com/"
    
    recaptchaSolver = RecaptchaSolver(driver=browser)

    # open browser and begin search
    GetUrl(search_url, browser, recaptchaSolver)

    # wait till the web response is received
    time.sleep(lowestWaitingTime)

    #if not received, then try again
    try:
        element = browser.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[1]")
    except:
        PrintVerbose("Google Consent Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            element = browser.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[1]")
        except:
            ErrorMessage("Google Consent Error")
    element.click()

    return browser, recaptchaSolver


def AskChatGPTResult(prompt:str):
    """
    DOCUMENTATION
        Function : AskChatGPTResult
        Description : Ask the chat GPT model for a result
        Input :
            prompt - The prompt to send to the model
        Output :
            None
    """
    """
    if len(prompt) > 2048:
        enter = ""
        while enter != "yes" and enter != "no":
            enter =input("Prompt is {} long, are you sure you want to continue? [yes][no]".format(len(prompt)))
        if enter == "no":
            ErrorMessage("Prompt too long, exiting...")
    """
    global openAIModel
    global askingChatGPT
    global lock
    #Verify if the model is a valid chat model
    if not is_chat_model(openAIModel) :
        ErrorMessage("Model \"{}\" is not a valid chat model".format(openAIModel))

    PrintVerbose("Trying to get access to Chat GPT...")
    promptToSend = [{"role" : "user", "content": prompt}]
    while not lock.acquire(blocking=False):
        time.sleep(0.2)
    PrintVerbose("Asking Chat GPT...")
    try:
        while askingChatGPT:
            time.sleep(0.1)
        askingChatGPT = True
        chat = openai.ChatCompletion.create(
                    model=openAIModel, messages=promptToSend, n=1, stop=None, temperature=0.9
                )
        askingChatGPT = False
    finally:
        lock.release()
    #Get the number of remaining tokens
    PrintVerbose("Used Input Token : " + str(chat["usage"]["prompt_tokens"]) +\
                   "\nUsed Output Token : " +str(chat["usage"]["completion_tokens"]) +\
                  "\nTotal Token Used : " +str(chat["usage"]["total_tokens"]) + \
                    "\nTotal Cost : $" + str(chat["usage"]["prompt_tokens"] * 0.0000015 + \
                                             chat["usage"]["completion_tokens"] * 0.000002))

    #Verify the finish reason
    if chat["choices"][0]["finish_reason"] == "incomplete":
        PrintWarningMessage("Chat GPT Request Incomplete")
    elif chat["choices"][0]["finish_reason"] == "length":
        PrintWarningMessage("Chat GPT Request Length")
    elif chat["choices"][0]["finish_reason"] == "timeout":
        PrintWarningMessage("Chat GPT Request Timeout")
    elif chat["choices"][0]["finish_reason"] == "error":
        PrintWarningMessage("Chat GPT Request Error")

    reply = chat['choices'][0]['message']['content']
    return reply


def GetPriceFromSimpleSearch(browser, recaptchaSolver, search):
    """
    DOCUMENTATION
        Function : GetPriceFromSimpleSearch
        Description : Get the price of the product from a simple google search
        Input :
            browser - the browser to use
            search : The search
        Output :
            the price of the product
    """
    global IsOnMainResultPage
    PrintVerbose("Getting Price from Google Search...")
    if not IsOnMainResultPage:
        search = "https://www.google.com/search?q=" + search 
        GetUrl(search.replace(" ", "+"), browser, recaptchaSolver)
        IsOnMainResultPage = True
        time.sleep(lowestWaitingTime)
    

    classNameOfFooterInGoogleSearch = "fG8Fp"
    try:
        footers = browser.find_elements(By.CLASS_NAME, classNameOfFooterInGoogleSearch)
    except:
        PrintVerbose("Getting Price Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            footers = browser.fin(By.CLASS_NAME, classNameOfFooterInGoogleSearch)
        except:
            ErrorMessage("Getting Price Error")
    

    if footers == []:
        PrintWarningMessage("No Price Found from Simple Search")

    #Get the sons of the footer
    #Get the price in footer sons
    prices = []
    for footer in footers:
        for son in footer.find_elements(By.XPATH, ".//*"):
            #look if son.text contain €
            if "€" in son.text:
                #Get only the price
                price = son.text.replace("€", "").replace(" ", "").replace(",", ".")
                try:
                    prices.append(("", float(price)))
                except:
                    PrintWarningMessage("Price {} is not a valid price".format(str(price)))
    return prices


def GetPricesFromGoogleShopping(browser, recaptchaSolver, search):
    """
    DOCUMENTATION
        Function : GetPricesFromGoogleShopping
        Description : Get the prices of the product from google shopping
        Input :
            browser : The browser to use
            search : The search
        Output :
            prices : The prices of the product
    """
    global IsOnMainResultPage
    PrintVerbose("Getting Price from Google Shopping...")

    if not IsOnMainResultPage:
        search = "https://www.google.com/search?q=" + search
        GetUrl(search.replace(" ", "+"), browser, recaptchaSolver)
        IsOnMainResultPage = True
        time.sleep(lowestWaitingTime)

    topButtonClass = "zItAnd"

    try:
        buttons = browser.find_elements(By.CLASS_NAME, topButtonClass)
    except:
        PrintVerbose("Getting Shopping button Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            buttons = browser.fin(By.CLASS_NAME, topButtonClass)
        except:
            ErrorMessage("Getting Shopping button Error")
    ShoppingButtonFinded = False
    for button in buttons:
        if "Shopping" in button.text:
            button.click()
            ShoppingButtonFinded = True
            break
    if not ShoppingButtonFinded:
        PrintWarningMessage("No Shopping Button Found")
        return []
    else:
        time.sleep(lowestWaitingTime)
        try:
            link = browser.find_element(By.XPATH, "/html/body/div[6]/div/div[4]/div[4]/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/a").get_attribute("href")
        except:
            PrintVerbose("Getting Shopping Product Link Error, Trying Again...")
            time.sleep(highestWaitingTime)
            try:
                link = browser.find_element(By.XPATH, "/html/body/div[6]/div/div[4]/div[4]/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/a").get_attribute("href")
            except:
                PrintWarningMessage("Getting Shopping Product Link Error")
                return []
        GetUrl(link, browser, recaptchaSolver)
        time.sleep(lowestWaitingTime)
        try:
            prices = browser.find_elements(By.CLASS_NAME, "g9WBQb")
        except:
            PrintVerbose("Getting Shopping Product Price Error, Trying Again...")
            time.sleep(highestWaitingTime)
            try:
                prices = browser.find_elements(By.CLASS_NAME, "g9WBQb")
            except:
                ErrorMessage("Getting Shopping Product Price Error")
        #delete poster price to not have duplicate
        filtredPrices = []
        for price in prices:
            #Verify if the price is in the table and add the name of the seller
            if price.find_element(By.XPATH, "..").get_attribute("class") == "SH30Lb":
                filtredPrices.append((price.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(By.XPATH, "td[1]/div[1]/a").text, price))
        #Get the price of the product
        finalPrices = []
        for (seller, price) in filtredPrices:
            try:
                finalPrices.append((seller, float(price.text.replace("€", "").replace(" ", "").replace(",", "."))))
            except:
                PrintVerbose("Error while getting {} price".format(seller))
        return finalPrices
    
def GetRecommendedPrice(price):
    """
    DOCUMENTATION
        Function : GetRecommendedPrice
        Description : Get the recommended price of the product
        Input :
            price : The price of the product
        Output :
            The recommended price of the product
    """
    price *= 1
    if price - int(price) <= 0.5:
        return int(price) + 0.5
    else:
        return int(price) +0.9

#===================================================================================================



# 5 - Main Functions
#===================================================================================================


def GetPrice(browser, recaptchaSolver):
    """
    DOCUMENTATION
        Function : GetPrice
        Description : Get the price of the product
        Input :
            browser : The browser to use
        Output :
            None

    """
    global movedToProductIDDirectory
    global yourEnterprisePrice
    global GSP
    CreateProductDir()

    with open(searchFile, "r") as f:
        search = IntegrateElementsInText(f.read())

    if GSP:
        prices = GetPricesFromGoogleShopping(browser, recaptchaSolver, search)
    else:
        prices = GetPriceFromSimpleSearch(browser, recaptchaSolver, search)
        prices += GetPricesFromGoogleShopping(browser, recaptchaSolver, search)

    if prices == []:
        ErrorMessage("No Price Found")
    prices = sorted(prices, key=lambda x: x[1])
    prices = CleanPrices(prices)
    s = 0
    yourEnterprisePrice = -1
    for (seller,price) in prices:
        s += price
        if enterpriseName.replace(" ", "").lower() in seller.replace(" ", "").lower():
            yourEnterprisePrice = price
    
    #get the position of yourEnterprisePrice
    if yourEnterprisePrice != -1:
        for i in range(len(prices)):
            if prices[i][1] == yourEnterprisePrice:
                yourEnterprisePricePosition = i
                break
        PrintVerbose("{} Price is the lowest price".format(enterpriseName) if yourEnterprisePricePosition == 0 else "Your Enterprise Price is the {}th lowest price".format(yourEnterprisePricePosition+1))
    else:
        PrintVerbose("{} Price Not Found".format(enterpriseName)) 
    lowestPrice = prices[0][1]
    highestPrice = prices[-1][1]
    average = s/len(prices)
    finalPrice = GetRecommendedPrice(average)
    stringPrices = ""
    emptyNames = 0
    for i in range(len(prices)):
        if prices[i][0] != "":
            stringPrices += "{} - {} : {}\n".format(i+1 - emptyNames, prices[i][0], prices[i][1])
        else:
            emptyNames += 1
    lastPath = os.getcwd()
    SaveData("price.txt", \
             "Recomanded Price : {finalPrice}\n\nAverage Price : {average}\nLowest Price : {lowestPrice}\nHighest Price : {highestPrice}\n\n{VendorAndPrice}"\
                .format(finalPrice=finalPrice, lowestPrice=lowestPrice, highestPrice = highestPrice, VendorAndPrice=stringPrices, average=average), "w", encoding="utf-8")


def GenerateAndSavePictures(browser, recaptchaSolver, cleanName):
    """
    DOCUMENTATION
        Function : GenerateAndSavePictures
        Description : Generate and save the pictures of the product
        Input :
            browser : The browser to use
        Output :
            None
    """
    PrintVerbose("Getting Images from Google Shopping...")
    CreateProductDir()
    global IsOnMainResultPage
    global searchFile
    global originalPath
    global changingDirectory
    count = 0
    

    changingDirectory = True

    productIDPath = os.getcwd()
    if not os.path.isdir("Products/" + productID + "/" +"img/"):
        os.chdir("Products/" + productID + "/")
        os.mkdir("img/")
        PrintVerbose("Created img/ directory")
    os.chdir(originalPath)

    changingDirectory = False


    with open(searchFile, "r") as f:
        sentenceSearch = IntegrateElementsInText(f.read()).replace("\n", "+").replace(" ", "+")

    if not IsOnMainResultPage:
        search = "https://www.google.com/search?q=" + sentenceSearch
        GetUrl(search.replace(" ", "+"), browser, recaptchaSolver)
        IsOnMainResultPage = True
        time.sleep(lowestWaitingTime)

    topButtonClass = "zItAnd"
    try:
        buttons = browser.find_elements(By.CLASS_NAME, topButtonClass)
    except:
        PrintVerbose("Getting Shopping button Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            buttons = browser.fin(By.CLASS_NAME, topButtonClass)
        except:
            ErrorMessage("Getting Shopping button Error")
    ShoppingButtonFinded = False
    for button in buttons:
        if "Shopping" in button.text:
            button.click()
            ShoppingButtonFinded = True
            break

    if not ShoppingButtonFinded:
        PrintWarningMessage("No Shopping Button Found")
    else:
        time.sleep(lowestWaitingTime)
        try:
            link = browser.find_element(By.XPATH, "/html/body/div[6]/div/div[4]/div[4]/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/a").get_attribute("href")
            do = True
        except:
            PrintVerbose("Getting Shopping Product Link Error, Trying Again...")
            time.sleep(highestWaitingTime)
            try:
                link = browser.find_element(By.XPATH, "/html/body/div[6]/div/div[4]/div[4]/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/a").get_attribute("href")
                do = True
            except:
                PrintWarningMessage("Getting Shopping Product Link Error")
                do = False
        if do :
            GetUrl(link, browser, recaptchaSolver)
            classImgOnGoogleShopping = "Xkiaqc"
            time.sleep(lowestWaitingTimeForPictures)
            try:
                dadImages_url = browser.find_elements(By.CLASS_NAME, classImgOnGoogleShopping)
            except:
                PrintVerbose("Getting Images on Google Shopping Error, Trying Again...")
                time.sleep(highestWaitingTime)
                try:
                    dadImages_url = browser.find_elements(By.CLASS_NAME, classImgOnGoogleShopping)
                except:
                    PrintWarningMessage("Getting Images on Google Shopping Error")
                    return
            for dadImage_url in dadImages_url:
                #Get src of the first son of dadImage_url
                image_url = dadImage_url.find_element(By.XPATH, "./*").get_attribute("src")
                try:
                    reponse = requests.get(image_url)
                    time.sleep(lowestWaitingTimeForPictures)
                    if reponse.status_code == 200:
                        
                        SaveData(f"img/image-{count+1}_{cleanName}.idk", reponse.content, moveToProductIDDirectory=False)
                        im = Image.open(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk").convert("RGB")
                        im.save(f"Products/{productID}/img/image-{count+1}_{cleanName}.jpg", "jpeg")
                        #delete the .idk file
                        os.remove(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk")
                        count += 1
                    else:
                        PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
                except:
                    PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
                    time.sleep(highestWaitingTimeForPictures)
                    try:
                        reponse = requests.get(image_url)
                        if reponse.status_code == 200:
                            SaveData(f"img/image-{count+1}_{cleanName}.idk", reponse.content, moveToProductIDDirectory=False)
                            im = Image.open(f"img/image-{count+1}_{cleanName}.idk").convert("RGB")
                            im.save(f"Products/{productID}/img/image-{count+1}_{cleanName}.jpg", "jpeg")
                            #delete the .idk file
                            os.remove(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk")
                            count += 1
                        else:
                            PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
                    except:
                        PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))

    PrintVerbose("Getting Pictures...")
    global picturesNumber
    
    IsOnMainResultPage = False

    if picturesNumber <= 0:
        PrintWarningMessage("Picture Number <= 0, No Images will be downloaded")
        return

    #Get Right Format for google search
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={sentenceSearch}"

    # begin search
    GetUrl(search_url, browser, recaptchaSolver)
    time.sleep(lowestWaitingTime)
    #if not loaded, then try again
    try:
        images = browser.find_elements(By.CLASS_NAME, 'rg_i') 
    except:
        PrintVerbose("Google Images Request Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            images = browser.find_elements(By.CLASS_NAME, 'rg_i') 
        except:
            ErrorMessage("Google Images Request Error")
    
    #Get images
    for image in images:
        #Get images source url
        image.click()
        # wait for the image to popup
        time.sleep(lowestWaitingTimeForPictures)
        try:
            element = browser.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]")
            if element.get_attribute("src").startswith("data:image/"):
                time.sleep(lowestWaitingTimeForPictures)
                raise Exception("Incorrect Img")
        except:
            PrintVerbose("Getting Image Link N°{} Error, Trying Again...".format(str(count+1)))
            time.sleep(highestWaitingTimeForPictures)
            try:
                element = browser.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]")
                if element.get_attribute("src").startswith("data:image/"):
                    raise Exception("You must wait more between each image if you want to get more images")
            except Exception as e:
                PrintWarningMessage("Error : {} , Cannot Get Image Link N°".format(ShortLinks(str(e))) + str(count+1))
                continue
            except:
                PrintWarningMessage("Cannot Get Image Link N°" + str(count+1))
                continue
        image_url = element.get_attribute("src")
        # write image to file
        try:
            reponse = requests.get(image_url)
            time.sleep(lowestWaitingTimeForPictures)
            if reponse.status_code == 200:
                SaveData(f"img/image-{count+1}_{cleanName}.idk", reponse.content, moveToProductIDDirectory=False)
                im = Image.open(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk").convert("RGB")
                im.save(f"Products/{productID}/img/image-{count+1}_{cleanName}.jpg", "jpeg")
                #delete the .idk file
                os.remove(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk")
                count += 1
            else:
                PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
        except:
            PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
            time.sleep(highestWaitingTimeForPictures)
            try:
                reponse = requests.get(image_url)
                if reponse.status_code == 200:
                    SaveData(f"img/image-{count+1}_{cleanName}.idk", reponse.content, moveToProductIDDirectory=False)
                    im = Image.open(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk").convert("RGB")
                    im.save(f"Products/{productID}/img/image-{count+1}_{cleanName}.jpg", "jpeg")
                    #delete the .idk file
                    os.remove(f"Products/{productID}/img/image-{count+1}_{cleanName}.idk")
                    count += 1
                else:
                    PrintWarningMessage("Cannot Get Image N°{} from URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
            except:
                PrintWarningMessage("Error While Requesting Image N°{} URL - url:".format(str(count+1)) + ShortLinks(str(image_url)))
        #Stop
        if count == picturesNumber:
            break
    
    if count < picturesNumber:
        PrintWarningMessage("Only {} Images were downloaded".format(str(count)))
    else:
        PrintVerbose("All {} Images were downloaded".format(str(count)))
    



def GenerateAndSaveText(browser, recaptchaSolver):
    """
    DOCUMENTATION
        Function : GenerateAndSaveText
        Description : Generate and save the text of the product
        Input :
            browser : The browser to use
        Output :
            None
    """
    PrintVerbose("Generating Text...")
    prompt = GetPrompt(browser, recaptchaSolver)


    if prompt.strip() == "":
        ErrorMessage("Empty Prompt?", "Prompt Error")

    
    chatGPTReply = AskChatGPTResult(prompt)
    
    if chatGPTReply.strip() == "":
        ErrorMessage("Empty OpenAI Response", "Open AI Error")
    
    try:
        parts = GetParts(chatGPTReply)
    except:
        ErrorMessage("Error while spliting Text", "Spliting Part Error")

    if parts == [] or parts == [""]:
        ErrorMessage("Error, Empty Parts", "Spliting Part Error")

    CreateProductDir()

    for i in range(len(parts)):
        SaveData("text_"+str(i+1)+".txt", parts[i], "w", encoding="utf-8")


def Main():
    """
    DOCUMENTATION
        Function : Main
        Description : Main Function
        Input :
            None
        Output :
            None
    """
    global toolMode
    global warningNumber
    global isWebSiteUsage
    global lowestWaitingTime

    if not isWebSiteUsage and len(sys.argv) < 3:
        print(__doc__)
        exit(0)

    if productID == None:
        ErrorMessage("Error, Product ID must be specified")
    if productBrand == None:
        defaultPrompt = defaultPromptNoBrand

    if toolMode == "000":
        ErrorMessage("This little tool is useless if you don't use it, be logical...")

    #mode to execute different functions
    if len(toolMode) != 3:
        ErrorMessage("Error, Tool Mode must be 3 digits long")
    c = 0
    for i in toolMode:
        if i != "0" and i != "1":
            ErrorMessage("Error, Tool Mode must be only digits")
        if i == "1":
            c+=1
    if c > 1:

        PrintVerbose("Current Path : " + originalPath)

        script_Path = os.getcwd() + "/Automatic_Product_Completion.py"
        args = ["-v", "-i", str(productID), "-n", str(productName), "-b", str(productBrand), "-e", str(productEAN13), "-m"]
        processes = []
        if toolMode[0] == "1":
            processes.append(subprocess.Popen(["python", script_Path] + args + ["100"]))
            time.sleep(0.002)
        if toolMode[1] == "1":
            processes.append(subprocess.Popen(["python", script_Path] + args + ["010"]))
            time.sleep(0.002)
        if toolMode[2] == "1":
            processes.append(subprocess.Popen(["python", script_Path] + args + ["001"]))
        
        for process in processes:
            process.wait()
        print("Main Program Finished with {} warning".format(warningNumber))
    else:
        PrintVerbose("Browser Initialized")
        browser, recaptchaSolver = InitGoogle()

        cleanName = CleanName(productName)

        if toolMode[0] == "1":
            GenerateAndSaveText(browser, recaptchaSolver)
            browser.close()
            PrintVerbose("Program DESCRIPTIONS Finished with {} warning".format(warningNumber))
        elif toolMode[1] == "1":
            GenerateAndSavePictures(browser, recaptchaSolver, cleanName)
            browser.close()
            PrintVerbose("Program PICTURES Finished with {} warning".format(warningNumber))
        elif toolMode[2] == "1":
            GetPrice(browser, recaptchaSolver)
            browser.close()
            PrintVerbose("Program PRICES Finished with {} warning".format(warningNumber))
    
        
    

#===================================================================================================




if __name__ == '__main__':
    Main()