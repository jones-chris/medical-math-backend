#db_path = '../data/math.db' # Path is relative to entry point of the application - which is app.py.

# Path is relative to the path of app.py that you pass to the python interpreter.
# For example, if you start the app with "python3 ./repos/medical-math/app.py", then when you try to query the database,
# the app will look for the database at ./data/math.db, not find it, and return a 500 response.
# However, if you first do "cd repos/medical-math" and then do "python3 ./app.py" then the app will look for the database
# at repos/medical-math/data/math.db and will successfully find the file.
db_path = './data/math.db'