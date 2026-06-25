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


st.set_page_config(
    page_title="Crack Segmentation Questionnaire",
    layout="wide"
)
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

/* prediction in normal state */
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

/* prediction in selected state */
.selected-card {
    border: 4px solid #0078D4;
    border-radius: 10px;
    padding: 2px;
    background-color: #f0f7ff;
    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.2);
    margin-bottom: 2px;
}
            

.normal-card,
.selected-card {
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
    background-color: #16a34a !important;
    color: white !important;
    border: 2px solid #15803d !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
}

div[data-testid="stButton"] button[kind="primary"] p {
    font-size: 24px !important;
    font-weight: 800 !important;
}




</style>
""", unsafe_allow_html=True)





DATA_DIR = Path("images")
RESPONSE_FILE = Path("responses.csv")


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




REAL_MODELS = ["model_01", "model_02", "model_03", "model_04", "model_05"]
DISPLAY_LABELS = ["A", "B", "C", "D", "E"]

CASES = [
    "case_01", "case_02", "case_03", "case_04", "case_05",
    "case_06", "case_07", "case_08", "case_09", "case_10",
    "case_11", "case_12", "case_13", "case_14", "case_15",
    "case_16", "case_17", "case_18", "case_19", "case_20"
]

MODEL_FILES = {
    "model_01": {"mask": "mask_1.png", "overlay": "overlay_1.png"},
    "model_02": {"mask": "mask_2.png", "overlay": "overlay_2.png"},
    "model_03": {"mask": "mask_3.png", "overlay": "overlay_3.png"},
    "model_04": {"mask": "mask_4.png", "overlay": "overlay_4.png"},
    "model_05": {"mask": "mask_5.png", "overlay": "overlay_5.png"},
}





if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "case_label_to_model" not in st.session_state:
    st.session_state.case_label_to_model = {}

    for case in CASES:
        shuffled_models = REAL_MODELS.copy()
        random.shuffle(shuffled_models)
        st.session_state.case_label_to_model[case] = dict(
            zip(DISPLAY_LABELS, shuffled_models)
        )


def select_best(case, label):
    st.session_state[f"best_selected_{case}"] = label


st.title("Expert Evaluation of Crack Segmentation Masks")

st.markdown("""
This questionnaire is part of a research study aimed at evaluating the quality of crack segmentation results produced by deep learning models.

Thank you very much for taking the time to participate. The questionnaire takes approximately 10 minutes to complete.

Your responses will be used only for research purposes and only to assess the quality of AI-based crack segmentation predictions. 

As structural engineers, inspectors, or potential end-users of such AI tools, your opinion is very important. In practice, these segmentation results may be used as the basis for extracting crack-related information such as crack width, length, and continuity. Therefore, we ask you to evaluate which prediction would be most useful and reliable from an inspection point of view.


""")




st.header("Participant Information")


participant_name = st.text_input(
    "Name (optional)"
)

degree = st.selectbox(
    "Education level",
    ["Bachelor's degree", "Master's degree", "PhD", "Other"]
)

role = st.selectbox(
    "Current role",
    [
        "Student",
        "PhD student",
        "Researcher",
        "Structural engineer",
        "Professor",
        "Other"
    ]
)

country = st.text_input("Country where you currently work or study")




inspection_experience = st.radio(
    "Do you have experience with visual inspection of concrete structures?",
    ["Yes", "No"],
    key="inspection_experience"
)


experience = st.selectbox(
    "Years of experience in structural engineering / inspection",
    ["0–2", "3–5", "6–10", "More than 10"]
)


st.header("Image Evaluation")

st.markdown("""
For each case, you will see the original crack image and five AI-generated predictions.

The questionnaire includes 20 cases. The prediction labels (A–E) are randomized for each case, so the same label does not necessarily refer to the same model across different cases.

Please select the prediction that you consider most representative of the actual crack. Imagine that this prediction would be used as the basis for further structural inspection analysis, such as estimating crack width, crack length, and crack continuity.

If more than one prediction is acceptable, you may also indicate additional acceptable predictions for that case.

