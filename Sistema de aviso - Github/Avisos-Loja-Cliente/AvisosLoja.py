import socket
from tkinter import *
import threading
import time

# Configurações do servidor
SERVER_HOST = '---.---.---.--'  # IP do servidor
SERVER_PORT = 0000             # Porta do servidor
RECONNECT_DELAY_SECONDS = 18000 #Tempo para reconexão

def connect_to_server():
    while True: # Loop principal de reconexão
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")

            while True:
                texto_aviso = client_socket.recv(1024).decode('utf-8')
                
                if not texto_aviso:
                    print("Servidor encerrou a conexão.")
                    break # Sai do loop de recebimento para forçar a reconexão
                    
                mostrar_aviso(texto_aviso)

        except (socket.error, ConnectionResetError, BrokenPipeError) as e:
            # Captura erros específicos de rede
            print(f"Erro de conexão: {e}")

        finally:
            client_socket.close()

        print(f"Conexão perdida. Tentando reconectar em {RECONNECT_DELAY_SECONDS} segundos...")
        time.sleep(RECONNECT_DELAY_SECONDS)

def mostrar_aviso(texto_aviso):
    aviso = Tk()
    aviso.title("AVISOS TI - ExecFlow")
    aviso.overrideredirect(True)
    aviso.attributes('-topmost', True)
    aviso.configure(bg="#292929")

    max_width = 480  # Largura máxima da janela
    wrap_length = 380  # Comprimento máximo por linha
    lines = len(texto_aviso.split('\n'))  # Conta o número de linhas no texto
    height = 300 + (lines * 20)  # Altura dinâmica com base no número de linhas

    aviso.geometry(f"{max_width}x{height}")
    aviso.eval('tk::PlaceWindow . center')

    titulo = Label(aviso, text=" AVISO T.I ", fg="red", bg="#292929", font=("Arial", 20, "bold"))
    titulo.pack(pady=(25, 20))

    mensagem = Label(aviso, text=texto_aviso, fg="#FFFFFF", bg="#292929", font=("Arial", 15, "bold"), wraplength=wrap_length, justify="left")
    mensagem.pack(pady=(15, 15), padx=10)

    botao_fechar = Button(aviso, text="Fechar", width=15, height=1, fg="#ffffff", bg="#6d53cc", font=("Arial", 13, "bold"), command=aviso.destroy)
    botao_fechar.pack(pady=(20, 0))

    marca = Label(aviso, text="ExecFlow - Sistema de avisos\nDesenvolvido por Gustavo da Rocha Ferreira", fg="#ffffff", bg="#292929", font=("Arial", 6))
    marca.pack(side=BOTTOM, pady=(0, 10))  # Fixa a label na parte inferior

    aviso.grab_set()
    aviso.mainloop()

threading.Thread(target=connect_to_server, daemon=True).start()

try:
    # Loop infinito para manter o cliente ativo
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Cliente encerrado.")