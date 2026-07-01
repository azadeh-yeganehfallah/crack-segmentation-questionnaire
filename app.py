import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
import random
import json
import gspread
from google.oauth2.service_account import Credentials
import base64
from zoneinfo import ZoneInfo
from case_selector import select_random_cases

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Crack Segmentation Questionnaire",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
div[data-testid="stButton"] button {
    border: none !important;
    background: transparent !important;
    color: #1f2937 !important;
    padding: 0 !important;
    margin-bottom: 0px !important;
    text-align: left !important;
}
div[data-testid="stButton"] button p {
    font-size: 24px !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
}
div[data-testid="stButton"] {
    margin-bottom: -18px !important;
}
div[data-testid="stButton"] button:hover {
    color: #0078D4 !important;
}
.normal-card {
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    padding: 3px;
    background-color: #ffffff;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 2px;
}
.normal-card:hover {
    border-color: #a3b8cc;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.selected-card {
    border: 4px solid #0078D4;
    border-radius: 10px;
    padding: 2px;
    background-color: #f0f7ff;
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.2);
    margin-bottom: 2px;
}
.normal-card, .selected-card {
    max-width: 320px;
    margin-left: 0px;
    margin-right: 0px;
    margin-bottom: 20px;        
}
.original-title {
    font-size: 26px;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 10px;
    line-height: 1.2;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #16a34a, #22c55e) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25) !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #15803d, #16a34a) !important;
    box-shadow: 0 6px 16px rgba(34, 197, 94, 0.35) !important;
}
div[data-testid="stProgress"] {
    height: 16px !important;
    border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("images")
RESPONSE_FILE = Path("responses.csv")

# --- GOOGLE SHEETS CONNECTION ---
def connect_to_google_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("crack_questionnaire_responses").sheet1
    return sheet

# --- CONSTANTS ---
REAL_MODELS = ["model_01", "model_02", "model_03", "model_04", "model_05"]
DISPLAY_LABELS = ["A", "B", "C", "D", "E"]

CASES = [f"case_{i:02d}" for i in range(1, 46)]

MODEL_FILES = {
    "model_01": {"mask": "mask_1.png", "overlay": "overlay_1.png"},
    "model_02": {"mask": "mask_2.png", "overlay": "overlay_2.png"},
    "model_03": {"mask": "mask_3.png", "overlay": "overlay_3.png"},
    "model_04": {"mask": "mask_4.png", "overlay": "overlay_4.png"},
    "model_05": {"mask": "mask_5.png", "overlay": "overlay_5.png"},
}

# --- STATE INITIALIZATION ---
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())


if "selected_cases" not in st.session_state:
    st.session_state.selected_cases = select_random_cases()

ACTIVE_CASES = st.session_state.selected_cases

if "case_label_to_model" not in st.session_state:
    st.session_state.case_label_to_model = {}
    for case_item in ACTIVE_CASES:
        shuffled_models = REAL_MODELS.copy()
        random.shuffle(shuffled_models)
        st.session_state.case_label_to_model[case_item] = dict(
            zip(DISPLAY_LABELS, shuffled_models)
        )

if "current_case_index" not in st.session_state:
    st.session_state.current_case_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "participant_info" not in st.session_state:
    st.session_state.participant_info = {}

if "info_submitted" not in st.session_state:
    st.session_state.info_submitted = False



# --- CORE SAVE FUNCTIONS ---
def save_participant_info():
    st.session_state.participant_info = {
        "participant_name": st.session_state.get("participant_name", ""),
        "degree": st.session_state.get("degree", ""),
        "role": st.session_state.get("role", ""),
        "country": st.session_state.get("country", ""),
        "inspection_experience": st.session_state.get("inspection_experience", ""),
        "experience": st.session_state.get("experience", "")
    }

def save_current_case_answer(case_name):
    best_choice = st.session_state.get(
        f"best_selected_{case_name}",
        "None selected"
    )

    acceptable_choices = st.session_state.get(
        f"acceptable_{case_name}",
        []
    )


    if best_choice != "None selected" and best_choice not in acceptable_choices:
        acceptable_choices = [best_choice] + acceptable_choices

    st.session_state.answers[case_name] = {
        "best_choice": best_choice,
        "acceptable_choices": acceptable_choices
    }

