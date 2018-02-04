from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_configure import Base, CategoryItem, Category, User


engine = create_engine('sqlite:///food_world.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


#Load Users
f = open("static/data/initial_db_data_Users.txt","r")
for line in f:
    data = line.split(',')
    print data
    currUser = User(name=data[0].strip(),
                    email=data[1].strip(),
                    picture=data[2].strip())
    session.add(currUser)

session.commit()
print "added users"

#Load Categories
f = open("static/data/initial_db_data_Categories.txt","r")
for line in f:
    data = line.split(',')
    print data
    currCategory = Category(name=data[0].strip(),
                            picture=data[1].strip(),
                            user_id=data[2].strip())
    session.add(currCategory)

session.commit()
print "added category"

#Load Items
f = open("static/data/initial_db_data_CategoryItems.txt", "r")
for line in f:
    data = line.split(',')
    print data
    currCategoryItem = CategoryItem(name=data[0].strip(),
                                    description=data[1].strip(),
                                    picture=data[2].strip(),
                                    category_id=data[3].strip(),
                                    user_id=data[4].strip())
    session.add(currCategoryItem)

session.commit()
print "added menu items!"

