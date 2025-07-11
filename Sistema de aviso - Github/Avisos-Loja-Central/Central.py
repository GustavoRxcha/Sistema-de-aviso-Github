import socket
import threading
import os
from datetime import datetime
from tkinter import Tk, Label, Text, Button, END, scrolledtext

# --- Constantes e Configurações ---
HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede
PORT = 0000       # Porta
LOG_DIR = "Logs"

# --- Variáveis Globais Protegidas ---
clients = []
lock = threading.Lock() # Um "cadeado" para proteger a lista de clientes

# --- Funções de Log ---
def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def registrar_log(tipo, mensagem):
    log_file = os.path.join(LOG_DIR, f"{tipo}.log")
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

# --- Lógica de Rede ---
def broadcast(message):

    with lock: # Adquire o lock para trabalhar na lista de clientes com segurança
        if not clients:
            print("Nenhum cliente conectado para enviar a mensagem.")
            return

        registrar_log('mensagens_enviadas', f"Iniciando envio para {len(clients)} clientes: {message}")
        print(f"Enviando aviso para {len(clients)} clientes: {message}")

        clientes_a_remover = []

        for client_socket, client_address in clients:
            try:
                client_socket.send(message.encode('utf-8'))
            except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                print(f"Erro ao enviar para {client_address}. Marcando para remoção: {e}")
                registrar_log('clientes_desconectados', f"Cliente {client_address} desconectado (erro no envio).")
                clientes_a_remover.append((client_socket, client_address))

        # Remove os clientes desconectados da lista principal
        if clientes_a_remover:
            print(f"Removendo {len(clientes_a_remover)} clientes inativos.")
            for client in clientes_a_remover:
                if client in clients:
                    clients.remove(client)
                    client[0].close() # Fecha o socket do cliente
    
    # Atualiza a interface gráfica fora do lock para evitar bloqueios
    root.after(0, update_client_count_label)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5) # Permite até 5 conexões pendentes
    
    registrar_log("sistema", f"Servidor iniciado e escutando em {HOST}:{PORT}.")
    print(f"Servidor aguardando conexões na porta {PORT}...")

    while True:
        try:
            client_socket, client_address = server.accept()
            handle_new_connection(client_socket, client_address)
        except OSError:
            # Ocorre quando o programa é fechado
            break
        except Exception as e:
            registrar_log("sistema", f"Erro crítico ao aceitar conexão: {e}")

def handle_new_connection(client_socket, client_address):
    print(f"Conexão recebida de {client_address}")
    registrar_log("clientes_conectados", f"Cliente conectado: {client_address}.")

    with lock: # Adquire o lock para modificar a lista 'clients'
        cliente_existente = None
        for c in clients:
            if c[1][0] == client_address[0]: # c[1] é o endereço, c[1][0] é o IP
                cliente_existente = c
                break
        
        # Se encontrou, remove a conexão antiga para substituí-la pela nova
        if cliente_existente:
            print(f"Cliente com IP {client_address[0]} reconectou. Atualizando conexão.")
            registrar_log("reconexao_clientes", f"Reconexão de {client_address[0]}. Removendo conexão antiga.")
            clients.remove(cliente_existente)
            cliente_existente[0].close()

        # Adiciona o novo cliente à lista
        clients.append((client_socket, client_address))

    # 'after(0, ...)' é a maneira segura de atualizar a GUI a partir de outra thread
    root.after(0, update_client_count_label)


# --- Funções da Interface Gráfica (GUI) ---
def update_client_count_label():
    with lock:
        count = len(clients)
    label_clientes_conectados.config(text=f"Clientes conectados: {count}")

def enviar_mensagem_gui():
    """Função chamada pelo botão 'Enviar'."""
    status_aviso.config(text="")
    mensagem = texto_aviso.get("1.0", "end-1c").strip()
    
    if mensagem:
        # Envia a mensagem numa thread separada para não bloquear a interface
        threading.Thread(target=broadcast, args=(mensagem,), daemon=True).start()
        status_aviso.config(text="Aviso enviado com sucesso!", fg='green')
        texto_aviso.delete("1.0", END)
    else:
        status_aviso.config(text="A mensagem não pode estar vazia!", fg='red')


# --- Inicialização ---
if __name__ == "__main__":
    setup_logging()

    root = Tk()
    root.title("Central de Avisos - ExecFlow")
    root.geometry("400x400")
    root.configure(bg="#292929")
    root.resizable(False, False)

    # Widgets da Interface
    titulo = Label(root, text="Digite o aviso abaixo:", fg="#ffffff", bg="#292929", font=("Arial", 20, "bold"))
    titulo.pack(pady=(40, 20))

    texto_aviso = scrolledtext.ScrolledText(root, height=5, width=40, font=("Arial", 11))
    texto_aviso.pack(pady=10, padx=20)

    botao_enviar = Button(root, text="Enviar Aviso", fg="#ffffff", bg="#6d53cc", font=("Arial", 13, "bold"), command=enviar_mensagem_gui, width=20, height=2)
    botao_enviar.pack(pady=10)
    
    status_aviso = Label(root, text="", bg="#292929", font=("Arial", 12, "bold"))
    status_aviso.pack(pady=(5, 10))

    label_clientes_conectados = Label(root, text="Clientes conectados: 0", fg="#ffffff", bg="#292929", font=("Arial", 12, "bold"))
    label_clientes_conectados.pack(pady=(10, 10))
    
    # Inicia a thread do servidor
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Inicia a interface gráfica
    root.mainloop()