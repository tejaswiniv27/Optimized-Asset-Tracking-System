from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database Connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@2911",
        database="OptimizedAsset"
    )
    return conn

# Route for Sign In
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    message = None  # Variable to store message to display
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists and credentials match
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return redirect(url_for('home'))
        else:
            message = 'Invalid username or password. Please try again or register.'
    
    return render_template('signin.html', message=message)

# Route for Loan Management
@app.route('/loan', methods=['GET', 'POST'])
def loan():
    if request.method == 'POST':
        # Retrieve form data
        person_id = request.form['person_id']
        principal_amount = request.form['principal_amount']
        loan_type = request.form['type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        monthly_emi = request.form['monthly_emi']
        interest_rate = request.form['interest_rate']
        status = request.form['status']

        # Insert the data into the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Loan (person_id, principal_amount, type, start_date, end_date, monthly_emi, interest_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (person_id, principal_amount, loan_type, start_date, end_date, monthly_emi, interest_rate, status))
        
        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()

        # Redirect to the loan page
        return redirect(url_for('loan'))
    
    # For GET request, retrieve and display existing loans
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Loan")
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('manage_loans.html', loans=loans)

# Route for Asset Management
@app.route('/asset', methods=['GET', 'POST'])
def asset():
    if request.method == 'POST':
        # Retrieve form data
        asset_name = request.form['asset_name']
        asset_type = request.form['asset_type']
        purchase_date = request.form['purchase_date']
        current_value = request.form['current_value']
        quantity = request.form['quantity']
        status = request.form['status']
        remarks = request.form['remarks']

        # Insert the data into the Asset table
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Asset (asset_name, asset_type, purchase_date, current_value, quantity, status, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (asset_name, asset_type, purchase_date, current_value, quantity, status, remarks))
        
        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()

        # Redirect to the asset page
        return redirect(url_for('asset'))
    
    # For GET request, retrieve and display existing assets
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Asset")
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('assets.html', assets=assets)

# Route for Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None  # Variable to store message to display
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the user already exists
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            message = 'Username already exists. Please sign in.'
            cursor.close()
            conn.close()
            return render_template('signin.html', message=message)
        
        # If user doesn't exist, register the user
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        
        message = 'Registration successful. Please sign in.'
        return redirect(url_for('signin', message=message))
    
    return render_template('register.html')

@app.route('/assets')
def assets():
    return render_template('assets.html')

@app.route('/manage_loans')
def manage_loans():
    return render_template('manage_loans.html')

# Home Page
@app.route('/home')
def home():
    return render_template('home.html')

# Route for displaying and adding new people
@app.route('/person', methods=['GET', 'POST'])
def person():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        employment_details = request.form['employment_details']
        date_of_birth = request.form['date_of_birth']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        photo_id = request.form['photo_id']

        # Call the stored procedure to insert a new person
        cursor.callproc('AddPerson', (name, employment_details, date_of_birth, street, city, state, photo_id))
        conn.commit()
    
    cursor.execute("SELECT * FROM Person")
    people = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('person.html', people=people)

@app.route('/edit_person/<int:person_id>', methods=['GET', 'POST'])
def edit_person(person_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        employment_details = request.form['employment_details']
        date_of_birth = request.form['date_of_birth']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        photo_id = request.form['photo_id']
        
        cursor.execute(""" 
            UPDATE Person 
            SET name = %s, employment_details = %s, date_of_birth = %s, 
                street = %s, city = %s, state = %s, photo_id = %s 
            WHERE person_id = %s
        """, (name, employment_details, date_of_birth, street, city, state, photo_id, person_id))
        conn.commit()
    
    cursor.execute("SELECT * FROM Person WHERE person_id = %s", (person_id,))
    person = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return render_template('edit_person.html', person=person)




# @app.route('/display')
# def display():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)  # dictionary=True to access columns by name
    
#     cursor.execute('''
#     SELECT 
#         p.person_id,
#         p.name AS person_name,
#         p.city,
#         p.state,
#         a.asset_id,
#         a.asset_name,
#         a.asset_type,
#         a.current_value,
#         a.status AS asset_status
#     FROM 
#         Person p
#     JOIN 
#         Asset a ON p.person_id = a.asset_id  -- assuming foreign key relationship
#     ORDER BY 
#         p.person_id;
#     ''')
    
#     data = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('display.html', data=data)


# @app.route('/display')
# def display():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     # Query for person and asset information
#     cursor.execute('''
#     SELECT 
#         p.person_id,
#         p.name AS person_name,
#         p.city,
#         p.state,
#         a.asset_type,
#         a.current_value,
#         a.status AS asset_status
#     FROM 
#         Person p
#     JOIN 
#         Asset a ON p.person_id = a.asset_id  -- assuming foreign key relationship
#     ORDER BY 
#         p.person_id;
#     ''')
#     data = cursor.fetchall()
    
#     # Query for total loan amount by person
#     cursor.execute('''
#     SELECT person_id, SUM(principal_amount) AS total_loan_amount
#     FROM Loan
#     GROUP BY person_id;
#     ''')
#     loan_totals = cursor.fetchall()

#     cursor.close()
#     conn.close()
#     return render_template('display.html', data=data, loan_totals=loan_totals)



@app.route('/display')
def display():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query for person and asset information
    cursor.execute('''
    SELECT 
        p.person_id,
        p.name AS person_name,
        p.city,
        p.state,
        a.asset_type,
        a.current_value,
        a.status AS asset_status
    FROM 
        Person p
    JOIN 
        Asset a ON p.person_id = a.asset_id
    ORDER BY 
        p.person_id;
    ''')
    data = cursor.fetchall()
    
    # Query for total loan amount by person
    cursor.execute('''
    SELECT person_id, SUM(principal_amount) AS total_loan_amount
    FROM Loan
    GROUP BY person_id;
    ''')
    loan_totals = cursor.fetchall()

    # Query for assets with loan amounts greater than 5000
    cursor.execute('''
    SELECT 
        asset_id, 
        asset_name, 
        current_value 
    FROM 
        Asset
    WHERE 
        asset_id IN (
            SELECT 
                asset_id 
            FROM 
                Loan 
            WHERE 
                principal_amount > 5000
        );
    ''')
    high_loan_assets = cursor.fetchall()

    cursor.close()
    conn.close()
    
    # Pass high_loan_assets to the template
    return render_template('display.html', data=data, loan_totals=loan_totals, high_loan_assets=high_loan_assets)




@app.route('/market')
def market():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT rate_id, asset_id, date, rate_value FROM market_rate')
    rates = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('market_rate.html', rates=rates)

@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        asset_name = request.form['asset_name']
        asset_type = request.form['asset_type']
        current_value = request.form['current_value']  # Use 'current_value' instead of 'asset_value'
        quantity = request.form['quantity']
        status = request.form['status']
        remarks = request.form['remarks']

        # Log form data
        print("Form data:", request.form)

        # Check if the asset exists
        cursor.execute("SELECT * FROM Asset WHERE asset_id = %s", (asset_id,))
        asset = cursor.fetchone()
        
        if asset is None:
            print(f"Asset with id {asset_id} not found.")
            return render_template('edit_asset.html', error="Asset not found")

        # Update the asset
        cursor.execute(""" 
            UPDATE Asset 
            SET asset_name = %s, asset_type = %s, current_value = %s, 
                quantity = %s, status = %s, remarks = %s 
            WHERE asset_id = %s
        """, (asset_name, asset_type, current_value, quantity, status, remarks, asset_id))

        # Check number of rows affected
        print(f"Rows affected: {cursor.rowcount}")
        try:
            conn.commit()
        except Exception as e:
            print(f"Error during commit: {e}")
            conn.rollback()

        # Fetch the updated asset
        cursor.execute("SELECT * FROM Asset WHERE asset_id = %s", (asset_id,))
        asset = cursor.fetchone()
        
        cursor.close()
        conn.close()

        return render_template('edit_asset.html', asset=asset)

    # For GET request, fetch and display asset
    cursor.execute("SELECT * FROM Asset WHERE asset_id = %s", (asset_id,))
    asset = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('edit_asset.html', asset=asset)





@app.route('/delete_asset/<int:asset_id>', methods=['GET', 'POST'])
def delete_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Attempt to delete the asset with the provided ID
    try:
        cursor.execute("DELETE FROM Asset WHERE asset_id = %s", (asset_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting asset with id {asset_id}: {e}")
        conn.rollback()

    cursor.close()
    conn.close()

    # Redirect to the asset management page after deletion
    return redirect(url_for('asset'))



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
