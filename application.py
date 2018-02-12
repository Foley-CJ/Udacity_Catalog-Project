from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_configure import Base, CategoryItem, Category, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__, template_folder="mainTemplates")

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///food_world.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all food categories
@app.route('/')
def show_homepage():
    categories = session.query(Category)
    print categories
    return render_template('homepage.html', categories=categories, category_name="test")


# show foods for a specific category
@app.route('/<int:category_id>/')
def show_items(category_id):
    items = session.query(CategoryItem).filter_by(category_id=category_id)
    name = session.query(Category).filter_by(id=category_id).one()

    print name
    return render_template('food_items.html', category_name=name, foods=items, category_id=category_id)


# add a new category
@app.route('/new/', methods=['GET', 'POST'])
def new_category():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_category_item = Category(name=request.form['name'],
                                     picture=request.form['picture'],
                                     user_id=login_session['user_id'])
        session.add(new_category_item)
        flash('New Restaurant %s Successfully Created' % new_category_item)
        session.commit()
        return redirect(url_for('show_homepage'))
    else:
        return render_template('newCategory.html', category_name="test")


#######################################
# category item management
#######################################

# add a new category item
@app.route('/<int:category_id>/new/', methods=['GET', 'POST'])
def new_food_item(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    name = session.query(Category).filter_by(id=category_id).one()
    # if login_session['user_id'] != category_id.user_id:
    #     return "<script>function myFunction() " \
    #            "{alert('You are not authorized to add menu items to this restaurant. " \
    #            "Please create your own restaurant in order to add items.');}" \
    #            "</script><body onload='myFunction()'>"
    if request.method == 'POST':
            new_category_item = CategoryItem(name=request.form['name'],
                                             description=request.form['description'],
                                             picture=request.form['picture'],
                                             category_id=category_id,
                                             user_id=login_session['user_id'])
            session.add(new_category_item)
            session.commit()
            flash('New Menu %s Item Successfully Created'.format(new_category_item.name))
            return redirect(url_for('show_items', category_id=category_id))
    else:
        return render_template('newCategoryItem.html', category_name=name)


# add a edit category item
@app.route('/<int:category_id>/edit/<int:categoryItem_id>', methods=['GET', 'POST'])
def editCategoryItem(category_id, categoryItem_id):
    if 'username' not in login_session:
        return redirect('/login')

    categoryItem = session.query(CategoryItem).filter_by(id=categoryItem_id).one()
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        if request.form['name']:
            categoryItem.name = request.form['name']
        if request.form['description']:
            categoryItem.description = request.form['description']
        if request.form['picture']:
            categoryItem.price = request.form['picture']
        session.add(categoryItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('show_items', category_id=category_id))
    else:
        return render_template('editCategoryItem.html',
                               category_id=category_id,
                               menu_id=categoryItem_id,
                               item=categoryItem,
                               category_name=category)


# Delete a menu item
@app.route('/<int:category_id>/delete/<int:categoryItem_id>', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, categoryItem_id):
    if 'username' not in login_session:
        return redirect('/login')

    categoryItem = session.query(CategoryItem).filter_by(id=categoryItem_id).one()
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        session.delete(categoryItem)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('show_items', category_id=category_id))
    else:
        return render_template('deleteCategoryItem.html',
                               item=categoryItem,
                               category_name=category)


# Login Modules
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# User Handling
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except "error":
        return None


# Google Login Handling
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print 'This is your user_id: ' + str(user_id)
    print login_session['user_id']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    #output += login_session['user_id']
    output += 'HEY!'
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_homepage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_homepage'))


#######################################
# Json Handling
#######################################

# JSON APIs to view Restaurant Information
@app.route('/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    items = session.query(CategoryItem).filter_by(id=category_id).all()
    return jsonify(All_Category_Items=[i.serialize for i in items])


@app.route('/<int:category_id>/<int:category_item_id>/JSON')
def itemJSON(category_id, category_item_id):
    category_item = session.query(CategoryItem).filter_by(id=category_item_id).one()
    return jsonify(Category_Item=category_item.serialize)


@app.route('/JSON')
@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])







if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
