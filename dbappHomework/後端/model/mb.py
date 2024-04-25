import mysql.connector
from model.db import database

class Member(database):
    def checkuser(self,id):
        sql = f"SELECT * FROM member_table WHERE id='{id}';"
        req = self.getSqlData(sql)
        return req.fetchone()==None

    def addData(self,data):
        if self.test():
            try:
                sql = "INSERT INTO `member_table` (`id`, `name`, `email`, `contact`) VALUES (%s, %s, %s, %s);"
                self.runSql(sql,data)
                return "新增成功"
            except mysql.connector.Error as error:
                if isinstance(error, mysql.connector.IntegrityError):
                    return "使用者已存在"
                return "發生未知錯誤"
        else:
            return "連結資料庫時發生錯誤"
    
    def getData(self,sortmode,id):
        if self.test():
            try:
                sql = "SELECT * FROM member_table "
                if id==None:
                    sql+=f"ORDER BY sno {sortmode};"
                else:
                    sql+=f"WHERE id='{id}';"
                cursor = self.getSqlData(sql)
                req = [dict([["sno",sno],["id",id],["name",name],["email",email]
                    ,["contact",contact]]) for (sno,id, name, email, contact) in cursor]
                cursor.close()
                return ("查詢成功",req)
            except mysql.connector.Error as error:
                return ("發生未知錯誤",None)
        else:
            return ("連結資料庫時發生錯誤",None)

    def del_Data(self,id):
        if self.test():
            try:
                if self.checkuser(id):
                    return "使用者不存在"
                else:
                    sql = f"DELETE FROM member_table WHERE id='{id}';"
                    self.runSql(sql)
                    return "刪除成功"
            except mysql.connector.Error as error:
                return "發生未知錯誤"    
        else:
            return "連結資料庫時發生錯誤"
        
    def updateData(self, id, name, email, contact):
        if self.test():
            try:
                if self.checkuser(id):
                    return "使用者不存在"
                else:
                    sql = "UPDATE `member_table` SET `name`=%s, `email`=%s, `contact`=%s WHERE `id`=%s;"
                    self.runSql(sql, (name, email, contact, id))
                    return "修改成功"
            except mysql.connector.Error as error:
                print(error)
                return "發生未知錯誤"
        else:
            return "連結資料庫時發生錯誤"



