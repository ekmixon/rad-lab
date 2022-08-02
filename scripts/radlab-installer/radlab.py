#!/usr/bin/env python3


'''
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

#  PREREQ: installer_prereq.py

import os
import shutil
import sys
import json
import random
import string
import platform
from os import path
from google.cloud import storage
from googleapiclient import discovery
from colorama import Fore, Back, Style
from python_terraform import Terraform
from oauth2client.client import GoogleCredentials

def main():

    orgid          = ""
    folderid       = ""
    billing_acc    = ""
    domain         = ""
    module          = ""
    state          = ""
    notebook_count = ""
    trusted_users  = []

    setup_path = os.getcwd()

    # Setting Credentials for non Cloud Shell CLI
    if(platform.system() != 'Linux' and platform.processor() !='' and not platform.system().startswith('cs-')):
        # countdown(5)
        print("Login with Cloud Admin account...")
        os.system("gcloud auth application-default login")

    module = input("\nList of available RADLab modules:\n[1] Data Science\n[2] Exit\n"+ Fore.YELLOW + Style.BRIGHT + "Choose a number for the RADLab Module"+ Style.RESET_ALL + ': ')

    if (module.strip() == "1"):

        print("\nRADLab Module (selected) : "+ Fore.GREEN + Style.BRIGHT +"Data Science"+ Style.RESET_ALL)

        # Select Action to perform
        state = select_state()

        # Get Terraform Bucket Details
        tfbucket = getbucket(state.strip())
        print("\nGCS bucket to save Terraform config & state (Selected) : " + Fore.GREEN + Style.BRIGHT + tfbucket + Style.RESET_ALL )

        # Setting Org ID, Billing Account, Folder ID, Domain
        if (state == "1"):  

            # Getting Base Inputs
            orgid, billing_acc, folderid, domain, randomid = basic_input()

            # Set environment path as deployment directory
            prefix = f'data_science_{randomid}'
            env_path = f'{setup_path}/deployments/{prefix}'

            # Checking if 'deployment' folder exist in local. If YES, delete the same.
            delifexist(env_path)

            # Copy module directory
            shutil.copytree(
                f'{os.path.dirname(os.path.dirname(os.getcwd()))}/modules/data_science',
                env_path,
            )


            # Set Terraform states remote backend as GCS
            settfstategcs(env_path,prefix,tfbucket)

            # Create file with billing/org/folder details
            create_env(env_path, orgid, billing_acc, folderid)

        elif state in ["2", "3"]:

            # Get Deployment ID
            randomid = input(Fore.YELLOW + Style.BRIGHT + "\nEnter RADLab Module Deployment ID (example 'l8b3' is the id for project with id - radlab-ds-analytics-l8b3)" + Style.RESET_ALL + ': ')
            randomid = randomid.strip()

            # Validating Deployment ID
            if (len(randomid) == 4 and randomid.isalnum()):

                # Set environment path as deployment directory
                prefix = f'data_science_{randomid}'
                env_path = f'{setup_path}/deployments/{prefix}'

                # Setting Local Deployment
                setlocaldeployment(tfbucket,prefix,env_path)

            else:
                sys.exit(Fore.RED + "\nInvalid deployment ID!\n")

            # Get env values
            orgid, billing_acc, folderid = get_env(env_path)

            # Fetching Domain name 
            domain = getdomain(orgid)

            # Set Terraform states remote backend as GCS
            settfstategcs(env_path,prefix,tfbucket)

            if(state == "3"):
                print("DELETING DEPLOYMENT...")

        else:
            sys.exit(Fore.RED + "\nInvalid RADLab Module State selected")

        ###########################
        # Module Specific Options #
        ###########################

        # No. of AI Notebooks and assigning trusted users
        if state in ["1", "2"]:
            # Requesting Number of AI Notebooks
            notebook_count = input(Fore.YELLOW + Style.BRIGHT + "\nNumber of AI Notebooks required [Default is 1 & Maximum is 10]"+ Style.RESET_ALL + ': ')
            if(len(notebook_count.strip()) == 0):
                notebook_count = '1'
                print("\nNumber of AI Notebooks (Selected) : " + Fore.GREEN + Style.BRIGHT + notebook_count + "\n"+ Style.RESET_ALL)
            elif(int(notebook_count) > 0 and int(notebook_count) <= 10):
                print("\nNumber of AI Notebooks (Selected) : " + Fore.GREEN + Style.BRIGHT + notebook_count + "\n"+ Style.RESET_ALL)
            else:
                # shutil.rmtree(env_path)
                sys.exit(Fore.RED + "\nInvalid Notbooks count")

            # Requesting Trusted Users
            new_name = ''
            while new_name != 'quit':
                # Ask the user for a name.
                new_name = input(Fore.YELLOW + Style.BRIGHT + "Enter the username of trusted users needing access to AI Notebooks, or enter 'quit'"+ Style.RESET_ALL + ': ')
                new_name = new_name.strip()
                # Add the new name to our list.
                if (new_name != 'quit' and len(new_name.strip()) != 0):
                    if "@" in new_name:
                        new_name = new_name.split("@")[0]
                    trusted_users.append(f"user:{new_name}@{domain}")
                    # print(trusted_users)

    elif(module.strip() == "2"):
        sys.exit(Fore.GREEN + "\nExiting Installer")

    else:
        sys.exit(Fore.RED + "\nInvalid module")

    env(state, orgid, billing_acc, folderid, domain, env_path, notebook_count, trusted_users, randomid, tfbucket)
    print("\nGCS Bucket storing Terrafrom Configs: "+ tfbucket +"\n")
    print("\nTERRAFORM DEPLOYMENT COMPLETED!!!\n")
	

def env(state, orgid, billing_acc, folderid, domain, env_path, notebook_count, trusted_users, randomid, tfbucket):
    tr = Terraform(working_dir=env_path)
    return_code, stdout, stderr = tr.init_cmd(capture_output=False)

    if state in ["1", "2"]:
        return_code, stdout, stderr = tr.apply_cmd(capture_output=False,auto_approve=True,var={'organization_id':orgid, 'billing_account_id':billing_acc, 'folder_id':folderid, 'domain':domain, 'file_path':env_path, 'notebook_count':notebook_count, 'trusted_users': trusted_users, 'random_id':randomid})
    elif(state == "3"):
        return_code, stdout, stderr = tr.destroy_cmd(capture_output=False,auto_approve=True,var={'organization_id':orgid, 'billing_account_id':billing_acc, 'folder_id':folderid, 'file_path':env_path,'random_id':randomid})

    # return_code - 0 Success & 1 Error
    if (return_code == 1):
        print(stderr)
        sys.exit(Fore.RED + Style.BRIGHT + "\nError Occured - Deployment failed for ID: "+ randomid+"\n"+ "Retry using above Deployment ID" +Style.RESET_ALL )
    elif state in ['1', '2']:
        os.system(
            f'gsutil -q -m cp -r {env_path}/*.tf gs://{tfbucket}/radlab/'
            + env_path.split('/')[len(env_path.split('/')) - 1]
            + '/deployments'
        )

        os.system(
            f'gsutil -q -m cp -r {env_path}/*.json gs://{tfbucket}/radlab/'
            + env_path.split('/')[len(env_path.split('/')) - 1]
            + '/deployments'
        )


    elif(state == '3'):
        # print(env_path)
        # print(env_path.split('/')[len(env_path.split('/'))-1])
        deltfgcs(tfbucket, 'radlab/'+ env_path.split('/')[len(env_path.split('/'))-1])

    # Deleting Local deployment config
    shutil.rmtree(env_path)

def select_state():
    state = input("\nAction to perform for RADLab Deployment ?\n[1] Create New\n[2] Update\n[3] Delete\n" + Fore.YELLOW + Style.BRIGHT + "Choose a number for the RADLab Module Deployment Action"+ Style.RESET_ALL + ': ')
    state = state.strip()
    return state

def basic_input():

    print("\nEnter following info to start the setup and use the user which have Project Owner & Billing Account User roles:-")

    # Selecting Org ID
    orgid = getorgid()
    print("\nOrg ID (Selected) : " + Fore.GREEN + Style.BRIGHT + orgid + Style.RESET_ALL )

    # Org ID Validation
    if (orgid.strip().isdecimal() == False) :
        sys.exit(Fore.RED + "\nError Occured - INVALID ORG ID\n")
    
    # Selecting Billing Account
    billing_acc = getbillingacc()
    print("\nBilling Account (Selected) : " + Fore.GREEN + Style.BRIGHT + billing_acc + Style.RESET_ALL )  
    
    # Selecting Folder ID
    folderid = input(Fore.YELLOW + Style.BRIGHT + "\nFolder ID [Optional]"+ Style.RESET_ALL + ': ')

    # Folder ID Validation
    if (folderid.strip() and folderid.strip().isdecimal() == False):
        sys.exit(Fore.RED + "\nError Occured - INVALID FOLDER ID ACCOUNT\n")

    # Fetching Domain name 
    domain = getdomain(orgid)
    
    # Create Random Deployment ID
    randomid = get_random_alphanumeric_string(4)

    return orgid, billing_acc, folderid, domain, randomid

def create_env(env_path, orgid, billing_acc, folderid):

    my_path = f'{env_path}/env.json'
    envjson = [
        {
            "orgid"         : orgid,
            "billing_acc"   : billing_acc,
            "folderid"      : folderid
        }
    ]
    with open(my_path , 'w') as file:
        json.dump(envjson, file, indent=4)

def get_env(env_path):

    # Read orgid / billing acc / folder id from env.json
    my_path = f'{env_path}/env.json'
    with open(my_path,) as f:
        # returns JSON object as a dictionary
        data = json.load(f)

        orgid       = data[0]['orgid']
        billing_acc = data[0]['billing_acc']
        folderid    = data[0]['folderid']

    return orgid, billing_acc, folderid

def setlocaldeployment(tfbucket,prefix, env_path):

    if (blob_exists(tfbucket, prefix)):

        # Checking if 'deployment' folder exist in local. If YES, delete the same.
        delifexist(env_path)

        # Creating Local directory
        os.mkdir(env_path)

        # Copy Terraform deployment configs from GCS to Local
        if (
            os.system(
                f'gsutil -q -m cp -r gs://{tfbucket}/radlab/{prefix}/deployments/* {env_path}'
            )
            == 0
        ):
            print("Terraform state downloaded to local...")
        else:
            print(Fore.RED + "\nError Occured whiled downloading Deployment Configs from GCS. Checking if the deployment exist locally...\n")

    elif(os.path.isdir(env_path)):
        print("Terraform state exist locally...")

    else:
        sys.exit(Fore.RED + "\nThe deployment with the entered ID do not exist !\n")

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_lowercase + string.digits
    	# print("Random alphanumeric String is:", result_str)
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def getdomain(orgid):
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    # The resource name of the Organization to fetch, e.g. "organizations/1234".
    name = f'organizations/{orgid}'

    request = service.organizations().get(name=name)
    response = request.execute()
    # print(response['displayName'])
    return response['displayName']

def getbillingacc():
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('cloudbilling', 'v1', credentials=credentials)

    request = service.billingAccounts().list()
    response = request.execute()

    print("\nList of Billing account you have access to: \n")
    billing_accounts = []
    # Print out Billing accounts
    for x in range(len(response['billingAccounts'])):
        print(
            f"[{str(x+1)}] "
            + response['billingAccounts'][x]['name']
            + "    "
            + response['billingAccounts'][x]['displayName']
        )

        billing_accounts.append(response['billingAccounts'][x]['name'])

    # Take user input and get the corresponding item from the list
    inp = int(input(Fore.YELLOW + Style.BRIGHT + "Choose a number for Billing Account" + Style.RESET_ALL + ': '))
    if inp in range(1, len(billing_accounts)+1):
        inp = billing_accounts[inp-1]

        billing_acc = inp.split('/')        
        # print(billing_acc[1])
        return billing_acc[1]
    else:
        sys.exit(Fore.RED + "\nError Occured - INVALID BILLING ACCOUNT\n")

def getorgid():
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('cloudresourcemanager', 'v1beta1', credentials=credentials)

    request = service.organizations().list()
    response = request.execute()

    # pprint(response)

    print("\nList of Org ID you have access to: \n")
    org_ids = []
    # Print out Org IDs accounts
    for x in range(len(response['organizations'])):
        print(
            f"[{str(x+1)}] "
            + response['organizations'][x]['organizationId']
            + "    "
            + response['organizations'][x]['displayName']
            + "    "
            + response['organizations'][x]['lifecycleState']
        )

        org_ids.append(response['organizations'][x]['organizationId'])

    # Take user input and get the corresponding item from the list
    inp = int(input(Fore.YELLOW + Style.BRIGHT + "Choose a number for Organization ID" + Style.RESET_ALL + ': '))
    if inp in range(1, len(org_ids)+1):
        # print(orgid)
        return org_ids[inp-1]
    else:
        sys.exit(Fore.RED + "\nError Occured - INVALID ORG ID SELECTED\n"+ Style.RESET_ALL)

def delifexist(env_path):
    # print(os.path.isdir(env_path))
    if(os.path.isdir(env_path)):
        shutil.rmtree(env_path)

def getbucket(state):
    """Lists all buckets."""

    storage_client = storage.Client()
    bucketoption = ''

    if(state == '1'):
        bucketoption = input("\nWant to use existing GCS Bucket for Terraform configs or Create Bucket ?:\n[1] Use Existing Bucket\n[2] Create New Bucket\n"+ Fore.YELLOW + Style.BRIGHT + "Choose a number for your choice"+ Style.RESET_ALL + ': ')

    if (bucketoption == '1' or state == '2' or state == '3'):
        try:
            buckets = storage_client.list_buckets()

            barray = []
            x = 0
            print("\nSelect a bucket to save Terraform Configs & States... \n")
            # Print out Buckets in the default project
            for bucket in buckets:
                print(f"[{str(x+1)}] {bucket.name}")
                barray.append(bucket.name)
                x=x+1

            # Take user input and get the corresponding item from the list
            try:
                inp = int(input(Fore.YELLOW + Style.BRIGHT + "Choose a number for Bucket Name" + Style.RESET_ALL + ': '))
            except:
                print(Fore.RED + "\nINVALID or NO OPTION SELECTED FOR BUCKET NAME.\n\nEnter the Bucket name Manually...\n"+ Style.RESET_ALL)

            if inp in range(1, len(barray)+1):
                tfbucket = barray[inp-1]
                return tfbucket
            else:
                print(Fore.RED + "\nINVALID or NO OPTION SELECTED FOR BUCKET NAME.\n\nEnter the Bucket name Manually...\n"+ Style.RESET_ALL)
                sys.exit(1)

        except:
            tfbucket = input(Fore.YELLOW + Style.BRIGHT +"Enter the GCS Bucket name where Terraform Configs & States will be stored"+ Style.RESET_ALL + ": ")
            tfbucket = tfbucket.lower().strip()
            return tfbucket

    elif bucketoption == '2':
        print("CREATE BUCKET")
        bucketprefix = input(Fore.YELLOW + Style.BRIGHT + "\nEnter the prefix for the bucket name i.e. radlab-[PREFIX] " + Style.RESET_ALL + ': ')
        # Creates the new bucket
        # Note: These samples create a bucket in the default US multi-region with a default storage class of Standard Storage. 
        # To create a bucket outside these defaults, see [Creating storage buckets](https://cloud.google.com/storage/docs/creating-buckets).
        projid = input(Fore.YELLOW + Style.BRIGHT + "\nEnter the project ID under which the bucket is to be created " + Style.RESET_ALL + ': ')
        bucket = storage_client.create_bucket(f'radlab-{bucketprefix}', project=projid)

        print(f"Bucket {bucket.name} created.")
        return bucket.name
    else:
        sys.exit(Fore.RED + "\nInvalid Choice")

def settfstategcs(env_path, prefix, tfbucket):

    prefix = f"radlab/{prefix}/terraform_state"

    # Validate Terraform Bucket ID
    client = storage.Client()
    try:
        bucket = client.get_bucket(tfbucket)
        # print(bucket)
    except:
        sys.exit(Fore.RED + "\nError Occured - INVALID BUCKET NAME or NO ACCESS\n"+ Style.RESET_ALL)

    with open(f'{env_path}/backend.tf', 'w+') as f:
        f.write('terraform {\n  backend "gcs"{\n    bucket="'+tfbucket+'"\n    prefix="'+prefix+'"\n  }\n}')

def deltfgcs(tfbucket, prefix):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(tfbucket)

    blobs = bucket.list_blobs(prefix=prefix)

    for blob in blobs:
        blob.delete()

def blob_exists(tfbucket, prefix):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(tfbucket)
    blob = bucket.blob(f'radlab/{prefix}/deployments/main.tf')
    # print(blob.exists())
    return blob.exists()

if __name__ == "__main__":
    main()
