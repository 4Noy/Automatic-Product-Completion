from flask import Flask, render_template, request
import subprocess
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
  
    if tool.toolMode == "":
        tool.toolMode = "111"

    # Exécute le script Python et capture la sortie
    
    #result = subprocess.run(['py', '../Automatic_Product_Completion.py', f"-i \"{i}\" -n \"{n}\" -b \"{b}\" -e \"{e}\" -m \"{m}\""], capture_output=True, text=True)

    if tool.toolMode[0] == "1":
        nbRequestChatGPT += 1

    if nbRequestChatGPT > 10 :
        print("Much Request to Chat GPT, must have big cost")

    tool.Main()

    return "fini"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)