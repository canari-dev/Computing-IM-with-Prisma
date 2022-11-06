import pandas as pd
import requests

class Prisma():

    def __init__(self, df):
        self.df = df
        API_key = "XXXX insert your key here XXXX"
        self.url_base = ("https://api.developer.deutsche-boerse.com/prod/prisma-margin-estimator-2-0/2.0.0/")
        self.api_header = {"X-DBP-APIKEY": API_key}


    def make_portfolio(self):
        self.etd = []
        e = 1
        for i, row in self.df.iterrows():

            a = requests.get(self.url_base + "series",
                             params={'products': row.udl},
                             headers=self.api_header).json()
            opt = [elt for elt in a['list_series'] if (elt['exercise_price'] >= row['Strike']*0.999) and
                   (elt['exercise_price'] <= row['Strike']*1.0001) and (elt['call_put_flag'] == row['Option_type'][0]) and (
                        str(elt['contract_date']) == row.Maturity) and (elt['exercise_style_flag'] == row.optstyle)]
            if len(opt)==0:
                print('Error cannot find opt in Prisma {}'.format(row))
            elif len(opt)>1:
                print('Error too many opt in Prisma {}'.format(opt))
            else:
                self.etd += [{'line_no': e, 'iid': opt[0]['iid'], 'net_ls_balance': row['Quantity']}]
                e+=1

    def compute_margin(self):
        self.results = requests.post(self.url_base + 'estimator',
                                        headers=self.api_header,
                                        json={'portfolio_components': [
                                            {'type': 'etd_portfolio',
                                             'etd_portfolio': self.etd}],
                                            'clearing_currency': 'EUR',
                                            'is_cross_margined': True}).json()
        return(self.results['portfolio_margin'][0]['market_risk'], self.results['portfolio_margin'][0]['liquidity_addon'],
               self.results['portfolio_margin'][0]['initial_margin'])


if __name__ == '__main__':
    leg1 = pd.DataFrame({'udl': 'SAP','Option_type':'Call', 'Strike': 88, 'delta': 0.5,'Quantity': 100, 'Contract_size':100, 'Maturity': '20231215', 'optstyle': 'A'}, index=[0])
    leg2 = pd.DataFrame({'udl': 'SAP', 'Option_type': 'Put', 'Strike': 88, 'delta': -0.5, 'Quantity': 100, 'Contract_size': 100, 'Maturity': '20231215', 'optstyle': 'A'}, index=[0])
    df = pd.concat([leg1, leg2])
    # print(df)
    PR = Prisma(df)
    PR.make_portfolio()
    print('market_risk: {0[0]}, liquidity_addon: {0[1]}, initial_margin: {0[2]}'.format(PR.compute_margin()))


