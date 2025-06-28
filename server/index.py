# Importações necessárias
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List
from dateutil.relativedelta import relativedelta

# --- Configuração do Banco de Dados ---
# Usando SQLite para simplicidade
SQLALCHEMY_DATABASE_URL = "sqlite:///./finance.db"

# Engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessão para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos ORM
Base = declarative_base()

# --- Modelos ORM (SQLAlchemy) ---

# Modelo para Categoria
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    bills = relationship("Bill", back_populates="category")

# Modelo para Carteira
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    initial_balance = Column(Float, default=0.0)

    # Relacionamento com as contas
    bills = relationship("Bill", back_populates="wallet")

# Modelo para Conta a Pagar
class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    value = Column(Float)
    due_date = Column(Date)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Relacionamento com a carteira
    wallet = relationship("Wallet", back_populates="bills")
    # Relacionamento com a categoria
    category = relationship("Category", back_populates="bills")

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# --- Schemas (Pydantic) ---
# Usados para validação de dados da API e serialização

# Schema base para Categoria
class CategoryBase(BaseModel):
    name: str

# Schema para criação de Categoria
class CategoryCreate(CategoryBase):
    pass

# Schema para leitura de Categoria
class CategorySchema(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Schema base para Conta
class BillBase(BaseModel):
    description: str
    value: float
    due_date: date
    category_id: int

# Schema para criação de Conta
class BillCreate(BillBase):
    wallet_id: int

# Schema para leitura de Conta (inclui o ID)
class BillSchema(BillBase):
    id: int
    wallet_id: int
    category: CategorySchema

    class Config:
        from_attributes = True

# Schema base para Carteira
class WalletBase(BaseModel):
    name: str
    initial_balance: float = 0.0

# Schema para criação de Carteira
class WalletCreate(WalletBase):
    pass

# Schema para leitura de Carteira (inclui ID e lista de contas)
class WalletSchema(WalletBase):
    id: int
    bills: List[BillSchema] = []

    class Config:
        from_attributes = True

# Schema para Conta Parcelada
class RecurringBillCreate(BaseModel):
    description: str
    total_value: float
    installments: int
    start_date: date
    wallet_id: int
    category_id: int

# --- Dependência do Banco de Dados ---
# Função para obter uma sessão do banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Inicialização do FastAPI ---
app = FastAPI(
    title="Sistema de Controle de Finanças Pessoais",
    description="API para gerenciar carteiras e contas a pagar.",
    version="1.0.0"
)

# --- Configuração do CORS ---
# Permite que o frontend (rodando em outra porta/domínio) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # A origem padrão do frontend Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints da API ---

# === Endpoints para Categorias (Categories) ===

@app.post("/categories/", response_model=CategorySchema, summary="Criar uma nova categoria")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova categoria para as contas.
    - **name**: Nome da categoria (deve ser único).
    """
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Categoria já existe")
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategorySchema], summary="Listar todas as categorias")
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as categorias cadastradas.
    """
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

# === Endpoints para Carteiras (Wallets) ===

@app.post("/wallets/", response_model=WalletSchema, summary="Criar uma nova carteira")
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova carteira financeira.
    - **name**: Nome da carteira.
    - **initial_balance**: Saldo inicial da carteira.
    """
    db_wallet = Wallet(name=wallet.name, initial_balance=wallet.initial_balance)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

@app.get("/wallets/", response_model=List[WalletSchema], summary="Listar todas as carteiras")
def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as carteiras cadastradas.
    """
    wallets = db.query(Wallet).offset(skip).limit(limit).all()
    return wallets

@app.get("/wallets/{wallet_id}", response_model=WalletSchema, summary="Obter detalhes de uma carteira")
def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de uma carteira específica, incluindo suas contas.
    """
    db_wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    return db_wallet

# === Endpoints para Contas (Bills) ===

@app.post("/bills/recurring/", response_model=List[BillSchema], summary="Adicionar uma conta parcelada")
def create_recurring_bill(bill_data: RecurringBillCreate, db: Session = Depends(get_db)):
    """
    Cria uma conta parcelada, gerando uma fatura para cada mês.
    - **description**: Descrição base da compra.
    - **total_value**: Valor total da compra.
    - **installments**: Número de parcelas.
    - **start_date**: Data de vencimento da primeira parcela.
    - **wallet_id**: ID da carteira.
    - **category_id**: ID da categoria da conta.
    """
    db_wallet = db.query(Wallet).filter(Wallet.id == bill_data.wallet_id).first()
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")

    db_category = db.query(Category).filter(Category.id == bill_data.category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if bill_data.installments <= 0:
        raise HTTPException(status_code=400, detail="O número de parcelas deve ser positivo.")

    installment_value = round(bill_data.total_value / bill_data.installments, 2)
    created_bills = []

    for i in range(bill_data.installments):
        due_date = bill_data.start_date + relativedelta(months=i)
        description = f"{bill_data.description} ({i + 1}/{bill_data.installments})"
        
        db_bill = Bill(
            description=description,
            value=installment_value,
            due_date=due_date,
            wallet_id=bill_data.wallet_id,
            category_id=bill_data.category_id
        )
        db.add(db_bill)
        created_bills.append(db_bill)
    
    db.commit()
    for bill in created_bills:
        db.refresh(bill)
        
    return created_bills

@app.post("/bills/", response_model=BillSchema, summary="Adicionar uma nova conta a pagar")
def create_bill_for_wallet(bill: BillCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova conta a pagar e a vincula a uma carteira existente.
    - **description**: Descrição da conta.
    - **value**: Valor da conta.
    - **due_date**: Data de vencimento (formato: YYYY-MM-DD).
    - **wallet_id**: ID da carteira à qual a conta pertence.
    - **category_id**: ID da categoria da conta.
    """
    # Verifica se a carteira e a categoria existem
    db_wallet = db.query(Wallet).filter(Wallet.id == bill.wallet_id).first()
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    db_category = db.query(Category).filter(Category.id == bill.category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    db_bill = Bill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@app.get("/bills/", response_model=List[BillSchema], summary="Listar todas as contas")
def read_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as contas a pagar cadastradas.
    """
    bills = db.query(Bill).offset(skip).limit(limit).all()
    return bills

# === Endpoint para Lembretes ===

@app.get("/reminders/monthly", response_model=List[BillSchema], summary="Obter contas do mês atual")
def get_monthly_reminders(db: Session = Depends(get_db)):
    """
    Simula o envio de lembretes listando todas as contas
    que vencem no mês e ano atuais.
    """
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Calcula o primeiro dia do próximo mês para definir o fim do mês atual
    if start_of_month.month == 12:
        next_month_start = start_of_month.replace(year=start_of_month.year + 1, month=1)
    else:
        next_month_start = start_of_month.replace(month=start_of_month.month + 1)

    monthly_bills = db.query(Bill).filter(
        Bill.due_date >= start_of_month,
        Bill.due_date < next_month_start
    ).all()
    
    # Em um cenário real, aqui você poderia enviar um e-mail, notificação, etc.
    # Por enquanto, apenas retornamos a lista de contas e imprimimos no console.
    print(f"Lembrete: {len(monthly_bills)} contas vencem este mês.")
    
    return monthly_bills

# --- Seed de Categorias Iniciais ---
def seed_initial_categories(db: Session):
    initial_categories = ["Moradia", "Transporte", "Alimentação", "Saúde", "Educação", "Lazer", "Outros"]
    for category_name in initial_categories:
        db_category = db.query(Category).filter(Category.name == category_name).first()
        if not db_category:
            db.add(Category(name=category_name))
    db.commit()

# Evento de inicialização do FastAPI para popular as categorias
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_initial_categories(db)
    finally:
        db.close()


# Para executar o servidor, instale as dependências:
# pip install fastapi uvicorn sqlalchemy python-multipart
# E rode o comando no terminal, na pasta 'server':
# uvicorn index:app --reload
# uvicorn index:app --reload
