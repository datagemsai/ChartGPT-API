"""
Transfer all email addresses in `closed_beta_email_addresses_waitlist` collection
to `closed_beta_email_addresses` collection in Firestore, unless it already exists
"""

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

# If email was successfully transferred, delete it from the waitlist
for email_address in closed_beta_email_addresses_waitlist:
    if email_address in closed_beta_email_addresses:
        print(
            f"Deleting email address {email_address} from closed_beta_email_addresses_waitlist collection"
        )
        db.collection("closed_beta_email_addresses_waitlist").document(
            email_address
        ).delete()
    else:
        print(
            f"Email address {email_address} does not exist in closed_beta_email_addresses_waitlist collection"
        )
