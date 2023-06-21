#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_from_directory
import subprocess, os
import Automatic_Product_Completion as tool

"""
To run the Website, and with all need from the main script
NEEDS :
Flask (pip install flask)
"""

app = Flask(__name__)
nbRequestChatGPT = 0

@app.route('/')
def index():
    tool.isWebSiteUsage = True
    return render_template('index.html')

@app.route('/product_images/<path:filename>')
def product_images(filename):
    return send_from_directory('Products', filename)

@app.route('/treatments')
def treatments():
    global nbRequestChatGPT
    tool.isWebSiteUsage = True
    try:
        tool.productID = request.args['i']
        tool.productName = request.args['n']
        tool.productBrand = request.args['b']
        tool.productEAN13 = request.args['e']
        tool.toolMode = request.args['m']
    except:
        return "Error, please check your inputs"
    tool.verbose = True
    if request.args['m'] == "":
        tool.toolMode = "111"
        tm = "111"
    else:
        tm = request.args['m']

    # Exécute le script Python et capture la sortie
    
    #result = subprocess.run(['py', '../Automatic_Product_Completion.py', f"-i \"{i}\" -n \"{n}\" -b \"{b}\" -e \"{e}\" -m \"{m}\""], capture_output=True, text=True)

    if request.args['i'] == "1":
        nbRequestChatGPT += 1

    if nbRequestChatGPT > 10 :
        print("Much Request to Chat GPT, must have big cost")

    tool.Main()

    page = """
    <!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Product</title>
<style>
.image-container {
    display: flex;
    flex-wrap: nowrap;
    justify-content: center;
    overflow-x: auto;
}
.image-container img {
    width: auto; /* Pour ajuster la largeur en fonction de la hauteur spécifiée */
    height: 300px; /* Hauteur fixe de 800 pixels */
    margin: 10px;
}
</style>
    <script>
function copyText(id) {
    // Sélectionner le texte à copier (remplacez "texte-a-copier" par l'ID ou la classe de votre élément texte)
    var textToCopy = document.getElementById(id);

    // Créer une zone de texte temporaire
    var tempTextArea = document.createElement("textarea");
    tempTextArea.value = textToCopy.textContent;

    // Ajouter la zone de texte temporaire à la page
    document.body.appendChild(tempTextArea);

    // Sélectionner le texte dans la zone de texte temporaire
    tempTextArea.select();

    // Copier le texte dans le presse-papiers
    document.execCommand("copy");

    // Supprimer la zone de texte temporaire
    document.body.removeChild(tempTextArea);
    }
</script>
  </head>
  <body>"""
    page +=f"""
    <h1>Automatic Product Completion - Product ID : {request.args['i']}</h1>
    """

    if tm[0] == "1": #Descriptions
        page += f"<h2 id=\"texte-a-copier\">Descriptions</h2>"
        descriptionsPath = f"Products/{request.args['i']}"
        descriptionsFiles = os.listdir(descriptionsPath)
        j = 0
        for i in descriptionsFiles:
            j+=1
            if i.startswith("text_"):
                with open(f"{descriptionsPath}/{i}", "r", encoding='utf_8') as f:
                    v = f.read().replace("\n", "<br>")
                    page += f"<button onclick=\"copyText('{j}')\">Copy</button><p id = '{j}' style=\"font-size:14pt;line-height:107%;font-family:Arial, sans-serif;\">{v}</p>"
                page += "<br>"
    if tm[1] == "1": #Images
        page += "<center>"
        page += f"<h2>Images</h2><div class=\"image-container\">"
        imgPath = f"Products/{request.args['i']}/img"
        imagesFiles = os.listdir(imgPath)
        for img in imagesFiles:
            page += "<img src=\"{{ url_for('product_images', filename='"
            page += f"{request.args['i']}/img/{img}"
            page += "')}}\"  width=\"auto\" height=\"auto\">"
        page += "</div>"
        page += "</center>"
    if tm[2] == "1": #Price
        page += f"<h2>Price</h2>"
        pricePath = f"Products/{request.args['i']}"
        priceFiles = os.listdir(pricePath)
        for i in priceFiles:
            if i.startswith("price"):
                with open(f"{pricePath}/{i}", "r", encoding='utf_8') as f:
                    v = f.read().replace("\n", "<br>")
                    page += f"<p>{v}</p>"

    page += "</center>  </body> </html>"

    #write the page
    with open("templates/treatments.html", "w", encoding="utf-8") as f:
        f.write(page)

    return render_template('treatments.html', encoding='utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)