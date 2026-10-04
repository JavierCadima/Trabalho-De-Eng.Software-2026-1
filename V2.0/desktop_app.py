"""Interface desktop para o sistema de gestao da loja de baterias."""

import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, simpledialog, ttk

from database.connection import conectar_bd
from models.bateria import Bateria
from models.cargo import Cargo
from models.cliente import Cliente
from models.funcionario import Funcionario
from models.sessao import SessaoSistema
from models.troca import TrocaGarantia
from models.venda import Venda
from repositories.bateria_repository import BateriaRepository
from repositories.cargo_repository import CargoRepository
from repositories.cliente_repository import ClienteRepository
from repositories.funcionario_repository import FuncionarioRepository
from repositories.troca_repository import TrocaRepository
from repositories.venda_repository import VendaRepository
from utils.password_security import avaliar_forca_senha, gerar_credencial, verificar_senha
from views.funcionario_view import TODAS_PERMISSOES


class DesktopApp(tk.Tk):
    """Aplicativo Tkinter com telas acessiveis de acordo com o cargo logado."""

    BG = "#f3f5f7"
    PANEL = "#ffffff"
    DARK = "#18232f"
    TEXT = "#202b36"
    MUTED = "#718096"
    GREEN = "#a6e22e"
    GREEN_DARK = "#6d9f12"
    BORDER = "#dce2e8"

    def __init__(self):
        super().__init__()
        self.title("Loja de Baterias | Gestao")
        self.geometry("1180x760")
        self.minsize(940, 620)
        self.configure(bg=self.BG)
        self._configurar_estilos()
        self.pagina = None
        self.pdv_carrinho = []
        self.pdv_baterias = []
        self._mostrar_login()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10),
                        background=self.PANEL, fieldbackground=self.PANEL,
                        foreground=self.TEXT)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background="#e9eef2", foreground=self.TEXT, padding=8)
        style.map("Treeview", background=[("selected", "#dff3ae")],
                  foreground=[("selected", self.TEXT)])
        style.configure("TCombobox", padding=7)

    def _limpar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _frame(self, parent, **kwargs):
        options = {"bg": self.PANEL, "highlightbackground": self.BORDER,
                   "highlightthickness": 1}
        options.update(kwargs)
        return tk.Frame(parent, **options)

    def _botao(self, parent, texto, comando, principal=False, **kwargs):
        return tk.Button(
            parent, text=texto, command=comando,
            bg=self.GREEN if principal else self.DARK,
            fg=self.DARK if principal else "white",
            activebackground=self.GREEN_DARK if principal else "#263747",
            activeforeground="white" if principal else "white",
            relief="flat", borderwidth=0, padx=16, pady=10,
            font=("Segoe UI", 10, "bold"), cursor="hand2", **kwargs
        )

    def _titulo(self, parent, titulo, descricao=""):
        tk.Label(parent, text=titulo, bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        if descricao:
            tk.Label(parent, text=descricao, bg=self.BG, fg=self.MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 18))

    def _campo(self, parent, rotulo, variavel=None, show=None):
        tk.Label(parent, text=rotulo, bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 4))
        entrada = ttk.Entry(parent, textvariable=variavel, show=show)
        entrada.pack(fill="x")
        return entrada

    def _mostrar_login(self):
        self._limpar()
        container = tk.Frame(self, bg=self.BG)
        container.place(relx=0.5, rely=0.5, anchor="center", width=420)
        self.title("Sistema de Gestão | Loja de Baterias")
        tk.Label(container, text="BATERIA", bg=self.BG, fg=self.GREEN_DARK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(container, text="Sistema de gestão", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(container, text="Entre com sua matrícula para acessar o sistema.",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        card = self._frame(container)
        card.pack(fill="x", pady=24, ipady=12, ipadx=18)
        tk.Label(card, text="Acesso do operador", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(14, 0))
        self.login_matricula = tk.StringVar()
        entrada = self._campo(card, "Matrícula", self.login_matricula)
        entrada.bind("<Return>", lambda _: self._entrar())
        entrada.pack_configure(padx=18)
        self._botao(card, "Entrar no sistema", self._entrar, principal=True).pack(
            fill="x", padx=18, pady=20
        )
        tk.Label(container, text="Acesso definido por cargo e permissões.",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        entrada.focus_set()

    def _entrar(self):
        matricula = self.login_matricula.get().strip()
        if not matricula:
            messagebox.showwarning("Matricula obrigatoria", "Informe sua matricula.")
            return
        try:
            operador = FuncionarioRepository.buscar_por_matricula(matricula)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        if not operador:
            messagebox.showerror("Acesso nao encontrado", "Matricula inexistente ou funcionario inativo.")
            return
        if not operador.is_administrador_principal():
            if not operador.senha_hash or not operador.senha_salt:
                credencial = self._dialogo_nova_senha(primeiro_acesso=True)
                if credencial is None:
                    return
                try:
                    FuncionarioRepository.definir_credencial(operador.id, *credencial)
                except (sqlite3.Error, ValueError) as erro:
                    messagebox.showerror("Erro ao cadastrar senha", str(erro))
                    return
                operador.senha_hash, operador.senha_salt = credencial
            else:
                senha = simpledialog.askstring(
                    "Autenticação", "Digite sua senha:", show="*", parent=self
                )
                if senha is None:
                    return
                if not verificar_senha(senha, operador.senha_hash, operador.senha_salt):
                    messagebox.showerror("Acesso negado", "Senha incorreta.")
                    return
        SessaoSistema.definir_operador(operador)
        self._mostrar_aplicativo()

    def _dialogo_nova_senha(self, primeiro_acesso=False):
        janela = tk.Toplevel(self)
        janela.title("Criar senha" if primeiro_acesso else "Redefinir senha")
        janela.configure(bg=self.PANEL)
        janela.transient(self)
        janela.grab_set()
        janela.resizable(False, False)
        area = tk.Frame(janela, bg=self.PANEL, padx=24, pady=20)
        area.pack(fill="both", expand=True)
        titulo = "Crie sua senha de acesso" if primeiro_acesso else "Defina a nova senha"
        tk.Label(area, text=titulo, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(area, text="A senha será armazenada protegida, nunca em texto puro.",
                 bg=self.PANEL, fg=self.MUTED, wraplength=380,
                 justify="left").pack(anchor="w", pady=(4, 10))
        senha = self._campo(area, "Nova senha", show="*")
        confirmar = self._campo(area, "Confirme a senha", show="*")
        estado = tk.Label(area, text="Força: informe uma senha.",
                          bg=self.PANEL, fg=self.MUTED)
        estado.pack(anchor="w", pady=(10, 0))
        saida = []

        def atualizar_forca(_=None):
            classificacao, motivo = avaliar_forca_senha(senha.get())
            cor = {"Fraca": "#c0392b", "Média": "#b7791f", "Forte": self.GREEN_DARK}
            estado.configure(text=f"Força: {classificacao}. {motivo}",
                             fg=cor[classificacao])

        senha.bind("<KeyRelease>", atualizar_forca)

        def salvar():
            valor = senha.get()
            classificacao, motivo = avaliar_forca_senha(valor)
            if valor != confirmar.get():
                messagebox.showerror("Senhas diferentes", "A confirmação não corresponde à senha.", parent=janela)
                return
            if classificacao == "Fraca":
                messagebox.showwarning("Senha fraca", motivo, parent=janela)
                return
            saida.extend(gerar_credencial(valor))
            janela.destroy()

        self._botao(area, "Salvar senha", salvar, principal=True).pack(fill="x", pady=(18, 0))
        senha.focus_set()
        self.wait_window(janela)
        return tuple(saida) if saida else None

    def _verificar_autorizacao_superior(self, funcionario):
        operador_sessao = SessaoSistema.obter_operador()
        if not operador_sessao:
            messagebox.showerror("Acesso negado", "Nenhum operador está autenticado.")
            return False
        try:
            funcionarios = FuncionarioRepository.obter_todos(apenas_ativos=True)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro ao validar autorização", str(erro))
            return False
        operador = next((item for item in funcionarios if item.id == operador_sessao.id), None)
        alvo = next((item for item in funcionarios if item.id == funcionario.id), None)
        if not operador or not alvo or not operador.tem_permissao("funcionarios_gerenciar"):
            messagebox.showerror(
                "Acesso negado",
                "O autorizador e o funcionário precisam estar ativos, e o autorizador precisa gerenciar funcionários."
            )
            return False
        if (not alvo.cargo or not operador.cargo or operador.id == alvo.id
                or operador.cargo.nivel <= alvo.cargo.nivel):
            messagebox.showerror(
                "Acesso negado",
                "A redefinição exige autorização de outro funcionário com cargo de nível superior."
            )
            return False
        if operador.is_administrador_principal():
            return True
        if not operador.senha_hash or not operador.senha_salt:
            messagebox.showerror(
                "Senha do autorizador ausente",
                "O autorizador precisa cadastrar sua senha antes de liberar redefinições."
            )
            return False
        senha = simpledialog.askstring(
            "Autorizar redefinição",
            "Confirme a senha do funcionário autorizador:",
            show="*",
            parent=self,
        )
        if senha is None:
            return False
        if not verificar_senha(senha, operador.senha_hash, operador.senha_salt):
            messagebox.showerror("Autorização negada", "Senha do autorizador incorreta.")
            return False
        return True

    def _mostrar_aplicativo(self):
        self._limpar()
        operador = SessaoSistema.obter_operador()
        shell = tk.Frame(self, bg=self.BG)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=self.DARK, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="BATERIA", bg=self.DARK, fg=self.GREEN,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=22, pady=(24, 0))
        tk.Label(sidebar, text="GESTÃO DA LOJA", bg=self.DARK, fg="#a8b5c2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(2, 18))

        botoes = [("Inicio", self._tela_inicio, True)]
        if SessaoSistema.tem_permissao("venda_realizar"):
            botoes.append(("Ponto de venda", self._tela_pdv, True))
        if (SessaoSistema.tem_permissao("estoque_consultar")
                or SessaoSistema.tem_permissao("estoque_gerenciar")):
            botoes.append(("Estoque", self._tela_estoque, True))
        if (SessaoSistema.tem_permissao("venda_consultar")
                or SessaoSistema.tem_permissao("venda_realizar")):
            botoes.append(("Vendas", self._tela_vendas, True))
        if (SessaoSistema.tem_permissao("cliente_consultar")
                or SessaoSistema.tem_permissao("cliente_ver_dados")):
            botoes.append(("Clientes", self._tela_clientes, True))
        if (SessaoSistema.tem_permissao("garantia_consultar")
                or SessaoSistema.tem_permissao("garantia_troca")):
            botoes.append(("Garantias", self._tela_garantias, True))
        if any(SessaoSistema.tem_permissao(permissao) for permissao in (
                "area_gerente", "relatorios_ver", "funcionarios_gerenciar",
                "cargos_gerenciar")):
            botoes.append(("Gestao", self._tela_gestao, True))

        for label, comando, _ in botoes:
            tk.Button(sidebar, text=label, command=comando, anchor="w",
                      bg=self.DARK, fg="white", activebackground="#263747",
                      activeforeground=self.GREEN, relief="flat", bd=0,
                      padx=22, pady=12, font=("Segoe UI", 10),
                      cursor="hand2").pack(fill="x")

        tk.Frame(sidebar, bg="#364655", height=1).pack(fill="x", padx=18, pady=16)
        tk.Label(sidebar, text=operador.nome, bg=self.DARK, fg="white",
                 font=("Segoe UI", 10, "bold"), wraplength=180,
                 justify="left").pack(anchor="w", padx=22)
        tk.Label(sidebar, text=operador.cargo.nome if operador.cargo else "Sem cargo",
                 bg=self.DARK, fg="#a8b5c2", font=("Segoe UI", 9),
                 wraplength=180, justify="left").pack(anchor="w", padx=22, pady=(3, 12))
        self._botao(sidebar, "Trocar operador / Sair", self._sair).pack(
            side="bottom", fill="x", padx=14, pady=18
        )

        self.conteudo = tk.Frame(shell, bg=self.BG, padx=30, pady=24)
        self.conteudo.pack(side="left", fill="both", expand=True)
        self._tela_inicio()

    def _sair(self):
        SessaoSistema.definir_operador(None)
        self._mostrar_login()

    def _tela_inicio(self):
        self._limpar_conteudo()
        operador = SessaoSistema.obter_operador()
        self._titulo(self.conteudo, f"Olá, {operador.nome.split()[0]}",
                     "Acesse as operacoes disponiveis para o seu cargo.")
        cards = tk.Frame(self.conteudo, bg=self.BG)
        cards.pack(fill="x")
        opcoes = []
        if SessaoSistema.tem_permissao("venda_realizar"):
            opcoes.append(("PDV", "Registrar uma venda", self._tela_pdv))
        if SessaoSistema.tem_permissao("estoque_consultar") or SessaoSistema.tem_permissao("estoque_gerenciar"):
            opcoes.append(("Estoque", "Consultar produtos e precos", self._tela_estoque))
        if SessaoSistema.tem_permissao("venda_consultar") or SessaoSistema.tem_permissao("venda_realizar"):
            opcoes.append(("Vendas", "Consultar vendas registradas", self._tela_vendas))
        if SessaoSistema.tem_permissao("garantia_consultar") or SessaoSistema.tem_permissao("garantia_troca"):
            opcoes.append(("Garantias", "Consultar ou registrar trocas", self._tela_garantias))
        if any(SessaoSistema.tem_permissao(permissao) for permissao in (
                "area_gerente", "relatorios_ver", "funcionarios_gerenciar",
                "cargos_gerenciar")):
            opcoes.append(("Gestão", "Relatórios, equipe e cargos", self._tela_gestao))
        for index, (title, detail, command) in enumerate(opcoes):
            card = self._frame(cards)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=(0, 14), pady=(0, 14))
            cards.grid_columnconfigure(index % 2, weight=1)
            tk.Label(card, text=title, bg=self.PANEL, fg=self.TEXT,
                     font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=18, pady=(18, 4))
            tk.Label(card, text=detail, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 12))
            self._botao(card, "Abrir", command, principal=True).pack(
                anchor="w", padx=18, pady=(0, 16)
            )
        if SessaoSistema.tem_permissao("relatorios_ver"):
            relatorio = self._frame(self.conteudo)
            relatorio.pack(fill="x", pady=(10, 0))
            tk.Label(relatorio, text="Resumo gerencial", bg=self.PANEL, fg=self.TEXT,
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
            try:
                vendas, defeitos = TrocaRepository.obter_dados_relatorio()
                total_vendas, faturamento = vendas[0] or 0, vendas[1] or 0
                texto = f"{total_vendas} itens vendidos    |    Faturamento acumulado: R$ {faturamento:.2f}    |    {len(defeitos)} trocas em garantia"
            except sqlite3.Error as erro:
                texto = f"Nao foi possivel carregar o resumo: {erro}"
            tk.Label(relatorio, text=texto, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 16))
        if not opcoes:
            tk.Label(self.conteudo, text="Seu cargo nao possui operacoes liberadas.",
                     bg=self.BG, fg=self.MUTED).pack(anchor="w", pady=20)

    def _limpar_conteudo(self):
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    def _tabela(self, parent, colunas, larguras=None):
        tabela = ttk.Treeview(parent, columns=colunas, show="headings")
        for index, coluna in enumerate(colunas):
            tabela.heading(coluna, text=coluna)
            tabela.column(coluna, width=larguras[index] if larguras else 130,
                          anchor="w")
        tabela.pack(fill="both", expand=True)
        return tabela

    def _tela_estoque(self):
        self._limpar_conteudo()
        pode_consultar = SessaoSistema.tem_permissao("estoque_consultar")
        pode_gerenciar = SessaoSistema.tem_permissao("estoque_gerenciar")
        self._titulo(self.conteudo, "Estoque", "Produtos, disponibilidade e preços.")
        acoes = tk.Frame(self.conteudo, bg=self.BG)
        acoes.pack(fill="x", pady=(0, 14))
        if pode_gerenciar:
            self._botao(acoes, "Cadastrar bateria", self._dialogo_nova_bateria,
                        principal=True).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Repor estoque", self._repor_estoque).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Alterar precos", self._alterar_precos).pack(side="left")
        if pode_consultar:
            tabela = self._tabela(self.conteudo,
                                  ("ID", "Marca / Modelo", "Especificacao", "Aplicacao",
                                   "Unidades", "Preco", "Minimo", "Carcaca"),
                                  (55, 190, 120, 180, 80, 100, 100, 100))
            try:
                produtos = BateriaRepository.obter_todas()
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            for item in produtos:
                id_bat, marca, modelo, ah, cca, aplicacao, qtd, pv, pm, carcaca = item
                tabela.insert("", "end", values=(id_bat, f"{marca} {modelo}",
                              f"{ah}Ah / {cca}A", aplicacao, qtd,
                              f"R$ {pv:.2f}", f"R$ {pm:.2f}", f"R$ {carcaca:.2f}"))
        else:
            tk.Label(self.conteudo, text="Seu cargo pode gerenciar estoque, mas nao consultar a listagem geral.",
                     bg=self.BG, fg=self.MUTED).pack(anchor="w")

    def _dialogo_nova_bateria(self):
        if not SessaoSistema.tem_permissao("estoque_gerenciar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode cadastrar produtos.")
            return
        campos = [("Marca", "marca"), ("Modelo", "modelo"), ("Amperagem (Ah)", "ah"),
                  ("CCA", "cca"), ("Voltagem (V)", "voltagem"), ("Aplicacao", "aplicacao"),
                  ("Garantia (meses)", "garantia"), ("Quantidade inicial", "quantidade"),
                  ("Preço de custo", "custo"), ("Preço de venda", "venda"),
                  ("Preço mínimo", "minimo"), ("Desconto carcaça", "carcaca")]
        valores = self._dialogo_formulario("Cadastrar bateria", campos)
        if valores is None:
            return
        try:
            bateria = Bateria(valores["marca"], valores["modelo"], int(valores["ah"]),
                              int(valores["cca"]), int(valores["voltagem"]),
                              valores["aplicacao"], int(valores["garantia"]),
                              int(valores["quantidade"]), float(valores["custo"].replace(",", ".")),
                              float(valores["venda"].replace(",", ".")),
                              float(valores["minimo"].replace(",", ".")),
                              float(valores["carcaca"].replace(",", ".")))
            if min(bateria.amperagem, bateria.cca, bateria.voltagem,
                   bateria.garantia_meses) <= 0:
                raise ValueError("Especificacoes e garantia devem ser maiores que zero.")
            if bateria.quantidade < 0 or min(bateria.preco_custo, bateria.preco_venda,
                                             bateria.preco_minimo, bateria.valor_carcaca) < 0:
                raise ValueError("Quantidade e precos devem ser zero ou maiores.")
            BateriaRepository.salvar(bateria)
        except ValueError as erro:
            messagebox.showerror("Dados invalidos", str(erro))
            return
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        messagebox.showinfo("Cadastro concluido", "Bateria cadastrada com sucesso.")
        self._tela_estoque()

    def _dialogo_formulario(self, titulo, campos):
        janela = tk.Toplevel(self)
        janela.title(titulo)
        janela.configure(bg=self.PANEL)
        janela.transient(self)
        janela.grab_set()
        janela.geometry("500x760")
        area = tk.Frame(janela, bg=self.PANEL, padx=24, pady=20)
        area.pack(fill="both", expand=True)
        tk.Label(area, text=titulo, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        entradas = {}
        for rotulo, chave in campos:
            entradas[chave] = self._campo(area, rotulo)
        resultado = {}

        def confirmar():
            resultado.update({chave: entrada.get().strip()
                              for chave, entrada in entradas.items()})
            if any(not valor for valor in resultado.values()):
                messagebox.showwarning("Campos obrigatorios", "Preencha todos os campos.", parent=janela)
                resultado.clear()
                return
            janela.destroy()

        self._botao(area, "Salvar", confirmar, principal=True).pack(fill="x", pady=20)
        self.wait_window(janela)
        return resultado or None

    def _produto_por_id(self, produto_id):
        for bateria in BateriaRepository.buscar_baterias(str(produto_id)):
            return bateria
        return None

    def _repor_estoque(self):
        if not SessaoSistema.tem_permissao("estoque_gerenciar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode repor estoque.")
            return
        produto_id = simpledialog.askinteger("Reposicao", "ID do produto:")
        if produto_id is None:
            return
        quantidade = simpledialog.askinteger("Reposicao", "Unidades a adicionar:", minvalue=1)
        if quantidade is None:
            return
        try:
            if not self._produto_por_id(produto_id):
                messagebox.showerror("Produto nao encontrado", "Confira o ID e tente novamente.")
                return
            BateriaRepository.adicionar_estoque(produto_id, quantidade)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        messagebox.showinfo("Estoque atualizado", "A reposicao foi registrada.")
        self._tela_estoque()

    def _alterar_precos(self):
        if not SessaoSistema.tem_permissao("estoque_gerenciar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode alterar precos.")
            return
        produto_id = simpledialog.askinteger("Alterar precos", "ID do produto:")
        if produto_id is None:
            return
        try:
            bateria = self._produto_por_id(produto_id)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        if not bateria:
            messagebox.showerror("Produto nao encontrado", "Confira o ID e tente novamente.")
            return
        venda = simpledialog.askfloat("Alterar precos", "Novo preco de venda:", initialvalue=bateria[6], minvalue=0)
        if venda is None:
            return
        minimo = simpledialog.askfloat("Alterar precos", "Novo preco minimo:", initialvalue=bateria[7], minvalue=0)
        if minimo is None:
            return
        carcaca = simpledialog.askfloat("Alterar precos", "Novo desconto de carcaca:", initialvalue=bateria[8], minvalue=0)
        if carcaca is None:
            return
        try:
            BateriaRepository.atualizar_precos(produto_id, venda, minimo, carcaca)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        self._tela_estoque()

    def _tela_pdv(self):
        if not SessaoSistema.tem_permissao("venda_realizar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode realizar vendas.")
            return
        self._limpar_conteudo()
        self._titulo(self.conteudo, "Ponto de venda", "Adicione baterias ao carrinho e conclua o atendimento.")
        area = tk.Frame(self.conteudo, bg=self.BG)
        area.pack(fill="both", expand=True)
        area.columnconfigure(0, weight=4)
        area.columnconfigure(1, weight=6)
        area.rowconfigure(0, weight=1)

        catalogo = self._frame(area)
        catalogo.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(catalogo, text="Buscar produto", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(catalogo, text="Pesquise pelo nome, marca ou codigo.", bg=self.PANEL,
                 fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        busca = ttk.Entry(catalogo)
        busca.pack(fill="x", padx=16, pady=12)
        lista = tk.Listbox(catalogo, font=("Segoe UI", 10), activestyle="none",
                           selectbackground=self.GREEN, selectforeground=self.TEXT,
                           relief="flat", height=15)
        lista.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        try:
            self.pdv_baterias = BateriaRepository.obter_todas()
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        exibidos = []

        def filtrar(_=None):
            exibidos.clear()
            lista.delete(0, "end")
            termo = busca.get().strip().lower()
            for bateria in self.pdv_baterias:
                id_bat, marca, modelo, ah, cca, _, quantidade, preco, *_ = bateria
                descricao = f"{id_bat} | {marca} {modelo} | {ah}Ah / {cca}A | {quantidade} un. | R$ {preco:.2f}"
                if quantidade > 0 and (not termo or termo in descricao.lower()):
                    exibidos.append(bateria)
                    lista.insert("end", descricao)

        busca.bind("<KeyRelease>", filtrar)
        filtrar()

        pedido = self._frame(area)
        pedido.grid(row=0, column=1, sticky="nsew")
        tk.Label(pedido, text="Carrinho", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(16, 10))
        tree = ttk.Treeview(pedido, columns=("produto", "troca", "preco"),
                            show="headings", height=8)
        for col, rotulo, width in (("produto", "Produto", 220), ("troca", "Carcaca", 75),
                                   ("preco", "Valor", 95)):
            tree.heading(col, text=rotulo)
            tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True, padx=16)

        cliente = tk.Frame(pedido, bg=self.PANEL, padx=16)
        cliente.pack(fill="x", pady=(12, 0))
        tk.Label(cliente, text="Dados do cliente", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        cpf_var, nome_var, tel_var, endereco_var = (tk.StringVar() for _ in range(4))

        def campo_cliente(rotulo, var, linha, coluna):
            bloco = tk.Frame(cliente, bg=self.PANEL)
            bloco.grid(row=linha, column=coluna, sticky="ew",
                       padx=(0, 8) if coluna == 0 else 0, pady=(6, 0))
            tk.Label(bloco, text=rotulo, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 3))
            campo = ttk.Entry(bloco, textvariable=var)
            campo.pack(fill="x")
            return campo

        cpf_entry = campo_cliente("CPF", cpf_var, 1, 0)
        campo_cliente("Nome", nome_var, 1, 1)
        campo_cliente("Telefone", tel_var, 2, 0)
        campo_cliente("Endereco", endereco_var, 2, 1)
        cliente.columnconfigure(0, weight=1)
        cliente.columnconfigure(1, weight=1)

        total_var = tk.StringVar(value="R$ 0,00")
        total = tk.Frame(pedido, bg=self.PANEL, padx=16, pady=10)
        total.pack(fill="x")
        tk.Label(total, text="TOTAL", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(total, textvariable=total_var, bg=self.PANEL, fg=self.GREEN_DARK,
                 font=("Segoe UI", 20, "bold")).pack(side="right")

        def atualizar_carrinho():
            tree.delete(*tree.get_children())
            total_venda = 0.0
            for index, item in enumerate(self.pdv_carrinho):
                tree.insert("", "end", iid=str(index),
                            values=(f"{item['marca']} {item['modelo']}",
                                    "Sim" if item["com_troca"] else "Nao",
                                    f"R$ {item['valor']:.2f}"))
                total_venda += item["valor"]
            total_var.set(f"R$ {total_venda:.2f}".replace(".", ","))

        def adicionar():
            selecionado = lista.curselection()
            if not selecionado:
                messagebox.showwarning("Selecione um produto", "Escolha um produto do catalogo.")
                return
            resumo = exibidos[selecionado[0]]
            try:
                detalhes = BateriaRepository.buscar_baterias(str(resumo[0]))
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            if not detalhes:
                messagebox.showwarning("Produto indisponivel", "Atualize a busca e tente novamente.")
                return
            bateria = detalhes[0]
            id_bat, marca, modelo, _, _, quantidade, preco, minimo, valor_carcaca, garantia = bateria
            qtd_no_carrinho = sum(1 for item in self.pdv_carrinho if item["id"] == id_bat)
            if qtd_no_carrinho >= quantidade:
                messagebox.showwarning("Estoque insuficiente", "Nao ha unidades disponiveis para adicionar.")
                return
            com_troca = messagebox.askyesno("Troca de carcaca",
                                             "O cliente vai entregar uma bateria usada?")
            piso = minimo - valor_carcaca if com_troca else minimo
            sugerido = max(0, preco - (valor_carcaca if com_troca else 0))
            valor = simpledialog.askfloat("Preco da venda",
                                          f"Preco final (minimo permitido: R$ {piso:.2f}):",
                                          initialvalue=sugerido, minvalue=piso)
            if valor is None:
                return
            serie = simpledialog.askstring("Numero de serie", "Informe a serie da bateria:")
            if not serie or not serie.strip():
                messagebox.showwarning("Serie obrigatoria", "Informe o numero de serie do produto.")
                return
            self.pdv_carrinho.append({"id": id_bat, "marca": marca, "modelo": modelo,
                                      "valor": valor, "com_troca": int(com_troca),
                                      "serie": serie.strip(), "garantia": garantia})
            atualizar_carrinho()

        def remover():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecione um item", "Escolha o item que deseja remover.")
                return
            if not SessaoSistema.tem_permissao("venda_remover_item"):
                matricula = simpledialog.askstring(
                    "Autorizacao necessaria",
                    "Informe a matricula do fiscal/gerente para autorizar a remocao:"
                )
                if not matricula:
                    return
                try:
                    fiscal = FuncionarioRepository.buscar_por_matricula(matricula.strip())
                except sqlite3.Error as erro:
                    messagebox.showerror("Erro no banco de dados", str(erro))
                    return
                if not fiscal or not fiscal.tem_permissao("venda_remover_item"):
                    messagebox.showerror("Remocao negada", "Matricula invalida ou sem permissao.")
                    return
            self.pdv_carrinho.pop(int(selected[0]))
            atualizar_carrinho()

        def localizar_cliente(_=None):
            cpf = cpf_var.get().strip()
            if len(cpf) < 5:
                return
            try:
                existente = ClienteRepository.buscar_por_cpf(cpf)
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            if existente:
                nome_var.set(existente.nome)
                tel_var.set(existente.telefone)
                endereco_var.set(existente.endereco if SessaoSistema.tem_permissao("cliente_ver_dados") else "")
        cpf_entry.bind("<FocusOut>", localizar_cliente)

        pagamento_var = tk.StringVar(value="PIX")
        rodape = tk.Frame(pedido, bg=self.PANEL, padx=16, pady=8)
        rodape.pack(fill="x")
        tk.Label(rodape, text="Pagamento", bg=self.PANEL, fg=self.MUTED).pack(side="left")
        ttk.Combobox(rodape, textvariable=pagamento_var, state="readonly",
                     values=("PIX", "Cartao", "Dinheiro"), width=15).pack(side="left", padx=10)
        botoes = tk.Frame(pedido, bg=self.PANEL, padx=16, pady=12)
        botoes.pack(fill="x")
        self._botao(botoes, "Adicionar item", adicionar, principal=True).pack(side="left", padx=(0, 8))
        self._botao(botoes, "Remover item", remover).pack(side="left", padx=(0, 8))
        self._botao(botoes, "Finalizar venda", lambda: finalizar(), principal=True).pack(side="right")

        def finalizar():
            if not self.pdv_carrinho:
                messagebox.showwarning("Carrinho vazio", "Adicione pelo menos um produto.")
                return
            cpf, nome = cpf_var.get().strip(), nome_var.get().strip()
            if not cpf or not nome:
                messagebox.showwarning("Dados do cliente", "Informe pelo menos o CPF e o nome do cliente.")
                return
            try:
                cliente_existente = ClienteRepository.buscar_por_cpf(cpf)
                if not cliente_existente and not SessaoSistema.tem_permissao("cliente_cadastrar"):
                    messagebox.showerror("Permissao necessaria",
                                         "Seu cargo nao pode cadastrar clientes novos; venda cancelada.")
                    return
                endereco_cliente = (cliente_existente.endereco if cliente_existente
                                    else endereco_var.get().strip())
                if not cliente_existente:
                    if not endereco_cliente:
                        messagebox.showwarning("Endereco obrigatorio", "Informe o endereco do cliente.")
                        return
                    ClienteRepository.salvar(Cliente(cpf=cpf, nome=nome, endereco=endereco_cliente,
                                                      telefone=tel_var.get().strip()))
                agora = datetime.now()
                data_venda = agora.strftime("%Y-%m-%d %H:%M:%S")
                for item in self.pdv_carrinho:
                    if BateriaRepository.obter_quantidade_estoque(item["id"]) <= 0:
                        messagebox.showerror("Estoque alterado",
                                             f"Produto {item['marca']} {item['modelo']} sem estoque.")
                        return
                    garantia = (agora + timedelta(days=item["garantia"] * 30)).strftime("%Y-%m-%d")
                    VendaRepository.salvar(Venda(
                        bateria_id=item["id"], cliente_cpf=cpf, numero_serie=item["serie"],
                        data_venda=data_venda, com_troca=item["com_troca"],
                        valor_pago=item["valor"], forma_pagamento=pagamento_var.get(),
                        garantia_ate=garantia, cliente_nome=nome,
                        cliente_endereco=endereco_cliente
                    ))
                    BateriaRepository.decrementar_estoque(item["id"])
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            total_pago = sum(item["valor"] for item in self.pdv_carrinho)
            self.pdv_carrinho.clear()
            messagebox.showinfo("Venda concluida", f"Venda registrada com sucesso.\nTotal: R$ {total_pago:.2f}")
            self._tela_pdv()

    def _tela_vendas(self):
        if not (SessaoSistema.tem_permissao("venda_consultar")
                or SessaoSistema.tem_permissao("venda_realizar")):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode consultar vendas.")
            return
        self._limpar_conteudo()
        self._titulo(self.conteudo, "Vendas", "Historico de vendas registradas.")
        filtros = tk.Frame(self.conteudo, bg=self.BG)
        filtros.pack(fill="x", pady=(0, 14))
        tipo = tk.StringVar(value="Todas")
        ttk.Combobox(filtros, textvariable=tipo, state="readonly",
                     values=("Todas", "CPF do cliente", "Numero de serie"),
                     width=22).pack(side="left", padx=(0, 8))
        termo = ttk.Entry(filtros, width=32)
        termo.pack(side="left", padx=(0, 8))
        tabela = self._tabela(self.conteudo,
                              ("Venda", "Produto", "CPF", "Cliente", "Serie", "Data", "Pagamento", "Valor"),
                              (60, 160, 120, 150, 110, 150, 100, 90))

        def carregar():
            filtro = {"Todas": "1", "CPF do cliente": "2", "Numero de serie": "3"}[tipo.get()]
            parametro = termo.get().strip() or None
            try:
                vendas = VendaRepository.consultar_vendas(filtro, parametro)
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            tabela.delete(*tabela.get_children())
            mostrar_endereco = SessaoSistema.tem_permissao("cliente_ver_dados")
            for venda in vendas:
                (id_venda, marca, modelo, cpf, serie, data, valor, pagamento,
                 _, nome, endereco) = venda
                cliente = nome or "—"
                if mostrar_endereco and endereco:
                    cliente = f"{cliente} | {endereco}"
                tabela.insert("", "end", values=(id_venda, f"{marca} {modelo}", cpf,
                              cliente, serie, data, pagamento, f"R$ {valor:.2f}"))
        self._botao(filtros, "Buscar", carregar, principal=True).pack(side="left")
        carregar()

    def _tela_clientes(self):
        if not (SessaoSistema.tem_permissao("cliente_consultar")
                or SessaoSistema.tem_permissao("cliente_ver_dados")):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode consultar clientes.")
            return
        self._limpar_conteudo()
        self._titulo(self.conteudo, "Clientes", "Cadastro e consulta de clientes.")
        acoes = tk.Frame(self.conteudo, bg=self.BG)
        acoes.pack(fill="x", pady=(0, 14))
        if SessaoSistema.tem_permissao("cliente_cadastrar"):
            self._botao(acoes, "Cadastrar cliente", self._dialogo_novo_cliente,
                        principal=True).pack(side="left")
        tabela = self._tabela(self.conteudo, ("CPF", "Nome", "Endereco", "Telefone"),
                              (150, 220, 320, 140))
        try:
            clientes = ClienteRepository.obter_todos()
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        pode_ver_endereco = SessaoSistema.tem_permissao("cliente_ver_dados")
        for cliente in clientes:
            tabela.insert("", "end", values=(cliente.cpf, cliente.nome,
                          cliente.endereco if pode_ver_endereco else "[RESTRITO]",
                          cliente.telefone))

    def _dialogo_novo_cliente(self):
        if not SessaoSistema.tem_permissao("cliente_cadastrar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode cadastrar clientes.")
            return
        valores = self._dialogo_formulario("Cadastrar cliente",
                   (("CPF", "cpf"), ("Nome", "nome"), ("Endereco", "endereco"),
                    ("Telefone", "telefone")))
        if not valores:
            return
        try:
            existente = ClienteRepository.buscar_por_cpf(valores["cpf"])
            if existente and not messagebox.askyesno(
                    "Cliente existente", "Esse CPF ja esta cadastrado. Deseja atualizar os dados?"):
                return
            ClienteRepository.salvar(Cliente(**valores))
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        self._tela_clientes()

    def _tela_garantias(self):
        pode_consultar = SessaoSistema.tem_permissao("garantia_consultar")
        pode_trocar = SessaoSistema.tem_permissao("garantia_troca")
        if not (pode_consultar or pode_trocar):
            messagebox.showerror("Acesso negado", "Seu cargo nao possui acesso a garantias.")
            return
        self._limpar_conteudo()
        self._titulo(self.conteudo, "Garantias", "Consulte uma venda ou registre uma troca.")
        busca = tk.Frame(self.conteudo, bg=self.BG)
        busca.pack(fill="x", pady=(0, 14))
        termo = ttk.Entry(busca, width=40)
        termo.pack(side="left", padx=(0, 8))
        ttk.Label(busca, text="CPF do cliente ou numero de serie").pack(side="left", padx=(0, 10))
        tabela = self._tabela(self.conteudo,
                              ("Venda", "Produto", "Serie", "CPF", "Data", "Garantia ate", "Status"),
                              (70, 190, 140, 140, 150, 130, 160))
        acoes = tk.Frame(self.conteudo, bg=self.BG)
        acoes.pack(fill="x", pady=12)

        def consultar():
            if not SessaoSistema.tem_permissao("garantia_consultar"):
                messagebox.showerror("Acesso negado", "Seu cargo nao pode consultar garantias.")
                return
            try:
                vendas = VendaRepository.buscar_garantia(termo.get().strip())
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            tabela.delete(*tabela.get_children())
            hoje = datetime.now().date()
            for venda in vendas:
                id_venda, marca, modelo, serie, cpf, data, ate, _ = venda
                vencimento = datetime.strptime(ate, "%Y-%m-%d").date()
                status = "Dentro da garantia" if hoje <= vencimento else "Expirada"
                tabela.insert("", "end", iid=str(id_venda), values=(id_venda, f"{marca} {modelo}", serie,
                              cpf, data, vencimento.strftime("%d/%m/%Y"), status),
                              tags=(str(id_venda),))

        def trocar():
            if not SessaoSistema.tem_permissao("garantia_troca"):
                messagebox.showerror("Acesso negado", "Seu cargo nao pode registrar trocas.")
                return
            selection = tabela.selection()
            if not selection:
                messagebox.showwarning("Selecione uma venda", "Consulte e selecione a venda a trocar.")
                return
            venda_id = int(selection[0])
            try:
                venda_sel = next((v for v in VendaRepository.buscar_garantia(termo.get().strip())
                                  if v[0] == venda_id), None)
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            if not venda_sel:
                messagebox.showerror("Venda nao localizada", "Consulte novamente a garantia.")
                return
            try:
                dt = datetime.strptime(venda_sel[6], "%Y-%m-%d").date()
                if datetime.now().date() > dt and not messagebox.askyesno(
                        "Garantia expirada", "A garantia expirou. Deseja registrar a troca como excecao?"):
                    return
                estoque = BateriaRepository.obter_quantidade_estoque(venda_sel[7])
                if estoque <= 0:
                    messagebox.showerror("Sem estoque", "Nao ha bateria para reposicao.")
                    return
                serie_nova = simpledialog.askstring("Nova bateria", "Numero de serie da bateria de reposicao:")
                if not serie_nova or not serie_nova.strip():
                    return
                defeito = simpledialog.askstring("Defeito", "Descreva o defeito constatado:")
                if not defeito or not defeito.strip():
                    return
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                TrocaRepository.salvar(TrocaGarantia(venda_id, venda_sel[7],
                                          venda_sel[3], defeito.strip(), agora))
                VendaRepository.atualizar_numero_serie(venda_id, serie_nova.strip())
                BateriaRepository.decrementar_estoque(venda_sel[7])
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            messagebox.showinfo("Troca registrada", "A troca em garantia foi registrada.")
            consultar()

        if pode_consultar:
            self._botao(busca, "Consultar", consultar, principal=True).pack(side="left")
        if pode_trocar:
            self._botao(acoes, "Registrar troca da venda selecionada", trocar,
                        principal=True).pack(side="left")
        if pode_consultar:
            self._botao(acoes, "Quantidade de baterias ruins",
                        self._mostrar_total_baterias_ruins).pack(side="left", padx=8)

    def _mostrar_total_baterias_ruins(self):
        if not (SessaoSistema.tem_permissao("garantia_consultar")
                or SessaoSistema.tem_permissao("estoque_consultar")):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode consultar esse total.")
            return
        try:
            carcacas, garantias = TrocaRepository.obter_totais_ruins()
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        messagebox.showinfo("Baterias ruins",
                            f"Carcacas recebidas: {carcacas}\nTrocas em garantia: {garantias}\nTotal: {carcacas + garantias}")

    def _tela_gestao(self):
        if not (SessaoSistema.tem_permissao("area_gerente")
                or SessaoSistema.tem_permissao("relatorios_ver")
                or SessaoSistema.tem_permissao("funcionarios_gerenciar")
                or SessaoSistema.tem_permissao("cargos_gerenciar")):
            messagebox.showerror("Acesso negado", "Seu cargo nao possui acesso a gestao.")
            return
        self._limpar_conteudo()
        self._titulo(self.conteudo, "Gestão", "Relatórios, equipe e configuração de cargos.")
        permissoes = (
            ("relatorios_ver", "Relatorios"),
            ("funcionarios_gerenciar", "Equipe"),
            ("cargos_gerenciar", "Cargos"),
        )
        area = tk.Frame(self.conteudo, bg=self.BG)
        area.pack(fill="x", pady=(0, 16))
        for permissao, rotulo in permissoes:
            if SessaoSistema.tem_permissao(permissao):
                self._botao(area, rotulo, lambda p=permissao: self._mostrar_gestao(p),
                            principal=True).pack(side="left", padx=(0, 8))
        self.gestao_resultado = tk.Frame(self.conteudo, bg=self.BG)
        self.gestao_resultado.pack(fill="both", expand=True)
        if SessaoSistema.tem_permissao("relatorios_ver"):
            self._mostrar_gestao("relatorios_ver")
        elif SessaoSistema.tem_permissao("funcionarios_gerenciar"):
            self._mostrar_gestao("funcionarios_gerenciar")
        elif SessaoSistema.tem_permissao("cargos_gerenciar"):
            self._mostrar_gestao("cargos_gerenciar")
        else:
            tk.Label(self.gestao_resultado,
                     text="Seu cargo acessa a area, mas nao possui permissoes para as operacoes disponiveis.",
                     bg=self.BG, fg=self.MUTED).pack(anchor="w")

    def _mostrar_gestao(self, tipo):
        if not SessaoSistema.tem_permissao(tipo):
            messagebox.showerror("Acesso negado", "Seu cargo nao possui essa permissao.")
            return
        for widget in self.gestao_resultado.winfo_children():
            widget.destroy()
        if tipo == "relatorios_ver":
            try:
                resumo, defeitos = TrocaRepository.obter_dados_relatorio()
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            labels = (("Vendas registradas", resumo[0] or 0),
                      ("Faturamento total", f"R$ {(resumo[1] or 0):.2f}"),
                      ("Carcacas recebidas", resumo[2] or 0),
                      ("Trocas em garantia", len(defeitos)))
            for titulo, valor in labels:
                card = self._frame(self.gestao_resultado)
                card.pack(fill="x", pady=5)
                tk.Label(card, text=titulo, bg=self.PANEL, fg=self.MUTED).pack(
                    anchor="w", padx=16, pady=(12, 0))
                tk.Label(card, text=str(valor), bg=self.PANEL, fg=self.TEXT,
                         font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16, pady=(0, 12))
        elif tipo == "funcionarios_gerenciar":
            acoes = tk.Frame(self.gestao_resultado, bg=self.BG)
            acoes.pack(fill="x", pady=(0, 12))
            self._botao(acoes, "Cadastrar funcionário",
                        self._dialogo_novo_funcionario, principal=True).pack(side="left", padx=(0, 8))
            tabela = self._tabela(self.gestao_resultado,
                                  ("ID", "Matrícula", "Nome", "Cargo", "Nível", "Status"),
                                  (55, 115, 200, 165, 70, 85))
            self.funcionario_tabela = tabela
            try:
                for funcionario in FuncionarioRepository.obter_todos(apenas_ativos=False):
                    tabela.insert(
                        "", "end", iid=str(funcionario.id),
                        values=(funcionario.id, funcionario.matricula, funcionario.nome,
                                funcionario.cargo.nome if funcionario.cargo else "—",
                                funcionario.cargo.nivel if funcionario.cargo else "—",
                                "Ativo" if funcionario.ativo else "Inativo"),
                    )
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            self._botao(acoes, "Editar funcionário",
                        self._editar_funcionario_selecionado).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Excluir / inativar",
                        self._inativar_funcionario_selecionado).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Reativar funcionário",
                        self._reativar_funcionario_selecionado).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Redefinir senha",
                        self._redefinir_senha_funcionario).pack(side="left")
        elif tipo == "cargos_gerenciar":
            acoes = tk.Frame(self.gestao_resultado, bg=self.BG)
            acoes.pack(fill="x", pady=(0, 12))
            self._botao(acoes, "Criar cargo",
                        self._dialogo_novo_cargo, principal=True).pack(side="left", padx=(0, 8))
            tabela = self._tabela(
                self.gestao_resultado,
                ("ID", "Cargo", "Nível hierárquico", "Permissões"),
                (55, 200, 120, 500),
            )
            self.cargo_tabela = tabela
            try:
                for cargo in CargoRepository.obter_todos():
                    tabela.insert("", "end", iid=str(cargo.id),
                                  values=(cargo.id, cargo.nome, cargo.nivel,
                                          ", ".join(cargo.permissoes)))
            except sqlite3.Error as erro:
                messagebox.showerror("Erro no banco de dados", str(erro))
                return
            self._botao(acoes, "Editar cargo",
                        self._editar_cargo_selecionado).pack(side="left", padx=(0, 8))
            self._botao(acoes, "Excluir cargo",
                        self._excluir_cargo_selecionado).pack(side="left")

    def _dialogo_novo_funcionario(self):
        if not SessaoSistema.tem_permissao("funcionarios_gerenciar"):
            messagebox.showerror("Acesso negado", "Seu cargo nao pode cadastrar funcionarios.")
            return
        janela = tk.Toplevel(self)
        janela.title("Cadastrar funcionario")
        janela.configure(bg=self.PANEL)
        janela.transient(self)
        janela.grab_set()
        area = tk.Frame(janela, bg=self.PANEL, padx=24, pady=20)
        area.pack(fill="both", expand=True)
        tk.Label(area, text="Novo funcionario", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        matricula = self._campo(area, "Matrícula")
        nome = self._campo(area, "Nome completo")
        try:
            operador = SessaoSistema.obter_operador()
            cargos = [
                cargo for cargo in CargoRepository.obter_todos()
                if not cargo.tem_permissao("cargos_gerenciar")
                and operador.cargo
                and cargo.nivel <= operador.cargo.nivel
            ]
        except sqlite3.Error as erro:
            janela.destroy()
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        cargo_var = tk.StringVar()
        if not cargos:
            janela.destroy()
            messagebox.showerror(
                "Sem cargos disponíveis",
                "Crie um cargo não proprietário de nível igual ou inferior ao seu."
            )
            return
        tk.Label(area, text="Cargo", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 4))
        combo = ttk.Combobox(area, textvariable=cargo_var, state="readonly",
                             values=tuple(f"{cargo.id} - {cargo.nome}" for cargo in cargos))
        combo.pack(fill="x")

        def salvar():
            if not matricula.get().strip() or not nome.get().strip() or not cargo_var.get():
                messagebox.showwarning("Campos obrigatorios", "Preencha matricula, nome e cargo.", parent=janela)
                return
            cargo_id = int(cargo_var.get().split(" - ", 1)[0])
            try:
                todos_funcionarios = FuncionarioRepository.obter_todos(apenas_ativos=False)
                if any(f.matricula == matricula.get().strip() for f in todos_funcionarios):
                    messagebox.showerror("Matricula existente", "Essa matricula ja esta cadastrada.", parent=janela)
                    return
                cargo = CargoRepository.buscar_por_id(cargo_id)
                operador = SessaoSistema.obter_operador()
                if (not cargo or cargo.tem_permissao("cargos_gerenciar")
                        or not operador.cargo or cargo.nivel > operador.cargo.nivel):
                    messagebox.showerror(
                        "Cargo inválido",
                        "Só é permitido atribuir cargo não proprietário até o seu próprio nível.",
                        parent=janela,
                    )
                    return
                FuncionarioRepository.salvar(Funcionario(matricula.get().strip(),
                                               nome.get().strip(), cargo))
            except (sqlite3.Error, ValueError) as erro:
                messagebox.showerror("Erro no banco de dados", str(erro), parent=janela)
                return
            janela.destroy()
            self._mostrar_gestao("funcionarios_gerenciar")

        self._botao(area, "Salvar funcionario", salvar, principal=True).pack(fill="x", pady=20)

    def _funcionario_selecionado(self):
        if not SessaoSistema.tem_permissao("funcionarios_gerenciar"):
            messagebox.showerror("Acesso negado", "Seu cargo não pode gerenciar funcionários.")
            return None
        selecionado = self.funcionario_tabela.selection()
        if not selecionado:
            messagebox.showwarning("Selecione um funcionário", "Escolha um funcionário na lista.")
            return None
        try:
            funcionario_id = int(selecionado[0])
            return next(
                (funcionario for funcionario in FuncionarioRepository.obter_todos(apenas_ativos=False)
                 if funcionario.id == funcionario_id),
                None,
            )
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Erro ao consultar funcionário", str(erro))
            return None

    def _editar_funcionario_selecionado(self):
        funcionario = self._funcionario_selecionado()
        operador = SessaoSistema.obter_operador()
        if not funcionario:
            return
        if (funcionario.is_administrador_principal() or funcionario.id == operador.id
                or not operador.cargo or not funcionario.cargo
                or operador.cargo.nivel <= funcionario.cargo.nivel):
            messagebox.showerror(
                "Edição bloqueada",
                "Só é possível editar outro funcionário de nível inferior; o dono é protegido."
            )
            return
        janela = tk.Toplevel(self)
        janela.title("Editar funcionário")
        janela.configure(bg=self.PANEL)
        janela.transient(self)
        janela.grab_set()
        area = tk.Frame(janela, bg=self.PANEL, padx=24, pady=20)
        area.pack(fill="both", expand=True)
        tk.Label(area, text="Editar funcionário", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        matricula = self._campo(area, "Matrícula")
        matricula.insert(0, funcionario.matricula)
        nome = self._campo(area, "Nome completo")
        nome.insert(0, funcionario.nome)
        try:
            cargos = [
                cargo for cargo in CargoRepository.obter_todos()
                if not cargo.tem_permissao("cargos_gerenciar")
                and operador.cargo
                and cargo.nivel <= operador.cargo.nivel
            ]
        except sqlite3.Error as erro:
            janela.destroy()
            messagebox.showerror("Erro no banco de dados", str(erro))
            return
        cargo_var = tk.StringVar()
        tk.Label(area, text="Cargo", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 4))
        opcoes = tuple(f"{cargo.id} - {cargo.nome}" for cargo in cargos)
        combo = ttk.Combobox(area, textvariable=cargo_var, state="readonly", values=opcoes)
        combo.pack(fill="x")
        cargo_atual = next((cargo for cargo in cargos if cargo.id == funcionario.cargo.id), None)
        if cargo_atual:
            cargo_var.set(f"{cargo_atual.id} - {cargo_atual.nome}")

        def salvar():
            if not matricula.get().strip() or not nome.get().strip() or not cargo_var.get():
                messagebox.showwarning("Campos obrigatórios", "Preencha matrícula, nome e cargo.", parent=janela)
                return
            cargo_id = int(cargo_var.get().split(" - ", 1)[0])
            try:
                FuncionarioRepository.atualizar(
                    funcionario.id, matricula.get().strip(), nome.get().strip(), cargo_id
                )
            except (sqlite3.Error, ValueError) as erro:
                messagebox.showerror("Não foi possível atualizar", str(erro), parent=janela)
                return
            janela.destroy()
            self._mostrar_gestao("funcionarios_gerenciar")

        self._botao(area, "Salvar alterações", salvar, principal=True).pack(fill="x", pady=20)

    def _inativar_funcionario_selecionado(self):
        funcionario = self._funcionario_selecionado()
        operador = SessaoSistema.obter_operador()
        if not funcionario:
            return
        if (funcionario.id == operador.id or funcionario.is_administrador_principal()
                or not operador.cargo or not funcionario.cargo
                or operador.cargo.nivel <= funcionario.cargo.nivel):
            messagebox.showerror(
                "Exclusão bloqueada",
                "Só é possível inativar outro funcionário de nível inferior; o dono é protegido."
            )
            return
        if not messagebox.askyesno(
                "Inativar funcionário",
                f"Desativar {funcionario.nome} ({funcionario.matricula})?\n"
                "O cadastro será preservado para manter o histórico."):
            return
        try:
            FuncionarioRepository.desativar(funcionario.id)
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Não foi possível excluir", str(erro))
            return
        messagebox.showinfo("Funcionário inativado", "O funcionário não poderá mais entrar no sistema.")
        self._mostrar_gestao("funcionarios_gerenciar")

    def _redefinir_senha_funcionario(self):
        funcionario = self._funcionario_selecionado()
        if not funcionario:
            return
        if not funcionario.ativo:
            messagebox.showwarning(
                "Funcionário inativo",
                "Não é possível redefinir a senha de um funcionário inativo."
            )
            return
        if not self._verificar_autorizacao_superior(funcionario):
            return
        credencial = self._dialogo_nova_senha()
        if credencial is None:
            return
        try:
            FuncionarioRepository.definir_credencial(funcionario.id, *credencial)
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Não foi possível redefinir a senha", str(erro))
            return
        messagebox.showinfo("Senha redefinida", "A nova senha foi cadastrada.")

    def _reativar_funcionario_selecionado(self):
        funcionario = self._funcionario_selecionado()
        operador = SessaoSistema.obter_operador()
        if not funcionario:
            return
        if (funcionario.id == operador.id or funcionario.is_administrador_principal()
                or not operador.cargo or not funcionario.cargo
                or operador.cargo.nivel <= funcionario.cargo.nivel):
            messagebox.showerror(
                "Reativação bloqueada",
                "Só é possível reativar outro funcionário de nível inferior."
            )
            return
        if not messagebox.askyesno(
                "Reativar funcionário",
                f"Reativar {funcionario.nome} ({funcionario.matricula})?"):
            return
        try:
            FuncionarioRepository.reativar(funcionario.id)
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Não foi possível reativar", str(erro))
            return
        self._mostrar_gestao("funcionarios_gerenciar")

    def _cargo_selecionado(self):
        if not SessaoSistema.is_administrador_principal():
            messagebox.showerror("Acesso restrito", "Somente o dono pode gerenciar cargos.")
            return None
        selecionado = self.cargo_tabela.selection()
        if not selecionado:
            messagebox.showwarning("Selecione um cargo", "Escolha um cargo na lista.")
            return None
        try:
            cargo = CargoRepository.buscar_por_id(int(selecionado[0]))
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Erro ao consultar cargo", str(erro))
            return None
        if cargo and cargo.tem_permissao("cargos_gerenciar"):
            messagebox.showerror("Cargo protegido", "O cargo do dono não pode ser alterado ou excluído.")
            return None
        return cargo

    def _editar_cargo_selecionado(self):
        cargo = self._cargo_selecionado()
        if cargo:
            self._dialogo_novo_cargo(cargo)

    def _excluir_cargo_selecionado(self):
        cargo = self._cargo_selecionado()
        if not cargo:
            return
        if not messagebox.askyesno("Excluir cargo", f"Excluir o cargo '{cargo.nome}'?"):
            return
        try:
            CargoRepository.excluir(cargo.id)
        except (sqlite3.Error, ValueError) as erro:
            messagebox.showerror("Não foi possível excluir", str(erro))
            return
        messagebox.showinfo("Cargo excluído", f"O cargo '{cargo.nome}' foi removido.")
        self._mostrar_gestao("cargos_gerenciar")

    def _dialogo_novo_cargo(self, cargo_existente=None):
        if not SessaoSistema.is_administrador_principal():
            messagebox.showerror("Acesso restrito", "Somente o dono pode criar ou editar cargos.")
            return
        janela = tk.Toplevel(self)
        editando = cargo_existente is not None
        janela.title("Editar cargo" if editando else "Criar cargo")
        janela.configure(bg=self.PANEL)
        janela.transient(self)
        janela.grab_set()
        janela.geometry("660x720")
        area = tk.Frame(janela, bg=self.PANEL, padx=24, pady=18)
        area.pack(fill="both", expand=True)
        tk.Label(area, text="Editar cargo" if editando else "Criar novo cargo",
                 bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        nome = self._campo(area, "Nome do cargo")
        if cargo_existente:
            nome.insert(0, cargo_existente.nome)
        nivel = self._campo(area, "Nível hierárquico (1 a 999999)")
        if cargo_existente:
            nivel.insert(0, str(cargo_existente.nivel))
        canvas = tk.Canvas(area, bg=self.PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
        lista = tk.Frame(canvas, bg=self.PANEL)
        lista.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=lista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, height=390)
        permissoes = {}
        for codigo, descricao in TODAS_PERMISSOES:
            if codigo == "cargos_gerenciar":
                continue
            var = tk.BooleanVar(
                value=bool(cargo_existente and codigo in cargo_existente.permissoes)
            )
            permissoes[codigo] = var
            tk.Checkbutton(lista, text=descricao, variable=var, bg=self.PANEL,
                           fg=self.TEXT, activebackground=self.PANEL,
                           anchor="w", justify="left").pack(fill="x", pady=2)
        canvas.pack(side="left", fill="both", expand=True, pady=12)
        scrollbar.pack(side="right", fill="y", pady=12)

        def salvar():
            nome_cargo = nome.get().strip()
            try:
                nivel_cargo = int(nivel.get().strip())
            except ValueError:
                messagebox.showwarning(
                    "Nível inválido", "Informe um número inteiro entre 1 e 999999.", parent=janela
                )
                return
            if not nome_cargo or not 1 <= nivel_cargo < 1_000_000:
                messagebox.showwarning(
                    "Dados inválidos", "Informe um nome e nível entre 1 e 999999.", parent=janela
                )
                return
            selecionadas = [codigo for codigo, var in permissoes.items() if var.get()]
            try:
                cargo_com_nome = CargoRepository.buscar_por_nome(nome_cargo)
                if cargo_com_nome and cargo_com_nome.id != (
                        cargo_existente.id if cargo_existente else None):
                    messagebox.showerror("Cargo existente", "Ja existe um cargo com esse nome.", parent=janela)
                    return
                if cargo_existente:
                    CargoRepository.atualizar(cargo_existente.id, nome_cargo,
                                              selecionadas, nivel_cargo)
                else:
                    CargoRepository.salvar(Cargo(nome=nome_cargo,
                                                 permissoes=selecionadas,
                                                 nivel=nivel_cargo))
            except (sqlite3.Error, ValueError) as erro:
                messagebox.showerror("Erro no banco de dados", str(erro), parent=janela)
                return
            janela.destroy()
            self._mostrar_gestao("cargos_gerenciar")

        self._botao(
            area, "Salvar alterações" if editando else "Salvar cargo",
            salvar, principal=True
        ).pack(fill="x", pady=(4, 0))


def iniciar_interface():
    """Prepara o banco e inicia a interface desktop."""
    conexao = conectar_bd()
    conexao.close()
    app = DesktopApp()
    app.mainloop()
