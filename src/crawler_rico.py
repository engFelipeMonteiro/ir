import tabula
import pandas as pd
import PyPDF2
# import os
import glob
import datetime
import math
from decimal import Decimal as dec
from pdb import set_trace as pdbug
from pandas._libs.tslibs.timestamps import Timestamp
import datetime
class CrawlerRico:
    list_dfs = []

    def find_files(self, path='tests/data/'):
        list_files = glob.glob(path+'*.pdf')
        return list_files

    def add_index(self, nota):

        def set_index(row, op_info=nota['op_info']):
            return f"{op_info}-{row.name}"

        nota['df']['index'] = nota['df'].apply(set_index, axis=1)

    def ditribui_taxas(self, nota):
        # try:
        #     #nota['df']['qtd'] = nota['df']['qtd'].apply( lambda q: dec(str(q))) 
        #     nota['df']['valor'] = nota['df'].apply(
        #                             lambda r: r['qtd']*r['preco'], axis=1)
        # except Exception as err:
        #     import pdb; pdb.set_trace()
        def set_taxa_prop(
                    row,
                    total=nota['df']['valor'].sum()-nota['taxas'],
                    taxa=nota['taxas']):
            try:
                result = (row['preco']*row['qtd']/total)*taxa
                if result > row['preco']:
                    pdbug()
                    print("result > row['preco']")
                return result
            except Exception:
                import pdb; pdb.set_trace()
        nota['df']['tax_prop'] = nota['df'].apply(set_taxa_prop, axis=1)

        # check if tax correctly distributed
        if nota['df']['tax_prop'].sum() != nota['taxas']:
            print("Diferença no calculo das taxas\n"
                  f"taxa proporcional somada: {nota['df']['tax_prop'].sum()}"
                  f"taxa via nota: {nota['df']['tax_prop'].sum()}")

    def ajusta_preco_qtd(self, nota):

        def get_preco_ajustado(row):
            if row['operacao'].upper() == 'V':
                return (row['valor']-row['tax_prop'])*-1
            elif row['operacao'].upper() == 'C':
                return row['valor']+row['tax_prop']
            else:
                return 'operation_unknown'

        def get_qtd_ajustada(row):
            if row['operacao'].upper() == 'V':
                return (row['qtd'])*-1
            elif row['operacao'].upper() == 'C':
                return row['qtd']
            else:
                return 'operation_unknown'

        def get_valor_compra(row):
            if row['operacao'].upper() == 'V':
                return dec('0.0')
            elif row['operacao'].upper() == 'C':
                return row['valor']
            else:
                return 'operation_unknown'

        def get_qtd_compra(row):
            if row['operacao'].upper() == 'V':
                return dec('0.0')
            elif row['operacao'].upper() == 'C':
                return row['qtd']
            else:
                return 'operation_unknown'

        nota['df']['valor_ajustado'] = nota['df'].apply(
                                            get_preco_ajustado, axis=1)
        nota['df']['qtd_ajustada'] = nota['df'].apply(
                                            get_qtd_ajustada, axis=1)

        nota['df']['valor_compra'] = nota['df'].apply(
                                            get_valor_compra, axis=1)
        nota['df']['qtd_compra'] = nota['df'].apply(
                                            get_qtd_compra, axis=1)

    def __process_notas(self) -> None:
        """
            one call for each file
            trasforma valores para Decimals, date para datetime, preco.

            valor
            Vc = valor + taxas
            Vv = Valor - taxas
        """

        for nota in self.list_notas:
            nota['taxas'] = sum([x for x in nota['taxas'].values()])
            # transforma valores de string em decimal
            # nota['df']['preco'] = nota['df']['preco']\
            #     .apply(self._CrawlerRico__get_dec_from_string)
            # nota['df']['valor'] = nota['df']['valor']\
            #     .apply(self._CrawlerRico__get_dec_from_string)
            # adiciona data ao dataframe
            nota['df']['data'] = nota['date']
            nota['df'][['classe', 'ticker']] = self.ajusta_ticker_name(nota)
            nota['df']['aquisicao_via'] = 'HomeBroker'
            self.ditribui_taxas(nota)
            self.ajusta_preco_qtd(nota)
            self.add_index(nota)
            # create index
            nota['df'].set_index('index', inplace=True)
            # append processed dataframe
            self.list_dfs.append(nota['df'])
            # import pdb; pdb.set_trace()


        # ajust values for export
        # new_df['valor_ajustado'] = new_df['valor_ajustado'].apply(lambda x: round(x,5))

    def process_pages(self, file='tests/data/nota01.pdf', len_files=0, counter=0):
        with open(file, 'rb') as f:
            page_count = PyPDF2.PdfFileReader(f).numPages

        self.list_notas = []
        error = False
        for page in range(1, page_count+1):
            print(f"iniciando leitura de arquivo ({file})[{counter}/{len_files}], pagina {page}/{page_count}")
            nota_dic = self.__get_dict_from_page(file, str(page))
            if nota_dic:
                self.list_notas.append(nota_dic)
            else:
                print(f"pulando nota {file}")
                error = True
                break
            #import pdb; pdb.set_trace()

        if not error:
            self.__process_notas()

    def __get_dec_from_string(self, ss, sep='#'):
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
        # s.replace('.', sep).replace(',','.').replace(sep,',')
        try:
            l_split = ss.split(',')
        except Exception as err:
            if math.isnan(ss):
                return dec('0.0')
            else:
                print(f"exception: {err.args}")
                import pdb; pdb.set_trace()
                return -1
        return dec('.'.join([l_split[0].replace('.', ','), l_split[1]]))

    def convert_dec(self, df, dfs):
        df['preco'] = df['preco'].apply(self._CrawlerRico__get_dec_from_string)
        df['qtd'] = df['qtd'].apply(lambda q: dec(str(q)))
        df['valor'] = df.apply(lambda q: q['qtd']*q['preco'], axis=1)
        if df['preco'][0] == dec('0.0'):
            df['preco'] = dfs[0]['Unnamed: 1'].apply(self._CrawlerRico__get_dec_from_string)
            df['valor'] = df.apply(lambda q: q['qtd']*q['preco'], axis=1)
            if df['preco'][0] == dec('0.0'):
                pdbug()
        

    def __get_dict_from_page(
                    self,
                    filepath='tests/data/nota01.pdf',
                    page='1'
                    ):
        dfs = tabula.read_pdf(
                        filepath,
                        multiple_tables=False,
                        stream=True,
                        pages=page,
                        guess=False)
        # read_pdf returns list of DataFrames
        # df_final = pd.concat(dfs, ignore_index=True)
        # if filepath == 'tests/data/2021_11.pdf' and page == '5':
        #     pdbug()
        for field in ['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Nr. nota Folha']:
            if field in dfs[0] and not isinstance(dfs[0][field][1], float):
                try:
                    op_info = dfs[0][field].iloc[1].replace(' ', '-')
                    break
                except Exception:
                    import pdb; pdb.set_trace()
        # try:
        #     op_info = dfs[0]['Unnamed: 2'].iloc[1].replace(' ', '-')
        # except AttributeError:
        #     #import pdb; pdb.set_trace()
        #     try:
        #         op_info = dfs[0]['Unnamed: 3'].iloc[1].replace(' ', '-')
        #     except AttributeError:
        #         op_info = dfs[0]['Nr. nota Folha'].iloc[1].replace(' ', '-')
        #     except Exception:
        #         pdbug()
        #         print('exceptio 01')
        # except KeyError:
        #     #import pdb; pdb.set_trace()
        #     op_info = dfs[0]['Unnamed: 4'].iloc[1].replace(' ', '-')
        # except (Exception, AttributeError) as err:
        #     import pdb; pdb.set_trace()
        #     print('exceptio 02')


        try:
            date = datetime.datetime.strptime(
                            dfs[0]['Unnamed: 3'].iloc[1],
                            "%d/%m/%Y")
        except Exception:
            try:
                date = datetime.datetime.strptime(
                            dfs[0]['Unnamed: 4'].iloc[1],
                            "%d/%m/%Y")
            except Exception:
                try:
                    date = datetime.datetime.strptime(
                                dfs[0]['Unnamed: 5'].iloc[1],
                                "%d/%m/%Y")
                except Exception:
                    try:
                        date = datetime.datetime.strptime(
                                    dfs[0]['Unnamed: 6'].iloc[1],
                                    "%d/%m/%Y")
                    except Exception:
                        try:
                            date = datetime.datetime.strptime(
                                        dfs[0]['Data pregão'].iloc[0],
                                        "%d/%m/%Y")
                        except Exception:
                            import pdb; pdb.set_trace()

        bc_ag = dfs[0]['Unnamed: 0'].iloc[15]
        cc = dfs[0]['NOTA DE NEGOCIAÇÃO'].iloc[15]
        info_nota = {
            "date": date,
            "cc_info": bc_ag.replace(' ', '-')+'-'+cc,
            "op_info": op_info
            }

        # (top,left,bottom,right)
        # add operations
        dfs = tabula.read_pdf(filepath,stream=True,pages=page,area=[235.0, 32.0, 450.0, 580.0])
        # remove df from list
        try:
            df_final = pd.concat(dfs, ignore_index=True)
        except Exception:
            return None
        # qtd fix

        qtd_str = 'Unnamed: 1'
        if 'NaN' in df_final[qtd_str].to_string() or ',' in df_final[qtd_str].to_string():
            qtd_str = 'Unnamed: 0'
            if 'NaN' in df_final[qtd_str].to_string() or ',' in df_final[qtd_str].to_string():
                qtd_str = 'Unnamed: 2'
                if 'NaN' in df_final[qtd_str].to_string() or ',' in df_final[qtd_str].to_string():
                    pdbug()

        # if date == datetime.datetime(2021, 8, 18, 0, 0):
        #     pdbug()
        
        
        new_df =  df_final[
                [
                    'C/V', 'Tipo mercado', 'Especificação do título',
                    qtd_str, 'Preço / Ajuste',
                    'Valor Operação / Ajuste'
                ]
            ].rename(columns={
                    'C/V': 'operacao',
                    'Tipo mercado': 'mercado',
                    'Especificação do título': 'ticker',
                    qtd_str: 'qtd',
                    'Preço / Ajuste': 'preco',
                    'Valor Operação / Ajuste': 'valor'
                    })

        self.convert_dec(new_df, dfs)
        info_nota['df'] = new_df
        #resultado financeiro
        # (top,left,bottom,right)
        dfs = tabula.read_pdf(
                    filepath,
                    multiple_tables=True,
                    stream=True,
                    pages=page,
                    area=[450.0, 300.0, 660.0, 560.0],
                    guess=False)

        taxas_liquidacao_mais_registro = \
            self.__get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[2]) \
            + \
            self.__get_dec_from_string(dfs[0]['Unnamed: 0'].iloc[3])

        taxas_bovespa = self.__get_dec_from_string(
                            dfs[0]['Unnamed: 0'].iloc[9])
        outros_custos_despesas = self.__get_dec_from_string(
                            dfs[0]['Unnamed: 0'].iloc[18])

        info_nota['taxas'] = {
            'liq_reg': taxas_liquidacao_mais_registro,
            'bovespa': taxas_bovespa,
            'operacional': outros_custos_despesas
        }

        info_nota['total_nota'] = self.__get_dec_from_string(
                            dfs[0]['Unnamed: 0'].iloc[19])

        return info_nota

    def to_csv(self, path):
        new_df = pd.concat(
                        self.list_dfs,
                        ignore_index=False,
                        verify_integrity=True)
        
        # format columns
        new_df['tax_prop'] = new_df['tax_prop'].apply(lambda x: round(x,5) )
        new_df['valor_ajustado'] = new_df['valor_ajustado'].apply(lambda x: round(x,5) )
        new_df = new_df.sort_values(by=['data'],ascending=True)
        new_df.to_csv(path)
    
    def to_parquet(self, path):
        new_df = pd.concat(
                        self.list_dfs,
                        ignore_index=False,
                        verify_integrity=True)
        
        # format columns
        #new_df['tax_prop'] = new_df['tax_prop'].apply(lambda x: round(x,5) )
        #new_df['valor_ajustado'] = new_df['valor_ajustado'].apply(lambda x: round(x,5) )
        new_df = new_df.sort_values(by=['data'],ascending=True)
        new_df.to_parquet(path)

    def ajusta_ticker_name(self, nota):
        fii_list = {
            "CRIVSLH11": ("VSLH11", "FII"),
            "EITORD11": ("TORD11", "FII"),
            "REITCPFF11": ("CPFF11", "FII"),
            "URBHGRU11": ("HGRU11", "FII"),
            "RENMXRF11": ("MXRF11", "FII"),
            "SHOPVSHO11": ("VSHO11", "FII"),
            "HECTAREHCTR11": ("HCTR11", "FII"),
            "IIRBRD11CI": ("RBRR11", "FII"),
            "MACAEXPCM11": ("XPCM11", "FII"),
            "IMOBABCP11": ("ABCP11", "FII"),
            "SCPSCPF11CI": ("SCPF11", "FII"),
            "SCPSCPF11": ("SCPF11", "FII"),
            "IIHABT11": ("HABT11", "FII"),
            "RENURPR11": ("URPR11", "FII"),
            "HEVGHF11": ("VGHF11", "FII"),
            "LOGSDIL11": ("SDIL11", "FII"),
            "SCVISC11": ("VISC11", "FII"),
            "LOGXPLG11": ("XPLG11", "FII"),
            "ARCTIUMARCT11": ("ARCT11", "FII"),
            "PCRIRBRY11": ("RBRY11", "FII"),
            "RBRHGRADRBRR11": ("RBRR11", "FII"),
            "SECCPTS11": ("CPTS11", "FII"),
            "IRBGS11": ("RBGS11", "FII"),
            "IIRBRD11": ("RBRD11", "FII"),
            "MALLHSML11": ("MALL11", "FII"),
            "PROPRBRP11": ("RBRP11", "FII"),
            "IRIDIUMIRDM11": ("IRDM34", "FII"),
            "RECERECR11": ("RECR11", "FII"),
            "MALLSXPML11": ("XPML11", "FII"),
        }
        def find_fii(l_spt):
            try:
                if '11' in l_spt[-1]:
                    return fii_list[l_spt[-1]]
                elif '11' in l_spt[-2]:
                    return fii_list[l_spt[-2]]
                else:
                    print(f"não encontrado fii string {l_spt}")
                    return ("unknown, unknown")
            except Exception:
                print(f"not found {l_spt[-1]} on fiis dict.")
                pdbug()
        ops = {
            "FII": find_fii,
            "BRADESCOPN": ("BBDC4", "AÇÃO"),
            "ENERGIAS": ("ENBR3", "AÇÃO"),
            "TAESAUNT": ("TAEE11", "AÇÃO"),
            "TRAN": ("TRPL4", "AÇÃO"),
            "ISHARE": ("IVVB11", "ETF"),
            "AES": ("AESB3", "AÇÃO"),
            "CEBON": ("CEBR3", "AÇÃO"),
            "PAR": ("PEAB4", "AÇÃO"),
            "AMAZONDRN": ("AMAZO34", "BDR"),
            "IRON": ("I1RM34", "BDR"),
            "CPFL": ("CPFE3", "AÇÃO"),
            "CYRELA": ("CYRE3", "AÇÃO"),
            "APPLEDRN": ("AAPL34", "BDR"),
            "WALT": ("DISB34", "BDR"),
            "ITAUSAPN": ("ITSA4", "AÇÃO"),
            "TESLA": ("TSLA34", "BDR"),
            "PETROBRAS": ("PETR4", "AÇÃO"),
            "PETROBRASPN": ("PETR4", "AÇÃO"),
            "TAESAPN": ("TAEE4", "AÇÃO"),
            "BRASILON": ("BBAS3", "AÇÃO"),
            "SINQIAON": ("SQIA3", "AÇÃO"),
            "COPELON": ("CPLE3", "AÇÃO"),
            "BBSEGURIDADEON": ("BBSE3", "AÇÃO"),
            "INDS": ("BBSE3", "AÇÃO"),
            "FERBASAPN": ("FESA4", "AÇÃO"),
            "ENAUTA": ("ENAT3", "AÇÃO"),
            "WEGON": ("WEGE3", "AÇÃO"),
            "COPASAON": ("CSMG3", "AÇÃO"),
            "TELEF": ("VIVT3", "AÇÃO"),
            "ITAUUNIBANCOPN": ("ITUB4", "AÇÃO"),
            "VALEON": ("VALE3", "AÇÃO"),
            "PGDRN": ("PGCO34", "BDR"),
            "TAIWANSMFACDRN": ("TSMC34", "BDR"),
            "VERIZONDRN": ("VERZ34", "BDR"),
            "MELIUZON": ("CASH3", "AÇÃO"),
            "MICROSOFTDRN": ("MSFT34", "BDR"),



        }
        def make_ticker(row) -> pd.DataFrame:
            # import pdb; pdb.set_trace()
            ticker_split = row['ticker'].split()
            classe = ticker = 'unknown'
            
            try:
                OP = ops[ticker_split[0]]
                if callable(OP):
                    ticker, classe  = OP(ticker_split)
                else:
                    ticker, classe  = OP
            except Exception:
                print(f"not found {ticker_split[0]} on ops vars.")
                pdbug()
                print(f"not found {ticker_split[0]} on ops vars.")
            return pd.Series(data={ 'classe': classe, 'ticker':ticker}, index=['classe', 'ticker'])
        return nota['df'].apply(make_ticker, axis=1)
