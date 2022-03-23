import requests
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import threading
import logging
from flask_swagger_ui import get_swaggerui_blueprint
import pandas as pd
import numpy as np

import json

app = Flask(__name__)
CORS(app,resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Blockchain Explorer"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

walletAddress = '0x0F0CbA474C2C9F859A8519a34b0B278A2B998801'
APIKEY = ''
BSCAPIKEY = 'CFE5EM79FR81CH7C1GEJTB2IIFAC91TC2I'
ETHAPIKEY = 'PQ3GK8R48PZWZE3KJN4ZZBQE81AVEPBFQX'
ethurl = 'https://api.etherscan.io/api'
apiurl = ''
bscurl = 'https://api.bscscan.com/api'
APIKEY = ETHAPIKEY
apiurl = ethurl


@app.route('/getTable/<address>/<contract>', methods=['GET'])
def get_Table(address, contract):
    return null


@app.route('/getTokenInfo/<address>/', methods=['GET'])
def get_Token_Info(address):
    address = address.lower()

    obj = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()

    transfers = token_transfer_events['result']
    trxs = pd.DataFrame(transfers)
    print(trxs.columns)
    trxs['value'] = pd.to_numeric(trxs['value'], errors='coerce')
    uniqueTokens = trxs['contractAddress'].unique()

    returnArr = [getEthTrxs(address)]
    for i in uniqueTokens:
        returnArr.append(getTokenInfo(i, address, trxs))
    return {'tokens': returnArr}


def getTokenInfo(contract, address, df):
    df = df.groupby('contractAddress')
    tokenTrxs = df.get_group(contract)
    # Get Decimal
    decimal = 10 ** int(tokenTrxs['tokenDecimal'].unique()[0])
    tokenSymbol = tokenTrxs['tokenSymbol'].unique()[0]
    tokenName = tokenTrxs['tokenName'].unique()[0]
    sentTrxs = tokenTrxs['from'].unique()
    recTrxs = tokenTrxs['to'].unique()
    uniqueSentToAdd = pd.DataFrame([])
    uniqueSentToAddCount = 0
    totalSentTrxs = 0
    myTotalSentValue = 0
    uniqueRecFromAdd = pd.DataFrame([])
    uniqueRecFromAddCount = 0
    totalRecTrxs = 0
    myTotalRecValue = 0
    if (address in sentTrxs):
        mySentTrxs = tokenTrxs.groupby('from').get_group(address)
        uniqueSentToAdd = pd.DataFrame(mySentTrxs['to'].unique())
        uniqueSentToAddCount = len(mySentTrxs['to'].unique())
        totalSentTrxs = len(mySentTrxs)
        myTotalSentValue = mySentTrxs['value'].sum() / decimal
    else:
        uniqueSentToAdd = pd.DataFrame([])
        uniqueSentToAddCount = 0
        totalSentTrxs = 0
        myTotalSentValue = 0

    if (address in recTrxs):
        myRecTrxs = tokenTrxs.groupby('to').get_group(address)
        # Get count unqiue sent and rec addresses
        uniqueRecFromAdd = pd.DataFrame(myRecTrxs['from'].unique())
        uniqueRecFromAddCount = len(myRecTrxs['from'].unique())
        # Get the total count of sent and Rec Transactions
        totalRecTrxs = len(myRecTrxs)
        # Get Value of sent and rec transactions
        myTotalRecValue = myRecTrxs['value'].sum() / decimal
    else:
        uniqueRecFromAdd = pd.DataFrame([])
        uniqueRecFromAddCount = 0
        totalRecTrxs = 0
        myTotalRecValue = 0

    obj = {
        'token': tokenName,
        'contract': contract,
        'tokenSymbol': tokenSymbol,
        'uniqueSentToAddCount': uniqueSentToAddCount,
        'totalSentTrxs': totalSentTrxs,
        'myTotalSentValue': round(myTotalSentValue, 2),
        'uniqueRecFromAddCount': uniqueRecFromAddCount,
        'totalRecTrxs': totalRecTrxs,
        'myTotalRecValue': round(myTotalRecValue, 2),
        'balance': round(myTotalRecValue - myTotalSentValue, 2),
        'show': True,
        'expand': False
    }
    return obj


# returns dataframe of eth transactions
def getEthTrxs(address):
    address = address.lower()

    obj = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()
    balance = token_transfer_events['result']

    print(balance)
    obj = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()
    transfers = token_transfer_events['result']
    tokenTrxs = pd.DataFrame(transfers)
    tokenTrxs = tokenTrxs[tokenTrxs['contractAddress'] == '']
    tokenTrxs['value'] = pd.to_numeric(tokenTrxs['value'], errors='coerce')
    decimal = 10 ** 18
    tokenSymbol = 'ETH'
    tokenName = 'Ethereum'
    sentTrxs = tokenTrxs['from'].unique()
    recTrxs = tokenTrxs['to'].unique()
    uniqueSentToAdd = []
    uniqueSentToAddCount = 0
    totalSentTrxs = 0
    myTotalSentValue = 0
    uniqueRecFromAdd = []
    uniqueRecFromAddCount = 0
    totalRecTrxs = 0
    myTotalRecValue = 0
    if (address in sentTrxs):
        mySentTrxs = tokenTrxs.groupby('from').get_group(address)
        uniqueSentToAdd = pd.DataFrame(mySentTrxs['to'].unique())
        uniqueSentToAddCount = len(mySentTrxs['to'].unique())
        totalSentTrxs = len(mySentTrxs)
        myTotalSentValue = mySentTrxs['value'].sum() / decimal

    if (address in recTrxs):
        myRecTrxs = tokenTrxs.groupby('to').get_group(address)
        # Get count unqiue sent and rec addresses
        uniqueRecFromAdd = pd.DataFrame(myRecTrxs['from'].unique())
        uniqueRecFromAddCount = len(myRecTrxs['from'].unique())
        # Get the total count of sent and Rec Transactions
        totalRecTrxs = len(myRecTrxs)
        # Get Value of sent and rec transactions
        myTotalRecValue = myRecTrxs['value'].sum() / decimal

    obj = {
        'token': tokenName,
        'contract': '',
        'tokenSymbol': tokenSymbol,
        'uniqueSentToAddCount': uniqueSentToAddCount,
        'totalSentTrxs': totalSentTrxs,
        'myTotalSentValue': round(myTotalSentValue, 2),
        'uniqueRecFromAddCount': uniqueRecFromAddCount,
        'totalRecTrxs': totalRecTrxs,
        'myTotalRecValue': round(myTotalRecValue, 2),
        'balance': round(int(balance) / 10 ** 18, 2),
        'show': True,
        'expand': False
    }
    print(obj)
    return obj


@app.route('/getTokenAddInfo/<address>/<token>', methods=['GET'])
def get_Token_Add_Info(address, token):
    address = address.lower()
    obj = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()

    transfers = token_transfer_events['result']
    trxs = pd.DataFrame(transfers)
    trxs['value'] = pd.to_numeric(trxs['value'], errors='coerce')
    tokens = trxs.groupby('tokenName')
    tokenTrxs = tokens.get_group(token)
    sentTrxs = tokenTrxs['from'].unique()
    recTrxs = tokenTrxs['to'].unique()
    allAddresses = np.concatenate([sentTrxs, recTrxs])
    allAddDf = pd.DataFrame(allAddresses, columns=['Addresses'])
    allAddDf = allAddDf[allAddDf['Addresses'] != address]
    unqiueAdd = allAddDf['Addresses'].unique()
    returnArr = []
    for i in unqiueAdd:
        returnArr.append(getTokenAddInfo(token, i, tokens))

    return {'Addresses': returnArr}


def getTokenAddInfo(token, Address, tokens):
    tokenTrxs = tokens.get_group(token)

    print(tokenTrxs.columns)
    # Get Decimal
    decimal = 10 ** int(tokenTrxs['tokenDecimal'].unique()[0])
    tokenSymbol = tokenTrxs['tokenSymbol'].unique()[0]

    sentTrxs = tokenTrxs['from'].unique()
    recTrxs = tokenTrxs['to'].unique()

    if (Address in sentTrxs):
        addSentTrxs = tokenTrxs.groupby('from').get_group(Address)
        totalSentTrxs = len(addSentTrxs)
        addTotalSentValue = addSentTrxs['value'].sum() / decimal
        sentTrxs = addSentTrxs.to_json(orient='records')
        sentTrxs = json.loads(sentTrxs)

    else:
        addSentTrxs = pd.DataFrame()
        totalSentTrxs = 0
        addTotalSentValue = 0
        sentTrxs = []

    if (Address in recTrxs):
        addRecTrxs = tokenTrxs.groupby('to').get_group(Address)
        totalRecTrxs = len(addRecTrxs)
        addTotalRecValue = addRecTrxs['value'].sum() / decimal
        recTrxs = addRecTrxs.to_json(orient='records')
        recTrxs = json.loads(recTrxs)


    else:
        addRecTrxs = pd.DataFrame()
        totalRecTrxs = 0
        addTotalRecValue = 0
        recTrxs = []

    allTrxs = pd.concat([addRecTrxs, addSentTrxs])
    allTrxs = allTrxs.to_json(orient='records')
    allTrxs = json.loads(allTrxs)

    obj = {
        'address': Address,
        'token': token,
        'tokenSymbol': tokenSymbol,
        'totalSentTrxs': totalSentTrxs,
        'addTotalSentValue': round(addTotalSentValue, 2),
        'totalRecTrxs': totalRecTrxs,
        'addTotalRecValue': round(addTotalRecValue, 2),
        # 'recTrxs': recTrxs,
        # 'sentTrxs': sentTrxs,
        'allTrxs': allTrxs,
        'expand': False,
        'show': True

    }
    return obj


@app.route('/getAllTrxs2/<address>', methods=['GET'])
def getAllTrxs2(address):
    address = address.lower()
    trxs = pd.DataFrame()
    apiInteractions = ['tokentx', 'txlist']
    for i in apiInteractions:
        obj = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'sort': 'asc',
            'apikey': APIKEY
        }
        token_transfer_events = requests.post(apiurl, obj).json()
        transfers = token_transfer_events['result']
        trxs = trxs.append(transfers)
    trxs['value'] = pd.to_numeric(trxs['value'], errors='coerce')
    allTrxs = trxs.to_json(orient='records')
    allTrxs = json.loads(allTrxs)
    print(allTrxs)
    return {'AllTrxs': allTrxs}