The predictions may differ in the extent, continuity, shape, width, and level of detail of the detected crack region.
""")

answers = {}

for case in CASES:
    case_dir = DATA_DIR / case
    original_path = case_dir / "original.png"

    st.markdown("---")
    #st.subheader(f"Original image - {case.replace('_', ' ').title()}")

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
                    st.markdown(f"<div class='original-title'>Original image: {case}</div>",
                                unsafe_allow_html=True)
                    if img_path.exists():
                        st.image(
                            str(img_path),
                            width=320
                        )
                    else:
                        st.warning(f"Missing original image: {img_path}")

                else:
                    selected = st.session_state.get(f"best_selected_{case}") == label

                    
                    card_class = "selected-card" if selected else "normal-card"
                    icon = "🟢" if selected else "⚪"  

                    
                    if img_path.exists():
                        with open(img_path, "rb") as image_file:

                            # Render the custom-styled button
                            if st.button(
                                f"{icon} Prediction {label}",
                                key=f"select_{case}_{label}"
                            ):
                                st.session_state[f"best_selected_{case}"] = label
                                st.rerun()

                            
                            st.markdown(f"""
                                <div class="{card_class}">
                                    <img src="data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
                                    style="width:100%; height:320px; object-fit:cover; border-radius:8px; display:block; margin:0px;">
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Missing overlay: {img_path}")

#<img src="data:image/png;base64,{base64.b64encode(image_file.read()).decode()}" style="width:340%; border-radius:6px; display:block;MARGIN:AUTO">
#<img src="data:image/png;base64,{base64.b64encode(image_file.read()).decode()}" style="width:100%; border-radius:10px; display:block; margin:0px;">          

    best_choice = st.session_state.get(
        f"best_selected_{case}",
        "None selected"
    )

    acceptable_choices = st.multiselect(
        f"If more than one prediction is acceptable for {case}, please select all acceptable options:",
        DISPLAY_LABELS,
        key=f"acceptable_{case}"
    )

    answers[case] = {
        "best_choice": best_choice,
        "acceptable_choices": acceptable_choices
    }


st.markdown("---")

submitted = st.button(
    "Submit questionnaire",
    type="primary",
    )

if submitted:
    rows = []

    for case, ans in answers.items():
        case_mapping = st.session_state.case_label_to_model[case]
        mapping_json = json.dumps(case_mapping)

        best_label = ans["best_choice"]

        if best_label == "None selected":
            best_model = "None selected"
        else:
            best_model = case_mapping[best_label]

        acceptable_labels = ans["acceptable_choices"]
        acceptable_models = [
            case_mapping[label]
            for label in acceptable_labels
        ]

        if participant_name.strip():
            participant_identifier = participant_name
        else:
            participant_identifier = st.session_state.participant_id[:8]

        rows.append({
            "timestamp": datetime.now().isoformat(),
            "participant": participant_identifier,
            "degree": degree,
            "role": role,
            "country": country,
            "inspection_experience": inspection_experience,
            "experience_years": experience,
            "case": case,
            "best_prediction_label": best_label,
            "best_prediction_model": best_model,
            "acceptable_prediction_labels": ", ".join(acceptable_labels),
            "acceptable_prediction_models": ", ".join(acceptable_models),
            "mapping": mapping_json
        })



    try:
        sheet = connect_to_google_sheet()

        headers = [
            "timestamp",
            "participant",
            "degree",
            "role",
            "country",
            "inspection_experience",
            "experience_years",
            "case",
            "best_prediction_label",
            "best_prediction_model",
            "acceptable_prediction_labels",
            "acceptable_prediction_models",
            "mapping"
        ]

        if len(sheet.get_all_values()) == 0:
            sheet.append_row(headers, value_input_option="RAW")

        data_to_append = []

        for row in rows:
            data_to_append.append([
                row["timestamp"],
                row["participant"],
                row["degree"],
                row["role"],
                row["country"],
                row["inspection_experience"],
                row["experience_years"],
                row["case"],
                row["best_prediction_label"],
                row["best_prediction_model"],
                row["acceptable_prediction_labels"],
                row["acceptable_prediction_models"],
                row["mapping"]
            ])

        sheet.append_rows(data_to_append, value_input_option="RAW")

        st.success("Thank you. Your responses have been submitted successfully.")

    except Exception as e:
        st.error("There was an error while saving your responses.")
        st.exception(e)




#git add .
#git commit -m "the changes "
#git push

