from typing import Tuple

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER
from threading import Lock, Condition

class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.

    # Parte não original

    taxas : int
        Quantidade recebida pelas as taxas de cheque especial e transação internacional
    num_transaçoes
        Numero de transações realizadas pelo banco
    saldo_total
        Quantidad total de dinheiro guardado no banco pelos seus clientes
    lock_taxa : Lock
        Mutex para fazer o controle do somatario das taxas que o banco ganhou
    lock_num_transaçao : Lock
        Mutex para fazer a contagem de quantas transações foram realizadas
    lock_condition : Lock
        Mutex para a condition
    condition : Condition
        Condição para ver se existe um transação a ser feita, evitando espera ocupada
        
    # Parte não originalself.lock

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.

    # Parte não original

    taxa(quantia, tipo) -> None:
        Incrementa a quantia ganha pelo banco quando é usado o cheque especial ou é feita uma trasanção internacional
        
    # Parte não original

    
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves(_id)
        self.operating          = False
        self.accounts           = []
        self.transaction_queue  = []
        self.taxas              = int()
        self.num_trasançoes     = int()
        self.lock_taxa= Lock()
        self.lock_num_transaçao = Lock()
        self.lock_condition = Lock()
        self.condition = Condition(lock=self.lock_condition)

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)


    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco -> Feito
        2. Número de transferências nacionais e internacionais realizadas -> Feito
        3. Número de contas bancárias registradas no banco -> Testar
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco -> Feito
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados -> Feito
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!
        # Parte não original
        saldo_total = 0 # Indica o somatorio do saldo das contas do banco
        for acc in self.accounts: # Percorre as contas dos bancos
            saldo_total += acc.balance # Faz a soma dos saldos
        LOGGER.info(f"==========================================")
        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")  
        LOGGER.info(f"Reserva de USD: {self.reserves.USD.balance}")
        LOGGER.info(f"Reserva de EUR: {self.reserves.EUR.balance}")
        LOGGER.info(f"Reserva de GBP: {self.reserves.GBP.balance}")
        LOGGER.info(f"Reserva de JPY: {self.reserves.JPY.balance}")
        LOGGER.info(f"Reserva de CHF: {self.reserves.CHF.balance}")
        LOGGER.info(f"Reserva de BRL: {self.reserves.BRL.balance}")
        LOGGER.info(f"Numero de transações realizadas: {self.num_trasançoes}")
        LOGGER.info(f"Numero de contas registradas no banco: {len(self.accounts)}")
        LOGGER.info(f"Saldo total do banco: {saldo_total} {str(self.currency)[-3:]}")
        LOGGER.info(f"Lucro do Banco: {self.taxas} {str(self.currency)[-3:]}")
        LOGGER.info(f"FIM DAS INFORMAÇÕES DO BANCO {self._id}")
        LOGGER.info(f"==========================================")
        # Fim parte não original

    def taxa(self, quantia: int, tipo: int) -> None:
        self.lock_taxa.acquire()
        if tipo == 0:
            self.taxas += quantia*0.05
        else:
            self.taxas += quantia*0.01
        self.lock_taxa.release()