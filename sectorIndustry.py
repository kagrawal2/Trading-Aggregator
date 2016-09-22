import csv

def industrySectorDict():
    with open('coLists/NasdaqcoList.csv', mode='r') as infile:
        reader = csv.reader(infile)
        with open('coLists/NasdaqcoList_new.csv', mode='w') as outfile:
            writer = csv.writer(outfile)
            mydict = {rows[0] : [rows[5], rows[6]] for rows in reader}
    with open('coLists/AMEXcoList.csv', mode='r') as infile:
        reader = csv.reader(infile)
        with open('coLists/AMEXcoList_new.csv', mode='w') as outfile:
            writer = csv.writer(outfile)
            mydict = {rows[0] : [rows[5], rows[6]] for rows in reader}
    with open('coLists/NYSEcoList.csv', mode='r') as infile:
        reader = csv.reader(infile)
        with open('coLists/NYSEcoList_new.csv', mode='w') as outfile:
            writer = csv.writer(outfile)
            mydict = {rows[0] : [rows[5], rows[6]] for rows in reader}

    return mydict

sectorData = industrySectorDict()