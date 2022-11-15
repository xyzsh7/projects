import streamlit as st
import pandas as pd
import os
import io
from xlsxwriter import Workbook

buffer = io.BytesIO()
prefix = 'ANON'

st.title('Data Anonymization Tool')
uploaded_files = st.file_uploader("Choose your CSV or Excel files", accept_multiple_files=True)

if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        if uploaded_file.name == 'Instruments.csv':
            ins = pd.read_csv(uploaded_file,low_memory=False)
            ins['InstrumentID'] = [f'{prefix}{instrument_id:06}' for instrument_id in ins['InstrumentID']]
            st.header(uploaded_file.name)
            st.write(ins)
            
        if uploaded_file.name == 'AccessoryHistory.csv':    
            acchis = pd.read_csv(uploaded_file,low_memory=False)
            acchis['AccessoryId'] = [f'{prefix}{accessory_id:06}' for accessory_id in acchis['AccessoryId']]
            acchis['ExperimentId'] = [f'{prefix}{experiment_id:06}' for experiment_id in acchis['ExperimentId']]
            st.header(uploaded_file.name)
            st.write(acchis)
            
        if uploaded_file.name == 'OperationHistory.csv':
            opehis = pd.read_csv(uploaded_file,low_memory=False)
            opehis['Expression'] = opehis['Expression'].fillna('').astype(str)
            opehis['OperationId'] = [f'{prefix}{operation_id:06}' for operation_id in opehis['OperationId']]
            opehis['Expression'] = [f'Note Charaters: {len(x):03}' if not pd.isnull(x) else '' for x in opehis['Expression']]
            opehis['ExperimentId'] = [f'{prefix}{experiment_id:06}' for experiment_id in opehis['ExperimentId']]
            st.header(uploaded_file.name)
            st.write(opehis)
            
        if uploaded_file.name == 'ExperimentHistory.csv':
            csv = pd.read_csv(uploaded_file,low_memory=False)
            csv[['ExperimentName', 'HostAddress', 'User', 'Project']] = csv[['ExperimentName', 'HostAddress', 'User','Project']].apply(lambda x: x.str.lower() if pd.notnull(x).all() else x)
            csv['HostAddress'] = csv['HostAddress'].apply(lambda x: x.replace('.', ''))

            experiment_names, host_addresses, projects, users = {}, {}, {}, {}
            current_names, current_IP_addresses, current_project, current_users, current_computer_addresses = 1, 1, 1, 1, 1
            fixed_users, fixed_projects = [], []
            for index, row in csv.iterrows():

                if row['ExperimentName'] not in experiment_names and not pd.isnull(
                        row['ExperimentName']):
                    experiment_names[row['ExperimentName']] = current_names
                    current_names += 1
                if row['Project'] not in projects and not pd.isnull(row['Project']):
                    projects[row['Project']] = current_project
                    current_project += 1
                if row['User'] not in users and not pd.isnull(row['User']):
                    users[row['User']] = current_users
                    current_users += 1
                if row['HostAddress'] not in host_addresses and not pd.isnull(
                        row['HostAddress']):
                    if row['HostAddress'].isdigit():
                        host_addresses[row['HostAddress']] = current_IP_addresses
                        current_IP_addresses += 1
                    elif not row['HostAddress'].isdigit():
                        host_addresses[row['HostAddress']] = current_computer_addresses
                        current_computer_addresses += 1

            csv['ExperimentId'] = [
                f'{prefix}{x:06}' if not pd.isnull(x) else ''
                for x in csv['ExperimentId']
            ]

            csv['HostAddress'] = [
            f'{prefix}-IPAddress-{host_addresses[x]:06}'
            if x.isdigit() and not pd.isnull(x) else
            f'{prefix}-ComputerAddress-{host_addresses[x]:06}'
            for x in csv['HostAddress']
            ]

            csv['ExperimentName'] = [
                f'{prefix}-ExperimentName-{len(x):03d}-{experiment_names[x]:06}'
                if not pd.isnull(x) else '' for x in csv['ExperimentName']
            ]

            # Update the User column first to include the correct users, then update the values
            csv['Project'] = [
                f'{prefix}-Project-{len(x):03d}-{projects[x]:06}'
                if not pd.isnull(x) else '' for x in csv['Project']
            ]

            # Update the User column first to include the correct users, then update the values
            csv['User'] = [f'{prefix}-User-{len(x):03d}-{users[x]:06}' if not pd.isnull(x) else '' for x in csv['User']]
            st.header(uploaded_file.name)
            st.write(csv)
         
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Each call to to_excel creates a new sheet in our excel file output.xlsx
        csv.to_excel(writer, sheet_name='ExperimentHistory', index=False)
        opehis.to_excel(writer, sheet_name='OperationHistory', index=False)
        acchis.to_excel(writer, sheet_name='AccessoryHistory', index=False)
        ins.to_excel(writer, sheet_name='Instruments', index=False)

        writer.save()

        st.download_button(
            label="Download",
            data=buffer,
            file_name=f'{prefix}-output.xlsx',
            mime="application/vnd.ms-excel"
        )
    
st.balloons()