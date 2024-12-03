from flask import Flask, render_template, request, jsonify
import pandas as pd
from functools import reduce
import operator
import ast

app = Flask(__name__)

base = r'^{}'
expr = '(?=.*{})'
echant = pd.read_csv('echant_10k_recipes.csv')
echant = echant.set_index(echant['Unnamed: 0'].values).drop(columns=['Unnamed: 0'])

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/spacy/prediction", methods=["GET", "POST"])
def prediction():
    if request.method == "POST":
        text = request.form["text"]
        sentence = text.split(' ')
        nb = len(sentence)
        rep = echant[echant['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]
        rep['%'] = rep['NER'].apply(lambda sentence: round((nb / len(ast.literal_eval(sentence)))*100,1))
        if len(rep) != 0 : 
            best = rep['%'].idxmax()
            res = echant.loc[best]
        else : 
            res = "Il n'y a pas de recette correspondante"
        return render_template("preds.html", text=text, predictions=res) 
    return render_template("preds.html")