# Stuff for the database
import sqlite3
import os
import datetime

# Command line parsing
import sys, getopt

# Code reuse
from app import init_db 

DATABASE = './media/media.db'

def main(argv):

    #Command line parsing
    try:
        opts, args = getopt.getopt(argv, "nlr:a:h", ["remove=", "add="])
    except getopt.GetoptError:
        print "Unknown command, try -h for help"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "-h for help"
            print "-n for a new database"
            print "-l for listing database"
            print "-r <filename> for removing a file from the database"
            print "-a <filename> for adding a file to the database"
            sys.exit()
        elif opt in ("-n"):
            print "Creating a new database..."
            init_db() # Calls this from app.py, where I intend to add most of this functionality 
            print "Done"
            sys.exit()
        elif opt in ("-l"):
            db = sqlite3.connect(DATABASE)
            for row in db.execute('SELECT date, fileName FROM media ORDER BY id ASC'):
                print row
            sys.exit()
        elif opt in ("-r", "--remove"):
            filename = arg
            db = sqlite3.connect(DATABASE)
            # This returns 1 if there is at least 1 record of the filename in the database
            exist = db.execute('SELECT EXISTS (SELECT 1 FROM media WHERE fileName=? LIMIT 1)', [filename]).fetchone()[0]
            if exist == 1:
                db.execute('DELETE FROM media WHERE fileName=?', [filename])
                db.commit()
            sys.exit()
        elif opt in ("-a", "--add"):
            filename = arg
            path = "./media/" + filename
            if os.path.isfile(path) == True:
                date = datetime.date.today() # Since there isn't a sure way to get the time the file was created, use today instead
                db = sqlite3.connect(DATABASE)
                db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [date, filename])
                db.commit()
                sys.exit()
            print "File does not exist, or is not in the media folder"
            sys.exit()
        else:
            sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
