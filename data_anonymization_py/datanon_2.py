import os
import pandas as pd

# Read Acronym File
#acronym = pd.read_csv('Acronym.csv', index_col='Name')
#type in the company abbreviation code
prefix = 'ANON'
print('Processing... Please wait...')

# looking for acronym in the Acronym CSV
path = os.getcwd()

# Get rid of the \ if included in the path name
if path[-1] == '\\':
    path = path[:-1]


# Each of these 4 functions create a dataframe and update the columns to be anonymized
def anonymize_instruments(prefix):
    csv = pd.read_csv(f'{path}\Instruments.csv', low_memory=False)
    csv['InstrumentID'] = [f'{prefix}{instrument_id:06}' for instrument_id in csv['InstrumentID']]
    return csv

def anonymize_accessory_history(prefix):
    csv = pd.read_csv(f'{path}\AccessoryHistory.csv', low_memory=False)
    csv['AccessoryId'] = [f'{prefix}{accessory_id:06}' for accessory_id in csv['AccessoryId']]
    csv['ExperimentId'] = [f'{prefix}{experiment_id:06}' for experiment_id in csv['ExperimentId']]
    return csv

def anonymize_operation_history(prefix):
    csv = pd.read_csv(f'{path}\OperationHistory.csv', low_memory=False)
    csv['Expression'] = csv['Expression'].fillna('').astype(str)
    csv['OperationId'] = [f'{prefix}{operation_id:06}' for operation_id in csv['OperationId']]
    csv['Expression'] = [
        f'Note Charaters: {len(x):03}' if not pd.isnull(x) else ''
        for x in csv['Expression']
    ]
    csv['ExperimentId'] = [
        f'{prefix}{experiment_id:06}' for experiment_id in csv['ExperimentId']
    ]
    return csv


def anonymize_experiment_history(prefix):
    csv = pd.read_csv(f'{path}\ExperimentHistory.csv', low_memory=False)
    csv[['ExperimentName', 'HostAddress', 'User', 'Project']] = csv[['ExperimentName', 'HostAddress', 'User','Project']].apply(lambda x: x.str.lower())
    csv['HostAddress'] = csv['HostAddress'].apply(lambda x: x.replace('.', ''))

    # Use try/except in case the substitutions file is not provided, then just proceed without it
    try:
        substitution_csv = pd.read_csv(f'{path}\Substitutions.csv',
                                       low_memory=False)
        substitutions_provided = True

        # Make a dictionary with the key being the prefix along with the incorrect name
        # and the value is the correct name so we can substitute the correct name in later
        substitutions = {}
        for index, row in substitution_csv.iterrows():
            if prefix + row['Bad User'] not in substitutions:
                substitutions[prefix + row['Bad User']] = row['Fixed User']

    except:
        print("Substitutions file could not be read.")
        substitutions_provided = False

    # This is a bit trickier, we have to run through and see which values we have
    # for these columns so that we can assign them the right number later, with
    # the same value getting the same number
    experiment_names, host_addresses, projects, users = {}, {}, {}, {}
    current_names, current_IP_addresses, current_project, current_users, current_computer_addresses = 1, 1, 1, 1, 1
    fixed_users, fixed_projects = [], []
    for index, row in csv.iterrows():
        if substitutions_provided and prefix + str(
                row['User']) in substitutions:
            row['User'] = substitutions[prefix + str(row['User'])]
        if substitutions_provided and prefix + str(
                row['Project']) in substitutions:
            row['Project'] = substitutions[prefix + str(row['Project'])]
        fixed_users.append(row['User'])
        fixed_projects.append(row['Project'])

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
    csv['Project'] = fixed_projects
    csv['Project'] = [
        f'{prefix}-Project-{len(x):03d}-{projects[x]:06}'
        if not pd.isnull(x) else '' for x in csv['Project']
    ]

    # Update the User column first to include the correct users, then update the values
    csv['User'] = fixed_users
    csv['User'] = [
        f'{prefix}-User-{len(x):03d}-{users[x]:06}' if not pd.isnull(x) else ''
        for x in csv['User']
    ]

    return csv


# Now we can call the functions and pass in our prefix to
# get 4 dataframes which will become the excel sheets
instruments_anon = anonymize_instruments(prefix)
accessory_history_anon = anonymize_accessory_history(prefix)
operation_history_anon = anonymize_operation_history(prefix)
experiment_history_anon = anonymize_experiment_history(prefix)

# Create and ExcelWriter to write to an excel file
# in the same folder as the csv files were in
with pd.ExcelWriter(f'{path}\{prefix}-output.xlsx',
                    engine='xlsxwriter') as writer:
    # Each call to to_excel creates a new sheet in our excel file output.xlsx
    experiment_history_anon.to_excel(writer,
                                     sheet_name='ExperimentHistory',
                                     index=False)
    operation_history_anon.to_excel(writer,
                                    sheet_name='OperationHistory',
                                    index=False)
    accessory_history_anon.to_excel(writer,
                                    sheet_name='AccessoryHistory',
                                    index=False)
    instruments_anon.to_excel(writer, sheet_name='Instruments', index=False)
