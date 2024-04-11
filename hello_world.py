import flask

app = flask.Flask(__name__)
app.config['DEBUG']=True

@app.route('/',methods=['GET'])
def home():
    return '<h1>ChatBlock by Drys-Pentzakis Odyssefs, Markantonatos Gerasimos and Konstantinos Katsigiannis</h1>'

app.run()