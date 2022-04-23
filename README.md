# ir - Projeto de calculo de Imposto de Renda em operacoes na bovespa automaticamente

## o que se propoe a fazer
 - Automaticamente busca todos as suas operacoes na bolsa no site do canal eletronico do investidor (CEI) (https://cei.b3.com.br/)
 - Apos buscar os trades no CEI, salva tudo em um arquivo csv no dropbox da sua conta
 - Todo dia 5 de cada mes executa e calcula (**automaticamente**):
    - Preco medio de compra
    - Preco medio de venda
    - Lucro/Prejuizo no mes
    - IR a pagar, ja considerando o possivel prejuizo acumulado
    - Tabela com a custodia atual para conferencia
    - Envia email com todas as informacoes para voce pagar o imposto
 - A ideia é ser TUDO automatico, mas ainda ter a opcao de voce manualmente ter controle de tudo via um arquivo csv caso algum papel sofra desdobramento ou mude o ticker de negociacao
 - Funciona com FIIs, ETFs, Acoes e Opcoes. Em desenvolvimento (FIP, FIPIE, Futuros)
 - Funciona com qualquer corretora. (Na verdade, nao depende da corretora)

## o que voce vai precisar
 - Uma conta no CEI (https://cei.b3.com.br/)
 - Uma conta no dropbox com API habilitada (https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/)
 - Configurar as variaveis de ambiente conforme (https://github.com/guilhermecgs/ir/blob/master/tests/test_environment_variables.py)
 - Executar os comandos abaixo:
    - python ./ir.py --do check_environment_variables
    - python ./ir.py --do busca_trades_e_faz_merge_operacoes
    - python ./ir.py --do calculo_ir

   
## exemplo do relatorio gerado no seu email
https://github.com/guilhermecgs/ir/blob/master/exemplo_relatorio_automatico.pdf

## Exemplo de variáveis de ambiente:

 - DROPBOX_FILE_LOCATION:/Finance/GCGS/export_operacoes_gcgs.txt
 - DROPBOX_API_KEY:jOznaw_xxxxxxxxxxxxxxxxxxxxtkw9ox_a9I_8-_aU2xw1xxxxxxxxxxKWek69Z
 - GMAIL_FROM:emailremetente@gmail.com
 - GMAIL_PASSWORD:minha_senha_gmail
 - SEND_TO:emaildestinatario@gmail.com
 - CPF:00098765434
 - SENHA_CEI:minha_senha_cei


## disclaimer
 - Aceito PRs :-)   Eu fiz o software pensando em automatizar exatamente como eu fazia as coisas manualmente
 - Nao funciona com daytrade e aluguel de acoes/fii
 - Desconsidera custos e emolumentos para simplificação do calculo!


# To do list
    - Incluir desconto de taxas, emolumentos e dedo duro - http://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/renda-variavel/tarifas-de-acoes-e-fundos-de-investimento/a-vista/
    - Incluir opcao completa ou so ultimos x meses
   
# techstack
    - python
    - selenium
    - gitlab ci
    - beautifulsoap
    - pandas
    
# Exemplos de Ajustes manuais
Na maioria das vezes, nenhuma intervenção manual é necessária. 
Apenas algumas situaçoes (listadas abaixo) será preciso alterar alguma coisa no csv de dados de forma pontual.
Geralmente só acrescentando uma linha a mais com a compra/venda já resolve. 
- Subscricao de titulos (nao existe essa informacao no cei; é necessário acrescentar uma linha com dos dados da compra)
- Venda de direitos subscricao
- IPOs
- Mudança no ticker de negociacao
- Desdobramento do ticker 
- Na primeira execução, é intessante bater a custódia calculada com o que aparece na sua corretora
   
    
# tags
canal eletronico do investidor, CEI, selenium, bovespa, IRPF, IR, imposto de renda, finance, yahoo finance, acao, fii, 
etf, python, crawler, webscraping, calculadora ir


# (algumas) fontes para consulta utilizadas 
- https://br.advfn.com/investimentos/futuros/imposto-de-renda
- https://www.arenadopavini.com.br/acoes-na-arena/receita-permite-compensar-perdas-de-etf-com-ganhos-de-acoes

## debug tools
- csv to table: https://codesandbox.io/s/csv-import-example-hw3nex

## TODO LIST
`iniciando leitura de arquivo (tests/data/2020_12.pdf), pagina 6
Diferença no calculo das taxas
taxa proporcional somada: -1753.380000000000000000000000taxa via nota: -1753.380000000000000000000000
Diferença no calculo das taxas
taxa proporcional somada: -1580.920000000000000000000000taxa via nota: -1580.920000000000000000000000
Diferença no calculo das taxas
taxa proporcional somada: -1677.150000000000000000000000taxa via nota: -1677.150000000000000000000000
Diferença no calculo das taxas
taxa proporcional somada: 0.0taxa via nota: 0.0`

----------
import math
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.randn(8, 4),index=dates, columns=['A', 'B', 'C', 'D'])
df2 = pd.DataFrame(np.random.randn(8, 4),index=dates, columns=['E', 'F', 'G', 'H'])
df.combine(df2, lambda x,y: x if math.isnan(y.iloc[0]) else y)

>>> df.combine(df2, lambda x,y: x if math.isnan(y.iloc[0]) else y)
                   A         B         C         D         E         F         G         H
2000-01-01  0.572291 -0.376415  0.096499 -0.501556 -0.609520  1.366202 -1.097944 -0.069581
2000-01-02 -0.745446 -0.734310  0.026820  0.310755  0.370891 -0.324463 -1.495252 -0.488626
2000-01-03 -0.008442 -0.818752  0.775730  1.138191 -1.217939 -1.625876  0.304386 -1.467019
2000-01-04  0.646485  0.356571 -0.437486  0.446287 -0.240879  0.802476  0.207504  0.875761
2000-01-05 -0.038022 -0.549357  0.853325 -0.672601 -1.015454  0.072294 -0.128029 -1.013214
2000-01-06  0.523978  1.758997 -0.889266 -0.818600 -0.627424  2.013190 -0.209348  0.498383
2000-01-07 -0.717477  0.876361 -0.348383  0.471164  0.046945  1.532670  0.277389 -1.134186
2000-01-08  1.249751 -0.009308 -0.024992 -0.890212 -1.022445 -0.124705 -1.790870  0.081974