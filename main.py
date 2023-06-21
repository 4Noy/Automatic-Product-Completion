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

    page = f"""
    <!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Intitule de ma page</title>
    <link rel="stylesheet" href="templates/style.css">
  </head>
  <body>
    <h1>Automatic Product Completion - Product ID : {request.args['i']}</h1>
    <center>
    """

    if tm[0] == "1": #Descriptions
        page += f"<h2>Descriptions</h2>"
        descriptionsPath = f"Products/{request.args['i']}"
        descriptionsFiles = os.listdir(descriptionsPath)
        for i in descriptionsFiles:
            if i.startswith("text_"):
                page += f"<p>{i}</p>"
                with open(f"{descriptionsPath}/{i}", "r", encoding='utf_8') as f:
                    v = f.read().replace("\n", "<br>")
                    page += f"<p>{v}</p>"
    if tm[1] == "1": #Images
        page += f"<h2>Images</h2><div class=\"image-container\">"
        imgPath = f"Products/{request.args['i']}/img"
        imagesFiles = os.listdir(imgPath)
        for img in imagesFiles:
            page += "<img src=\"{{ url_for('product_images', filename='"
            page += f"{request.args['i']}/img/{img}"
            page += "')}}\"  width=\"auto\" height=\"auto\">"
        page += "</div>"
    if tm[2] == "1": #Price
        page += f"<h2>Price</h2>"
        pricePath = f"Products/{request.args['i']}"
        priceFiles = os.listdir(pricePath)
        for i in priceFiles:
            if i.startswith("price"):
                page += f"<p>{i}</p>"
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