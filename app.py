from flask import Flask, render_template, send_file, jsonify, request, Response
from pymongo import MongoClient
import json
import csv


app = Flask(__name__)

#MongoDB connection settings
MONGO_URI = "mongodb://mojaBazaSpremnik:27017/"
DATABASE_NAME = "sportski_klubovi"
COLLECTION_NAME = "klubovi"
filtered_data =[]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datatable')
def datatable():
    return render_template('datatable.html')

@app.route('/download_csv')
def download_csv():
    csv_filename = "klubovi.csv"
    return send_file(csv_filename, as_attachment=True)

@app.route('/download_json')
def download_json():
    json_filename = "klubovi.json"
    return send_file(json_filename, as_attachment=True)

@app.route('/data', methods=['GET'])
def get_data():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    data = list(collection.find({}))
    return jsonify(data)

@app.route('/filter_data', methods=['POST'])
def filter_data():
    global filtered_data
    query = request.form.get('query')
    attribute = request.form.get('attribute', '')

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    filter = {}
    if attribute and query:
        filter[attribute] = {"$regex": query, "$options": "i"}  # Case-insensitive regex search
        filtered_data = list(collection.find(filter))
    if attribute == "wildcard" and query:
        filtered_data = list(collection.find({ "$text": { "$search": query} }))
    if attribute == "RangNatjecanja" and query:
        int_query = int(query)
        filtered_data = list(collection.find({"RangNatjecanja": int_query}))
    if attribute == "GodinaOsnutka" and query:
        int_query = int(query)
        filtered_data = list(collection.find({"GodinaOsnutka": int_query}))
    if attribute == "Igrač.Ime" and query:
        filtered_data = list(collection.find({ "$text": { "$search": query }}))
    if attribute == "Igrač.Prezime" and query:
        filtered_data = list(collection.find({ "$text": { "$search": query }}))


    print("Received query:", query, "and attribute:", attribute)
    return jsonify(filtered_data)

