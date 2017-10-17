# Stuff for the database
import sqlite3
import os

# Command line parsing
import sys, getopt

# Code reuse
from app import init_db, grab_entries 

def main(argv):

    #Command line parsing
    try:
        opts, args = getopt.getopt(argv, "h:n:l:r")
    except getopt.GetoptError:
        print "Unknown command, try -h for help"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "-h for help, -n for a new database, -l for listing database, -r <filename> for removing a file from the database"
            sys.exit()
        elif opt in ("-n"):
            print "Creating a new database..."
            init_db()
            print "Done"
            sys.exit()
        elif opt in ("-l"):
            entries = grab_entries()
            for row in entries:
                print row[0] + "\t" + row[1]
            sys.exit()
        elif opt in ("-r"):
            print "soon to remove"
            sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
