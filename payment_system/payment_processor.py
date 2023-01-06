import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.logger import LOGGER
from utils.currency import get_exchange_rate

class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank

    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las 
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!")
        queue = self.bank.transaction_queue
        while self.bank.operating: # Antes: while True -> Foi trocado o True pela variavel da classe banco que indica o estado do banco
            with self.bank.lock_condition:
                self.bank.condition.wait()
                if self.bank.operating == False: # Caso o banco feche encerra a thread
                    break
                try:
                    transaction = queue.pop(0) # Foi passado o 0 como argumento da função pop para a queue se torne uma FIFO
                    LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {queue}")
                except Exception as err:
                    LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
                else:
                    self.process_transaction(transaction) # Chama a funcção process_transaction para realizar a trasação
            time.sleep(3 * time_unit)  # Remova esse sleep após implementar sua solução!

        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")


    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a 
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!")
        
        # Parte não original
    
        if transaction.origin[0] == transaction.destination[0]: # Retorna True caso a transação seja entre o mesmo banco

            contas = self.bank.accounts # Lista das contas do banco
            quantia = transaction.amount # quantia a ser transferida

            index_origem = transaction.origin[1] # Indiaca a possição da conta na lista de contas do banco
            index_destino = transaction.destination[1] # Indiaca a possição da conta na lista de contas do banco
            
            sucesso, quantia_cheque_especial = contas[index_origem].withdraw(quantia) # Faz a retirada do dinheiro da conta de origem 
            # sucesso indica se a retirada do dinheriro foi feita com sucesso 
            # quantia_cheque_especial é a quantia que foi usada do cheque especial da conta, gerando uma taxa para o banco

            if sucesso:
                self.bank.taxa(quantia_cheque_especial, 0)
                contas[index_destino].deposit(quantia) # Faz o deposito do dinheiro na conta de destino
                
            else: # Caso a transação não seja realizada com sucesso
                transaction.set_status(TransactionStatus.FAILED) # O estado é mudado para Failed
                return transaction.status # Retorna o estado da transação
        
        else:
            contas_origem = self.bank.accounts # Lista das contas do banco de origem
            contas_destino = banks[transaction.destination[0]].accounts # Lista das contas do banco de destino

            quantia = transaction.amount # quantia a ser transferida

            index_origem = transaction.origin[1] # Indiaca a possição da conta na lista de contas do banco
            index_destino = transaction.destination[1] # Indiaca a possição da conta na lista de contas do banco
            
            quantia_deposito = quantia + quantia*0.01 # Adiciona a taxa de transação internacional na quantia a ser retidada da conta de origem
            
            sucesso, quantia_cheque_especial = contas_origem[index_origem].withdraw(quantia_deposito) # Faz a retirada do dinheiro da conta de origem 
            # sucesso indica se a retirada do dinheriro foi feita com sucesso 
            # quantia_cheque_especial é a quantia que foi usada do cheque especial da conta, gerando uma taxa para o banco
            
            if sucesso:
                if quantia_cheque_especial > 0:
                    self.bank.taxa(quantia_cheque_especial, 0)
                self.bank.taxa(quantia, 1)         
            else: # Caso a transação não seja realizada com sucesso
                transaction.set_status(TransactionStatus.FAILED) # O estado é mudado para Failed
                return transaction.status # Retorna o estado da transação
            
            moeda_antiga = self.bank.currency # Indica a moeda do banco de origem
            moeda_nova = transaction.currency # Inda a moeda que vai ser feito o deposito

            taxa_conversao = get_exchange_rate(moeda_antiga, moeda_nova) # Indica a taxa de converção entre as moedas

            nova_quantia = quantia * taxa_conversao # Indica a quantia de dinheiro na nova moeda

            self.trasaçao_internacional(moeda_nova, nova_quantia) # Faz o deposito na conta especial do banco referente aquela moeda
                                                                  # E depois realiza a retirada do dinheiro para depositar na conta destino
            
            contas_destino[index_destino].deposit(nova_quantia) # Deposita a quantia na conta de destino, na moeda correta do banco
                                                                    # Com a taxa de conversão entre as moedas já aplicada

        
            
        self.bank.lock_num_transaçao.acquire() # Trava o mutex para incrementar o numero de transações realizadas

        self.bank.num_trasançoes += 1 # Incrementa o numero de transações realizadas

        self.bank.lock_num_transaçao.release() # Destrava o mutex que incrementa o numero de transações realizadas
        
        # Fim da parte não original
        
        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        transaction.set_status(TransactionStatus.SUCCESSFUL)
        return transaction.status

    def trasaçao_internacional(self, currency: int, quantia: int):
        if currency == 1:
            self.bank.reserves.USD.deposit(quantia)
            self.bank.reserves.USD.withdraw(quantia)
        elif currency == 2:
            self.bank.reserves.EUR.deposit(quantia)
            self.bank.reserves.EUR.withdraw(quantia)
        elif currency == 3:
            self.bank.reserves.GBP.deposit(quantia)
            self.bank.reserves.GBP.withdraw(quantia)
        elif currency == 4:
            self.bank.reserves.JPY.deposit(quantia)
            self.bank.reserves.JPY.withdraw(quantia)
        elif currency == 5:
            self.bank.reserves.CHF.deposit(quantia)
            self.bank.reserves.CHF.withdraw(quantia)
        elif currency == 6:
            self.bank.reserves.BRL.deposit(quantia)
            self.bank.reserves.BRL.withdraw(quantia)

