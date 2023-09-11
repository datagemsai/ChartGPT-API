"""
Download `closed_beta_email_addresses_waitlist` collection to a CSV file from Firestore
"""

from datetime import datetime

import pandas as pd

from app import db

# Get all documents in the collection
closed_beta_email_addresses_waitlist_stream = db.collection(
    "closed_beta_email_addresses_waitlist"
).stream()
closed_beta_email_addresses_waitlist = [
    doc.id for doc in closed_beta_email_addresses_waitlist_stream
]

closed_beta_email_addresses_stream = db.collection(
    "closed_beta_email_addresses"
).stream()
closed_beta_email_addresses = [doc.id for doc in closed_beta_email_addresses_stream]

# Convert list of dictionaries to a DataFrame
df = pd.DataFrame(closed_beta_email_addresses)
df_waitlist = pd.DataFrame(closed_beta_email_addresses_waitlist)

# Save DataFrame to CSV file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

df.to_csv(f"email_waitlists/closed_beta_email_addresses_{timestamp}.csv", index=False)
df_waitlist.to_csv(
    f"email_waitlists/closed_beta_email_addresses_waitlist_{timestamp}.csv", index=False
)
