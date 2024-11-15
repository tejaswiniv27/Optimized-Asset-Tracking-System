from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector  # Ensure MySQL Connector is installed

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key for sessions and flash messages

# MySQL database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root@2911',
        database='OptimizedAsset'
    )

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials using SQL function
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT check_user_login(%s, %s)", (username, password))
        result = cursor.fetchone()

        # If result is 1, login is successful
        if result and result[0] == 1:
            session['logged_in'] = True
            return redirect(url_for('market_rates'))
        else:
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

# Route to view market rates
@app.route('/market_rates')
def market_rates():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT rate_id, asset_id, date, rate_value FROM market_rate')
    rates = cursor.fetchall()
    conn.close()
    return render_template('market_rates.html', rates=rates)

# Route to edit rate value
@app.route('/edit_rate/<int:rate_id>', methods=['GET', 'POST'])
def edit_rate(rate_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        new_rate_value = request.form['rate_value']
        
        try:
            cursor.execute('UPDATE market_rate SET rate_value = %s WHERE rate_id = %s', (new_rate_value, rate_id))
            conn.commit()
            conn.close()
            return redirect(url_for('market_rates'))
        except mysql.connector.Error as e:
            conn.close()
            if e.errno == 1644:  # This is the SQLSTATE error code for custom error messages raised by the SIGNAL statement
                flash('Rate value cannot be negative', 'error')
                return redirect(url_for('edit_rate', rate_id=rate_id))

    cursor.execute('SELECT rate_id, asset_id, date, rate_value FROM market_rate WHERE rate_id = %s', (rate_id,))
    rate = cursor.fetchone()
    conn.close()
    return render_template('edit_rate.html', rate=rate)

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
