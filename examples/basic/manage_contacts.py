#!/usr/bin/env python3
"""Example: Manage contacts in Pylon.

This example demonstrates how to:
- List all contacts
- Search for contacts
- Get a specific contact by ID
- Create a new contact
"""

import os

from pylon import PylonClient


def main():
    """Demonstrate contact management operations."""
    api_key = os.environ.get("PYLON_API_KEY")
    if not api_key:
        print("Please set PYLON_API_KEY environment variable")
        return

    with PylonClient(api_key=api_key) as client:
        # List contacts
        print("=== Listing Contacts ===")
        for contact_count, contact in enumerate(client.contacts.list(), start=1):
            print(f"  {contact.name} ({contact.email})")
            if contact_count >= 10:
                print("  ... (showing first 10)")
                break

        # Search for a specific contact
        print("\n=== Searching Contacts ===")
        search_query = "john"
        print(f"Searching for '{search_query}'...")
        for contact in client.contacts.search(search_query, limit=5):
            print(f"  Found: {contact.name} - {contact.email}")

        # List accounts
        print("\n=== Listing Accounts ===")
        for account_count, account in enumerate(client.accounts.list(), start=1):
            print(f"  {account.name} ({account.type})")
            if account_count >= 10:
                print("  ... (showing first 10)")
                break


def example_get_contact():
    """Get a specific contact by ID."""
    with PylonClient() as client:
        contact_id = "contact_abc123"  # Replace with actual ID
        try:
            contact = client.contacts.get(contact_id)
            print(f"Contact: {contact.name}")
            print(f"Email: {contact.email}")
            print(f"Portal Role: {contact.portal_role}")
            if contact.account:
                print(f"Account ID: {contact.account.id}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
