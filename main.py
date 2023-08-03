import json
import requests

login_url = 'https://api.salesta.jp/api/v1/open/login'
import_log_url = 'https://api.salesta.jp/api/v1/app/import-logs?importPublishedStatus=PUBLISHED&importStatus=NORMAL%2CPARTIAL_ERROR%2CERROR&pageNo=1&pageSize=10&sortBy=id%3Adesc%2CcreatedAt%3Adesc&storageType=PAYEE_INVOICE'
download_url = 'https://api.salesta.jp//api/v1/app/reports/exports/'
token = 'basic c2FsZXN0YS13ZWI6c2FsZXN0YUB3ZWIqMjAyMg=='

# input
tanant = input('enter tanants: ')
tanants = tanant.split()
year = input('enter year: ')
month = input('enter month: ')
search = year+month

import os
if not os.path.exists('files'):
   os.makedirs('files')
   os.makedirs('files/unzipped')

for tanant in tanants:
    user = input(f'enter user id for tanant {tanant}: ')
    password = input(f'enter password for tanant {tanant}: ')

    headers = {
    'Authorization': token,
    'X-TenantID': tanant
    }

    data = {
    "password": password,
    "userId": user
    }
    # print(data)
    login_res = requests.post(url=login_url, json=data, headers=headers)
    login_res_json = json.loads(login_res.text)
    # print(login_res_json)
    access_token = login_res_json['access_token']

    import_log = requests.get(url=import_log_url, headers={'Authorization': f'bearer {access_token}'})

    # print(f"import_log: {import_log.text}")
    import_log_json = json.loads(import_log.text)
    invoices = []

    for i in import_log_json['content']:
        # print(f"this is the filename: {i['fileName']}")
        if search in i['fileName']:
            invoices.append(i['fileName'])

    # print(invoices)

    for invoice in invoices:
        res = requests.get(url=f'{download_url}{invoice}', headers={'Authorization': f'bearer {access_token}'})
        print(f'downloading file: {invoice}')
        open(f'files/{invoice}', "wb").write(res.content)

    import glob
    import zipfile

    files = glob.glob('files/*.zip') + glob.glob('files/*.ZIP')
    # print(files)
    for file in files:
        print('Unzipping:',file)

        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall('files/unzipped')

    zip_files = glob.glob('files/unzipped/*.zip') + glob.glob('files/unzipped/*.ZIP')
    # print(zip_files)
    for file in zip_files:
        print('Unzipping inner zip:',file)

        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall('files/unzipped')

    csv_files = glob.glob('files/unzipped/*.csv') + glob.glob('files/unzipped/*.CSV')

    total_lines = 0
    for csv_file in csv_files:
        with open(csv_file, 'r') as f:
            total_lines += len(f.readlines())-1
            print('getting invoice count from csv file')

    with open(f'result_{search}.txt', '+a') as f:
        f.write(f'{tanant}: {str(total_lines)}\n')
        print('generating result.txt')

    rm_files = files + zip_files + csv_files + glob.glob('files/unzipped/*.pdf')

    print('deleting files')

    for file in rm_files:
        os.remove(file)

    print('files deleted')


os.rmdir('files/unzipped')
os.rmdir('files')