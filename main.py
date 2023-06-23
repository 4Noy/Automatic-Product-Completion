#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_from_directory
import subprocess, os

"""
To run the Website, and with all need from the main script
NEEDS :
Flask (pip install flask)
"""



app = Flask(__name__)
nbRequestChatGPT = 0

@app.route('/')
def index():
    brands = []
    if os.path.exists("Brands.txt"):
        with open("Brands.txt", "r", encoding="utf-8") as f:
            brands = sorted(f.read().split("\n"))
    return render_template('index.html', brands=brands)

@app.route('/product_images/<path:filename>')
def product_images(filename):
    return send_from_directory('Products', filename)

@app.route('/treatments_<id_product>')
def treatments(id_product):
    global nbRequestChatGPT
    try:
        productName = request.args['n']
        productBrand = request.args['b']
        productEAN13 = request.args['e']
        modes = request.args.getlist('m')
    except:
        return "Error, please check your inputs"
    tm = ""
    if "desc" in modes:
        tm += "1"
    else:
        tm += "0"
    if "imgs" in modes:
        tm += "1"
    else:
        tm += "0"
    if "pric" in modes:
        tm += "1"
    else:
        tm += "0"

    if id_product == "1":
        nbRequestChatGPT += 1

    if nbRequestChatGPT > 100 :
        print("Much Request to Chat GPT, must have big cost")
    
    script_Path = os.getcwd() + "/Automatic_Product_Completion.py"

    if productBrand == "Brand" or productBrand == "":
        args = ["-v", "-i", id_product, "-n", productName, "-e", productEAN13, "-m", tm]
    else:
        args = ["-v", "-i", id_product, "-n", productName, "-b", productBrand, "-e", productEAN13, "-m", tm]

    

    

    subprocess.call(["python", script_Path] + args)

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
    var textToCopy = document.getElementById(id);

    var tempTextArea = document.createElement("textarea");
    tempTextArea.value = textToCopy.textContent;

    document.body.appendChild(tempTextArea);

    tempTextArea.select();

    document.execCommand("copy");

    document.body.removeChild(tempTextArea);
    }
    function goBack() {
          window.location.href = '/?activated=true';
        }
</script>
  </head>
  <body>"""
    page +=f"""
    <h1>Automatic Product Completion - Product ID : {id_product}</h1>  <button onclick="goBack()">Back</button>
    """

    #if tm[0] == "1": #Descriptions
    page += f"<h2 id=\"texte-a-copier\">Descriptions</h2>"
    descriptionsPath = f"Products/{id_product}"
    descriptionsFiles = os.listdir(descriptionsPath)
    j = 0
    for i in descriptionsFiles:
        j+=1
        if i.startswith("text_"):
            with open(f"{descriptionsPath}/{i}", "r", encoding='utf_8') as f:
                v = f.read().replace("\n", "<br>")
                page += f"<button onclick=\"copyText('{j}')\">Copy</button><p id = '{j}' style=\"font-size:14pt;line-height:107%;font-family:Arial, sans-serif;\">{v}</p>"
            page += "<br>"
    #if tm[1] == "1": #Images
    page += "<center><h2>Images</h2><div class=\"image-container\">"
    imgPath = f"Products/{id_product}/img"
    try:
        imagesFiles = os.listdir(imgPath)
        for img in imagesFiles:
            page += "<img src=\"{{ url_for('product_images', filename='"
            page += f"{id_product}/img/{img}"
            page += "')}}\"  width=\"auto\" height=\"auto\">"
    except:
        pass
    page += "</div>"
    page += "</center>"
    #if tm[2] == "1": #Price
    page += f"<h2>Price</h2>"
    pricePath = f"Products/{id_product}"
    priceFiles = os.listdir(pricePath)
    for i in priceFiles:
        if i.startswith("price"):
            with open(f"{pricePath}/{i}", "r", encoding='utf_8') as f:
                v = f.read().replace("\n", "<br>")
                page += f"<p>{v}</p>"

    page += "</center>  </body> </html>"

    #write the page
    with open(f"templates/treatments_{id_product}.html", "w", encoding="utf-8") as f:
        f.write(page)

    return render_template(f'treatments_{id_product}.html', encoding='utf-8', id_product=id_product)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)