"""
Simple text-based interaction tester
Shows how the state machine works without voice
"""
from state_machine import EligibilityStateMachine

def interactive_demo():
    """Run an interactive text-based demo"""
    print("\n" + "="*60)
    print("🎙️  QuickRupee Voice Bot - Interactive Demo")
    print("="*60)
    print("\nType 'yes' or 'no' to answer each question")
    print("Type 'quit' to exit\n")
    
    sm = EligibilityStateMachine()
    
    # Start conversation
    greeting = sm.start()
    print(f"Bot: {greeting}\n")
    
    # Ask questions
    while not sm.is_complete():
        # Get current question
        current_state = sm.get_current_state()
        
        # Get user input
        user_input = input("You: ").strip().lower()
        
        if user_input == 'quit':
            print("\nExiting demo. Goodbye!")
            break
        
        if user_input not in ['yes', 'no', 'yeah', 'nope', 'yep', 'nah']:
            print("Please answer with 'yes' or 'no'\n")
            continue
        
        # Process response
        result = sm.process_response(user_input)
        
        print(f"\nBot: {result['message']}")
        print(f"[State: {result['state']}]")
        
        if result['should_end']:
            if result['is_eligible']:
                print("\n✅ Result: ELIGIBLE")
            else:
                print("\n❌ Result: NOT ELIGIBLE")
            print("="*60 + "\n")
            break
        
        print()  # Empty line for readability

if __name__ == "__main__":
    interactive_demo()
