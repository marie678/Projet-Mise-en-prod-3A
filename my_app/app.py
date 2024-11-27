from flask import Flask, render_template, request, jsonify
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/hello_world")
def hello_world():
    return "Hello World!"

# @app.route("/spacy/prediction/<text>")
# def prediction(text: str):
#     sentence = nlp(text)
#     ents = dict()
#     for ent in sentence.ents :
#         ents[ent.text] = ent.label_
#     return ents

# @app.route("/spacy/prediction", methods=["GET", "POST"])
# def prediction():
#         # data = request.get_json()
#         # text = data.get('text', '')
#         text = request.json['text']

#         sentence = nlp(text)
#         ents = dict()
#         for ent in sentence.ents :
#             ents[ent.text] = ent.label_
#         return jsonify(ents)



@app.route("/spacy/prediction", methods=["GET", "POST"])
def prediction():
    if request.method == "POST":
        text = request.form["text"]
        sentence = nlp(text)
        ents = dict()
        for ent in sentence.ents :
            ents[ent.text] = ent.label_
        # return jsonify(ents) 
        return render_template("preds.html", text=text, predictions=ents) 
    return render_template("preds.html")