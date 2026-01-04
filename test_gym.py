"""
Automated Tests for Gym Assistant - Extended Version
Tests the FastMCP tools: list_classes, book_class, cancel_booking, get_my_bookings
"""
import asyncio
import json
import os
import shutil

# Test configuration
ORIGINAL_DATA_FILE = "bookings.json"

def setup_test_data():
    """Create a clean test data file."""
    test_data = [
        {"class_name": "Yoga", "day": "Monday", "time": "10:00", "slots": 2, "booked_by": []},
        {"class_name": "Pilates", "day": "Tuesday", "time": "11:00", "slots": 1, "booked_by": ["Alice"]},
    ]
    with open(ORIGINAL_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)

def backup_data():
    """Backup original data file if it exists."""
    if os.path.exists(ORIGINAL_DATA_FILE):
        shutil.copy(ORIGINAL_DATA_FILE, ORIGINAL_DATA_FILE + ".backup")

def restore_data():
    """Restore original data file from backup."""
    if os.path.exists(ORIGINAL_DATA_FILE + ".backup"):
        shutil.move(ORIGINAL_DATA_FILE + ".backup", ORIGINAL_DATA_FILE)

def get_text(result):
    """Extract text from ToolResult."""
    return result.content[0].text if result.content else ""

async def run_tests():
    """Run all tests."""
    # Import after setting up test data
    from gym_server import mcp
    
    print("=" * 50)
    print("GYM ASSISTANT - AUTOMATED TESTS (Extended)")
    print("=" * 50)
    
    results = {"passed": 0, "failed": 0}
    
    # Get tool instances
    tools = await mcp.get_tools()
    
    # Test 1: List Classes
    print("\n[TEST 1] list_classes - Basic functionality")
    try:
        result = await tools['list_classes'].run(arguments={})
        text = get_text(result)
        assert "Yoga" in text, f"Expected 'Yoga' in output, got: {text}"
        assert "Pilates" in text, f"Expected 'Pilates' in output, got: {text}"
        print("  ✓ PASSED: list_classes returns all classes")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 2: Book Class - Success
    print("\n[TEST 2] book_class - Successful booking")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "Yoga", "user_name": "TestUser"})
        text = get_text(result)
        assert "Successfully booked" in text, f"Expected success message, got: {text}"
        print("  ✓ PASSED: book_class creates booking successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 3: Book Class - Duplicate booking
    print("\n[TEST 3] book_class - Duplicate booking prevention")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "Yoga", "user_name": "TestUser"})
        text = get_text(result)
        assert "already booked" in text, f"Expected duplicate warning, got: {text}"
        print("  ✓ PASSED: book_class prevents duplicate bookings")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 4: Book Class - Class full
    print("\n[TEST 4] book_class - Class full handling")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "Pilates", "user_name": "Bob"})
        text = get_text(result)
        assert "full" in text.lower(), f"Expected 'full' message, got: {text}"
        print("  ✓ PASSED: book_class handles full classes")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 5: Book Class - Class not found
    print("\n[TEST 5] book_class - Non-existent class")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "NonExistent", "user_name": "TestUser"})
        text = get_text(result)
        assert "not found" in text.lower(), f"Expected 'not found' message, got: {text}"
        print("  ✓ PASSED: book_class handles non-existent classes")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 6: Cancel Booking - Success
    print("\n[TEST 6] cancel_booking - Successful cancellation")
    try:
        result = await tools['cancel_booking'].run(arguments={"class_name": "Yoga", "user_name": "TestUser"})
        text = get_text(result)
        assert "cancelled" in text.lower(), f"Expected cancellation message, got: {text}"
        print("  ✓ PASSED: cancel_booking works correctly")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 7: Cancel Booking - No booking exists
    print("\n[TEST 7] cancel_booking - No booking to cancel")
    try:
        result = await tools['cancel_booking'].run(arguments={"class_name": "Yoga", "user_name": "NonExistentUser"})
        text = get_text(result)
        assert "does not have" in text.lower(), f"Expected no-booking message, got: {text}"
        print("  ✓ PASSED: cancel_booking handles missing bookings")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 8: Case insensitivity
    print("\n[TEST 8] book_class - Case insensitivity")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "yOgA", "user_name": "CaseTest"})
        text = get_text(result)
        assert "Successfully booked" in text, f"Expected success with case-insensitive match, got: {text}"
        print("  ✓ PASSED: book_class is case-insensitive")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 9: Input Validation - Empty class name
    print("\n[TEST 9] book_class - Empty class name validation")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "", "user_name": "TestUser"})
        text = get_text(result)
        assert "error" in text.lower() or "empty" in text.lower(), f"Expected validation error, got: {text}"
        print("  ✓ PASSED: book_class validates empty class name")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 10: Input Validation - Empty user name
    print("\n[TEST 10] book_class - Empty user name validation")
    try:
        result = await tools['book_class'].run(arguments={"class_name": "Yoga", "user_name": "   "})
        text = get_text(result)
        assert "error" in text.lower() or "empty" in text.lower(), f"Expected validation error, got: {text}"
        print("  ✓ PASSED: book_class validates empty user name")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 11: Get My Bookings - With bookings
    print("\n[TEST 11] get_my_bookings - User with bookings")
    try:
        result = await tools['get_my_bookings'].run(arguments={"user_name": "Alice"})
        text = get_text(result)
        assert "Pilates" in text, f"Expected Pilates in bookings, got: {text}"
        print("  ✓ PASSED: get_my_bookings returns user's bookings")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Test 12: Get My Bookings - No bookings
    print("\n[TEST 12] get_my_bookings - User without bookings")
    try:
        result = await tools['get_my_bookings'].run(arguments={"user_name": "NewUser"})
        text = get_text(result)
        assert "no bookings" in text.lower(), f"Expected 'no bookings' message, got: {text}"
        print("  ✓ PASSED: get_my_bookings handles users without bookings")
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        results["failed"] += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {results['passed']} passed, {results['failed']} failed")
    print("=" * 50)
    
    return results["failed"] == 0

if __name__ == "__main__":
    print("Setting up test environment...")
    backup_data()
    setup_test_data()
    
    try:
        success = asyncio.run(run_tests())
    finally:
        restore_data()
        print("\nTest data cleaned up.")
    
    exit(0 if success else 1)
