from src.crawler_rico import CrawlerRico


def test_crawler_rico_build():
    print("")
    crawler = CrawlerRico()
    list_files = crawler.find_files()
    len_files = len(list_files)
    for c, file in enumerate(list_files):
        crawler.process_pages(file=file, len_files=len_files, counter=c+1)
    crawler.to_csv('final_df.csv')
    crawler.to_parquet('final_df.p')


import pandas as pd
from tqdm import tqdm
def test_crawler_read_parquet():
    def make_PM(row):
        if row['operacao'].upper() == 'C':
            make_PM.cum += row['valor_ajustado']
            make_PM.qtd += row['qtd_ajustada']
            pm = make_PM.cum/make_PM.qtd
        elif row['operacao'].upper() == 'V':
            pm = make_PM.cum/make_PM.qtd
            make_PM.cum += pm*row['qtd_ajustada']
            make_PM.qtd += row['qtd_ajustada']
        else:
            import pdb; pdb.set_trace()
        return pd.Series(data={ 'preco_medio_compra': pm, 'qtd_acum':make_PM.qtd}, index=['preco_medio_compra', 'qtd_acum'])

    df = pd.read_parquet('final_df.p')
    # adicionar preco medio de compra
    for ticker in tqdm(df['ticker'].unique()):
        make_PM.cum = 0
        make_PM.qtd = 0
        df[['preco_medio_compra','qtd_acum']] = df[df['ticker'] == ticker].apply(make_PM, axis=1)

    import pdb; pdb.set_trace()
