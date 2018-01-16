import os
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from exceptions import NotAbleToConnectToSourceApi
from exceptions import ResponseFromCurrencyApiNotSuccessfull
from exceptions import NoAPIKeyPresent
from ah_requests import AhRequest
from logger import Logger
import json


CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', None)
if not CURRENCY_API_KEY:
    raise NoAPIKeyPresent("Can't find 'CURRENCY_API_KEY' in the env variables", status_code=500) 
    

LOG = Logger()

class MonteCarlo():
    def __init__(self, pair):
        self.pair = pair

    @staticmethod
    def monteCarloOneDay(mu, sigma, start_price):
        r = 1+np.random.normal(loc=mu, scale=sigma, size=1)*0.01
        v = start_price*r[0]
        return v

    def run(self):
        PAIR = self.pair
        date_ten_years_ago = datetime.now() - relativedelta(years=10)
        date_interval = [date_ten_years_ago + relativedelta(years=x) for x in range(0, 11)]

        request_urls = []
        for x in range(len(date_interval)-1):
            url = {'url':"http://www.apilayer.net/api/timeframe?start_date={0}&end_date={1}&access_key={4}&source={2}&currencies={3}".format(date_interval[x].strftime('%Y-%m-%d'), date_interval[x+1].strftime('%Y-%m-%d'), PAIR[:3], PAIR[3:], CURRENCY_API_KEY)}
            request_urls.append(url)
        try:
            ah_request = AhRequest()
            responses = []
            for req in request_urls:
                LOG.console(req['url'])
                responses.append( ah_request.get(req['url'], timeout=5) )
        except Exception as x:
            raise NotAbleToConnectToSourceApi('Failed calling ({0}).'.format(x.__class__.__name__), status_code=500) 
   

        rates = []
        for res in responses:
            if res.json()['success'] != True:
                raise ResponseFromCurrencyApiNotSuccessfull('Failed calling ({0}).'.format(res.url), status_code=500) 
            dates = list(res.json()['quotes'])
            values = list(res.json()['quotes'].values())
            for x in range(len(dates)):
                rates.append({'date':dates[x],'rate':values[x][PAIR]})
            
        rates = sorted(rates, key=lambda item: item['date'], reverse=False)

        start_rate = rates[-1]['rate']
        rates = np.array([x['rate'] for x in rates], dtype=float)
        change = np.diff(rates) / rates[:-1] * 100
        change = np.clip(change,-10,10) 

        mu = change.mean()
        sigma = change.std()

        sim_temp = []
        for _ in range(0, 10000):
            val = self.monteCarloOneDay(mu, sigma, start_rate)
            sim_temp.append(val)
        risk = float( (np.percentile(sim_temp,90)/start_rate*100)-100 )
        return json.dumps(dict(risk=risk))
