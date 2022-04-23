import tabula
import pandas as pd
from decimal import Decimal as dec

def test_scraper_rico_01():
    def __get_dec_from_string(s, sep='#'):
        """
        # # 1.000,00 -> 1,000.00
        # 1.000,00 -> 1#000,00  (replace)
        # 1#000,00 -> 1#000.00  (replace)
        # 1#000.00 -> 1,000.00  (replace)

        # ou 
        
        # # 1.000,00 -> 1,000.00
        # 1.000,00 -> ['1.000','00'] ## sempre len == 2 (split)
        # ['1.000','00'] -> ['1,000','00']  (index+replace)
        # ['1,000','00'] -> 1,000.00    (join)
        """
        #s.replace('.', sep).replace(',','.').replace(sep,',')
        l_split = s.split(',')
        return dec('.'.join([l_split[0].replace('.', ','), l_split[1]]))
    # list_final = []
    page = '1'
    filename = 'tests/data/nota01.pdf'
    dfs = tabula.read_pdf(filename, multiple_tables=False, stream=True, pages=page, guess=False)
    # read_pdf returns list of DataFrames
    # df_final = pd.concat(dfs, ignore_index=True)
    op_info = dfs[0]['Unnamed: 2'].iloc[1].replace(' ', '-')
    date = dfs[0]['Unnamed: 3'].iloc[1]
    bc_ag = dfs[0]['Unnamed: 0'].iloc[15]
    cc = dfs[0]['NOTA DE NEGOCIAÇÃO'].iloc[15]
    info_nota = {
        "date": date,
        "cc_info":bc_ag.replace(' ', '-')+'-'+cc,
        "op_info": op_info
        }
    # cc
    # info_nota
    # (top,left,bottom,right)
    dfs = tabula.read_pdf(filename, stream=True, pages=page, area=[235.0,32.0,450.0,580.0])
    df_final = pd.concat(dfs, ignore_index=True)
    info_nota['df'] = df_final
    print(info_nota)

    #resultado financeiro
    # (top,left,bottom,right)
    dfs = tabula.read_pdf(filename, multiple_tables=True, stream=True, pages=page, area=[450.0,300.0,660.0,560.0], guess=False)
    taxas_liquidacao_mais_registro = \
        __get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[2]) \
            + \
        __get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[3])

    taxas_bovespa = __get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[9])
    outros_custos_despesas = __get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[18])
    info_nota['taxas']= {
        'liq_reg': taxas_liquidacao_mais_registro,
        'bovespa': taxas_bovespa,
        'operacional': outros_custos_despesas
    }

    new_df = \
        info_nota['df']\
            [
                ['C/V', 'Tipo mercado','Especificação do título', 'Unnamed: 1', 'Preço / Ajuste', 'Valor Operação / Ajuste']
            ].rename(columns={
                    'C/V': 'operacao',
                    'Tipo mercado': 'mercado',
                    'Especificação do título': 'ticker',
                    'Unnamed: 1': 'qtd',
                    'Preço / Ajuste': 'preco',
                    'Valor Operação / Ajuste': 'valor'
                }
            )
    import pdb; pdb.set_trace()
    info_nota['df'] = None
    assert page == '1'
    assert info_nota ==\
        {
            'cc_info': '001-3477-53572',
            'date': '03/11/2021',
            'df': None,
            'op_info': '6307261-1',
            'taxas': {'bovespa': dec('0.01'),
                    'liq_reg': dec('0.08'),
                    'operacional': dec('0.00')}
        }

    # info_nota['df'][['C/V', 'Tipo mercado','Especificação do título', 'Unnamed: 1', 'Preço / Ajuste', 'Valor Operação / Ajuste']]
    #print(len(dfs))
    #date
    #nr_nota, nr_folha
    #dfs[0]
    #date