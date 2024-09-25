import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Para exibir imagens
import pygame  # Para sons
import pandas as pd  # Importar a biblioteca pandas

# Conectar ao banco de dados SQLite (ou criar caso não exista)
conn = sqlite3.connect('urna_eletronica.db')
cursor = conn.cursor()

# Criar tabela de votos
cursor.execute('''
CREATE TABLE IF NOT EXISTS votos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidato TEXT NOT NULL
)
''')

# Lista de candidatos (substituir pelos números e nomes reais)
# Incluindo caminhos para fotos de candidatos
candidatos = {
    '12': {'nome': 'Candidato 1', 'foto': './fotos/candidato1.png'},
    '34': {'nome': 'Candidato 2', 'foto': './fotos/candidato2.png'},
    '57': {'nome': 'Candidato 3', 'foto': './fotos/candidato3.png'},
    '77': {'nome': 'Candidato 4', 'foto': './fotos/candidato4.png'},
    '00': {'nome': 'Voto em Branco', 'foto': None}
}

# Inicializar o pygame para sons
pygame.mixer.init()

# Tentar carregar os sons com tratamento de erro
try:
    som_tecla = pygame.mixer.Sound('sons/som_tecla.wav')  # Som da tecla
    som_confirma = pygame.mixer.Sound('sons/som_confirma.wav')  # Som de confirmação
    som_corrige = pygame.mixer.Sound('sons/som_corrige.wav')  # Som de correção
except pygame.error as e:
    print(f"Erro ao carregar sons: {e}")

voto_atual = ""

# Função para atualizar a tela de votação e exibir a foto do candidato
def atualizar_tela():
    numero_candidato.set(voto_atual)
    if voto_atual in candidatos:
        exibir_foto(candidatos[voto_atual]['foto'])
        lbl_nome.config(text=candidatos[voto_atual]['nome'])  # Atualiza o nome do candidato
    else:
        exibir_foto(None)
        lbl_nome.config(text="")  # Limpa o nome se não houver candidato

# Função para registrar o voto no banco de dados
def confirmar_voto():
    global voto_atual
    if voto_atual in candidatos:
        cursor.execute("INSERT INTO votos (candidato) VALUES (?)", (candidatos[voto_atual]['nome'],))
        conn.commit()
        pygame.mixer.Sound.play(som_confirma)  # Som de confirmação
        messagebox.showinfo("Voto Computado", f"Voto computado para: {candidatos[voto_atual]['nome']}")
        limpar_tela()
    else:
        messagebox.showerror("Erro", "Número inválido. Corrija o voto.")
    
# Função para limpar a tela
def limpar_tela():
    global voto_atual
    voto_atual = ""
    atualizar_tela()
    pygame.mixer.Sound.play(som_corrige)  # Som de correção

# Função para votar em branco
def votar_branco():
    global voto_atual
    voto_atual = '00'
    confirmar_voto()

# Função para votar nulo
def votar_nulo():
    global voto_atual
    voto_atual = 'Nulo'  # Definindo como voto nulo
    cursor.execute("INSERT INTO votos (candidato) VALUES (?)", (voto_atual,))
    conn.commit()
    pygame.mixer.Sound.play(som_confirma)  # Som de confirmação
    messagebox.showinfo("Voto Computado", "Voto computado como Nulo.")
    limpar_tela()

# Função para adicionar número do candidato
def adicionar_numero(numero):
    global voto_atual
    if len(voto_atual) < 2:
        voto_atual += str(numero)
        atualizar_tela()
        pygame.mixer.Sound.play(som_tecla)  # Som de tecla ao digitar número

# Função para exibir resultados
def exibir_resultados():
    janela_resultados = tk.Toplevel(root)
    janela_resultados.title("Resultados da Votação")
    cursor.execute("SELECT candidato, COUNT(*) as total FROM votos GROUP BY candidato")
    resultados = cursor.fetchall()
    for candidato, total in resultados:
        tk.Label(janela_resultados, text=f"{candidato}: {total} votos").pack()

