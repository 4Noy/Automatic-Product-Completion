#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Noy."
__version__ = "0.1"
__credits__ = ["Mev"]


import sys, openai, re, os, time, optparse, random, requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup



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
Welcome to the Automatic Product Completion Tool installation.
This tool is a python script to automate Product Creation and Completion.
With this initial setup, you will add :
    - your OpenAI API key
    - your Selenium Web Driver path
    - your default language
    - your default chat model
    - your default prompt file
    - your default search file
"""

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
|   --picnum <Number>              |  Specify picture number, DEFAULT : 3                |
+                                  +                                                     +
|   --model <Model Name>           |  Specify Open AI LLM chat, DEFAULT : gpt-3.5-turbo  |
+                                  +                                                     +
|   --language <Language>          |  Change chat language response                      |
+                                  +                                                     +
|   --GSP                          |  Get the price only with google shopping            |
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

    /!\\ If you don't use the brand or Name in your prompt or search files, they aren't required by the script. But EAN13 and ID are required /!\\

If you want more documentation, see the README.md and the Github:https://github.com/4Noy/Automatic-Product-Completion

        """.format(sys.argv[0], __author__, sys.argv[0], sys.argv[0])
parser = optparse.OptionParser(usage = __doc__, version=__version__, add_help_option = False)

parser.add_option("-h", "--help", dest="help", action="store_true", default=False, help="Show Help Message")
parser.add_option("-n", "--name", dest="productName", type="string", help="Set Product Name")
parser.add_option("-b", "--brand", dest="productBrand", type="string", help="Set Product Brand")
parser.add_option("-e", "--EAN", dest="productEAN13", type="int", help="Set Product EAN13, must be a number")
parser.add_option("-i", "--ID", dest="productID", type="int", help= "Set Product ID, must be a number")
parser.add_option("-m", "--mode", dest="toolMode", type="string", default="111", help="Set the Tool mode, must an existing mode")
parser.add_option("-p", "--prompt", dest="promptFile", type="string", help="Set the Prompt File")
parser.add_option("-s", "--search", dest="searchFile", type="string", help="Set the search file")
parser.add_option("-o", "--output", dest="outputDirectory", type="string", default=os.getcwd(), help="Customize the Directory Output")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Activate Verbose Mode")
parser.add_option("--pictnum", dest="picturesNumber", type="int", default=3, help="Configure Picture Number, DEFAULT : 3")
parser.add_option("--model", dest="openAIModel", type="string", default="gpt-3.5-turbo", help="Configure Open AI LLM, DEFAULT : gpt-3.5-turbo")
parser.add_option("--language", dest="language", type="string", default="English", help="Set the search file")
parser.add_option("--GSP", dest="GSP", action="store_true", default=False, help="Get the price only with google shopping")

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
verbose = options.verbose
GSP = options.GSP

warningNumber = 0

lowestWaitingTime = 0.5
highestWaitingTime = 1

IsOnMainResultPage = False

movedToProductIDDirectory = False
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
    if len(link) > 35:
        return link[:31] + "..."
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
        seuil = 0.2
        moy = sum(prices) / len(prices)
        prices = [p for p in prices if p >= moy * (1 - seuil) and p <= moy * (1 + seuil)]
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
    return parts


def MoveToProductPath():
    """
    DOCUMENTATION
        Function : MoveToProductPath
        Description : Move to the product path
        Input :
            None
        Output :
            None
    """
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
    if not movedToProductIDDirectory:
        MoveToProductPath()

    if os.path.isfile(fileName):
        os.remove(fileName)
    with open(fileName, mode) as f:
        f.write(data)


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
        Funtion : GetWebPageText
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
        textToClean = BeautifulSoup(response.text, "html.parser").find_all("p")
        title = BeautifulSoup(response.content, "html.parser").find("title").text
    except Exception as e:
        ErrorMessage("WebPage Error", e)
    except:
        ErrorMessage("WebPage Error")
    
    textClean = ""
    for i in textToClean:
        if i.text != "":
            textClean += i.text.strip() + " "
    if len(textClean) < 500:
        return title, textClean
    else:
        return title, textClean[:500]


