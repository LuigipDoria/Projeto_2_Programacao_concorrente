from random import randint
import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER


class TransactionGenerator(Thread):
    """
    Uma classe para gerar e simular clientes de um banco por meio da geracão de transações bancárias.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do gerador de transações.
    bank: Bank
        Banco sob o qual o gerador de transações operará.

    Métodos
    -------
    run():
        ....
    popula_banco() -> None:
        Cria as 101 contas no banco, para ser possivel fazer as transações
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank
        self.popula_banco()
        

        
    def run(self):
        """
        Esse método deverá gerar transacões aleatórias enquanto o banco (self._bank_id)
        estiver em operação.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Inicializado TransactionGenerator para o Banco Nacional {self.bank._id}!")

        i = 0
        while banks[self.bank._id].operating: # Verifica se o banco já foi fechado
            origin = (self.bank._id, self._id)
            destination_bank = randint(0, 5)
            destination = (destination_bank, randint(0, 100))
            amount = randint(100, 1000000)
            new_transaction = Transaction(i, origin, destination, amount, currency=Currency(destination_bank+1))
            with self.bank.lock_condition:
                banks[self.bank._id].transaction_queue.append(new_transaction)
                self.bank.condition.notify() # Permite que uma transação seja feita
                i+=1
            time.sleep(0.2 * time_unit)
        
        with self.bank.lock_condition:
            self.bank.condition.notify_all() # Notifica todo mundo para caso alguma thread tenha ficado presa no wait, ela consiga ser finalizada
        
        LOGGER.info(f"O TransactionGenerator {self._id} do banco {self.bank._id} foi finalizado.")

    def popula_banco(self):
        for _ in range(101):
            self.bank.new_account(balance=randint(100_000_000, 10_000_000_000), overdraft_limit=randint(10_000_000, 100_000_000))