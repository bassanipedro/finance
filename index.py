import yfinance as yf
import sys

def get_stock_info(ticker_symbol):
    """
    Busca informações de uma ação usando o yfinance e exibe os dados principais.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Verifica se o ticker é válido (se 'longName' não existir, provavelmente o ticker é inválido)
        if not info.get('longName'):
            print(f"Erro: Não foi possível encontrar informações para o ticker '{ticker_symbol}'. Verifique o código e tente novamente.")
            return

        print("\n--- Informações da Ação ---")
        print(f"Empresa: {info.get('longName', 'N/A')} ({info.get('symbol', 'N/A')})")
        print(f"Setor: {info.get('sector', 'N/A')}")
        print(f"País: {info.get('country', 'N/A')}")
        
        print("\n--- Dados de Mercado ---")
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        print(f"Preço Atual: {info.get('currency', '')} {current_price:.2f}")
        print(f"Fechamento Anterior: {info.get('previousClose', 0):.2f}")
        print(f"Variação do Dia: {info.get('dayLow', 0):.2f} - {info.get('dayHigh', 0):.2f}")
        print(f"Variação 52 Semanas: {info.get('fiftyTwoWeekLow', 0):.2f} - {info.get('fiftyTwoWeekHigh', 0):.2f}")
        print(f"Volume: {info.get('volume', 0):,}")
        print(f"Capitalização de Mercado: {info.get('marketCap', 0):,}")

        print("\n--- Indicadores Fundamentais ---")
        print(f"P/L (Preço/Lucro): {info.get('trailingPE', 'N/A')}")
        print(f"P/VP (Preço/Valor Patrimonial): {info.get('priceToBook', 'N/A')}")
        print(f"Dividend Yield: {info.get('dividendYield', 0) * 100:.2f}%")
        
        print("\n--- Resumo do Negócio ---")
        print(info.get('longBusinessSummary', 'Nenhum resumo disponível.'))
        print("-" * 27 + "\n")

    except Exception as e:
        print(f"Ocorreu um erro ao buscar as informações: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("--- Bot de Análise de Ações ---")
    
    while True:
        ticker_input = input("Digite o código da ação (ex: PETR4.SA, AAPL) ou 'sair' para fechar: ").strip().upper()
        
        if ticker_input == 'SAIR':
            break
        
        if not ticker_input:
            print("Por favor, digite um código de ação.")
            continue
            
        get_stock_info(ticker_input)
