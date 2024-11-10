from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dbmsproject'
app.config['MYSQL_DB'] = 'dbms'

mysql = MySQL(app)



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Get JSON data from frontend
    email = data['email']
    name = data['name']
 
    try:
        cursor = mysql.connection.cursor()

        # Step 1: Get the latest clientid from the database
        cursor.execute("SELECT clientid FROM clients ORDER BY clientid DESC LIMIT 1")
        latest_client = cursor.fetchone()

        # Step 2: Generate the new clientid
        if latest_client and latest_client[0].startswith("C"):
            # Extract the numeric part and increment it
            latest_id_num = int(latest_client[0][1:])  # Skip 'C' and get the number
            new_clientid = f"C{latest_id_num + 1}"
        else:
            # If no records exist, start with 'C1'
            new_clientid = "C1"

        # Step 3: Insert the new client record into the table
        query = "INSERT INTO clients (clientid, email, name) VALUES (%s, %s, %s)"
        cursor.execute(query, (new_clientid, email, name))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"status": "success", "message": "User added to clients table!", "clientid": new_clientid})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to add user"}), 500


@app.route('/submit_testimonial', methods=['POST'])
def submit_testimonial():
    data = request.get_json()
    clientid = data.get('clientid')
    rating = data.get('rating')
    comments = data.get('message')

    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO testimonials (clientid, rating, comments) VALUES (%s, %s, %s)"
        cursor.execute(query, (clientid, rating, comments))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"status": "success", "message": "Testimonial submitted successfully!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to submit testimonial"}), 500
    

@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.get_json()
    clientid = data.get('clientid')
    event_date = data.get('event_date')  # This should be in 'YYYY-MM-DD' format
    enteredAmount = data.get('enteredAmount')
    paymentStatus = data.get('paymentStatus')

    try:
        cursor = mysql.connection.cursor()
        
        event_query = "INSERT INTO events (event_date, clientid) VALUES (%s, %s)"
        cursor.execute(event_query, (event_date, clientid))

        # Insert payment data into the payments table
        payment_query = "INSERT INTO payments (clientid, amount, status) VALUES (%s, %s, %s)"
        cursor.execute(payment_query, (clientid, enteredAmount, paymentStatus))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"status": "success", "message": "Event added successfully!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to add event"}), 500


    
if __name__ == "__main__":
    app.run(debug=True)