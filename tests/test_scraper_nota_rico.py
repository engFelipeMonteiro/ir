import tabula
import pandas as pd

def test_scraper_rico_01():
    # list_final = []
    filename = 'tests/data/nota.pdf'
    dfs = tabula.read_pdf(filename, multiple_tables=False, stream=True, pages="1", guess=False)
    # read_pdf returns list of DataFrames
    # df_final = pd.concat(dfs, ignore_index=True)
    nr_nota, nr_folha = dfs[0]['Unnamed: 2'].iloc[1].split()
    date = dfs[0]['Unnamed: 3'].iloc[1]
    bc_ag = dfs[0]['Unnamed: 0'].iloc[15]
    cc = dfs[0]['NOTA DE NEGOCIAÇÃO'].iloc[15]
    info_nota = {
        "date": date,
        "cc_info":bc_ag.replace(' ', '-')+'-'+cc,
        "nr_nota": nr_nota,
        "nr_folha": nr_folha
        }
    # cc
    # info_nota
    dfs = tabula.read_pdf(filename, stream=True, pages="1", area=[235.0,32.0,450.0,580.0])
    df_final = pd.concat(dfs, ignore_index=True)
    info_nota['df'] = df_final
    print(info_nota)

    #resultado financeiro
    dfs = tabula.read_pdf(filename, multiple_tables=True, stream=True, pages="1", area=[450.0,300.0,660.0,560.0], guess=False)
    import pdb; pdb.set_trace()
    #print(len(dfs))
    #date
    #nr_nota, nr_folha
    #dfs[0]
    #date