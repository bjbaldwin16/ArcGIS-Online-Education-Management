# This script was created to help automating the removal of users in education related ArcGIS Online accounts (those with a lot of turnover)
# This script could be scheduled to run at any interval (ex. daily, weekly) in an ArcGIS Online Notebook
#
# The script does the following:
    # Selects users based on their assigned 'category' in ArcGIS Online (ex. 1-year Researcher) - CATEGORY
    # Filters those users based on their account creation date and NOW (ex. More than 1-year) - DATE
    # Adds a tag with the users e-mail to the items and groups they own (if any)
    # Transfers the selected users content and groups to another user (ex. TEMPSTORAGE_baldwin) - TO_USER
    # Deletes the selected users

from datetime import datetime, timedelta

# Transfer content from one user to another
def transfer_content(from_user, to_user):
    print(f"Transferring content from {from_user.username} to {to_user.username}...")
    
    # Get all items owned by the user
    items = from_user.items(max_items=1000)
    
    for item in items:
        try:
            # Append the user's email to the item's tags
            if from_user.email:
                email_tag = from_user.email
                # Check if the email tag already exists to avoid duplicates
                if email_tag not in item.tags:
                    item.tags.append(email_tag)
                    item.update()  # Update the item with the new tags
            
            item.reassign(to_user.username)
            print(f"Transferred item: {item.title}")
        except Exception as e:
            print(f"Error transferring item {item.title}: {e}")

# Transfer groups from one user to another
def transfer_groups(from_user, to_user):
    print(f"Transferring groups from {from_user.username} to {to_user.username}...")
    
    # Get all groups where the user is an owner
    groups = from_user.groups
    
    for group in groups:
        if group.owner == from_user.username:
            try:
                # Append the user's email to the group's tags
                if from_user.email:
                    email_tag = from_user.email
                    # Check if the email tag already exists to avoid duplicates
                    if email_tag not in group.tags:
                        group.tags.append(email_tag)
                        group.update()  # Update the group with the new tags
                
                group.reassign_to(to_user.username)
                print(f"Transferred group: {group.title}")
            except Exception as e:
                print(f"Error transferring group {group.title}: {e}")

# Delete the selected user
def delete_user(user):
    print(f"Deleting user: {user.username}...")
    
    try:
        user.delete()
        print(f"User {user.username} deleted successfully.")
    except Exception as e:
        print(f"Error deleting user {user.username}: {e}")

# Select users by category and created date
def select_users_by_category_and_creation(gis, selected_category):
    print(f"Searching for users with category: {selected_category} and created more than 1 year ago...")
    
    # Fetch all users (adjust max_users if necessary)
    users = gis.users.search(max_users=1000)

    # Calculate the date 1 year ago - DATE
    one_year_ago = datetime.now() - timedelta(days=365)

    # Filter users by matching category and creation date
    matching_users = []
    for user in users:
        # Get the user's categories (if they exist)
        categories = getattr(user, 'categories', [])

        # Get the user's creation date (convert from Unix timestamp to datetime)
        created_timestamp = getattr(user, 'created', None)
        if created_timestamp:
            created_date = datetime.utcfromtimestamp(created_timestamp / 1000)  # Convert to seconds

            # Check if the selected category exists in the user's categories and if created more than 1 year ago
            if selected_category in categories and created_date < one_year_ago:
                matching_users.append(user)

    return matching_users

# Main process
if __name__ == "__main__":
    # Define the selected category (as found in a previous search) - CATEGORY
    selected_category = '/Categories/1-year Researcher'
    
    # Define the static user to whom all content/groups will be transferred - TO_USER
    to_username = "TEMPSTORAGE_baldwin"
    to_user = gis.users.get(to_username)

    if to_user:
        # Select users by category and created date
        matching_users = select_users_by_category_and_creation(gis, selected_category)

        # Transfer content and groups for each selected user, then delete the user
        if matching_users:
            for from_user in matching_users:
                print(f"\nProcessing user: {from_user.username}")
                
                # Transfer content from the user to the new owner
                transfer_content(from_user, to_user)

                # Transfer groups owned by the user to the new owner
                transfer_groups(from_user, to_user)

                # Delete the user after transferring content and groups
                #delete_user(from_user)
        else:
            print(f"No users found matching category '{selected_category}' and created more than 1 year ago.")
    else:
        print(f"Could not find the target user: {to_username}")
