import argparse, time, sys
from logging import INFO, DEBUG
from random import randint

from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER


if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write('Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u", help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    parser.add_argument("--num_processors", "-p", help="Numero de payment_processor por banco") # Pode ser passado com argumento o numero de payment_processor por banco
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True
    if args.num_processors: # Caso tenha sido passado como argumento o numero de payment_processor por banco
        num_processors = int(args.num_processors) 

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n\tNumero de payment_processor por banco = {num_processors}")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0
    
    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):

        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency)
        
        # Parte não orginal
        
        bank.operating = True # Abre o banco

        # Fim parte não orginal

        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))

        # Adiciona banco na lista global de bancos
        banks.append(bank)
    
    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    
    transactiongenerator_list = list() # Lista que contem todos os geradores de transição
    paymentprocessor_list = list() # Lista que contem todos os processadores de pagamento
    aux = 0 # Variavel auxiliar para percorrer a lista de processadores de pagamentos.

    for i, bank in enumerate(banks):
        # Inicializa um TransactionGenerator thread por banco:
        transactiongenerator_list.append(TransactionGenerator(_id=0, bank=bank))
        # o _id foi fixado em 0 pois cada banco possui apenas 1 gerador de transição
        # deste modo fica mais claro o entendimento no final da execução.
        # Antes falava que o gerador 5 do banco 5 tinha sido finalizado
        # Sendo que o banco 5 não possui outros 4 geradores 


        transactiongenerator_list[i].start()
        # Inicializa um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.
        for j in range(num_processors):
            paymentprocessor_list.append(PaymentProcessor(_id=j, bank=bank))
            paymentprocessor_list[aux].start()
            aux += 1

    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        # Aguarda um tempo aleatório antes de criar o próximo cliente:
        dt = randint(0, 3)
        time.sleep(dt * time_unit)

        # Atualiza a variável tempo considerando o intervalo de criação dos clientes:
        t += dt
    
    # Finaliza todas as threads
    # TODO
    # Não original do codigo

    for bank in banks: # Percorre a lista de bancos
        bank.operating = False # Fecha o banco

    # Aguarda o termino de todas as threads para finalizar o codigo:
    for generator in transactiongenerator_list:
        generator.join()
    
    for processor in paymentprocessor_list:
        processor.join()
        #PaymentProcessor(_id=i+10, bank=bank).join()

    # Fim da parte não original

    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")

    # Parte não original

    num_trasaçoes_restantes = 0 # indica o numero de transações que faltaram ser feitas
    for bank in banks:
        bank.info()
        num_trasaçoes_restantes += len(bank.transaction_queue)

    LOGGER.info(f"==========================================")
    LOGGER.info(f"O numero de transações que faltou ser feita foi: {num_trasaçoes_restantes}")
    LOGGER.info(f"E a media de tempo seria aproximadamente: {round((num_trasaçoes_restantes/num_processors)*3*time_unit/60,3)} Minutos")
    LOGGER.info(f"==========================================")

    # Fim da parte não original