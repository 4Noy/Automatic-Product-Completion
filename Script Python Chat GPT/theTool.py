#Format : py promptManager.py ProductID ProductName BrandName EAN13 Mode
import sys
import openai
import re
import os
import time 
import requests
import random

#All For Web Request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Write your own prompt and add : {Product}
# for the product Name and add : {Brand}
# for the brand name
promptFile = "prompt Opti.txt"
openai.api_key = "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"
seleniumSearchEngineDriverPath = "C:\selenium browser drivers\chromedriver.exe"

def PrintErrorMessage(message:str, exeption = ""):
    print("====SCRIPT ERROR====\nMESSAGE : " + message + "\n====================")
    raise Exception(exeption)

def PrintMultipleErrorMesssages(messages:str, exeption = ""):
    lengthMessages = len(messages)
    if lengthMessages == 0:
        print("====SCRIPT ERROR====\nNO MESSAGE\n====================")
    elif lengthMessages == 1:
        print("====SCRIPT ERROR====\nMESSAGE : " + messages[0] + "\n====================")
    else:
        print("====SCRIPT ERROR====")
        for i in range(lengthMessages):
            print("MESSAGE N°{} : ".format(i) + messages[i] + "\n====================")

    raise Exception(exeption)

def GetParts(chatGPTReply:str):
    parts = re.split(r'Partie\s*\d+\s*:', chatGPTReply)
    parts = [part.strip() for part in parts if part.strip()]
    return parts

def MoveToProductPath(productID:str, originalPath = os.getcwd()):
    if not os.path.isdir("Products/") :
        print("Création du Dossier /Products/")
        os.mkdir('Products/')
    os.chdir(originalPath + "/Products")

    if not os.path.isdir(productID + "/"):
        print("Création du Dossier /Products/productID")
        os.mkdir(productID + "/")
    os.chdir(originalPath + "/Products/" + productID + "/")

def SaveData(fileName:str ,data, mode = "wb"):
    with open(fileName, mode) as f:
        f.write(data)
            
"""def GetPicturesFromEAN13(EAN13):"""
    

def AskChatGPTResult(prompt:str):
    print("Requesting Chat GPT...")
    promptToSend = [{"role" : "user", "content": prompt}]
    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=promptToSend
            )
    reply = chat.choices[0].message.content
    return reply


def GetPrompt(productName:str, productBrand:str):
    with open(promptFile, 'r', encoding="utf-8") as f:
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
                    finalPrompt += productBrand
                else:
                    finalPrompt += productName
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
    print("Getting Pictures...")

    originalPath = os.getcwd()
    if not os.path.isdir("img/"):
        os.mkdir("img/")
    os.chdir(originalPath + "/img/")

    if nbPictures <= 0:
        #PrintWarningMessage("Number of pictures asked <= 0")
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
            #PrintWarningMessage("Cannot Get Image N°" + count)
            print("Cannot Get Image N°" + str(count))
            continue

        images_url.append(element.get_attribute("src"))

        # write image to file
        try:
            reponse = requests.get(images_url[count])
            if reponse.status_code == 200:
                SaveData(f"image-{count+1}.jpg", reponse.content)
            else:
                #PrintWarningMessage("Cannot Get Image from Url - url:" + str(images_url[count]))
                print("Cannot Get Image N°" + str(count))
                print("Cannot Get Image from Url - url:" + str(images_url[count]))
        except:
            ##PrintWarningMessage("Error While Requesting Image URL - url:" + str(images_url[count]))
            print("Cannot Get Image N°" + str(count))
            print("Error While Requesting Image URL - url:" + str(images_url[count]))

        #Stop
        count += 1
        if count == nbPictures:
            break
    browser.close()


    return images_url
    

def Main():
    errorTab = ["Veuillez Rentrer l'ID du Produit","Veuillez Rentrer un nom de Produit", "Veuillez Rentrer la marque du Produit", "Veuillez Rentrer L'EAN13 du produit", "Veuillez Rentrer le mode"]
    if len(sys.argv) < 5:
        i = len(sys.argv)
        PrintMultipleErrorMesssages(errorTab[i:], "Erreur d'Arguments")
    else:
        originalPath = os.getcwd()
        print("Current Path : " + originalPath)

        #Get all Args
        productID = sys.argv[1]
        productName = sys.argv[2]
        productBrand = sys.argv[3]
        productEAN13 = sys.argv[4]
        mode = sys.argv[5]
        
        try :
            prompt = GetPrompt(productName, productBrand)
        except:
            PrintErrorMessage("Erreur lors de la génération du prompt", "Prompt Error")

        if prompt.strip() == "":
            PrintErrorMessage("Erreur, Prompt Vide", "Prompt Error")

        try:
            chatGPTReply = AskChatGPTResult(prompt)
        except:
            PrintErrorMessage("Erreur Chat GPT, \n\t1 - Vérifiez votre connection Internet\n\t2 - Vérifiez votre votre clé API\n\t3 - Vérifiez votre nombres de requêtes restantes via l'API de Open AI\n\t4 - Vérifiez votre Parre Feux", "Chat GPT Error")

        if chatGPTReply.strip() == "":
            PrintErrorMessage("Erreur, Réponse de Chat GPT Vide", "Chat GPT Error")
        
        try:
            parts = GetParts(chatGPTReply)
        except:
            PrintErrorMessage("Erreur Lors de la séparation des différentes parties du Texte", "Spliting Part Error")

        if parts == [] or parts == [""]:
            PrintErrorMessage("Erreur, parties vides", "Spliting Part Error")

        MoveToProductPath(productID, originalPath)

        for i in range(len(parts)):
            SaveData("part"+str(i+1), parts[i], "w")

        GetPictures(productEAN13, 5)

if __name__ == '__main__':
    Main()