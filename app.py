from flask import Flask, render_template, redirect, url_for, request
from tinydb import TinyDB, Query, where
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)

loginList = list()
dictToReturn = dict()

loginMap = dict()


db = TinyDB('database/db.json')
ip_user = db.table('ip_user')
user_table = db.table('user_table')
listing_table = db.table('listing_table')
user = None


# user_table.insert({
#   'ip': 'ip here',
#   'user_id': '1',
#   'user_name': 'admin',
#   'password': 'admin',
#   'funds': 100,
# })
#
# listing_table.insert({
#     'user_id': '1',
#     'listing_id': '1',
#     'title': 'FlexTape',
#     'price': 10,
#     'description': 'FLEX TAPE!!!',
#     'status': 'SOLD',
#     'date_listed': '2/15/19',
#     'date_sold': '2/16/19'
# })

def add_new_user(username, password):
    count = 0
    for user in user_table:
        count = count + 1
    user_id = count + 1
    user_table.insert({
        'ip': request.remote_addr,
        'user_id': user_id,
        'username': username,
        'password': password,
        'funds': 0
    })
    return

def add_new_listing(title, description, price):
    count = 0
    for item in listing_table:
        count = count + 1
    listing_id = count + 1
    User = Query()
    print()
    listing_table.insert({
        'user_id': ((user_table.search(User.username == currentUser))[0])['user_id'],
        'listing_id': listing_id,
        'title': title,
        'description': description,
        'price': price,
        'status': 'For sale',
        'date_listed': 'date1',
        'date_sold': 'NULL'

    })
    return listing_id

def valid_user(username,password):
    User = Query()
    if(len(user_table.search(User.username == username)) > 0):
        if(((user_table.search(User.username == username))[0])['password'] == password):
            return True
    return False

@app.route('/')
def index():
    if request.remote_addr in loginList:
        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/funds', methods=['GET','POST'])
def add_funds():
    User = Query()
    if request.remote_addr in loginList:
        if request.method == 'POST':
            user_table.update({'funds': int(request.form['funds'])}, where('username') == currentUser)
            return render_template("index.html")
        return render_template('funds.html')
    else:
        return redirect("http://localhost:5000/login", code=302)

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        add_new_user(request.form['username'], request.form['password'])
        return redirect("http://localhost:5000/login", code=302)
    return render_template('create_account.html')


@app.route('/getListings')
def returnListings():
    global dictToReturn
    return json.dumps(listing_table.all())

@app.route('/myListings')
def returnMyListings():
    userId = user_table.search(where('username') == loginMap[request.remote_addr])[0]['user_id']
    return (json.dumps(listing_table.search(where('user_id') == userId)))


@app.route('/getItem', methods=['GET','POST'])
def getItem():
    Listing = Query()
    itemID = request.args.get('item')
    if request.method == 'GET':
        return json.dumps(listing_table.search(Listing.listing_id == itemID))
    return render_template('checkout.html')

@app.route('/getUser', methods=['GET', 'POST'])
def getUserFunds():
    User = Query()
    if(request.method == 'GET'):
        return user_table.search(User.username == currentUser)[0]['funds']
        

@app.route('/submit', methods=['GET','POST'])
def submitNow():
    if request.remote_addr in loginList:
        if request.method == 'POST':
            itemId = add_new_listing(request.form['title'], request.form['description'], request.form['price'])
            global dictToReturn
            dictToReturn[itemId] = [request.form['title'],'Active',request.form['description'],request.form['price']]
            return redirect("http://localhost:5000/", code=302) 
        return render_template('submit.html')
    else:
        return redirect("http://localhost:5000/login", code=302)

@app.route('/my')
def returnMyPage():
    if request.remote_addr in loginList:
        return render_template('my.html')
    else:
        return redirect("http://localhost:5000/login", code=302)

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_user(request.form['username'], request.form['password']):
            global loginList
            global loginMap
            loginMap[request.remote_addr] = request.form['username']
            loginList.append(request.remote_addr)
            global currentUser
            currentUser = request.form['username']
        else:
            error = 'Invalid Credentials. Please try again.'
        return redirect("http://localhost:5000/", code=302)
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug = True)