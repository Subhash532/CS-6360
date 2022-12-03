import csv

f = open('C:\\Users\\nxk210028\\Documents\\DB\\Project\\Individual\\books.csv', 'r', encoding="utf-8")
books = open('C:\\Users\\nxk210028\\Documents\\DB\\Project\\Individual\\Books.txt','w')
b_A = open('C:\\Users\\nxk210028\\Documents\\DB\\Project\\Individual\\Book_Authors.txt','w')
a = open('C:\\Users\\nxk210028\\Documents\\DB\\Project\\Individual\\Authors.txt','w')

f.readline()
rowCounter_1 = 0
rowCounter_2 = 0 

author_id = 1
book_id   = 1
authDict = {}
header = ['ISBN', 'Author','AuthorID']


for row in f:
    cols = row.split("\t")
    authors = cols[3].split(",")   
    isbn = cols[0]
    title = cols[2]
    bookValues = '"' + '","'.join(cols) + '"'
    b_statement = ('INSERT INTO `BOOKS` (`Isbn`,`Title`) VALUES (\'' + str(isbn) + '\',\'' + str(title) + '\');')
    print(b_statement)
    books.write(b_statement)
    books.write('\n')
   
    for auth in authors:
        if(not((str(auth)) in authDict.keys())):
            authDict[str(auth)]=author_id
            statement = ('INSERT INTO `AUTHORS` (`Author_id`,`Name`) VALUES (' + str(author_id) + ',\'' + auth + '\');')
            print(statement)
            a.write(statement)
            a.write('\n')
            author_id +=1
    rowCounter_1 += 1
    
    for auth in authors:
        statement = ('INSERT INTO `BOOK_AUTHORS` (`AUTHOR_id`,`Isbn`) VALUES (' + str(authDict[auth]) + ',\'' + str(isbn) + '\');')
        print(statement)
        b_A.write(statement)
        b_A.write('\n')

books.close()
a.close()
b_A.close()
f.close()