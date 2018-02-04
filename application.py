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

CLIENT_ID = json.loads(open('secrets/google_client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///food_world.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/hello')
def hello_world():
    return render_template('homepage.html')


# Show all restaurants
@app.route('/')
@app.route('/home/')
def show_restaurants():
    categories = session.query(Category)
    print categories
    return render_template('homepage.html', categories=categories, category_name="test")


@app.route('/home/<int:category_id>/')
def show_items(category_id):
    items = session.query(CategoryItem).filter_by(category_id=category_id)
    name = session.query(Category).filter_by(id=category_id).one()
    print name
    return render_template('food_items.html', category_name=name, foods=items)




    # creator = getUserInfo(restaurant.user_id)
    # items = session.query(MenuItem).filter_by(
    #     restaurant_id=restaurant_id).all()
    # if 'username' not in login_session or creator.id != login_session['user_id']:
    #     return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    # else:
    #     return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8021)
