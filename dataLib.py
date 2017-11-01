import _sqlite3

#cnnect the server of sqlite
Map = _sqlite3.connect('Mac2ShortMap.db')

def OpenMap():
    Map = _sqlite3.connect('Mac2ShortMap.db')

# return the short address
def GetShortAddress(Mac):
    # creat a operation cursor
    MapCursor = Map.cursor()
    MapCursor.execute('select * from user where MacAddr=?', (Mac,))
    value = MapCursor.fetchall()
    MapCursor.close()
    return value;

#if map is existing already, it will modify the map. if not, it will add a table
def InsetMap(Mac, SortAddr):
    MapCursor = Map.cursor()
    MapCursor.execute('select * from user where MacAddr=?', (Mac,))
    value = MapCursor.fetchall()
    if value  == []:
        print("No This Device!\n")
        MapCursor.execute('insert into user (MacAddr, ShortAddr) values (Mac, SortAddr)')
    else:
        print("Cread New Device Map\n")
        print(value)
        MapCursor.execute("update user set ShortAddr=? where MacAddr=?", (SortAddr,Mac))#('update user set ShortAddr =?,where MacAddr=?', (SortAddr,Mac))
    print("SQL Insert Line: %d\n" % MapCursor.rowcount)
    Map.commit()
    MapCursor.close()


def CloseMap():
    Map.close()

def main():
    InsetMap("F7 7F BB 0D 00 4B 12 00", "2345")
    CloseMap()
if __name__ == '__main__':
    main()