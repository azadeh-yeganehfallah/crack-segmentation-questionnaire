import random

TOTAL_CASES = [f"case_{i:02d}" for i in range(1, 46)]
CASES_PER_PARTICIPANT = 15

CURRENT_COUNTS = {
    "case_01": 7,
    "case_02": 7,
    "case_03": 10,
    "case_04": 7,
    "case_05": 7,
    "case_06": 9,
    "case_07": 7,
    "case_08": 13,
    "case_09": 9,
    "case_10": 6,
    "case_11": 10,
    "case_12": 8,
    "case_13": 10,
    "case_14": 7,
    "case_15": 7,
    "case_16": 3,
    "case_17": 10,
    "case_18": 8,
    "case_19": 9,
    "case_20": 7,
    "case_21": 3,
    "case_22": 5,
    "case_23": 8,
    "case_24": 3,
    "case_25": 5,
    "case_26": 8,
    "case_27": 4,
    "case_28": 9,
    "case_29": 5,
    "case_30": 14,
    "case_31": 11,
    "case_32": 12,
    "case_33": 13,
    "case_34": 12,
    "case_35": 11,
    "case_36": 12,
    "case_37": 13,
    "case_38": 10,
    "case_39": 14,
    "case_40": 11,
    "case_41": 10,
    "case_42": 17,
    "case_43": 14,
    "case_44": 13,
    "case_45": 7,
}

def select_random_cases():
    counts = {case: CURRENT_COUNTS.get(case, 0) for case in TOTAL_CASES}

    sorted_cases = sorted(TOTAL_CASES, key=lambda c: counts[c])
    
    selected = sorted_cases[:CASES_PER_PARTICIPANT]
  
    random.shuffle(selected)

    return selected