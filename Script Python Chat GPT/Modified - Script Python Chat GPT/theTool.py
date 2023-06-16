#Format : py promptManager.py ProductID ProductName BrandName EAN13 Mode
import sys, openai, re, os, time, optparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""
NEEDS :
openai python package - to install on windows : pip install openai
selenium python package - to install on windows : pip install selenium

"""

# Write your own prompt and add : {Product}
# for the product Name and add : {Brand}
# for the brand name and add : {EAN}
# for the EAN13
promptFile = "prompt Opti.txt"
openai.api_key = "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"

def PrintWarningMessage(message):
    print("| Warning : " + message + " |")

def PrintErrorMessage(message, exeption = ""):
    print("====SCRIPT ERROR====\nMESSAGE : " + message + "\n====================")
    raise Exception(exeption)

def PrintMultipleErrorMesssages(messages, exeption = ""):
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

def GetParts(chatGPTReply):
    parts = re.split(r'Partie\s*\d+\s*:', chatGPTReply)
    parts = [part.strip() for part in parts if part.strip()]
    return parts
            
"""def GetPicturesFromEAN13(EAN13):"""
    

def AskChatGPTResult(prompt):
    print("Requesting Chat GPT...")
    promptToSend = [{"role" : "user", "content": prompt}]
    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=promptToSend
            )
    reply = chat.choices[0].message.content
    return reply


def GetPrompt(productName, productBrand, EAN13):
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
                elif "product" in theWordeuuuu:
                    finalPrompt += productName
                elif "ean" in theWordeuuuu :
                    finalPrompt += EAN13
                else:
                    PrintWarningMessage("Balise : " + "{" + theWordeuuuu + "} Introuvable, Utilisez soit : ")
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

def Main():
    errorTab = ["Veuillez Rentrer l'ID du Produit","Veuillez Rentrer un nom de Produit", "Veuillez Rentrer la marque du Produit", "Veuillez Rentrer L'EAN13 du produit", "Veuillez Rentrer le mode"]
    if len(sys.argv) < 5:
        i = len(sys.argv)
        PrintMultipleErrorMesssages(errorTab[i:], "Erreur d'Arguments")
    else:
        print("Current Path : " + os.getcwd())

        parse = optparse.OptionParser( """Usage: py ./{0} [Options]
 _________________________________________________________________________
|           OPTIONS:			                   Description:			  |
+=========================================================================+
    -n --name <Product Name>       |  Set Product Name                    |
				                   +									  +
    -b --brand <Product Brand>     |  Set Product Brand			          |
				                   +									  +
    -ean --EAN13 <Product EAN13>   |  Set Product EAN13			          |
				                   +									  +
    -id <Product ID>               |  Set Product ID			          |
				                   +									  +
    -m --mode <mode>               |  Set Tool Mode  			          |
                                   +                                      +
    -id <Product ID>               |  Set Product ID			          |
				                   +									  +
    -o --output <Directory>        |  Save the result IN Directory	      |
				                   +									  +
==========================================================================+
    -v --version                   |  SHOW TOOL VERSION  ||
				                   +			         ++
    -e --examples                  |  SHOW TOOL EXAMPLES ||
===========================================================
        """.format(sys.argv[0]))
        parse.add_option

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

        if not os.path.isdir("Products/") :
            print("Création du Dossier /Products/")
            os.mkdir('Products/')
        os.chdir(os.getcwd()+"/Products")

        if not os.path.isdir(productID + "/"):
            print("Création du Dossier /Products/productID")
            os.mkdir(productID + "/")

        for i in range(len(parts)):
            with open(productID + "/""part"+str(i+1), "w") as f:
                f.write(parts[i])
        

if __name__ == '__main__':
    Main()