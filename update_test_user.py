#!/usr/bin/env python3
"""Update test user to have subscription or reset estimate count"""

import sqlite3

# Connect to database
conn = sqlite3.connect('backend/specsharp.db')
cursor = conn.cursor()

# Find test user
cursor.execute("SELECT id, email, estimate_count, is_subscribed FROM users WHERE email = 'test2@example.com'")
user = cursor.fetchone()

if user:
    user_id, email, estimate_count, is_subscribed = user
    print(f"Found user: {email}")
    print(f"Current estimate count: {estimate_count}")
    print(f"Is subscribed: {is_subscribed}")
    
    # Update user to be subscribed
    cursor.execute("UPDATE users SET is_subscribed = 1, estimate_count = 0 WHERE id = ?", (user_id,))
    conn.commit()
    
    print("\nUpdated user to be subscribed and reset estimate count")
else:
    print("Test user not found")

conn.close()