import _sqlite3

#cnnect the server of sqlite
Map = _sqlite3.connect('Mac2ShortMap.db')

#creat a operation cursor
MapCursor = Map.cursor()
newdev = 'F7 7F BB 0D 00 4B 12 00'
MapCursor.execute('select * from user where MacAddr=?', (newdev,))

value = MapCursor.fetchall()

if value == []:
    print("No This Device!\n")
else:
    print("Cread New Device Map\n")
    print(value)

#creat a data table by the SQL CMD
#MapCursor.execute('create table user (MacAddr varchar(23) primary key, ShortAddr varchar(4))')

#MapCursor.execute('insert into user (MacAddr, ShortAddr) values (\'F7 7F BB 0D 00 4B 12 00\', \'5680\')')

print("SQL Insert Line: %d\n"%MapCursor.rowcount)

#close the Cursor
MapCursor.close()




Map.commit()

Map.close()
def GetShortAddress(Mac):

    return 0;