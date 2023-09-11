"""
Transfer all email addresses from a CSV file
to `closed_beta_email_addresses` collection in Firestore, unless it already exists
"""

import pandas as pd

from app import db

# Get all email addresses from CSV with header
filename = "20230904.csv"
closed_beta_email_addresses_df = pd.read_csv(f"email_waitlists/form_signups/{filename}")
closed_beta_email_addresses_waitlist = closed_beta_email_addresses_df[
    "user_email"
].tolist()

closed_beta_email_addresses_stream = db.collection(
    "closed_beta_email_addresses"
).stream()
closed_beta_email_addresses = [doc.id for doc in closed_beta_email_addresses_stream]

# Transfer email addresses from waitlist
for email_address in closed_beta_email_addresses_waitlist:
    if email_address not in closed_beta_email_addresses:
        print(
            f"Adding email address {email_address} to closed_beta_email_addresses collection"
        )
        db.collection("closed_beta_email_addresses").document(email_address).set({})
    else:
        print(
            f"Email address {email_address} already exists in closed_beta_email_addresses collection"
        )
