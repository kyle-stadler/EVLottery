from flask import Flask, render_template

app = Flask(__name__)

# Route to handle the homepage
@app.route('/')
def homepage():

    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True)