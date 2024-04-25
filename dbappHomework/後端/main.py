from flask import Flask, jsonify, request
from flask_cors import CORS

from model.mb import Member

app = Flask(__name__)
CORS(app)

member = Member(host="49.159.20.196",port=82,dbname="dbapp",username="access",pwd="dbapp")
@app.route('/create', methods=['POST'])
def createUser():
    data = request.get_json()
    id = data['id']
    name = data['name']
    email = data['email']
    contact = data['contact']    
    return jsonify({'result': member.addData((id,name,email,contact))})

@app.route('/get', methods=['GET'])
def getData():
    sortmode = request.args.get('sort')
    id = request.args.get('id')

    req = member.getData(sortmode,id)
    return jsonify({'result': req[0],'data':req[1]})


@app.route('/delete/<string:id>', methods=['DELETE'])
def del_Data(id):
    return jsonify({'result': member.del_Data(id)})

@app.route('/update/<id>', methods=['PUT'])
def updateUser(id):
    data = request.get_json()
    name = data['name']
    email = data['email']
    contact = data['contact']
    return jsonify({'result': member.updateData(id, name, email, contact)})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
