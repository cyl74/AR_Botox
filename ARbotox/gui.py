import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import mediapipe as mp
from src.vision.ArBotox import ArBotox, DrawOptions
from datetime import datetime, date, time
from PIL import Image

# Import database functions
from db_api import db

# Config
st.set_page_config(
    page_title='AR Botox',
    page_icon='💉',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Load injection data
injection_data = pd.read_csv('data/mapped_landmarks_to_regions.csv')
mp_data = pd.read_csv('data/mp_pointData/mpPoint.csv')
injection_points = pd.merge(injection_data, mp_data, left_on='landmark', right_on='mp_point').reset_index(drop=True)
selected_items = []

# Style sheet
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e7f8ff;
    }
    .stApp * {
        color: #808080;
    }
    div[data-testid="stHorizontalBlock"] > div {
        box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.3);
        padding: 10px;
        border-radius: 5px;
        background-color: #ffffff;
        text-align: center;
    }
    img {
        border-radius: 3px;
    }
    header {visibility: hidden;}
    div[data-testid="stTabs"] div[data-testid="stTabs"] > div {
        max-height: 67vh;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<h1 style="font-family: Tahoma, sans-serif; font-size: 56px"><span style="color:#202a7a;">💉AR '
            'Botox</span></h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="font-size: 16px"><span style="color:#202a7a;"><strong>This tool overlays facial injection points to '
    'guide with Botox treatment using Augmented Reality.<strong></span></p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 0.7, 0.7], gap='medium')

# Patient Information
with col2:
    st.markdown('<h1 style="font-size: 28px"><span style="color:#202a7a;">Patient Information</span></h1>',
                unsafe_allow_html=True)
    reference, details, search_tab, add_patient, appointments_tab = st.tabs(['Reference', 'Details', 'Search', 'Add Patient', 'Appointments'])

    # Reference image
    with reference:
        reference_image = st.image(
            "https://t3.ftcdn.net/jpg/05/16/27/58/360_F_516275801_f3Fsp17x6HQK0xQgDQEELoTuERO4SsWV.jpg",
            use_container_width=True)

        uploaded_patient_image = st.file_uploader('Upload the patient\'s image for injection point reference.')
        if uploaded_patient_image is not None:

            # Save the uploaded image
            path = 'uploaded_reference_image.png'
            with open(path, "wb") as f:
                f.write(uploaded_patient_image.getbuffer())

            injections = injection_data = pd.read_csv('data/inputs/injections.csv')
            regions = []
            treatment_types = []

            selected_points = pd.DataFrame(selected_items)
            for index, point in selected_points.iterrows():
                id = point['landmark']
                injection = injections[injections['point'] == id]

                regions.append(point['region_name'])
                treatment_types.append(injection['treatment_type'].iloc[0])

            draw_options = DrawOptions(
                regions=regions,
                treatment_type=treatment_types,
                draw_all_injections=True,
                draw_tesselations=False,
                draw_all_regions=True
            )

            # arBotox.detect_on_image_proto(WOMAN_1, draw_options)
            arBotox = ArBotox(reload_data_to_database=False)
            arBotox.detect_on_image_proto(image_path=path, drawing_options=draw_options, st_frame=reference_image)

    # Add Patient Tab
    with add_patient:
        with st.form('add_patient_form'):
            name = st.text_input('Full Name')
            contact_info = st.text_input('Contact Info')
            birthdate = st.date_input(
            'Date of Birth',
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            )
            medical_history = st.text_area('Medical History')
            submitted = st.form_submit_button('Add Patient')

            if submitted:
                new_patient = db.add_patient(
                    name=name,
                    contact_info=contact_info,
                    birthdate=birthdate,
                    medical_history=medical_history
                )
                st.success(f'Patient {new_patient.name} added successfully with ID {new_patient.patient_id}')

    # Database search
    with search_tab:
        search_query = st.text_input('Search by Patient Name', key='search_tab_query', placeholder='Enter patient name')

        # Check if search_results is in session_state, otherwise initialize it
        if 'search_results' not in st.session_state:
            st.session_state['search_results'] = []

        if st.button('Search', key='search_tab_button'):
            patients = db.search_patients(search_query)
            st.session_state['search_results'] = patients  
        else:
            patients = st.session_state.get('search_results', [])

        if patients:
            st.write('### Search Results:')
            for patient in patients:
                if st.button(f'**Name:** {patient.name}, **Patient ID:** {patient.patient_id}', key=f'search_tab_select_{patient.patient_id}',):
                    st.session_state['selected_patient'] = patient.patient_id
                    st.success(f"Patient {patient.name} selected. Go to the 'Details' tab to view details.")
        elif len(search_query) > 0:
            st.write('No patients found.')

    # Patient Details
    with details:
        # Check if a patient has been selected in the session state
        if 'selected_patient' in st.session_state:
            patient = db.get_patient_by_id(st.session_state['selected_patient'])  

            if patient:
                st.write(f"**First Name:** {patient.name.split()[0] if ' ' in patient.name else patient.name}")
                st.write(f"**Last Name:** {patient.name.split()[-1] if ' ' in patient.name else 'N/A'}")
                st.write(f"**Date of Birth:** {patient.birthdate}")
                st.write(f"**Contact:** {patient.contact_info}")
                st.write(f"**Medical History:** {patient.medical_history}")
            else:
                st.write("No details available for the selected patient.")
        else:
            st.write("No patient selected. Please use the 'Search' tab to select a patient.")

    # Appointments/treatment details of a patient
    with appointments_tab:
        if 'selected_patient' in st.session_state:
            patient_id = st.session_state['selected_patient']

            if 'show_schedule_form' not in st.session_state:
                st.session_state['show_schedule_form'] = False

            if st.button('Schedule New Appointment'):
                st.session_state['show_schedule_form'] = True

            if st.session_state['show_schedule_form']:
                st.markdown('### Select Treatments')
                treatments = db.get_all_treatment_info()

                if treatments:
                    # Create a dictionary mapping treatment names to their IDs
                    treatment_options = {t.treatment_name: t.treatment_info_id for t in treatments}

                    selected_treatments = st.multiselect(
                        'Select Treatments', 
                        options=list(treatment_options.keys()), 
                        key='selected_treatments'
                    )
                else:
                    st.warning("No treatments available. Please add treatments before scheduling appointments.")
                    selected_treatments = []

                with st.form('schedule_appointment_form'):
                    appointment_date = st.date_input('Appointment Date', value=date.today())
                    clinician_name = st.text_input('Clinician Name')
                    location = st.text_input('Location')
                    appointment_details = st.text_area('Appointment Details')

                    treatment_details_dict = {}
                    for treatment in selected_treatments:
                        # Use a unique key for each text area to maintain state
                        treatment_details = st.text_area(
                            f'Details for {treatment}', 
                            key=f'details_{treatment}'
                        )
                        treatment_details_dict[treatment] = treatment_details

                    submitted = st.form_submit_button('Schedule Appointment')

                if submitted:
                    if not selected_treatments:
                        st.error("Please select at least one treatment.")
                    else:
                        try:
                            # Fetch or add clinician
                            clinician = db.get_clinician_by_name(clinician_name)
                            if not clinician:
                                clinician = db.add_clinician(clinician_name)

                            if clinician is None:
                                st.error("Failed to add clinician. Please check the logs.")
                            else:
                                # Schedule the appointment
                                new_appointment = db.schedule_appointment(
                                    patient_id=patient_id,
                                    clinician_id=clinician.clinician_id,
                                    appointment_date=appointment_date,
                                    location=location,
                                    details=appointment_details
                                )
                                if new_appointment is not None:
                                    # Add Treatment Histories
                                    for treatment_name in selected_treatments:
                                        treatment_info_id = treatment_options[treatment_name]
                                        treatment_details = treatment_details_dict.get(treatment_name, "")
                                        db.add_treatment_history(
                                            appointment_id=new_appointment.appointment_id,
                                            treatment_details=treatment_details,
                                            treatment_info_id=treatment_info_id
                                        )
                                    st.success(
                                        f'Appointment scheduled on {new_appointment.appointment_date.strftime("%Y-%m-%d")} with {clinician.name}'
                                    )
                                    st.session_state['show_schedule_form'] = False
                                else:
                                    st.error("Failed to schedule appointment. Please check the logs.")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
            else:
                # Display upcoming appointments
                upcoming_appointments = db.get_upcoming_appointments(patient_id)
                if upcoming_appointments:
                    st.write('##### Upcoming Appointments')
                    for appointment in upcoming_appointments:
                        with st.expander(f"Appointment on {appointment.appointment_date.strftime('%Y-%m-%d')}"):
                            st.write(f"**Clinician:** {appointment.clinician.name}")
                            
                            if appointment.details:
                                st.write(f"**Appointment Details:** {appointment.details}")

                            treatment_histories = db.get_treatment_history_by_appointment(appointment.appointment_id)
                            if treatment_histories:
                                st.write("**Treatments:**")
                                for th in treatment_histories:
                                    st.write(f"- **Treatment:** {th.treatment_info.treatment_name}")
                                    st.write(f"  - **Treatment Details:** {th.treatment_details}")
                                    st.write(f"  - **Number of Injections:** {th.treatment_info.num_injections}")
                                    st.write(f"  - **Notes:** {th.treatment_info.notes}")
                            else:
                                st.write("No treatments recorded for this appointment.")
                else:
                    st.write("No upcoming appointments.")

                # Display past appointments
                past_appointments = db.get_past_appointments(patient_id)
                if past_appointments:
                    st.write('##### Past Appointments')
                    for appointment in past_appointments:
                        with st.expander(f"Appointment on {appointment.appointment_date.strftime('%Y-%m-%d')}"):
                            st.write(f"**Clinician:** {appointment.clinician.name}")

                            if appointment.details:
                                st.write(f"**Appointment Details:** {appointment.details}")

                            treatment_histories = db.get_treatment_history_by_appointment(appointment.appointment_id)
                            if treatment_histories:
                                st.write("**Treatments:**")
                                for th in treatment_histories:
                                    st.write(f"- **Treatment:** {th.treatment_info.treatment_name}")
                                    st.write(f"  - **Details:** {th.treatment_details}")
                                    st.write(f"  - **Number of Injections:** {th.treatment_info.num_injections}")
                                    st.write(f"  - **Notes:** {th.treatment_info.notes}")
                            else:
                                st.write("No treatments recorded for this appointment.")
                else:
                    st.write("No past appointments.")

            st.markdown('### Manage Treatments')
            with st.expander("Add New Treatment"):
                with st.form('add_treatment_form'):
                    treatment_name = st.text_input('Treatment Name')
                    num_injections = st.number_input('Number of Injections', min_value=1, step=1)
                    notes = st.text_area('Notes')
                    add_treatment_submitted = st.form_submit_button('Add Treatment')

                    if add_treatment_submitted:
                        if not treatment_name:
                            st.error("Treatment name cannot be empty.")
                        else:
                            try:
                                new_treatment = db.add_treatment_info(
                                    treatment_name=treatment_name,
                                    num_injections=num_injections,
                                    notes=notes
                                )
                                st.success(f'Treatment "{new_treatment.treatment_name}" added successfully.')
                            except Exception as e:
                                st.error(f"An error occurred while adding the treatment: {e}")

            with st.expander("View Existing Treatments"):
                st.markdown('##### Existing Treatments')
                treatments = db.get_all_treatment_info()
                if treatments:
                    for treatment in treatments:
                        st.write(f"**Name:** {treatment.treatment_name}")
                        st.write(f"**Number of Injections:** {treatment.num_injections}")
                        st.write(f"**Notes:** {treatment.notes}")
                        st.markdown("---")
                else:
                    st.write("No treatments available.")
        else:
            st.write("No patient selected. Please use the 'Search' tab to select a patient.")

# Injection Points 
with col3:
    st.markdown('<h1 style="font-size: 28px"><span style="color:#202a7a;">Injection Points</span></h1>',
                unsafe_allow_html=True)

    injection_areas = injection_points['area'].drop_duplicates().reset_index(drop=True)
    tab_names = injection_areas.squeeze().tolist()

    # Point Selection
    for i, tab in enumerate(st.tabs([s.capitalize() for s in tab_names])):
        with tab:
            area_data = injection_points[injection_points['area'] == tab_names[i]].reset_index(drop=True)
            region_data = area_data['region_name'].drop_duplicates().reset_index(drop=True)

            if len(region_data) > 1:
                sub_tab_names = region_data.squeeze().tolist()
            else:
                sub_tab_names = [region_data[0]]

            for j, sub_tab in enumerate(st.tabs([s.replace('_', ' ').title() for s in sub_tab_names])):
                with sub_tab:
                    items = area_data[area_data['region_name'] == sub_tab_names[j]].reset_index(drop=True)

                    outcome = items['desired_outcome'][0]
                    effects = items['side_effects'][0]
                    st.markdown(
                        f'<p style="text-align: left;">• <strong>Desired Outcome:</strong> {outcome}.<br>'
                        f'• <strong>Side Effects:</strong> {effects}.</p>',
                        unsafe_allow_html=True
                    )

                    with st.container():
                        for k, item in items.iterrows():
                            checkbox_label = f"{item['injection_name_y']}"
                            if st.checkbox(checkbox_label, key=f"{tab_names[i]} {sub_tab_names[j]}_{k}"):
                                selected_items.append(item)

# AR Scan 
with col1:
    st.markdown('<h1 style="font-size: 28px;"><span style="color:#202a7a;">Real-Time Feed</span></h1>',
                unsafe_allow_html=True)
    st_frame = st.image('https://res.cloudinary.com/bytesizedpieces/image/upload/v1656084931/article/a-how-to-guide-on'
                        '-making-an-animated-loading-image-for-a-website/animated_loader_gif_n6b5x0.gif',
                        use_container_width=True)
    st.write('Update which injection points are currently highlighted by selecting them on the right within their '
             'specified region tab.')

    # Update the feed real-time
    if len(selected_items) > 0:

        injections = injection_data = pd.read_csv('data/inputs/injections.csv')
        regions = []
        treatment_types = []

        selected_points = pd.DataFrame(selected_items)
        for index, point in selected_points.iterrows():
            id = point['landmark']
            injection = injections[injections['point'] == id]

            regions.append(point['region_name'])
            treatment_types.append(injection['treatment_type'].iloc[0])

        draw_options = DrawOptions(
            regions=regions,
            treatment_type=treatment_types,
            draw_all_injections=True,
            draw_tesselations=False,
            draw_all_regions=True
        )

        # arBotox.detect_on_image_proto(WOMAN_1, draw_options)
        arBotox = ArBotox(reload_data_to_database=False)
        arBotox.detect_on_stream_proto(draw_options, st_frame=st_frame)

