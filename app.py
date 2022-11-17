sudo pip install xlsxwriter
import streamlit as st
import pandas as pd
import io
import xlsxwriter

st.title('Data Anonymization Tool')
st.subheader('I. Upload Files')
uploaded_files = st.file_uploader('Choose CSV files:',accept_multiple_files=True)

buffer = io.BytesIO()
prefix = 'ANON'

global exphis, opehis, acchis, ins
if uploaded_files:
    for uploaded_file in uploaded_files: 
        st.subheader(uploaded_file.name)
        upload_container = st.expander("Check your uploaded .csv")  
        output_container = st.expander("Check your Output .csv")
        

        if uploaded_file.name == 'ExperimentHistory.csv':
            exphis = pd.read_csv(uploaded_file,low_memory=False)
            uploaded_file.seek(0)
            upload_container.write(exphis)
            exphis[['ExperimentName', 'HostAddress', 'User', 'Project']] = exphis[['ExperimentName', 'HostAddress', 'User','Project']].apply(lambda x: x.str.lower() if pd.notnull(x).all() else x)
            exphis['HostAddress'] = exphis['HostAddress'].apply(lambda x: x.replace('.', ''))

            experiment_names, host_addresses, projects, users = {}, {}, {}, {}
            current_names, current_IP_addresses, current_project, current_users, current_computer_addresses = 1, 1, 1, 1, 1
            
            for index, row in exphis.iterrows():

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

            exphis['ExperimentId'] = [
                f'{prefix}{x:06}' if not pd.isnull(x) else ''
                for x in exphis['ExperimentId']
            ]
            exphis['HostAddress'] = [
            f'{prefix}-IPAddress-{host_addresses[x]:06}'
            if x.isdigit() and not pd.isnull(x) else
            f'{prefix}-ComputerAddress-{host_addresses[x]:06}'
            for x in exphis['HostAddress']
            ]
            exphis['ExperimentName'] = [
                f'{prefix}-ExperimentName-{len(x):03d}-{experiment_names[x]:06}'
                if not pd.isnull(x) else '' for x in exphis['ExperimentName']
            ]
            # Update the User column first to include the correct users, then update the values
            exphis['Project'] = [
                f'{prefix}-Project-{len(x):03d}-{projects[x]:06}'
                if not pd.isnull(x) else '' for x in exphis['Project']
            ]
            # Update the User column first to include the correct users, then update the values
            exphis['User'] = [f'{prefix}-User-{len(x):03d}-{users[x]:06}' if not pd.isnull(x) else '' for x in exphis['User']]
            output_container.write(exphis)
            
        if uploaded_file.name == 'OperationHistory.csv':
            opehis = pd.read_csv(uploaded_file,low_memory=False)
            uploaded_file.seek(0)
            upload_container.write(opehis)
            opehis['Expression'] = opehis['Expression'].fillna('').astype(str)
            opehis['OperationId'] = [f'{prefix}{operation_id:06}' for operation_id in opehis['OperationId']]
            opehis['Expression'] = [f'Note Charaters: {len(x):03}' if not pd.isnull(x) else '' for x in opehis['Expression']]
            opehis['ExperimentId'] = [f'{prefix}{experiment_id:06}' for experiment_id in opehis['ExperimentId']]
            output_container.write(opehis)
                
        if uploaded_file.name == 'AccessoryHistory.csv':    
            acchis = pd.read_csv(uploaded_file,low_memory=False)
            uploaded_file.seek(0)
            upload_container.write(acchis)
            acchis['AccessoryId'] = [f'{prefix}{accessory_id:06}' for accessory_id in acchis['AccessoryId']]
            acchis['ExperimentId'] = [f'{prefix}{experiment_id:06}' for experiment_id in acchis['ExperimentId']]
            output_container.write(acchis)            
        
        if uploaded_file.name == 'Instruments.csv':
            ins = pd.read_csv(uploaded_file,low_memory=False)
            uploaded_file.seek(0)
            upload_container.write(ins)
            ins['InstrumentID'] = [f'{prefix}{instrument_id:06}' for instrument_id in ins['InstrumentID']]
            output_container.write(ins)           
  
    st.balloons()  

else: 
    st.info(
            f"""
                Upload a file here.
                """
        )
    st.stop()


st.subheader('II. Combine & Download')
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    exphis.to_excel(writer, sheet_name='ExperimentHistory', index=False)
    opehis.to_excel(writer, sheet_name='OperationHistory', index=False)
    acchis.to_excel(writer, sheet_name='AccessoryHistory', index=False)
    ins.to_excel(writer, sheet_name='Instruments', index=False)    

    writer.save()
        
    st.download_button(
        label="Download",
        data=buffer.getvalue(),
        file_name=f'{prefix}-output.xlsx',
        mime="application/vnd.ms-excel"
    ) 
