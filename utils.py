import json
import requests
import sqlite3
import pandas as pd

def get_instruments(key):
    instruments_headers = {
      "Authorization": key
  }
    instruments_response = requests.get("https://live.trading212.com/api/v0/equity/metadata/instruments", headers=instruments_headers)
    return(instruments_response)

def get_all_pies(key):
    print(key)
    url = "https://live.trading212.com/api/v0/equity/pies"
    headers = {"Authorization": key}
    response = requests.get(url, headers=headers)
    return(response)

def reweight(user, url, id, currency, subs):
  conn = sqlite3.connect('db/t212.db')
  cursor = conn.cursor()
  cursor.execute('SELECT api_key FROM user WHERE user = ?', (user,))
  key = cursor.fetchone()[0]
  conn.close()

  df = pd.read_excel(url)
  df = df.drop(df.index[0:4])
  new_header = df.iloc[0] #grab the first row for the header
  df.columns = new_header #set the header row as the df header
  df = df.drop(df.index[0]).reset_index(drop=True)
  df = df.drop(df.index[101:]).reset_index(drop=True)

  for sub in subs['subs']:
    print(sub['Name_Sub'])
    df.loc[df['ISIN'] == sub['ISIN'], ['Full name', 'ISIN']]= [sub['Name_Sub'], sub['ISIN_Sub']]

  instruments_headers = {
      "Authorization": key
  }
  instruments_response = requests.get("https://live.trading212.com/api/v0/equity/metadata/instruments", headers=instruments_headers)
  instruments_data_df  = pd.DataFrame(instruments_response.json())
  merged = df.merge(instruments_data_df, how = 'left', left_on = 'ISIN', right_on = 'isin')
  local_currency_df = merged[merged['currencyCode'] == currency].reset_index(drop=True)
  pie_candidates = local_currency_df[0:50].copy()
  #normalise remaining constituents so that they sum to 1
  pie_candidates['Weight'] = (pie_candidates['Weight']/sum(pie_candidates['Weight'])).apply(lambda x: round(x, 6))
  pie_candidates_dict = dict(zip(pie_candidates['ticker'], pie_candidates['Weight']))
  
  #circumvent floating point division problems
  int_dict = dict.fromkeys(pie_candidates_dict)
  for dict_key in pie_candidates_dict.keys():
    int_dict[dict_key] = int(pie_candidates_dict[dict_key] * 1000)
  print(sum(int_dict.values()))
  
  remainder = 1000 - sum(int_dict.values())
  
  while(remainder != 0):
    min_key = min(int_dict, key=int_dict.get)
    max_key = max(int_dict, key=int_dict.get)
    if(remainder > 0):
      int_dict[min_key] = int(int_dict[min_key] + remainder/abs(remainder))
    else:
      int_dict[max_key] = int(int_dict[max_key] + remainder/abs(remainder))
    remainder -= int(remainder/abs(remainder))

  for dict_key in int_dict.keys():
    int_dict[dict_key] = str(int_dict[dict_key])
    if(len(int_dict[dict_key]) == 3):
      int_dict[dict_key] = '0.' + int_dict[dict_key]
    elif(len(int_dict[dict_key]) == 2):
      int_dict[dict_key] = '0.0' + int_dict[dict_key]
    else:
      int_dict[dict_key] = '0.00' + int_dict[dict_key] 


  print(key)
  payload = {
    "dividendCashAction": "REINVEST",
    "endDate": "2019-08-24T14:15:22Z",
    "goal": 25000,
    "icon": "Home",
    "instrumentShares": int_dict
    }
  headers = {
    "Content-Type": "application/json",
    "Authorization": key
    }
  
  pie_URL = "https://live.trading212.com/api/v0/equity/pies/" + str(id)
  response = requests.post(pie_URL, json=payload, headers=headers)
  return response