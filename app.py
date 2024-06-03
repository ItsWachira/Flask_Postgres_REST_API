import os 
#import this package -- it's a ORM for python applications with postgres DBs (still an SQL db) replace this with a similar package for mysql db e.g mysql2  or sqlalchemy or sequalize(something of the sort
# not sure about this exact package --- look it app.
import psycopg2
# dotenv package allows you to load any environment variable e.g the db connection URL, host name, et.c in my case i was using an external postgres db in the cloud, i only needed the URl.
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()



app = Flask(__name__)
# this is how you establish the db connection. - you can move this code to a db.py file then  export it, and import it in the app.py
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)



@app.get("/")
def home():
    return "hello world"

# now make sure to create you models using your ORMs methods--dont go the raw sql route like i did, you can however opt for it.

CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);"

with connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_USERS_TABLE)

INSERT_USER_RETURN_ID = "INSERT INTO users (name) VALUES (%s) RETURNING id;"
SELECT_ALL_USERS = "SELECT * FROM users;"
SELECT_USER_BY_ID = "SELECT id, name FROM users WHERE id = %s;"
UPDATE_USER_BY_ID = "UPDATE users SET name = %s WHERE id = %s;"
DELETE_USER_BY_ID = "DELETE FROM users WHERE id = %s;"


# all the API methods to interact with the database.

@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_USER_RETURN_ID, (name,))
            user_id = cursor.fetchone()[0]
    return {"id": user_id, "name": name, "message": f"User {name} created."}, 201

@app.route("/api/user", methods=["GET"])
def get_all_users():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_USERS)
            users = cursor.fetchall()
            if users:
                result = []
                for user in users:
                    result.append({"id": user[0], "name": user[1]})
                return jsonify(result)
            else:
                return jsonify({"error": f"Users not found."}), 404

@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({"id": user[0], "name": user[1]})
            else:
                return jsonify({"error": f"User with ID {user_id} not found."}), 404


@app.route("/api/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_USER_BY_ID, (name, user_id))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {user_id} not found."}), 404
    return jsonify({"id": user_id, "name": name, "message": f"User with ID {user_id} updated."})

@app.route("/api/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_USER_BY_ID, (user_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {user_id} not found."}), 404
    return jsonify({"message": f"User with ID {user_id} deleted."})




