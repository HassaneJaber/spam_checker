from flask import Flask, render_template, request, jsonify
import joblib
import sqlite3

app = Flask(__name__)

# Load the trained model
model = joblib.load("spam_model.pkl")

# Initialize database
def init_db():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    
    # Create table for storing messages
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY, 
                 text TEXT, 
                 prediction TEXT, 
                 confidence REAL)""")

    # Create table for storing reported incorrect predictions
    c.execute("""CREATE TABLE IF NOT EXISTS reported_messages (
                 id INTEGER PRIMARY KEY, 
                 text TEXT, 
                 correct_label TEXT)""")

    conn.commit()
    conn.close()

init_db()  # Ensure DB is created before app starts

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    message = request.form["message"]
    prediction_prob = model.predict_proba([message])[0]  # Get probability scores
    prediction = model.predict([message])[0]
    
    result = "Spam" if prediction == 1 else "Not Spam"
    confidence = round(prediction_prob.max() * 100, 2)  # Convert to percentage

    # Save message to database
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (text, prediction, confidence) VALUES (?, ?, ?)", 
              (message, result, confidence))
    conn.commit()
    conn.close()

    return jsonify({"result": result, "confidence": f"{confidence}%"})

@app.route("/report", methods=["POST"])
def report():
    message = request.form["message"]
    correct_label = request.form["correct_label"]

    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("INSERT INTO reported_messages (text, correct_label) VALUES (?, ?)", 
              (message, correct_label))
    conn.commit()
    conn.close()

    return jsonify({"status": "Reported Successfully"})

@app.route("/stats")
def stats():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM messages WHERE prediction='Spam'")
    spam_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM messages WHERE prediction='Not Spam'")
    not_spam_count = c.fetchone()[0]
    
    conn.close()
    return jsonify({"spam_count": spam_count, "not_spam_count": not_spam_count})

if __name__ == "__main__":
    app.run(debug=True)
