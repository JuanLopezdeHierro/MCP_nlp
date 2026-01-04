from fastmcp import FastMCP
import json
import os

# Initialize FastMCP server
mcp = FastMCP("GymAssistant")

DATA_FILE = "bookings.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def list_classes() -> str:
    """Lists all available gym classes with their details."""
    data = load_data()
    if not data:
        return "No classes available."
    
    result = "Available Classes:\n"
    for c in data:
        slots_left = c['slots'] - len(c['booked_by'])
        result += f"- {c['class_name']} ({c['day']} {c['time']}): {slots_left} slots left\n"
    return result

@mcp.tool()
def book_class(class_name: str, user_name: str) -> str:
    """Books a class for a user. Returns success or error message."""
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
    """Cancels a booking for a user. Returns success or error message."""
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

if __name__ == "__main__":
    mcp.run()
