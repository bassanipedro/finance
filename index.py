import yfinance as yf
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

def load_config():
    """Carrega o token do bot do Telegram do arquivo config.txt."""
    config = {}
    config_file = 'config.txt'
    if not os.path.exists(config_file):
        print(f"Erro: Arquivo '{config_file}' não encontrado.", file=sys.stderr)
        return None
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    token = config.get('TELEGRAM_TOKEN')

    if not token or 'SEU_TOKEN_AQUI' in token:
        print(f"Erro: 'TELEGRAM_TOKEN' não encontrado ou não configurado em '{config_file}'.", file=sys.stderr)
        return None
        
    return token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    await update.message.reply_text(
        "Olá! Sou seu bot de análise de ações.\n"
        "Envie o código de uma ação (ex: PETR4.SA) ou use o comando /stock <TICKER>."
    )

async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca informações da ação enviada com o comando /stock."""
    if not context.args:
        await update.message.reply_text("Por favor, envie o código da ação junto com o comando. Ex: /stock PETR4.SA")
        return
    
    ticker_symbol = context.args[0].upper()
    info_message = get_stock_info(ticker_symbol)
    await update.message.reply_text(info_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca informações da ação enviada como texto."""
    ticker_symbol = update.message.text.strip().upper()
    info_message = get_stock_info(ticker_symbol)
    await update.message.reply_text(info_message)


def get_stock_info(ticker_symbol):
    """
    Busca informações de uma ação usando o yfinance e retorna os dados como uma string formatada.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Verifica se o ticker é válido (se 'longName' não existir, provavelmente o ticker é inválido)
        if not info.get('longName'):
            return f"Erro: Não foi possível encontrar informações para o ticker '{ticker_symbol}'. Verifique o código e tente novamente."

        message = f"\n--- Informações da Ação ---\n"
        message += f"Empresa: {info.get('longName', 'N/A')} ({info.get('symbol', 'N/A')})\n"
        message += f"Setor: {info.get('sector', 'N/A')}\n"
        message += f"País: {info.get('country', 'N/A')}\n"
        
        message += f"\n--- Dados de Mercado ---\n"
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        message += f"Preço Atual: {info.get('currency', '')} {current_price:.2f}\n"
        message += f"Fechamento Anterior: {info.get('previousClose', 0):.2f}\n"
        message += f"Variação do Dia: {info.get('dayLow', 0):.2f} - {info.get('dayHigh', 0):.2f}\n"
        message += f"Variação 52 Semanas: {info.get('fiftyTwoWeekLow', 0):.2f} - {info.get('fiftyTwoWeekHigh', 0):.2f}\n"
        message += f"Volume: {info.get('volume', 0):,}\n"
        message += f"Capitalização de Mercado: {info.get('marketCap', 0):,}\n"

        message += f"\n--- Indicadores Fundamentais ---\n"
        message += f"P/L (Preço/Lucro): {info.get('trailingPE', 'N/A')}\n"
        message += f"P/VP (Preço/Valor Patrimonial): {info.get('priceToBook', 'N/A')}\n"
        message += f"Dividend Yield: {info.get('dividendYield', 0) * 100:.2f}%\n"
        
        message += f"\n--- Resumo do Negócio ---\n"
        message += f"{info.get('longBusinessSummary', 'Nenhum resumo disponível.')}\n"
        message += "-" * 27 + "\n"
        
        return message

    except Exception as e:
        return f"Ocorreu um erro ao buscar as informações: {e}"

def main():
    """Inicia o bot do Telegram."""
    token = load_config()
    if not token:
        print("Encerrando o bot por falta de token.")
        sys.exit(1)

    application = Application.builder().token(token).build()

    # Handlers de Comando
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stock", stock_command))

    # Handler de Mensagem de Texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot iniciado. Pressione Ctrl+C para parar.")
    
    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()