@app.route('/export_json', methods=['GET'])
def export_json():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    global filtered_data
    data = filtered_data
    filtered_data = list(collection.find({}))
    with open('filtered_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    return send_file('filtered_data.json', as_attachment=True)

@app.route('/export_csv', methods=['GET'])
def export_csv():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    global filtered_data
    data = filtered_data
    filtered_data = list(collection.find({}))
    with open('filtered_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    with open('filtered_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Create a CSV file and write the data with UTF-8 encoding
    with open('filtered_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header
        csv_writer.writerow(
            ['ImeKluba', 'Sport', 'Mjesto', 'Liga', 'RangNatjecanja', 'GodinaOsnutka', 'Predsjednik.Ime',
             'Predsjednik.Prezime', 'Kontakt_Email', 'Kontakt_Telefon', 'Igrač.Ime', 'Igrač.Prezime'])

        # Iterate through each document and write data to CSV
        for document in data:
            players = document.get('Igrači', [])
            for player in players:
                csv_writer.writerow([
                    document.get('ImeKluba', ''),
                    document.get('Sport', ''),
                    document.get('Mjesto', ''),
                    document.get('Liga', ''),
                    document.get('RangNatjecanja', ''),
                    document.get('GodinaOsnutka', ''),
                    document.get('Predsjednik', {}).get('Ime', ''),
                    document.get('Predsjednik', {}).get('Prezime', ''),
                    document.get('Kontakt', {}).get('Email', ''),
                    document.get('Kontakt', {}).get('Telefon', ''),
                    player.get('Ime', ''),
                    player.get('Prezime', '')
                ])
    return send_file('filtered_data.csv', as_attachment=True)


@app.route('/api/v1/klubovi', methods=['GET', 'POST'])
def api_get_data():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    data = list(collection.find({}))
    try:
        if request.method == 'GET':

            return jsonify({"Status": "OK", "message": "Fetched all data", "response": {"data": data}}), 200

        if request.method == 'POST':
            newImeKluba = request.form["ImeKluba"]
            newSport = request.form["Sport"]
            newMjesto = request.form["Mjesto"]
            newLiga = request.form["Liga"]
            newRang = request.form["RangNatjecanja"]
            newGodina = request.form["GodinaOsnutka"]
            newPredsjednik = {"Ime" : request.form["Predsjednik"].split()[0], "Prezime": request.form["Predsjednik"].split()[1]}
            newKontakt = {"Email" : request.form["Email"], "Telefon" : request.form["Telefon"]}
            newIgraci = request.form["Igrači"]
            igraci = newIgraci.split("\n")
            pomIgraci = []
            for i in igraci:
                igrac = i.split()
                pomIgraci.append({"Ime" : igrac[0], "Prezime" : igrac [1]})
            newIgraci = pomIgraci
            newId = len(data) + 1
            #print(newIgraci, newKontakt, newPredsjednik, newRang, newId)
            if (collection.insert_one(
                {
                    "_id" : newId,
                    "ImeKluba" : newImeKluba,
                    "Sport" : newSport,
                    "Mjesto" : newMjesto,
                    "Liga" : newLiga,
                    "RangNatjecanja" : newRang,
                    "GodinaOsnutka" : newGodina,
                    "Predsjednik" : newPredsjednik,
                    "Kontakt" : newKontakt,
                    "Igrači": newIgraci
                }
            )):
                data = list(collection.find({}))
                return jsonify({"Status": "OK", "message": "Inserted data", "response": {"data": data[-1]}}), 201
    except:
        return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500



# GET endpoint for a specific resource
@app.route('/api/v1/klubovi/<int:data_id>', methods=['GET', 'PUT', 'DELETE'])
def api_get_id_data(data_id):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    if request.method == 'GET':
        try:
            data = list(collection.find({"_id": data_id}))
            if data:
                return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}
            else:
                return {"Status": "Not found", "message": f"Data with ID {data_id} doesn't exist", "response": None}, 404
        except:
            return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

    if request.method == 'PUT':
        try:
            data = list(collection.find({"_id": data_id}))
            if data:
                dict_data = {}
                for i in data:
                    dict_data.update(i)

                if request.form["ImeKluba"] != "":
                    newIme = request.form["ImeKluba"]
                else:
                    newIme = dict_data["ImeKluba"]

                if request.form["Sport"] != "":
                    newSport = request.form["Sport"]
                else:
                    newSport = dict_data["Sport"]

                if request.form["Mjesto"] != "":
                    newMjesto = request.form["Mjesto"]
                else:
                    newMjesto = dict_data["Mjesto"]

                if request.form["Rang"] != "":
                    newRang = request.form["Rang"]
                else:
                    newRang = dict_data["RangNatjecanja"]

                if request.form["Liga"] != "":
                    newLiga = request.form["Liga"]
                else:
                    newLiga = dict_data["Liga"]

                if request.form["Godina"] != "":
                    newGodina = request.form["Godina"]
                else:
                    newGodina = dict_data["GodinaOsnutka"]

                if request.form["Predsjednik"] != "":
                    newPredsjednik = {"Ime" : request.form["Predsjednik"].split()[0], "Prezime": request.form["Predsjednik"].split()[1]}
                else:
                    newPredsjednik = dict_data["Predsjednik"]

                if request.form["Kontakt"] != "":
                    newKontakt = {"Email" : request.form["Email"], "Telefon" : request.form["Telefon"]}
                else:
                    newKontakt = dict_data["Kontakt"]

                if request.form["Igrači"] != "":
                    newIgraci = request.form["Igrači"]
                    igraci = newIgraci.split("\n")
                    pomIgraci = []
                    for i in igraci:
                        igrac = i.split()
                        pomIgraci.append({"Ime": igrac[0], "Prezime": igrac[1]})
                    newIgraci = pomIgraci
                else:
                    newIgraci = dict_data["Igrači"]

                if (collection.update_one(
                        {"_id" : dict_data["_id"]},
                        {"$set" : {
                            "ImeKluba": newIme,
                            "Sport": newSport,
                            "Mjesto": newMjesto,
                            "Liga": newLiga,
                            "RangNatjecanja": newRang,
                            "GodinaOsnutka": newGodina,
                            "Predsjednik": newPredsjednik,
                            "Kontakt": newKontakt,
                            "Igrači": newIgraci
                        }
                        }
                )):
                    data = list(collection.find({"_id": data_id}))
                    return {"Status": "OK", "message": "Updated data", "response": {"data": data}}, 200
            else:
                return {"Status": "Not found", "message": f"Data with ID {data_id} doesn't exist", "response": None}, 404
        except:
            return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500


    if request.method == 'DELETE':
        try:
            data = list(collection.find({"_id": data_id}))
            if data:
                if collection.delete_one({"_id" : data_id}):
                    return {"Status": "OK", "message": f"Deleted data with ID {data_id}", "response": "null"}, 200
            else:
                return {"Status": "Not found", "message": f"Data with ID {data_id} doesn't exist", "response": None}, 404
        except:
            return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

@app.route('/api/v1/gradovi', methods=['GET'])
def api_get_grad_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        data = list(collection.find({}, {"Mjesto" : 1, "_id" : 0}))
        pom = []
        for i in data:
            if i not in pom:
                pom.append(i)
        data = pom
        if data:
            return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}, 200
    except:
        return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

@app.route('/api/v1/gradovi/<string:grad>', methods=['GET'])
def api_get_one_grad_data(grad):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        data = list(collection.find({}))
        pom = []
        for i in data:
            if i not in pom and grad in str(i.values()):
                pom.append(i)
        data = pom
        if data:
            return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}, 200
        else:
            return {"Status": "Not found", "message": f"Data with grad {grad} doesn't exist", "response": None}, 404
    except:
        return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

@app.route('/api/v1/sportovi', methods=['GET'])
def api_get_sport_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        data = list(collection.find({}, {"Sport" : 1, "_id" : 0}))
        pom = []
        for i in data:
            if i not in pom:
                pom.append(i)
        data = pom
        if data:
            return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}, 200
    except:
        return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

@app.route('/api/v1/sportovi/<string:sport>', methods=['GET'])
def api_get_one_sport_data(sport):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        data = list(collection.find({}))
        pom = []
        for i in data:
            if i not in pom and sport in str(i.values()):
                pom.append(i)
        data = pom
        if data:
            return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}, 200
        else:
            return {"Status": "Not found", "message": f"Data with sport {sport} doesn't exist", "response": None}, 404
    except:
        return jsonify({"Status": "Internal server error", "message": "Unable to retrieve data from database", "response": "null"}), 500

@app.route('/api/specification', methods=['GET'])
def api_specification():
    with open('openapi.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if data:
        return {"Status": "OK", "message": "Fetched data", "response": {"data": data}}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

