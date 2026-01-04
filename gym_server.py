from fastmcp import FastMCP
import json
import os

# Initialize FastMCP server
mcp = FastMCP("GymAssistant")

# Use absolute path based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "bookings.json")

def load_data():
    """Load booking data from JSON file with error handling."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Validate data structure
            if not isinstance(data, list):
                print(f"Warning: Invalid data format in {DATA_FILE}, resetting to empty list")
                return []
            return data
    except json.JSONDecodeError as e:
        print(f"Warning: JSON decode error in {DATA_FILE}: {e}")
        return []
    except Exception as e:
        print(f"Warning: Error loading data: {e}")
        return []

def save_data(data):
    """Save booking data to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")

@mcp.tool()
def list_classes() -> str:
    """Lists all available gym classes with their details."""
    data = load_data()
    if not data:
        return "No classes available."
    
    result = "Available Classes:\n"
    for c in data:
        try:
            slots_left = c['slots'] - len(c['booked_by'])
            result += f"- {c['class_name']} ({c['day']} {c['time']}): {slots_left} slots left\n"
        except KeyError as e:
            result += f"- [Invalid class data: missing {e}]\n"
    return result

@mcp.tool()
def book_class(class_name: str, user_name: str) -> str:
    """Books a class for a user. Returns success or error message.
    
    Args:
        class_name: Name of the class to book (e.g., Yoga, Pilates)
        user_name: Name of the user making the booking
    """
    # Input validation
    if not class_name or not class_name.strip():
        return "Error: Class name cannot be empty."
    if not user_name or not user_name.strip():
        return "Error: User name cannot be empty."
    
    class_name = class_name.strip()
    user_name = user_name.strip()
    
    data = load_data()
    for c in data:
        if c['class_name'].lower() == class_name.lower():
            if user_name in c['booked_by']:
                return f"{user_name} is already booked for {c['class_name']}."
            
            if len(c['booked_by']) < c['slots']:
                c['booked_by'].append(user_name)
                save_data(data)
                return f"Successfully booked {c['class_name']} for {user_name}."
            else:
                return f"Sorry, {c['class_name']} is full."
    return f"Class '{class_name}' not found."

@mcp.tool()
def cancel_booking(class_name: str, user_name: str) -> str:
    """Cancels a booking for a user. Returns success or error message.
    
    Args:
        class_name: Name of the class to cancel
        user_name: Name of the user cancelling the booking
    """
    # Input validation
    if not class_name or not class_name.strip():
        return "Error: Class name cannot be empty."
    if not user_name or not user_name.strip():
        return "Error: User name cannot be empty."
    
    class_name = class_name.strip()
    user_name = user_name.strip()
    
    data = load_data()
    for c in data:
        if c['class_name'].lower() == class_name.lower():
            if user_name in c['booked_by']:
                c['booked_by'].remove(user_name)
                save_data(data)
                return f"Booking cancelled for {user_name} in {c['class_name']}."
            else:
                return f"{user_name} does not have a booking for {c['class_name']}."
    return f"Class '{class_name}' not found."

@mcp.tool()
def get_my_bookings(user_name: str) -> str:
    """Gets all bookings for a specific user.
    
    Args:
        user_name: Name of the user to check bookings for
    """
    if not user_name or not user_name.strip():
        return "Error: User name cannot be empty."
    
    user_name = user_name.strip()
    data = load_data()
    bookings = []
    
    for c in data:
        if user_name in c['booked_by']:
            bookings.append(f"- {c['class_name']} ({c['day']} {c['time']})")
    
    if bookings:
        return f"Bookings for {user_name}:\n" + "\n".join(bookings)
    else:
        return f"{user_name} has no bookings."

if __name__ == "__main__":
    mcp.run()
