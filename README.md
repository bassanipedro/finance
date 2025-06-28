# Sistema de Controle de Finanças Pessoais

Este é um projeto full-stack simples para gerenciamento de finanças pessoais, construído com FastAPI no backend e React (Vite) no frontend.

## 📜 Sobre o Projeto

A aplicação permite que os usuários criem "carteiras" (representando contas bancárias, cartões de crédito, etc.) e adicionem contas a pagar a elas. O objetivo é fornecer uma visão clara das despesas futuras e ajudar no planejamento financeiro.

### Funcionalidades Principais

- **Gerenciamento de Carteiras**: Crie múltiplas carteiras com um saldo inicial.
- **Contas Únicas**: Adicione contas avulsas com descrição, valor, data de vencimento e categoria.
- **Contas Parceladas**: Registre compras parceladas, e o sistema criará automaticamente uma fatura para cada mês.
- **Lembretes Mensais**: Visualize rapidamente todas as contas que vencem no mês atual.
- **Interface Reativa**: A interface é atualizada em tempo real conforme os dados são alterados.

## 🛠️ Tecnologias Utilizadas

- **Backend (Pasta `server/`)**
  - **Python 3**
  - **FastAPI**: Framework web para a construção da API.
  - **SQLAlchemy**: ORM para interação com o banco de dados.
  - **SQLite**: Banco de dados relacional leve, usado para simplicidade.
  - **Uvicorn**: Servidor ASGI para rodar a aplicação FastAPI.

- **Frontend (Pasta `client/`)**
  - **React**: Biblioteca para construção da interface de usuário.
  - **Vite**: Ferramenta de build para um desenvolvimento frontend rápido.
  - **JavaScript**
  - **Axios**: Cliente HTTP para realizar requisições à API.
  - **CSS Moderno**: Estilização com variáveis, flexbox e grid para um layout responsivo.

## 🚀 Como Executar o Projeto

Para rodar o projeto, você precisará ter o **Python 3.8+** e o **Node.js** (que inclui o npm) instalados em sua máquina.

### 1. Backend (Servidor FastAPI)

Primeiro, vamos configurar e iniciar o servidor.

```bash
# 1. Navegue até a pasta do servidor
cd server

# 2. (Opcional, mas recomendado) Crie e ative um ambiente virtual
# Em Windows:
python -m venv venv
.\venv\Scripts\activate
# Em macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# 3. Instale as dependências do Python
pip install -r requirements.txt

# 4. Inicie o servidor
# O --reload faz com que o servidor reinicie automaticamente após alterações no código.
py -m uvicorn index:app --reload
```

O backend estará rodando em `http://127.0.0.1:8000`. Você pode acessar a documentação interativa da API em `http://127.0.0.1:8000/docs`.

### 2. Frontend (Cliente React)

Com o backend rodando, abra um **novo terminal** para configurar e iniciar a interface do usuário.

```bash
# 1. Navegue até a pasta do cliente
cd client

# 2. Instale as dependências do Node.js
npm install

# 3. Inicie o servidor de desenvolvimento
npm run dev
```

A aplicação frontend estará acessível em `http://localhost:5173` (ou outra porta, se a 5173 estiver em uso). Abra este endereço no seu navegador para usar o sistema.