def GetInternetSearchSites(browser):
    """
    DOCUMENTATION
        Funtion : GetInternetSearchSites
        Description : Get the first 10 results of a google search
        Input :
            browser : the browser used to get the results
        Output :
            sites : a list of the 3 first results urls
    """
    global IsOnMainResultPage
    IsOnMainResultPage = True
    
    
    search = "https://www.google.com/search?q=\"" + str(GetArgVariable(productEAN13, "Product EAN"))+ "\""
    browser.get(search.replace(" ", "+"))
    time.sleep(lowestWaitingTime)

    #Get all sons of elements in browser.find_elements(By.CLASS_NAME, "yuRUbf"), "yuRUbf" is the class name of the div containing the link to the website
    #Then get the href attribute of the first element in the div
    try:
        sites = [(site.find_element(By.XPATH, ".//*")).get_attribute("href") for site in browser.find_elements(By.CLASS_NAME, "yuRUbf")]    
    except:
        PrintWarningMessage("Getting Google results Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            sites = [(site.find_element(By.XPATH, ".//*")).get_attribute("href") for site in browser.find_elements(By.CLASS_NAME, "yuRUbf")]
        except:
            ErrorMessage("Getting Google results Error")
    if len(sites) > 3:
        return sites[:3]
    else:
        return sites


def GetPrompt(browser):
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
        ErrorMessage("Prompt File Not Found")
    except UnicodeDecodeError:
        ErrorMessage("Prompt File Not UTF-8 Encoded")
    except Exception as e:
        ErrorMessage("Prompt File Error", e)
    except:
        ErrorMessage("Prompt File Error")

    finalPrompt = """Disregard any previous instructions.

I will give you a question or an instruction. Your objective is to answer my question or fulfill my instruction.

My question or instruction is: {Question}
For your reference, today's date is {Date}.

It's possible that the question or instruction, or just a portion of it, requires relevant information from the internet to give a satisfactory answer or complete the task. Therefore, provided below is the necessary information obtained from the internet, which sets the context for addressing the question or fulfilling the instruction. You will write a comprehensive reply to the given question or instruction. Make sure to cite results using [[NUMBER](URL)] notation after the reference. If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject:
\"\"\"
    """.format(Question = IntegrateElementsInText(originalPrompt), Date = time.strftime("%Y-%m-%dT%H:%M:%S%z"))

    sites = GetInternetSearchSites(browser)
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

    finalPrompt += "\"\"\"\n\nDoes not cite websites or companies other than the brand\nEach Part will start like this:\nPart [number]: the text\n\nResult in " + language
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
    service = Service(seleniumSearchEngineDriverPath)
    browser = webdriver.Chrome(service=service)
    search_url = f"https://www.google.com/"

    # open browser and begin search
    browser.get(search_url)

    # wait till the web response is received
    time.sleep(lowestWaitingTime)
    #if not received, then try again
    try:
        element = browser.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[1]")
    except:
        PrintWarningMessage("Google Consent Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            element = browser.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[1]")
        except:
            ErrorMessage("Google Consent Error")
    element.click()
    return browser


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
    if len(prompt) > 2048:
        enter = ""
        while enter != "yes" and enter != "no":
            enter =input("Prompt is {} long, are you sure you want to continue? [yes][no]".format(len(prompt)))
        if enter == "no":
            ErrorMessage("Prompt too long, exiting...")

    global openAIModel
    #Verify if the model is a valid chat model
    if not is_chat_model(openAIModel) :
        ErrorMessage("Model \"{}\" is not a valid chat model".format(openAIModel))


    PrintVerbose("Asking Chat GPT...")

    promptToSend = [{"role" : "user", "content": prompt}]
    chat = openai.ChatCompletion.create(
                model=openAIModel, messages=promptToSend
            )

    #Get the number of remaining tokens
    PrintVerbose("Used Input Token : " + str(chat["usage"]["prompt_tokens"]) +  "\nUsed Output Token : " +str(chat["usage"]["completion_tokens"]) + "\nTotal Token Used : " +str(chat["usage"]["total_tokens"]))

    #Verify the finish reason
    if chat["choices"][0]["finish_reason"] == "incomplete":
        PrintWarningMessage("Chat GPT Request Incomplete")
    elif chat["choices"][0]["finish_reason"] == "length":
        PrintWarningMessage("Chat GPT Request Length")
    elif chat["choices"][0]["finish_reason"] == "timeout":
        PrintWarningMessage("Chat GPT Request Timeout")
    elif chat["choices"][0]["finish_reason"] == "error":
        PrintWarningMessage("Chat GPT Request Error")

    reply = chat.choices[0].message.content
    return reply


def GetPriceFromSimpleSearch(browser, search):
    """
    DOCUMENTATION
        Function: GetPriceFromSimpleSearch
        Description: Get the price of the product from a simple google search
        Input :
            browser - the browser to use
            search : The search
        Output :
            the price of the product
    """
    global IsOnMainResultPage
    print("Getting Price from Google Search...")
    if not IsOnMainResultPage:
        search = "https://www.google.com/search?q=\"" + search + "\""
        browser.get(search.replace(" ", "+"))
        IsOnMainResultPage = True
        time.sleep(lowestWaitingTime)

    classNameOfFooterInGoogleSearch = "fG8Fp"
    try:
        footers = browser.find_elements(By.CLASS_NAME, classNameOfFooterInGoogleSearch)
    except:
        PrintWarningMessage("Getting Price Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            footers = browser.fin(By.CLASS_NAME, classNameOfFooterInGoogleSearch)
        except:
            ErrorMessage("Getting Price Error")
    

    if footers == []:
        ErrorMessage("No Price Found")

    #Get the sons of the footer
    #Get the price in footer sons
    prices = []
    for footer in footers:
        for son in footer.find_elements(By.XPATH, ".//*"):
            #look if son.text contain €
            if "€" in son.text:
                #Get only the price
                price = son.text.replace("€", "").replace(" ", "").replace(",", ".")
                prices.append(float(price))
    return prices


def GetPricesFromGoogleShopping(browser, search):
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
    print("Getting Price from Google Shopping...")

    if not IsOnMainResultPage:
        search = "https://www.google.com/search?q=\"" + search + "\""
        browser.get(search.replace(" ", "+"))
        IsOnMainResultPage = True
        time.sleep(lowestWaitingTime)

    topButtonClass = "zItAnd"

    try:
        buttons = browser.find_elements(By.CLASS_NAME, topButtonClass)
    except:
        PrintWarningMessage("Getting Shopping button Error, Trying Again...")
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
            PrintWarningMessage("Getting Shopping Product Link Error, Trying Again...")
            time.sleep(highestWaitingTime)
            try:
                link = browser.find_element(By.XPATH, "/html/body/div[6]/div/div[4]/div[4]/div/div[3]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/a").get_attribute("href")
            except:
                ErrorMessage("Getting Shopping Product Link Error")
        browser.get(link)
        time.sleep(lowestWaitingTime)
        try:
            prices = browser.find_elements(By.CLASS_NAME, "g9WBQb")
        except:
            PrintWarningMessage("Getting Shopping Product Price Error, Trying Again...")
            time.sleep(highestWaitingTime)
            try:
                prices = browser.find_elements(By.CLASS_NAME, "g9WBQb")
            except:
                ErrorMessage("Getting Shopping Product Price Error")
        #delete poster price to not have duplicate
        filtredPrices = []
        for price in prices:
            #get dad of price
            if price.find_element(By.XPATH, "..").get_attribute("class") == "SH30Lb":
                filtredPrices.append(price)
        prices = [float(price.text.replace("€", "").replace(" ", "").replace(",", ".")) for price in filtredPrices]
        return prices
    
            

#===================================================================================================



# 5 - Main Functions
#===================================================================================================


def GetPrice(browser):
    """"
    DOCUMENTATION
        Function : GetPrice
        Description : Get the price of the product
        Input :
            browser : The browser to use
        Output :
            None

    """
    global movedToProductIDDirectory
    global GSP
    MoveToProductPath()
    lastPath = os.getcwd()
    os.chdir(originalPath)
    with open(searchFile, "r") as f:
        search = IntegrateElementsInText(f.read())
    os.chdir(lastPath)

    if GSP:
        prices = GetPricesFromGoogleShopping(browser, search)
    else:
        prices = GetPriceFromSimpleSearch(browser, search)
        prices += GetPricesFromGoogleShopping(browser, search)
    finalPrice = sum(CleanPrices(prices))/len(prices)
    lastPath = os.getcwd()
    os.chdir(originalPath)
    SaveData("Price.txt", str(finalPrice), "w")
    os.chdir(lastPath)


def GenerateAndSavePictures(browser):
    """
    DOCUMENTATION
        Function : GenerateAndSavePictures
        Description : Generate and save the pictures of the product
        Input :
            browser : The browser to use
        Output :
            None
    """
    PrintVerbose("Getting Pictures...")
    global picturesNumber
    global searchFile
    global originalPath
    global IsOnMainResultPage
    IsOnMainResultPage = True

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
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={search}"

    # begin search
    browser.get(search_url)
    time.sleep(lowestWaitingTime)
    #if not loaded, then try again
    try:
        images = browser.find_elements(By.CLASS_NAME, 'rg_i') 
    except:
        PrintWarningMessage("Google Images Request Error, Trying Again...")
        time.sleep(highestWaitingTime)
        try:
            images = browser.find_elements(By.CLASS_NAME, 'rg_i') 
        except:
            ErrorMessage("Google Images Request Error")

    count = 0
    for image in images:
        #Get images source url
        image.click()
        # wait for the image to popup
        time.sleep(lowestWaitingTime)
        try:
            element = browser.find_element(By.XPATH, "/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]")
        except Exception as e:
            PrintWarningMessage("Error : {} , Cannot Get Image N°".format(e) + count)
            continue
        except:
            PrintWarningMessage("Cannot Get Image N°" + count)

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
    

    os.chdir(productIDPath)
    

def GenerateAndSaveText(browser):
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
    try :
        prompt = GetPrompt(browser)
    except:
        ErrorMessage("Error while generating the prompt", "Prompt Error")

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

    MoveToProductPath()

    for i in range(len(parts)):
        SaveData("text_"+str(i+1)+".txt", parts[i], "w")


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
    if len(sys.argv) < 3:
        print(__doc__)
        exit(0)

    if productID == None:
        ErrorMessage("Error, Product ID must be specified")

    if toolMode == "000":
        ErrorMessage("This little tool is useless if you don't use it, be logical...")

    PrintVerbose("Current Path : " + originalPath)
    browser = InitGoogle()
    PrintVerbose("Browser Initialized")
    #mode to execute different functions
    if len(toolMode) != 3:
        ErrorMessage("Error, Tool Mode must be 3 digits long")
    for i in toolMode:
        if i != "0" and i != "1":
            ErrorMessage("Error, Tool Mode must be only digits")
    if toolMode[0] == "1":
        GenerateAndSaveText(browser)
    if toolMode[1] == "1":
        GenerateAndSavePictures(browser)
    if toolMode[2] == "1":
        GetPrice(browser)

    browser.quit()
    print("Progam Finished with {} warning".format(warningNumber))
        
    

#===================================================================================================




if __name__ == '__main__':
    Main()