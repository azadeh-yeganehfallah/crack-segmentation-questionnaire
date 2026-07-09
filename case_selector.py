import random

TOTAL_CASES = [f"case_{i:02d}" for i in range(1, 46)]
CASES_PER_PARTICIPANT = 15

CURRENT_COUNTS = {
    "case_01": 11,
    "case_02": 11,
    "case_03": 12,
    "case_04": 13,
    "case_05": 11,
    "case_06": 11,
    "case_07": 13,
    "case_08": 15,
    "case_09": 11,
    "case_10": 10,
    "case_11": 12,
    "case_12": 8,
    "case_13": 12,
    "case_14": 11,
    "case_15": 11,
    "case_16": 7,
    "case_17": 12,
    "case_18": 8,
    "case_19": 9,
    "case_20": 7,
    "case_21": 7,
    "case_22": 9,
    "case_23": 8,
    "case_24": 9,
    "case_25": 9,
    "case_26": 8,
    "case_27": 8,
    "case_28": 11,
    "case_29": 9,
    "case_30": 14,
    "case_31": 11,
    "case_32": 14,
    "case_33": 13,
    "case_34": 14,
    "case_35": 11,
    "case_36": 12,
    "case_37": 13,
    "case_38": 10,
    "case_39": 14,
    "case_40": 11,
    "case_41": 10,
    "case_42": 19,
    "case_43": 16,
    "case_44": 13,
    "case_45": 7,
}

def select_random_cases():
    counts = {case: CURRENT_COUNTS.get(case, 0) for case in TOTAL_CASES}

    sorted_cases = sorted(TOTAL_CASES, key=lambda c: counts[c])
    
    selected = sorted_cases[:CASES_PER_PARTICIPANT]
  
    random.shuffle(selected)

    return selected


