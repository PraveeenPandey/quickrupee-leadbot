"""
Test script for State Machine
Run this to test the eligibility logic without needing phone calls
"""
from state_machine import EligibilityStateMachine


def test_scenario(name: str, responses: list):
    """Test a conversation scenario"""
    print(f"\n{'='*60}")
    print(f"Testing Scenario: {name}")
    print('='*60)

    sm = EligibilityStateMachine()

    # Start conversation
    greeting = sm.start()
    print(f"Bot: {greeting}\n")

    # Process each response
    for i, response in enumerate(responses, 1):
        print(f"User: {response}")
        result = sm.process_response(response)

        print(f"Bot: {result['message']}")
        print(f"State: {result['state']}")

        if not result.get('is_valid', True):
            print(f"⚠️  Invalid response - re-asking question")

        if result['should_end']:
            print(f"\n✓ Call ended")
            print(f"✓ Eligible: {result['is_eligible']}")
            if result['rejection_reason']:
                print(f"✓ Reason: {result['rejection_reason']}")
            break

        print()


def run_tests():
    """Run all test scenarios"""
    print("🧪 QuickRupee Voice Bot - State Machine Tests")

    # Scenario 1: All eligible
    test_scenario(
        "Eligible Candidate (All Yes)",
        ["yes", "yes", "yes"]
    )

    # Scenario 2: Not salaried
    test_scenario(
        "Not Salaried Employee",
        ["no"]
    )

    # Scenario 3: Salary too low
    test_scenario(
        "Salary Below Threshold",
        ["yes", "no"]
    )

    # Scenario 4: Not in metro city
    test_scenario(
        "Not in Metro City",
        ["yes", "yes", "no"]
    )

    # Scenario 5: Different yes/no variations
    test_scenario(
        "Eligible with Variations (yeah, yep, sure)",
        ["yeah", "yep", "sure"]
    )

    # Scenario 6: Negative variations
    test_scenario(
        "Not Eligible with Variations (nope, nah)",
        ["yes", "nope"]
    )

    # Scenario 7: Invalid response handling
    test_scenario(
        "Invalid Response - Full Sentence",
        ["I am currently working as a software engineer", "yes", "yes", "yes"]
    )

    # Scenario 8: Invalid response handling - multiple times
    test_scenario(
        "Multiple Invalid Responses",
        ["maybe", "I'm not sure", "yes", "yes", "yes"]
    )

    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print('='*60)


if __name__ == "__main__":
    run_tests()