@app.route('/getAllTrxs/<address>', methods=['GET'])
def getAllTrxs(address):
    address = address.lower()

    obj = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }
    token_transfer_events = requests.post(apiurl, obj).json()
    transfers = token_transfer_events['result']
    trxs = pd.DataFrame(transfers)
    trxs['value'] = pd.to_numeric(trxs['value'], errors='coerce')
    allTrxs = trxs.to_json(orient='records')
    allTrxs = json.loads(allTrxs)
    print(allTrxs)
    return {'AllTrxs': allTrxs}


@app.route('/getTimeLine/', methods=['POST'])
def getTimeLine():
    print(request.data)
    data = json.loads(request.data)
    adds = data['addresses']
    contracts = data['contracts']
    res = pd.DataFrame()
    if (contracts[0] == 'none'):
        for add in adds:
            address = add.lower()
            print(add)
            obj = {
                'module': 'account',
                'action': 'tokentx',
                'address': address,
                'sort': 'asc',
                'apikey': APIKEY
            }
            token_transfer_events = requests.post(apiurl, obj).json()
            transfers = token_transfer_events['result']
            print(len(transfers))
            trxs = pd.DataFrame(transfers)
            trxs['value'] = pd.to_numeric(trxs['value'], errors='coerce')
            trxs['timeStamp'] = pd.to_numeric(trxs['timeStamp'], errors='coerce')
            res = res.append(trxs).drop_duplicates(subset=['hash'])

            print(res)
        # res=res.drop_duplicates(['hash'])
        res = res.sort_values('timeStamp')
        allTrxs = res.to_json(orient='records')
        allTrxs = json.loads(allTrxs)

    return {'AllTrxs': allTrxs}


if __name__ == '__main__':
    app.debug = True
    app.run()
