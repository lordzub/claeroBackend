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
cors = CORS(app)
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
ETHAPIKEY= 'PQ3GK8R48PZWZE3KJN4ZZBQE81AVEPBFQX'
ethurl='https://api.etherscan.io/api'
apiurl = ''
bscurl = 'https://api.bscscan.com/api'
APIKEY=ETHAPIKEY
apiurl =ethurl


@app.route('/getTokens/<address>', methods=['GET'])
def get_tokens(address):
    print(address)
    # address = request.json['account']
    if len(address) ==0:
        return {'res':'null'}
    else:
        obj = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'sort': 'asc',
            'apikey': APIKEY
        }
        token_transfer_events = requests.post(apiurl, obj).json()
        transfers = token_transfer_events['result']
        print(token_transfer_events)
        unq_contracts = []
        details = []
        for transfer in transfers:

            contractAddress = transfer['contractAddress']
            tokenName = transfer['tokenName']
            tokenSymbol = transfer['tokenSymbol']
            tokenDecimal = transfer['tokenDecimal']
            if contractAddress not in unq_contracts:
                unq_contracts.append(contractAddress)
                # get token balance of this contract
                obj = {
                    'module': 'account',
                    'action': 'tokenbalance',
                    'address': address,
                    'contractaddress': contractAddress,
                    'tag': 'latest',
                    'apikey': APIKEY
                }
                token_balance = requests.post(apiurl, obj).json()

                balance = int(token_balance['result']) / (10**int(tokenDecimal))
                print(balance)
                # if balance > 0:
                detObj = {

                        'tokenName': tokenName,
                        'tokenSymbol': tokenSymbol,
                        'tokenName': tokenName,
                        'balance': balance,
                        'contractAddress': contractAddress
                }
                details.append(detObj)

        return {'res': details}


@app.route('/getNormalTransactions/<address>/', methods=['GET'])
def get_normal_transactions(address):
    print('Getting Normal Trxs for', address)
    address = address.lower()
    # contract = contract.lower()
    obj ={
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'sort': 'asc',
        'apikey':APIKEY
    }
    token_transfer_events = requests.post(apiurl, obj).json()
    # transfers = token_transfer_events['result']
    transfers = token_transfer_events['result']
    # print(transfers)
    senders = []
    receivers = []
    for transfer in transfers:
        print(transfer)
        trx_hash = transfer['hash']
        sender = transfer['from']
        receiver = transfer['to']
        # token_name = transfer['tokenName']
        # token_symbol = transfer['tokenSymbol']
        # token_decimal = transfer['tokenDecimal']
        amount = int(transfer['value'])

        # print(sender,address.lower())
        if sender == address:
            obj = {'address': receiver, 'amount': amount, 'trxHash': trx_hash}
            receivers.append(obj)
        elif receiver == address:
            obj = {'address': sender, 'amount': amount, 'trxHash': trx_hash}
            senders.append(obj)
        res = {
            # 'tokenName': token_name,
            # 'tokenSymbol': token_symbol,
            'senders': senders,
            'receivers': receivers
        }
        # print(res)
    return {'transfers': res}

# BEP tokens
@app.route('/getTrxs/<address>/<contract>', methods=['GET'])
def get_trxs(address,contract):
    print(address, contract)
    address = address.lower()
    contract = contract.lower()
    obj ={
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': contract,
        'address': address,
        'sort': 'asc',
        'apikey':APIKEY
    }
    token_transfer_events = requests.post(apiurl, obj).json()

    transfers = token_transfer_events['result']

    senders = []
    receivers = []

    alltrans = []
    for transfer in transfers:
        print(transfer)
        trx_hash = transfer['hash']
        sender = transfer['from']
        receiver = transfer['to']
        token_name = transfer['tokenName']
        token_symbol = transfer['tokenSymbol']
        token_decimal = transfer['tokenDecimal']
        time_stamp = transfer['timeStamp']
        block_hash = transfer['blockHash']
        block_number = transfer['blockNumber']
        transactionIndex = transfer['transactionIndex']
        amount = int(transfer['value'])/10**int(token_decimal)

        # print(sender,address.lower())
        obj = {'receiver': receiver,
               'sender':sender,
               'amount': amount,
               'trxHash': trx_hash,
               'time_stamp':time_stamp,
               'block_hash':block_hash,
               'block_number':block_number,
               'transactionIndex':transactionIndex
               }
        alltrans.append(obj)

    res = {
        'tokenName': token_name,
        'tokenSymbol': token_symbol,
        'trans': alltrans,
    }

    return {'transfers': res}

