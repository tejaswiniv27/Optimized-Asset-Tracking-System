from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)  # Corrected __name__ here
app.secret_key = 'your_secret_key'

# Predefined credentials and roles
PREDEFINED_CREDENTIALS = {
    'admin1': {'password': 'password123', 'role': 'editor'},
    'admin2': {'password': 'password456', 'role': 'viewer'}
}

# MySQL database connection function
def get_db_connection(username):
    user_role = PREDEFINED_CREDENTIALS[username]['role']
    db_user = username if user_role == 'editor' else 'admin2'
    db_password = PREDEFINED_CREDENTIALS[username]['password']
    
    return mysql.connector.connect(
        host='localhost',
        user=db_user,
        password=db_password,
        database='OptimizedAsset'
    )

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check predefined credentials
        if username in PREDEFINED_CREDENTIALS and PREDEFINED_CREDENTIALS[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('market_rates'))
        else:
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

# Route to view market rates
@app.route('/market_rates')
def market_rates():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    conn = get_db_connection(session['username'])
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT rate_id, asset_id, date, rate_value FROM market_rate')
    rates = cursor.fetchall()
    conn.close()
    return render_template('market_rates.html', rates=rates)

# Route to edit rate value
@app.route('/edit_rate/<int:rate_id>', methods=['GET', 'POST'])
def edit_rate(rate_id):
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    username = session['username']
    if PREDEFINED_CREDENTIALS[username]['role'] == 'viewer':
        flash("You are not given permission to edit anything", 'error')
        return redirect(url_for('market_rates'))

    conn = get_db_connection(username)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        new_rate_value = request.form['rate_value']
        
        try:
            cursor.execute('UPDATE market_rate SET rate_value = %s WHERE rate_id = %s', (new_rate_value, rate_id))
            conn.commit()
            flash("Rate updated successfully", 'success')
        except mysql.connector.Error as e:
            if e.errno == 1644:  # Custom error for validation
                flash('Rate value cannot be negative', 'error')
            else:
                flash("Error updating rate", 'error')
        finally:
            conn.close()
            return redirect(url_for('market_rates'))

    cursor.execute('SELECT rate_id, asset_id, date, rate_value FROM market_rate WHERE rate_id = %s', (rate_id,))
    rate = cursor.fetchone()
    conn.close()
    return render_template('edit_rate.html', rate=rate)

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
