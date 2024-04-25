import mysql.connector

class database:
    def __init__(self, host, port, dbname, username, pwd):
        self.host = host
        self.port = port
        self.database = dbname
        self.user = username
        self.password = pwd
        self.__server = None

    @property
    def Server(self):
        return self.__server
    
    @Server.setter
    def Server(self, value):
        self.__server = value

    def setServer(self):
        self.Server = mysql.connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
    )

    def test(self):
        self.setServer()
        return self.Server.is_connected()

    def runSql(self,sql,data=None):
        self.setServer()
        cursor = self.Server.cursor()
        if data==None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, data)
        self.Server.commit()
        cursor.close()

    def getSqlData(self,sql):
        self.setServer()
        cursor = self.Server.cursor()
        cursor.execute(sql)
        return cursor
    