@app.route('/getTrxsConcat/<address>/<contract>', methods=['GET'])
def get_trxs_concat(address,contract):
    print(address, contract)
    print(request.json)
    address = address.lower()
    # contract = request.json['contractAddress']
    if contract == 'none':
        obj ={
            'module': 'account',
            'action': 'tokentx',
            # 'contractaddress': contract,
            'address': address,
            'sort': 'asc',
            'apikey':APIKEY
        }
    else:
        obj = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': contract,
            'address': address,
            'sort': 'asc',
            'apikey': APIKEY
        }


    token_transfer_events = requests.post(apiurl, obj).json()
    print(token_transfer_events)

    transfers = token_transfer_events['result']
    # print(transfers)
    senders = []
    receivers = []
    senderAddresses=[]
    receiverAddresses=[]

    tokens =  []

    returnArr=[]
    returnObj ={'data':{'totalSenders':0,'totalRec':0}}
    for transfer in transfers:
        print(transfer)
        trx_hash = transfer['hash']
        sender = transfer['from']
        receiver = transfer['to']
        token_name = transfer['tokenName']
        token_symbol = transfer['tokenSymbol']
        token_decimal = transfer['tokenDecimal']
        time_stamp = transfer['timeStamp']
        block_hash = transfer['blockHash']
        block_number = transfer['blockNumber']
        transactionIndex = transfer['transactionIndex']

        if token_name not in tokens:
            tokens.append(token_name)

            returnObj[token_name]= {'symbol': token_symbol, 'amount': 0, 'senders': [], 'receivers': []}


        amount = int(transfer['value'])/10**int(token_decimal)

        # print(sender,address.lower())
        if sender == address:
            if receiver not in receiverAddresses:

                obj = {'address': receiver,'totalAmount':amount, 'transactions':[{ 'amount':amount,'trxHash':trx_hash, 'timeStamp':time_stamp,'blockHash':block_hash,'trx_index':transactionIndex,'blockNumber':block_number}]}
                receivers.append(obj)
                returnObj[token_name]['receivers'].append(obj)
                returnObj[token_name]['amount'] += amount
                # returnObj[token_name]['totalAmount'] -= amount
                # returnObj[token_name]['totalSendAmount'] += amount
                receiverAddresses.append(receiver)

            else:
                for i in returnObj[token_name]['receivers']:
                    if i['address'] == receiver:
                        # returnObj[token_name]['totalAmount'] -= amount
                        # returnObj[token_name]['totalSendAmount'] += amount
                        # returnObj[token_name]['receivers'][address]['totalAmount']+= amount
                        i['totalAmount'] -= amount
                        returnObj[token_name]['amount'] -=amount
                        # returnObj[token_name]['receivers']['address']['transactions'].append({'amount':amount, 'trxHash':trx_hash, 'timeStamp':time_stamp,'blockHash':block_hash,'trx_index':transactionIndex,'blockNumber':block_number})
                        i['transactions'].append({'amount':amount, 'trxHash':trx_hash, 'timeStamp':time_stamp,'blockHash':block_hash,'trx_index':transactionIndex,'blockNumber':block_number})

        elif receiver == address:
            if sender not in senderAddresses:
                obj = {'address': sender,'totalAmount':amount,'transactions':[{'amount':amount,'trxHash':trx_hash, 'timeStamp':time_stamp,'blockHash':block_hash,'trx_index':transactionIndex,'blockNumber':block_number}]}
                senders.append(obj)
                returnObj[token_name]['senders'].append(obj)
                returnObj[token_name]['amount'] += amount
                senderAddresses.append(sender)
            else:
                for i in returnObj[token_name]['senders']:
                    if i['address'] == sender:
                        i['totalAmount']+=amount
                        returnObj[token_name]['amount']+=amount
                        # returnObj[token_name]['totalAmount'] +=amount
                        # returnObj[token_name]['totalSendAmount'] += amount

                        i['transactions'].append({'tokenSymbol': token_symbol,'tokenName': token_name,'amount':amount,'trxHash':trx_hash, 'timeStamp':time_stamp,'blockHash':block_hash,'trx_index':transactionIndex,'blockNumber':block_number})


    # for sender in senders:

    res = {


        'senders': senders,
        'receivers': receivers
        }
        # print(res)
    returnObj['data']['totalSenders'] = len(senderAddresses)
    returnObj['data']['totalRec'] = len(receiverAddresses)
    print(returnObj)
    return returnObj


