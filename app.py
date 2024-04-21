from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/members', methods=['GET'])
def get_members():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             port='3306',
                                             user='root',
                                             password='113409',
                                             database='fitness')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM `Members`;')
        records = cursor.fetchall()
        members = []
        for r in records:
            member = {
                'id': r[0],'name': r[1],'password': r[2],'e-mail':r[3],'gender':r[4],'birthday':r[5],'phone':r[6],'goal':r[7]
                # Add more fields as needed
            }
            members.append(member)
        return jsonify({'members': members})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
