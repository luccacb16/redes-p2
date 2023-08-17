import asyncio
from tcputils import *
import random


class Servidor:
    def __init__(self, rede, porta):
        self.rede = rede
        self.porta = porta
        self.conexoes = {}
        self.callback = None
        self.rede.registrar_recebedor(self._rdt_rcv)

    def registrar_monitor_de_conexoes_aceitas(self, callback):
        """
        Usado pela camada de aplicação para registrar uma função para ser chamada
        sempre que uma nova conexão for aceita
        """
        self.callback = callback

    def _rdt_rcv(self, src_addr, dst_addr, segment):
        src_port, dst_port, seq_no, ack_no, \
            flags, window_size, checksum, urg_ptr = read_header(segment)

        
        if dst_port != self.porta:
            # Ignora segmentos que não são destinados à porta do nosso servidor
            return
        if not self.rede.ignore_checksum and calc_checksum(segment, src_addr, dst_addr) != 0:
            print('descartando segmento com checksum incorreto')
            return

        payload = segment[4*(flags>>12):]
        id_conexao = (src_addr, src_port, dst_addr, dst_port)

        if (flags & FLAGS_SYN) == FLAGS_SYN:
            # A flag SYN estar setada significa que é um cliente tentando estabelecer uma conexão nova
            # TODO: talvez você precise passar mais coisas para o construtor de conexão
            print(f'seq_no = {seq_no}, ack_no = {ack_no}')
            #Torna-se necessário passar a info de qual a próxima informação a ser recebida (seq_no+1)
            conexao = self.conexoes[id_conexao] = Conexao(self, id_conexao, seq_no+1)
            
	    ###TESTE 1###
	    #Como estamos retornando a informação ao cliente, realizamos make_header e chekcsum junto com o envio de informações com as portas e endereços de destino e fonte)
            new_sequential_number = random.randint(1,1000)
            header = make_header(dst_port, src_port, new_sequential_number, seq_no+1, FLAGS_SYN | FLAGS_ACK)
            header = fix_checksum(header, dst_addr, src_addr)
            conexao.servidor.rede.enviar(header, src_addr)
            
            # TODO: você precisa fazer o handshake aceitando a conexão. Escolha se você acha melhor
            # fazer aqui mesmo ou dentro da classe Conexao.
            if self.callback:
                self.callback(conexao)
        elif id_conexao in self.conexoes:
            # Passa para a conexão adequada se ela já estiver estabelecida
            #Realiza uma atualização dos valores seq_no e ack_no
            self.conexoes[id_conexao]._rdt_rcv(seq_no, ack_no, flags, payload)
        else:
            print('%s:%d -> %s:%d (pacote associado a conexão desconhecida)' %
                  (src_addr, src_port, dst_addr, dst_port))


class Conexao:
    def __init__(self, servidor, id_conexao, ack_no):
        self.servidor = servidor
        self.id_conexao = id_conexao
        self.callback = None
        self.timer = asyncio.get_event_loop().call_later(1, self._exemplo_timer)  # um timer pode ser criado assim; esta linha é só um exemplo e pode ser removida
        #self.timer.cancel()   # é possível cancelar o timer chamando esse método; esta linha é só um exemplo e pode ser removida
        
        #Uso de seq_no+1 para definir qual seria o seq_no_esperado no momento conferir ordem certa ou duplicação de dados
        self.seq_no_esperado = ack_no

    def _exemplo_timer(self):
        # Esta função é só um exemplo e pode ser removida
        print('Este é um exemplo de como fazer um timer')

    def _rdt_rcv(self, seq_no, ack_no, flags, payload):
        src_addr, src_port, dst_addr, dst_port = self.id_conexao

        print(f'seq_no = {seq_no}, self.seq_no_esperado = {self.seq_no_esperado}')
    	
        #Definir se está na ordem certa ou duplicada
        #conferir se o seq_no passado como parâmetro é igual ao da conexão(está na ordem correta)
        if seq_no == self.seq_no_esperado:
            #Passar para o próximo valor de seq_no_esperado/ack_no
            self.seq_no_esperado += len(payload)
            self.callback(self, payload)
            # TODO: trate aqui o recebimento de segmentos provenientes da camada de rede.
            # Chame self.callback(self, dados) para passar dados para a camada de aplicação após
            # garantir que eles não sejam duplicados e que tenham sido recebidos em ordem.
            print('recebido payload: %r' % payload)
            #Retornar info para o servidor
            segmento = make_header(dst_port, src_port, random.randint(1,10000), self.seq_no_esperado, FLAGS_ACK)
            segmento = fix_checksum(segmento, dst_addr, src_addr)
            self.servidor.rede.enviar(segmento, src_addr)

    # Os métodos abaixo fazem parte da API

    def registrar_recebedor(self, callback):
        """
        Usado pela camada de aplicação para registrar uma função para ser chamada
        sempre que dados forem corretamente recebidos
        """
        self.callback = callback

    def enviar(self, dados):
        """
        Usado pela camada de aplicação para enviar dados
        """
        #Definir certos argumentos
        #src_addr, src_port, dst_addr, dst_port = self.id_conexao
        #Criação do cabeçalho para retorno das FLAGS DE SYN E ACK
        #header = make_header(src_port, dst_port, seq_no, ack_no, FLAGS_SYN|FLAG_ACK)
        #self.servidor.rede.enviar(header, dst_addr)
        # TODO: implemente aqui o envio de dados.
        # Chame self.servidor.rede.enviar(segmento, dest_addr) para enviar o segmento
        # que você construir para a camada de rede.
        pass

    def fechar(self):
        """
        Usado pela camada de aplicação para fechar a conexão
        """
        # TODO: implemente aqui o fechamento de conexão
        pass
