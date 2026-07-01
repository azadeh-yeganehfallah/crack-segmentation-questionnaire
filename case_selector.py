import random

TOTAL_CASES = [f"case_{i:02d}" for i in range(1, 46)]
CASES_PER_PARTICIPANT = 15


def select_random_cases():
    """
    Simple random selection:
    Selects 15 cases from 45 cases.
    """
    return random.sample(TOTAL_CASES, CASES_PER_PARTICIPANT)