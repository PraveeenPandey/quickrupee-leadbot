"""
State Machine for QuickRupee Eligibility Flow
Implements a simple finite state machine for fast, deterministic eligibility checks
"""
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re
from config import settings


class State(Enum):
    """States in the eligibility flow"""
    INIT = "init"
    GREETING = "greeting"
    ASK_EMPLOYMENT = "ask_employment"
    ASK_SALARY = "ask_salary"
    ASK_CITY = "ask_city"
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    END = "end"


@dataclass
class ConversationState:
    """Stores conversation state and user responses"""
    current_state: State = State.INIT
    is_salaried: Optional[bool] = None
    salary_above_threshold: Optional[bool] = None
    in_metro_city: Optional[bool] = None
    rejection_reason: Optional[str] = None


class EligibilityStateMachine:
    """
    Manages the eligibility screening conversation flow
    Uses rule-based logic for fast, explainable decisions
    """

    # Conversation scripts
    SCRIPTS = {
        State.GREETING: (
            "Hello! Welcome to QuickRupee Personal Loans. "
            "I'll ask you three quick questions to check your eligibility. "
            "Please answer with Yes or No. Let's begin."
        ),
        State.ASK_EMPLOYMENT: (
            "Are you currently a salaried employee?"
        ),
        State.ASK_SALARY: (
            f"Is your monthly in-hand salary above {settings.MIN_SALARY} rupees?"
        ),
        State.ASK_CITY: (
            "Do you currently live in a metro city such as Delhi, Mumbai, or Bangalore?"
        ),
        State.ELIGIBLE: (
            "Great news! You are eligible for a QuickRupee personal loan. "
            "One of our agents will call you back within the next ten minutes. "
            "Thank you for calling QuickRupee!"
        ),
        State.NOT_ELIGIBLE: (
            "Thank you for your interest in QuickRupee. "
            "Unfortunately, you do not meet our current eligibility criteria. "
            "Please feel free to check back with us in the future. "
            "Goodbye."
        ),
    }

    def __init__(self):
        self.state = ConversationState()

    def start(self) -> str:
        """Initialize conversation and return greeting"""
        self.state.current_state = State.GREETING
        return self.SCRIPTS[State.GREETING]

    def process_response(self, user_input: str) -> Dict[str, Any]:
        """
        Process user response and advance state machine

        Returns:
            dict: {
                "message": str,           # Bot's next message
                "state": str,             # Current state
                "should_end": bool,       # Whether to end call
                "is_eligible": bool|None  # Eligibility result
                "is_valid": bool          # Whether response was valid
            }
        """
        user_input = user_input.lower().strip()
        is_valid, is_yes = self._parse_yes_no(user_input)

        # State transitions
        if self.state.current_state == State.GREETING:
            return self._transition_to(State.ASK_EMPLOYMENT)

        elif self.state.current_state == State.ASK_EMPLOYMENT:
            if not is_valid:
                return self._invalid_response(State.ASK_EMPLOYMENT)
            self.state.is_salaried = is_yes
            if not is_yes:
                self.state.rejection_reason = "not_salaried"
                return self._transition_to(State.NOT_ELIGIBLE)
            return self._transition_to(State.ASK_SALARY)

        elif self.state.current_state == State.ASK_SALARY:
            if not is_valid:
                return self._invalid_response(State.ASK_SALARY)
            self.state.salary_above_threshold = is_yes
            if not is_yes:
                self.state.rejection_reason = "salary_below_threshold"
                return self._transition_to(State.NOT_ELIGIBLE)
            return self._transition_to(State.ASK_CITY)

        elif self.state.current_state == State.ASK_CITY:
            if not is_valid:
                return self._invalid_response(State.ASK_CITY)
            self.state.in_metro_city = is_yes
            if not is_yes:
                self.state.rejection_reason = "not_in_metro"
                return self._transition_to(State.NOT_ELIGIBLE)
            return self._transition_to(State.ELIGIBLE)

        else:
            # Shouldn't reach here, but handle gracefully
            return self._transition_to(State.END)

    def _transition_to(self, new_state: State) -> Dict[str, Any]:
        """Transition to new state and return response"""
        self.state.current_state = new_state

        # Determine if call should end and eligibility status
        should_end = new_state in [State.ELIGIBLE, State.NOT_ELIGIBLE]
        is_eligible = None
        if new_state == State.ELIGIBLE:
            is_eligible = True
        elif new_state == State.NOT_ELIGIBLE:
            is_eligible = False

        message = self.SCRIPTS.get(new_state, "")

        return {
            "message": message,
            "state": new_state.value,
            "should_end": should_end,
            "is_eligible": is_eligible,
            "rejection_reason": self.state.rejection_reason,
            "is_valid": True,
        }

    def _invalid_response(self, current_state: State) -> Dict[str, Any]:
        """Handle invalid response - ask user to say yes or no and repeat question"""
        # Don't change state - stay in same question
        clarification = "I'm sorry, I didn't understand. Please say Yes or No. "
        question = self.SCRIPTS.get(current_state, "")

        return {
            "message": clarification + question,
            "state": current_state.value,
            "should_end": False,
            "is_eligible": None,
            "rejection_reason": None,
            "is_valid": False,
        }

    def _parse_yes_no(self, text: str) -> tuple[bool, bool]:
        """
        Parse user input to determine yes/no response
        Handles various affirmative and negative responses

        Returns:
            tuple[bool, bool]: (is_valid, is_yes)
            - is_valid: True if response is clearly yes or no, False otherwise
            - is_yes: True for yes, False for no (only meaningful if is_valid=True)
        """
        # Affirmative patterns
        yes_patterns = [
            r'\byes\b', r'\byeah\b', r'\byep\b', r'\byup\b',
            r'\bsure\b', r'\baffirmative\b', r'\bcorrect\b',
            r'\bright\b', r'\bha\b', r'\bhaan\b'
        ]

        # Negative patterns
        no_patterns = [
            r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bnegative\b',
            r'\bnot\b', r'\bnahi\b', r'\bnahin\b'
        ]

        has_yes = False
        has_no = False

        # Check for yes patterns
        for pattern in yes_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_yes = True
                break

        # Check for no patterns
        for pattern in no_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_no = True
                break

        # Valid response if we found yes OR no (but not both)
        if has_yes and not has_no:
            return (True, True)  # Valid yes
        elif has_no and not has_yes:
            return (True, False)  # Valid no
        else:
            return (False, False)  # Invalid or ambiguous

    def get_current_state(self) -> str:
        """Get current state name"""
        return self.state.current_state.value

    def is_complete(self) -> bool:
        """Check if conversation is complete"""
        return self.state.current_state in [State.ELIGIBLE, State.NOT_ELIGIBLE, State.END]