@app.route('/getTable/<address>/<contract>', methods=['GET'])
def get_Table(address, contract):
    return null

@app.route('/getTokenInfo/<address>/', methods=['GET'])
def get_Token_Info(address):
    address = address.lower()
    obj = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()
    transfers = token_transfer_events['result']
    trxs = pd.DataFrame(transfers)
    print(trxs.columns)
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


    returnArr = []
    for i in uniqueTokens:
        returnArr.append(getTokenInfo(i,address, trxs))
    return {'tokens': returnArr}



def getTokenInfo(contract, address, df):
    df = df.groupby('contractAddress')
    tokenTrxs = df.get_group(contract)
    # Get Decimal
    decimal = 10 ** int(tokenTrxs['tokenDecimal'].unique()[0])
    tokenSymbol = tokenTrxs['tokenSymbol'].unique()[0]
    tokenName=tokenTrxs['tokenName'].unique()[0]
    sentTrxs = tokenTrxs['from'].unique()
    recTrxs = tokenTrxs['to'].unique()
    if (address in sentTrxs):
        mySentTrxs = tokenTrxs.groupby('from').get_group(address)
        uniqueSentToAdd =pd.DataFrame( mySentTrxs['to'].unique())
        uniqueSentToAddCount = len(mySentTrxs['to'].unique())
        totalSentTrxs = len(mySentTrxs)
        myTotalSentValue = mySentTrxs['value'].sum() / decimal
    else:
        uniqueSentToAdd =pd.DataFrame([])

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
        'contract':contract,
        'tokenSymbol': tokenSymbol,
        'uniqueSentToAddCount': uniqueSentToAddCount,
        'totalSentTrxs': totalSentTrxs,
        'myTotalSentValue': round(myTotalSentValue,2),
        'uniqueRecFromAddCount': uniqueRecFromAddCount,
        'totalRecTrxs': totalRecTrxs,
        'myTotalRecValue': round(myTotalRecValue,2),
        'balance': round(myTotalRecValue - myTotalSentValue,2),
        'show': True,
        'expand': False
    }
    return obj

# returns dataframe of eth transactions
def getEthTrxs(address):
    address = address.lower()
    obj = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'sort': 'asc',
        'apikey': APIKEY
    }

    token_transfer_events = requests.post(apiurl, obj).json()
    transfers = token_transfer_events['result']
    trxs = pd.DataFrame(transfers)
    return trxs

@app.route('/getTokenAddInfo/<address>/<token>', methods=['GET'])
def get_Token_Add_Info(address,token):
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
        addRecTrxs=pd.DataFrame()
        totalRecTrxs = 0
        addTotalRecValue = 0
        recTrxs = []


    allTrxs = pd.concat([addRecTrxs,addSentTrxs])
    allTrxs = allTrxs.to_json(orient='records')
    allTrxs= json.loads(allTrxs)

    obj = {
        'address': Address,
        'token': token,
        'tokenSymbol': tokenSymbol,
        'totalSentTrxs': totalSentTrxs,
        'addTotalSentValue': round(addTotalSentValue,2),
        'totalRecTrxs': totalRecTrxs,
        'addTotalRecValue': round(addTotalRecValue,2),
        # 'recTrxs': recTrxs,
        # 'sentTrxs': sentTrxs,
        'allTrxs':allTrxs,
        'expand':False,
        'show':True

    }
    return obj


@app.route('/getAllTrxs2/<address>', methods=['GET'])
def getAllTrxs2(address):
    address = address.lower()
    trxs=pd.DataFrame()
    apiInteractions = ['tokentx','txlist']
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
    if (contracts[0]=='none'):
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
            res= res.append(trxs).drop_duplicates(subset=['hash'])

            print(res)
        # res=res.drop_duplicates(['hash'])
        res=res.sort_values('timeStamp')
        allTrxs = res.to_json(orient='records')
        allTrxs = json.loads(allTrxs)

    return {'AllTrxs': allTrxs}





if __name__ == '__main__':
    app.debug = True
    app.run()

