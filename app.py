from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    with sqlite3.connect('messages.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (id TEXT PRIMARY KEY, message TEXT, responses TEXT, consent_form TEXT)''')
        conn.commit()

init_db()

# Route for the main page
@app.route('/')
def index():
    with sqlite3.connect('messages.db') as conn:
        c = conn.cursor()
        c.execute("SELECT id, message, responses FROM messages WHERE consent_form IS NULL")
        messages = c.fetchall()
    return render_template('index.html', messages=messages)

# Route for submitting a message
@app.route('/submit', methods=['POST'])
def submit_message():
    message = request.form['message']
    message_id = str(uuid.uuid4())
    with sqlite3.connect('messages.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (id, message, responses) VALUES (?, ?, ?)",
                  (message_id, message, ""))
        conn.commit()
    flash(f"Your message has been submitted. Your token is: {message_id}")
    return redirect(url_for('index'))

# Route for viewing and responding to a specific message
@app.route('/message/<message_id>', methods=['GET', 'POST'])
def view_message(message_id):
    if request.method == 'POST':
        response = request.form['response']
        with sqlite3.connect('messages.db') as conn:
            c = conn.cursor()
            c.execute("SELECT responses FROM messages WHERE id = ?", (message_id,))
            current_responses = c.fetchone()[0]
            updated_responses = current_responses + f"\n{response}"
            c.execute("UPDATE messages SET responses = ? WHERE id = ?", (updated_responses, message_id))
            conn.commit()
        flash("Response submitted successfully.")
    with sqlite3.connect('messages.db') as conn:
        c = conn.cursor()
        c.execute("SELECT message, responses FROM messages WHERE id = ?", (message_id,))
        message, responses = c.fetchone()
    return render_template('message.html', message_id=message_id, message=message, responses=responses)

# Route for the consent form
@app.route('/consent', methods=['GET', 'POST'])
def consent_form():
    if request.method == 'POST':
        consent_message = request.form['consent_message']
        message_id = str(uuid.uuid4())
        with sqlite3.connect('messages.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO messages (id, message, consent_form) VALUES (?, ?, ?)",
                      (message_id, consent_message, "true"))
            conn.commit()
        flash("Your consent form has been submitted.")
        return redirect(url_for('index'))
    return render_template('consent_form.html')

if __name__ == '__main__':
    app.run(debug=True)
