import sqlite3

# Connect to the database
conn = sqlite3.connect("messages.db")
c = conn.cursor()

# Fetch all stored messages
c.execute("SELECT * FROM messages")
rows = c.fetchall()

# Display results
print("\nStored Messages in Database:\n")
for row in rows:
    print(f"ID: {row[0]} | Message: {row[1]} | Prediction: {row[2]} | Confidence: {row[3]}%")

conn.close()
