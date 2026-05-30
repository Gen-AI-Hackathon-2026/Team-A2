"""
Authentication module for Synapse AI Tutor.
Uses hardcoded credentials with Streamlit session_state.
"""

# Hardcoded user credentials
USERS = {
    "user1": "123",
    "user2": "123",
    "user3": "123",
    "user4": "123",
    "demo": "demo"
}


def authenticate(username: str, password: str) -> bool:
    """
    Authenticate a user against hardcoded credentials.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if username in USERS and USERS[username] == password:
        return True
    return False


def get_all_users() -> list:
    """Return list of all registered usernames."""
    return list(USERS.keys())