# --- PARTICIPANT INFORMATION PAGE ---
if not st.session_state.info_submitted:
    st.title("Expert Evaluation of Crack Segmentation Masks")

    st.markdown("""
    This questionnaire is part of a research study aimed at evaluating the quality of crack segmentation results produced by deep learning models.
    Thank you very much for taking the time to participate. The questionnaire takes approximately 10 minutes to complete.
    Your responses will be used only for research purposes and only to assess the quality of AI-based crack segmentation predictions.
    """)

    st.header("Participant Information")

    st.text_input("Name (optional)", key="participant_name")
    st.selectbox("Education level", ["Bachelor's degree", "Master's degree", "PhD", "Other"], key="degree")
    st.selectbox("Current role", ["Student", "PhD student", "Researcher", "Structural engineer", "Engineer", "Professor", "Other"], key="role")
    st.text_input("Country where you currently work or study", key="country")
    st.radio("Do you have experience with visual inspection of concrete structures?", ["Yes", "No"], key="inspection_experience")
    st.selectbox("Years of experience with visual inspection of concrete structures", ["0–2", "3–5", "6–10", "More than 10"], key="experience")

    if st.button("Start Questionnaire", type="primary"):
        save_participant_info()
        st.session_state.info_submitted = True
        st.rerun()

    st.stop()

# --- INDEX BOUNDS ENFORCEMENT ---
case_index = st.session_state.current_case_index
if case_index < 0:
    case_index = 0
    st.session_state.current_case_index = 0
elif case_index >= len(ACTIVE_CASES):
    case_index = len(ACTIVE_CASES) - 1
    st.session_state.current_case_index = len(ACTIVE_CASES) - 1

case = ACTIVE_CASES[case_index]
display_case_name=f'{case_index + 1:02d}'

# --- INTRO & DEMOGRAPHICS PANEL ---
if case_index == 0:
    st.header("Image Evaluation")
    st.markdown("""
    For each case, you will see the original crack image and five AI-generated predictions.
    The questionnaire includes 15 randomly selected cases. The prediction labels (A–E) are randomized for each case, so the same label does not necessarily refer to the same model across different cases.
    Please select the prediction that you consider most representative of the actual crack. Imagine that this prediction would be used as the basis for further structural inspection analysis, such as estimating crack width, crack length, and crack continuity.
    If more than one prediction is acceptable, you may also indicate additional acceptable predictions for that case.
    The predictions may differ in the extent, continuity, shape, width, and level of detail of the detected crack region.""")

# --- MAIN QUESTIONNAIRE GRID ---
case_dir = DATA_DIR / case
original_path = case_dir / "original.png"

items = [("Original", original_path)]
for label in DISPLAY_LABELS:
    real_model = st.session_state.case_label_to_model[case][label]
    overlay_path = case_dir / MODEL_FILES[real_model]["overlay"]
    items.append((label, overlay_path))

