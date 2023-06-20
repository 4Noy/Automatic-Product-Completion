from flask import Flask, render_template, request
import subprocess

"""
To run the Website, and with all need from the main script
NEEDS :
Flask (pip install flask)
"""

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/treatments')
def treatments():
    for j in request.args:
        if j[0] == "i":
            i = j[1]
        if j[0] == "n":
            n = j[1]
        if j[0] == "b":
            b = j[1]
        if j[0] == "e":
            e = j[1]
        if j[0] == "m":
            m = j[1]
    try:
        i = i
        n = n
        b = b
        e = e
        m = m
    except:
        return "Error, please check your inputs"
  
    if m == "":
        m = "111"

    # Exécute le script Python et capture la sortie
    result = subprocess.run(['py', 'script1.py', f"-i \"{i}\" -n \"{n}\" -b \"{b}\" -e \"{e}\" -m \"{m}\""], capture_output=True, text=True)
  
    return result.stdout

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)