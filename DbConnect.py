import MySQLdb

# Open database connection
db = MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net",
                     user="b92deb64ef1abe",
                     passwd="0c6328ac",
                     db="heroku_c92d232bd6c80b1")
#db = MySQLdb.connect("10.238.197.95", "b92deb64ef1abe", "p0c6328ac", "heroku_c92d232bd6c80b1")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method
cursor.execute("SELECT VERSION()")

# fetch a single row using fetchone() method
data = cursor.fetchone()

print "Database version: %s" % data

# disconnect from server
db.close()