NUM_COLS = 3
for start in range(0, len(items), NUM_COLS):
    row_items = items[start:start + NUM_COLS]
    cols = st.columns(NUM_COLS)

    for idx, (label, img_path) in enumerate(row_items):
        with cols[idx]:
            if label == "Original":
                st.markdown(f"<div class='original-title'>Original image: {display_case_name}</div>",unsafe_allow_html=True)
                if img_path.exists():
                    st.image(str(img_path), width=320)
                else:
                    st.warning(f"Missing original image: {img_path}")
            else:
                selected = st.session_state.get(f"best_selected_{case}") == label
                card_class = "selected-card" if selected else "normal-card"
                icon = "🟢" if selected else "⚪"  

                if img_path.exists():
                    with open(img_path, "rb") as image_file:
                        if st.button(f"{icon} Prediction {label}", key=f"select_{case}_{label}"):
                            st.session_state[f"best_selected_{case}"] = label
                            save_current_case_answer(case)
                            st.rerun()

                        st.markdown(f"""
                            <div class="{card_class}">
                                <img src="data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
                                style="width:100%; height:320px; object-fit:cover; border-radius:8px; display:block; margin:0px;">
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning(f"Missing overlay: {img_path}")

# --- ACCEPTABLE MULTI-SELECT ---
st.markdown(f"""
<div style="font-size:20px; margin-top:10px; margin-bottom:6px;">
    <strong>Optional:</strong> If more than one prediction is acceptable for <strong>{display_case_name}</strong>, please select all acceptable options:
</div>
""", unsafe_allow_html=True)

acceptable_choices = st.multiselect(
    label="",
    options=DISPLAY_LABELS,
    default=st.session_state.answers.get(case, {}).get("acceptable_choices", []),
    key=f"acceptable_{case}",
    label_visibility="collapsed"
)

st.session_state.answers[case] = {
    "best_choice": st.session_state.get(f"best_selected_{case}", "None selected"),
    "acceptable_choices": acceptable_choices
}
st.markdown("<div style='margin-top:-10px;'></div>", unsafe_allow_html=True)

# --- PROGRESS BAR AND CONTROL LAYOUT ---
col_progress, col_prev, col_next = st.columns([3, 1, 1])
progress_percent = int(((case_index + 1) / len(ACTIVE_CASES)) * 100)

with col_progress:
    st.markdown(f"""
        <div style="transform: translateY(-18px);">
            <div style="font-size:36px; font-weight:800; margin-bottom:8px;">
                Case {case_index + 1} of {len(ACTIVE_CASES)}
            </div>
            <div style="width:100%; background-color:#e5e7eb; border-radius:999px; height:8px; overflow:hidden;">
                <div style="width:{progress_percent}%; background:#1f8ef1; height:100%; border-radius:999px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_prev:
    # Button is disabled completely on Case 1 (index 0)
    if st.button("Previous", disabled=(case_index == 0), type="primary", use_container_width=True):

        save_current_case_answer(case)
        st.session_state.current_case_index -= 1
        st.rerun()

with col_next:
    # Button is disabled completely on Case 20 (index 19)
    if st.button("Next", disabled=(case_index == len(ACTIVE_CASES) - 1), type="primary", use_container_width=True):

        save_current_case_answer(case)
        st.session_state.current_case_index += 1
        st.rerun()

# --- SUBMISSION LOGIC ---
if case_index == len(ACTIVE_CASES) - 1:
    st.markdown("---")
    submitted = st.button("Submit Responses", type="primary")
else:
    submitted = False

if submitted:
    save_current_case_answer(case)
    participant_info = st.session_state.get("participant_info", {})

    rows = []
    participant_name_value = participant_info.get("participant_name", "")

    for case_item in ACTIVE_CASES:
        ans = st.session_state.answers.get(
            case_item,
            {"best_choice": "None selected", "acceptable_choices": []}
        )

        case_mapping = st.session_state.case_label_to_model[case_item]
        mapping_json = json.dumps(case_mapping)

        best_label = ans["best_choice"]
        best_model = "None selected" if best_label == "None selected" else case_mapping[best_label]

        acceptable_labels = ans["acceptable_choices"]
        acceptable_models = [case_mapping[lbl] for lbl in acceptable_labels]

        participant_identifier = (
            participant_name_value.strip()
            if participant_name_value.strip()
            else st.session_state.participant_id[:8]
        )

        rows.append({
            "timestamp": datetime.now(ZoneInfo("Europe/Rome")).isoformat(),
            "participant": participant_identifier,
            "degree": participant_info.get("degree", ""),
            "role": participant_info.get("role", ""),
            "country": participant_info.get("country", ""),
            "inspection_experience": participant_info.get("inspection_experience", ""),
            "experience_years": participant_info.get("experience", ""),
            "case": case_item,
            "best_prediction_label": best_label,
            "best_prediction_model": best_model,
            "acceptable_prediction_labels": ", ".join(acceptable_labels),
            "acceptable_prediction_models": ", ".join(acceptable_models),
            "mapping": mapping_json
        })

    try:
        sheet = connect_to_google_sheet()
        headers = [
            "timestamp", "participant", "degree", "role", "country",
            "inspection_experience", "experience_years", "case",
            "best_prediction_label", "best_prediction_model",
            "acceptable_prediction_labels", "acceptable_prediction_models", "mapping"
        ]

        existing_values = sheet.get_all_values()
        if not existing_values or existing_values[0] != headers:
            sheet.insert_row(headers, index=1, value_input_option="RAW")

        data_to_append = []
        for row in rows:
            data_to_append.append([
                row["timestamp"], row["participant"], row["degree"], row["role"],
                row["country"], row["inspection_experience"], row["experience_years"],
                row["case"], row["best_prediction_label"], row["best_prediction_model"],
                row["acceptable_prediction_labels"], row["acceptable_prediction_models"],
                row["mapping"]
            ])

        sheet.append_rows(data_to_append, value_input_option="RAW", table_range="A:M")
        st.success("Thank you. Your responses have been submitted successfully.")
    except Exception as e:
        st.error("There was an error while saving your responses.")
        st.exception(e)



#git add .
#git commit -m "the changes "
#git push

