import csv

mylist = []
with open('test.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        mylist.append(row[0])
        
print(mylist)