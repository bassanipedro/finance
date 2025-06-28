import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// URL base da nossa API. Altere se o seu backend estiver rodando em outra porta.
const API_URL = 'http://127.0.0.1:8000';

function App() {
  // Estados para armazenar dados
  const [wallets, setWallets] = useState([]);
  const [categories, setCategories] = useState([]); // Novo estado para categorias
  const [selectedWallet, setSelectedWallet] = useState(null);
  const [monthlyBills, setMonthlyBills] = useState([]);

  // Estados para os formulários
  const [newWalletName, setNewWalletName] = useState('');
  const [newWalletBalance, setNewWalletBalance] = useState('');
  const [newBillDescription, setNewBillDescription] = useState('');
  const [newBillValue, setNewBillValue] = useState('');
  
  // Lógica para obter o dia 10 do próximo mês
  const getNextMonthDay10 = () => {
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 10);
    return nextMonth.toISOString().split('T')[0]; // Formato YYYY-MM-DD
  };

  const [newBillDueDate, setNewBillDueDate] = useState(getNextMonthDay10());
  const [newBillCategoryId, setNewBillCategoryId] = useState(''); // Alterado de newBillCategory

  // Estados para o formulário de conta parcelada
  const [newRecurringBillDescription, setNewRecurringBillDescription] = useState('');
  const [newRecurringBillTotalValue, setNewRecurringBillTotalValue] = useState('');
  const [newRecurringBillInstallments, setNewRecurringBillInstallments] = useState('');
  const [newRecurringBillStartDate, setNewRecurringBillStartDate] = useState(getNextMonthDay10());
  const [newRecurringBillCategoryId, setNewRecurringBillCategoryId] = useState(''); // Alterado de newRecurringBillCategory

  const [activeForm, setActiveForm] = useState('single'); // 'single' ou 'recurring'

  // Efeito para buscar os dados iniciais quando o componente é montado
  useEffect(() => {
    fetchWallets();
    fetchMonthlyReminders();
    fetchCategories(); // Busca as categorias
  }, []);

  // --- Funções de API ---

  // Buscar todas as carteiras
  const fetchWallets = async () => {
    try {
      const response = await axios.get(`${API_URL}/wallets/`);
      setWallets(response.data);
    } catch (error) {
      console.error("Erro ao buscar carteiras:", error);
    }
  };

  // Buscar todas as categorias
  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/categories/`);
      setCategories(response.data);
    } catch (error) {
      console.error("Erro ao buscar categorias:", error);
    }
  };

  // Buscar detalhes de uma carteira específica
  const fetchWalletDetails = async (walletId) => {
    try {
      const response = await axios.get(`${API_URL}/wallets/${walletId}`);
      setSelectedWallet(response.data);
    } catch (error) {
      console.error("Erro ao buscar detalhes da carteira:", error);
    }
  };

  // Buscar lembretes de contas do mês
  const fetchMonthlyReminders = async () => {
    try {
      const response = await axios.get(`${API_URL}/reminders/monthly`);
      setMonthlyBills(response.data);
    } catch (error) {
      console.error("Erro ao buscar lembretes mensais:", error);
    }
  };

  // --- Funções de Manipulação de Formulários ---

  // Criar uma nova carteira
  const handleCreateWallet = async (e) => {
    e.preventDefault();
    if (!newWalletName) {
      alert("O nome da carteira é obrigatório.");
      return;
    }
    try {
      await axios.post(`${API_URL}/wallets/`, {
        name: newWalletName,
        initial_balance: parseFloat(newWalletBalance) || 0,
      });
      setNewWalletName('');
      setNewWalletBalance('');
      fetchWallets(); // Atualiza a lista de carteiras
    } catch (error) {
      console.error("Erro ao criar carteira:", error);
    }
  };

  // Criar uma nova conta
  const handleCreateBill = async (e) => {
    e.preventDefault();
    if (!selectedWallet || !newBillDescription || !newBillValue || !newBillDueDate || !newBillCategoryId) {
      alert("Todos os campos da conta são obrigatórios.");
      return;
    }
    try {
      await axios.post(`${API_URL}/bills/`, {
        description: newBillDescription,
        value: parseFloat(newBillValue),
        due_date: newBillDueDate,
        wallet_id: selectedWallet.id,
        category_id: parseInt(newBillCategoryId),
      });
      setNewBillDescription('');
      setNewBillValue('');
      setNewBillDueDate('');
      setNewBillCategoryId('');
      fetchWalletDetails(selectedWallet.id); // Atualiza os detalhes da carteira selecionada
      fetchMonthlyReminders(); // Atualiza os lembretes
    } catch (error) {
      console.error("Erro ao criar conta:", error);
    }
  };

  // Criar uma nova conta parcelada
  const handleCreateRecurringBill = async (e) => {
    e.preventDefault();
    if (!selectedWallet || !newRecurringBillDescription || !newRecurringBillTotalValue || !newRecurringBillInstallments || !newRecurringBillStartDate || !newRecurringBillCategoryId) {
      alert("Todos os campos da conta parcelada são obrigatórios.");
      return;
    }
    try {
      await axios.post(`${API_URL}/bills/recurring/`, {
        description: newRecurringBillDescription,
        total_value: parseFloat(newRecurringBillTotalValue),
        installments: parseInt(newRecurringBillInstallments),
        start_date: newRecurringBillStartDate,
        wallet_id: selectedWallet.id,
        category_id: parseInt(newRecurringBillCategoryId),
      });
      // Limpa o formulário
      setNewRecurringBillDescription('');
      setNewRecurringBillTotalValue('');
      setNewRecurringBillInstallments('');
      setNewRecurringBillStartDate('');
      setNewRecurringBillCategoryId('');
      // Atualiza os dados
      fetchWalletDetails(selectedWallet.id);
      fetchMonthlyReminders();
    } catch (error)
    {
      console.error("Erro ao criar conta parcelada:", error);
      alert(`Erro ao criar conta: ${error.response?.data?.detail || 'Verifique os dados e tente novamente.'}`);
    }
  };

  // --- Renderização ---

  return (
    <div className="container">
      <header>
        <h1>Sistema de Finanças Pessoais</h1>
      </header>

      <main>
        <div className="column">
          {/* Seção para criar e listar carteiras */}
          <section>
            <h2>Minhas Carteiras</h2>
            <form onSubmit={handleCreateWallet} className="form-group">
              <input
                type="text"
                value={newWalletName}
                onChange={(e) => setNewWalletName(e.target.value)}
                placeholder="Nome da nova carteira"
              />
              <input
                type="number"
                value={newWalletBalance}
                onChange={(e) => setNewWalletBalance(e.target.value)}
                placeholder="Saldo inicial (opcional)"
              />
              <button type="submit">Criar Carteira</button>
            </form>
            <ul className="item-list">
              {wallets.map((wallet) => (
                <li 
                  key={wallet.id} 
                  onClick={() => fetchWalletDetails(wallet.id)} 
                  className={`wallet-item ${selectedWallet?.id === wallet.id ? 'selected' : ''}`}
                >
                  <span>{wallet.name}</span>
                  <span className="wallet-balance">R$ {wallet.initial_balance.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Seção para lembretes mensais */}
          <section>
            <h2 className="reminder">Lembretes do Mês</h2>
            {monthlyBills.length > 0 ? (
              <ul className="item-list">
                {monthlyBills.map((bill) => (
                  <li key={bill.id} className="bill-item">
                    <span>
                      {bill.description}
                      {bill.category && <span className="bill-category">{bill.category.name}</span>}
                    </span>
                    <span>{bill.value.toFixed(2)}</span>
                    <span>{new Date(bill.due_date + 'T00:00:00').toLocaleDateString('pt-BR')}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <p>Nenhuma conta para pagar este mês.</p>
              </div>
            )}
          </section>
        </div>

        <div className="column">
          {/* Seção para detalhes da carteira e adição de contas */}
          {selectedWallet ? (
            <section>
              <h2>Detalhes de: {selectedWallet.name}</h2>
              <h3>Adicionar Nova Conta</h3>
              <div className="form-tabs">
                <button type="button" className={activeForm === 'single' ? 'active' : ''} onClick={() => setActiveForm('single')}>
                  Conta Única
                </button>
                <button type="button" className={activeForm === 'recurring' ? 'active' : ''} onClick={() => setActiveForm('recurring')}>
                  Conta Parcelada
                </button>
              </div>

              {activeForm === 'single' ? (
                <form onSubmit={handleCreateBill} className="form-group">
                  <input
                    type="text"
                    value={newBillDescription}
                    onChange={(e) => setNewBillDescription(e.target.value)}
                    placeholder="Descrição da conta"
                  />
                  <input
                    type="number"
                    value={newBillValue}
                    onChange={(e) => setNewBillValue(e.target.value)}
                    placeholder="Valor"
                    step="0.01"
                  />
                  <input
                    type="date"
                    value={newBillDueDate}
                    onChange={(e) => setNewBillDueDate(e.target.value)}
                  />
                  <select
                    value={newBillCategoryId}
                    onChange={(e) => setNewBillCategoryId(e.target.value)}
                    required
                  >
                    <option value="" disabled>Selecione a Categoria</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  <button type="submit">Adicionar Conta</button>
                </form>
              ) : (
                <form onSubmit={handleCreateRecurringBill} className="form-group">
                  <input
                    type="text"
                    value={newRecurringBillDescription}
                    onChange={(e) => setNewRecurringBillDescription(e.target.value)}
                    placeholder="Descrição da compra"
                  />
                  <input
                    type="number"
                    value={newRecurringBillTotalValue}
                    onChange={(e) => setNewRecurringBillTotalValue(e.target.value)}
                    placeholder="Valor Total"
                    step="0.01"
                  />
                  <input
                    type="number"
                    value={newRecurringBillInstallments}
                    onChange={(e) => setNewRecurringBillInstallments(e.target.value)}
                    placeholder="Nº de Parcelas"
                    step="1"
                  />
                  <input
                    type="date"
                    value={newRecurringBillStartDate}
                    onChange={(e) => setNewRecurringBillStartDate(e.target.value)}
                    placeholder="Data da 1ª Parcela"
                  />
                  <select
                    value={newRecurringBillCategoryId}
                    onChange={(e) => setNewRecurringBillCategoryId(e.target.value)}
                    required
                  >
                    <option value="" disabled>Selecione a Categoria</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  <button type="submit">Adicionar Compra Parcelada</button>
                </form>
              )}

              <h3>Contas Pendentes</h3>
              {selectedWallet.bills.length > 0 ? (
                <ul className="item-list">
                  {selectedWallet.bills.map((bill) => (
                    <li key={bill.id} className="bill-item">
                      <span>
                        {bill.description}
                        {bill.category && <span className="bill-category">{bill.category.name}</span>}
                      </span>
                      <span>{bill.value.toFixed(2)}</span>
                      <span>{new Date(bill.due_date + 'T00:00:00').toLocaleDateString('pt-BR')}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="empty-state">
                  <p>Nenhuma conta cadastrada nesta carteira.</p>
                </div>
              )}
            </section>
          ) : (
            <section>
              <h2>Selecione uma carteira</h2>
              <div className="empty-state">
                <p>Clique em uma carteira à esquerda para ver os detalhes e adicionar contas.</p>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
