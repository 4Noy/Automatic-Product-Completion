#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_from_directory
import subprocess, os, json, openai, threading, time, urllib.parse

"""
To run the Website, and with all need from the main script
NEEDS :
Flask (pip install flask)
"""

#set openai api key
jsonFile = json.load(open("config.json", "r"))
openai.api_key= jsonFile["openai_api_key"]
app = Flask(__name__)
lock = threading.Lock()
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
    global lock

    try:
        regen = request.args['regen']
        idRegen = request.args['idRegen']
    except:
        regen = ""
        idRegen = ""
    try:
        productName = str(request.args['n'])
        productBrand = str(request.args['b'])
        productEAN13 = str(request.args['e'])
        modes = request.args.getlist('m')
    except:
        return "Error, please check your inputs"
    if regen == "" or idRegen == "" or regen is None or idRegen is None:
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

        if tm != "000":
            if id_product == "1":
                nbRequestChatGPT += 1

            if nbRequestChatGPT > 100 :
                print("/!\Much Request to Chat GPT, must have big cost")
            
            script_Path = os.getcwd() + "/Automatic_Product_Completion.py"

            if productBrand == "Brand" or productBrand == "" or productBrand is None:
                args = ["-v", "-i", id_product, "-n", productName, "-e", productEAN13, "-m", tm]
            else:
                args = ["-v", "-i", id_product, "-n", productName, "-b", productBrand, "-e", productEAN13, "-m", tm]

            subprocess.call(["python", script_Path] + args)
    else:
        print("Rephrasing...")
        nbRequestChatGPT += 1
        if nbRequestChatGPT > 100 :
            print("/!\\ Much Request to Chat GPT, must have big cost /!\\")
        
        #clean the text, ex:  %3A%20Fabriquez%20un%20monde%20lumineux%20en%20utilisant%20le%20kit%20de%20moulage%20Espace%20Fluorescent%20de%204M%20


        prompt = " Rephrase me that in maximum 10 pourcent longer : " + urllib.parse.unquote(regen) + "\n\nResult in " + jsonFile["default_language"]
        
        while not lock.acquire(blocking=False):
            time.sleep(0.2)
        print("Ask to Chat GPT...")
        chat = openai.ChatCompletion.create(model=jsonFile["default_model"], n=1, temperature=0.9, messages=[{"role" : "user", "content": prompt}])
        lock.release()
        with open("Products/" + str(id_product) + "/text_" + str(idRegen) +".txt", "w", encoding="utf-8") as f:
            f.write(chat['choices'][0]['message']['content'])
        print("Used Input Token : " + str(chat["usage"]["prompt_tokens"]) +\
                   "\nUsed Output Token : " +str(chat["usage"]["completion_tokens"]) +\
                  "\nTotal Token Used : " +str(chat["usage"]["total_tokens"]) + \
                    "\nTotal Cost : $" + str(chat["usage"]["prompt_tokens"] * 0.0000015 + \
                                             chat["usage"]["completion_tokens"] * 0.000002))
        time.sleep(0.1)


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
    function reloadPageWithParameter(id) {
  var text = document.getElementById(id).textContent;
  var params = new URLSearchParams(window.location.search);

  params.delete('regen');
  params.delete('idRegen');

  params.set('regen', encodeURIComponent(text));
  params.set('idRegen', encodeURIComponent(id));

  var newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + params.toString();

  history.replaceState({ path: newUrl }, '', newUrl);

  window.location.reload();
}
function copyText(id) {
        var textToCopy = document.getElementById(id);
        var range = document.createRange();
        range.selectNode(textToCopy);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);

        try {
          // Copy text format
          var successful = document.execCommand("copy");
        } catch(err) {
          console.log("Error copy :", err);
        }
        window.getSelection().removeAllRanges();
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
    try:
        descriptionsFiles = os.listdir(descriptionsPath)
    except:
        return "Product not found"
    j = 0
    for i in descriptionsFiles:
        if i.startswith("text_"):
            j+=1
            with open(f"{descriptionsPath}/{i}", "r", encoding='utf_8') as f:
                v = f.read().replace("\n", "<br>")
                page += f"<button onclick=\"reloadPageWithParameter('{j}')\">Rephrase</button><button onclick=\"copyText('{j}')\">Copy</button><p id = '{j}' style=\"font-size:14pt;line-height:107%;font-family:Arial, sans-serif;\">{v}</p>"
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
    time.sleep(0.1)
    return render_template(f'treatments_{id_product}.html', encoding='utf-8', id_product=id_product)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)