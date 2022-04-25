import csv

global lastline
lastline = ''
def scanfile():
    with open('DHT.log') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 5:
                print(row)
            else:
                lastline = row

try:
    scanfile()
except:
    print(lastline)