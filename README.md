# Udacity_Catalog-Project
Catalog capstone project for Udacity full stack nano degree


Flask Web application designed to list different categories of food and items that belong to those categories. Login required to change the database in any way. 


About the project:
* Python-flask based web application utilizing Jinja2 and Bootstrap for dynamics styling. Supporting database is a rdbs built on sqlite.
* Database can be configured using database_configure.py
* Database can be loaded with inital data by running datanase_data_load.py
  * database_data_load.py uses the files within static/data folder to load the sqlite base with default data.


This application is built using python 2.7 and relies upon the flask framework. Specific packages are shown below.

* python - 2.7.xx
* flask - 0.12.xx
* jinja2 - 2.10.xx
* sqlAlchemy - 1.12.xx

In order to run the application navigate to the root folder and run the whole application using the follwoing command.
"python application.py"