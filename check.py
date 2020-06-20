from flask import *  
app = Flask(__name__) 
import os 
app.secret_key = os.urandom(24)


@app.route('/')  
def home():  
    res = make_response("<h4>session variable is set, <a href='/get'>Get Variable</a></h4>")  
    session['response']='session#1'  
    return res;  


@app.route('/get')  
def getVariable():  
    print(session)
    if 'response' in session:  
        s = session['response']
        return render_template('session.html',name = s)  


if __name__ == '__main__':  
    app.run(debug = True)  