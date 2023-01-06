from dataclasses import dataclass

from utils.currency import Currency
from utils.logger import LOGGER

from threading import Lock

@dataclass
class Account:
    """
    Uma classe para representar uma conta bancária.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id: int
        Identificador da conta bancária.
    _bank_id: int
        Identificador do banco no qual a conta bancária foi criada.
    currency : Currency
        Moeda corrente da conta bancária.
    balance : int
        Saldo da conta bancária.
    overdraft_limit : int
        Limite de cheque especial da conta bancária.

    # Parte não original 
        
    lock : Lock
        Mutex para fazer o controle de entrada de dinheiro na conta

    overdraft_balance : int
        Quantia disponivel no cheque especial

    resto: int
        Valor que indica a quantia que sobrou do pagamento do cheque especial
        ou
        Valor utilizado do cheque especial para fazer a trasação

    # Fim parte não original 

    Métodos
    -------
    info() -> None:
        Printa informações sobre a conta bancária.
    deposit(amount: int) -> None:
        Adiciona o valor `amount` ao saldo da conta bancária.
    
    # Parte não original
    
    withdraw(amount: int) -> bool, int:
        Remove o valor `amount` do saldo da conta bancária.
        bool indica se foi possivel retirar o dinheiro
        int indica quanto foi usado do cheque especial

    __init__(self, _id, _bank_id, currency, balance, overdraft_limit) -> None:
        Inicializa a conta

    # Fim parte não original 

    """

    # Parte não original 
        
    def __init__(self, _id, _bank_id, currency, balance = 0, overdraft_limit = 0) -> None:
        self._id = _id
        self._bank_id = _bank_id
        self.currency = currency
        self.balance = balance
        self.overdraft_limit = overdraft_limit
        self.overdraft_balace = overdraft_limit
        self.lock = Lock()

    # Fim parte não original 

    """
    _id: int
    _bank_id: int
    currency: Currency
    balance: int = 0
    overdraft_limit: int = 0
    """

    def info(self) -> None:
        """
        Esse método printa informações gerais sobre a conta bancária.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        pretty_balance = f"{format(round(self.balance/100), ',d')}.{self.balance%100:02d} {self.currency.name}"
        pretty_overdraft_limit = f"{format(round(self.overdraft_limit/100), ',d')}.{self.overdraft_limit%100:02d} {self.currency.name}"
        LOGGER.info(f"Account::{{ _id={self._id}, _bank_id={self._bank_id}, balance={pretty_balance}, overdraft_limit={pretty_overdraft_limit} }}")


    def deposit(self, amount: int) -> bool:
        """
        Esse método deverá adicionar o valor `amount` passado como argumento ao saldo da conta bancária 
        (`balance`). Lembre-se que esse método pode ser chamado concorrentemente por múltiplos 
        PaymentProcessors, então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !
        
        # Parte não original 

        resto = 0 # Indica quanto do deposito sobrou após pagar os gastos do cheque especial

        self.lock.acquire() # Trava o mutex para ser lido e alterado os valores da conta 
 
        if self.overdraft_balace < self.overdraft_limit: # Verifica se tem algo para ser pago do cheque especial
            self.overdraft_balace += amount # Adicona o dinheiro do deposito na quantia do cheque especial
            resto = self.overdraft_limit - self.overdraft_balace # Indica a quantidade de dinheiro que passou do limite do cheque especial
            if resto > 0: # Caso a quantia seja maior que zero
                self.overdraft_balace -= resto # É retirada essa quantia do cheque especial
                self.balance += resto # E é adicionada no saldo da conta
        else: # Caso o saldo do cheque especial esteja igual ao seu limite
            self.balance += amount # O dinheiro é adicionado no saldo da conta

        self.lock.release() # Destrava o mutex após ser lido e alterado os valores da conta
   
        # Fim parte não original 

        LOGGER.info(f"deposit({amount}) successful!")
        return True


    def withdraw(self, amount: int) -> bool:
        """
        Esse método deverá retirar o valor `amount` especificado do saldo da conta bancária (`balance`).
        Deverá ser retornado um valor bool indicando se foi possível ou não realizar a retirada.
        Lembre-se que esse método pode ser chamado concorrentemente por múltiplos PaymentProcessors, 
        então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        # Parte não original 

        self.lock.acquire() # Trava o mutex para ser lido e alterado os valores da conta 
   

        if self.balance >= amount: # Caso tenha saldo para fazer a retirada da quantia
            self.balance -= amount # A quantia é retirada da coanta


            self.lock.release() # Destrava o mutex após ser lido e alterado os valores da conta
   

            LOGGER.info(f"withdraw({amount}) successful!") # Indica que a transação foi bem realizada com sucesso
            return True, 0 
                # Retorna Verdadeiro indicando que a transaçã foi realizada com sucesso
                # E '0' informando que não foi usado o cheque especial
        else:
            amount += amount *0.05 # Aumenta na quantia a ser paga o valor da taxa de uso do cheque especials
            overdrafted_amount = abs(self.balance - amount) # Indica quanto sera usado do cheque especial
            if self.overdraft_balace >= overdrafted_amount: # Caso essa quantia não passe do limite do cheque especial
                self.balance = 0 # É zerado o saldo da conta
                self.overdraft_balace -= overdrafted_amount # E é diminuido a quantia do saldo do cheque especial

                self.lock.release() # Destrava o mutex após ser lido e alterado os valores da conta

                LOGGER.info(f"withdraw({amount}) successful with overdraft!") # Indica que a transação foi bem realizada com sucesso, utilizando o cheque especial
                return True, overdrafted_amount
                # Retorna Verdadeiro indicando que a transaçã foi realizada com sucesso 
                # E a quantia usada do cheque especial

            else: # Caso não tenha saldo suficenete no cheque especial

                self.lock.release() # Destrava o mutex após ser lido e alterado os valores da conta
   
                # Fim parte não original 

                LOGGER.warning(f"withdraw({amount}) failed, no balance!") # Indica que a transação não foi bem realizada com sucesso
                return False, 0 
                # Retorna Falso indicando que a transaçã não foi realizada com sucesso
                # E '0' informando que não foi usado o cheque especial


@dataclass
class CurrencyReserves:
    """
    Uma classe de dados para armazenar as reservas do banco, que serão usadas
    para câmbio e transferências internacionais.
    OBS: NÃO É PERMITIDO ALTERAR ESSA CLASSE!
    """

    USD: Account
    EUR: Account
    GBP: Account
    JPY: Account
    CHF: Account
    BRL: Account

    def __init__(self, bank_id):
        self.USD = Account(_id=1, _bank_id=bank_id, currency=Currency.USD)
        self.EUR = Account(_id=2, _bank_id=bank_id, currency=Currency.EUR)
        self.GBP = Account(_id=3, _bank_id=bank_id, currency=Currency.GBP)
        self.JPY = Account(_id=4, _bank_id=bank_id, currency=Currency.JPY)
        self.CHF = Account(_id=5, _bank_id=bank_id, currency=Currency.CHF)
        self.BRL = Account(_id=6, _bank_id=bank_id, currency=Currency.BRL)