# Função para exibir a foto do candidato
def exibir_foto(caminho_foto):
    if caminho_foto:
        try:
            img = Image.open(caminho_foto)
            img = img.resize((150, 150))  # Redimensionar imagem para caber na tela
            img_tk = ImageTk.PhotoImage(img)
            lbl_foto.config(image=img_tk)
            lbl_foto.image = img_tk
        except Exception as e:
            lbl_foto.config(image='', text="Imagem não encontrada")
    else:
        lbl_foto.config(image='', text="")

# Criação da janela principal com Tkinter
root = tk.Tk()
root.title("Urna Eletrônica")

# Variável para exibir o número digitado
numero_candidato = tk.StringVar()

# Frame principal para dividir a tela em seções
frame_principal = tk.Frame(root)
frame_principal.pack(pady=20, padx=20)

# Frame à esquerda para a foto do candidato
frame_foto = tk.Frame(frame_principal)
frame_foto.grid(row=0, column=0, padx=20)

# Label para exibir a foto do candidato
lbl_foto = tk.Label(frame_foto, text="Foto do Candidato", font=("Arial", 14))
lbl_foto.pack()

# Label para exibir o nome do candidato
lbl_nome = tk.Label(frame_foto, text="", font=("Arial", 14))
lbl_nome.pack()

# Frame ao centro para exibir o número digitado
frame_display = tk.Frame(frame_principal)
frame_display.grid(row=0, column=1, padx=20)

# Tela de exibição do número digitado
tela = tk.Entry(frame_display, textvariable=numero_candidato, font=("Arial", 40), width=5, justify='center')
tela.pack()

# Função que cria os botões numéricos e de controle
def criar_teclado():
    frame_teclado = tk.Frame(frame_principal, bg='#0c0c0c')  # Alterando a cor de fundo do teclado
    frame_teclado.grid(row=0, column=2, padx=20)

    # Definindo o layout do teclado numérico (Grid 3x4)
    botoes = [
        ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
        ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
        ('0', 3, 1)
    ]
    
    # Criar botões numéricos com cor de fundo cinza escuro e texto branco
    for (text, row, col) in botoes:
        btn = tk.Button(frame_teclado, text=text, font=("Arial", 15), width=5, height=2, 
                        bg='#3c3c3c', fg='#fcfcfc',  # Cor de fundo cinza escuro e texto branco
                        command=lambda t=text: adicionar_numero(t))
        btn.grid(row=row, column=col, padx=5, pady=5)

    # Botões de controle (Corrige, Branco, Confirma, Nulo) com as mesmas cores
    btn_corrige = tk.Button(frame_teclado, text="CORRIGE", font=("Arial", 12), bg="orange", width=10, height=2, command=limpar_tela)
    btn_corrige.grid(row=4, column=0)

    btn_branco = tk.Button(frame_teclado, text="BRANCO", font=("Arial", 12), bg="white", width=10, height=2, command=votar_branco)
    btn_branco.grid(row=4, column=1)

   # btn_nulo = tk.Button(frame_teclado, text="NULO", font=("Arial", 15), bg="red", width=10, height=2, command=votar_nulo)
    #btn_nulo.grid(row=4, column=2)

    btn_confirma = tk.Button(frame_teclado, text="CONFIRMA", font=("Arial", 12), bg="green", width=10, height=2, command=confirmar_voto)
    btn_confirma.grid(row=4, column=2, columnspan=3)  # Colocando o botão de confirmação abaixo

# Botão para exibir resultados
btn_resultados = tk.Button(root, text="Exibir Resultados", font=("Arial", 15), command=exibir_resultados)
btn_resultados.pack(pady=20)

# Chamar função para criar o teclado
criar_teclado()

# Iniciar o loop da interface gráfica
root.mainloop()

# Fechar conexão com o banco de dados
conn.close()
