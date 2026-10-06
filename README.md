# Sistema de Gestão para Loja de Baterias

Aplicação desktop para apoiar as operações de uma loja de baterias. O sistema oferece ponto de venda, controle de estoque, cadastro de clientes, consulta de vendas e gestão de garantias, com acesso às funções definido pelas permissões do cargo.

Feito para disciplina:
Introdução a Engenharia de Software: 
Ministrada pela: Universidade do Estado do Rio de Janeiro e pelo professor 
Dener Santos
Realizado pelos alunos:
- Javier Blanco Rodrigues Cadima Matrícula 202410330911
- Antonio Walace Marins Vigant Matrícula 202310053311

## Funcionalidades

- Realização e consulta de vendas.
- Cadastro de baterias, reposição de estoque e atualização de preços.
- Cadastro e consulta de clientes.
- Consulta e processamento de trocas em garantia.
- Relatórios e área de gestão conforme as permissões do operador.
- Gestão de funcionários e cargos, incluindo edição e controle de permissões.
- Hierarquia de cargos definida pelo administrador principal.
- Login de funcionários por matrícula e senha, com cadastro de senha no primeiro acesso.
- Redefinição de senha autorizada por um funcionário de cargo superior.

## Requisitos

- Python 3 instalado.
- Tkinter disponível na instalação do Python para abrir a interface gráfica.
- SQLite disponível na instalação do Python.

### Bibliotecas utilizadas

O projeto utiliza somente bibliotecas da biblioteca padrão do Python; não há dependências externas para instalar com `pip`.

| Biblioteca | Utilização |
| --- | --- |
| `tkinter` e `tkinter.ttk` | Interface gráfica desktop. |
| `sqlite3` | Banco de dados SQLite. |
| `hashlib`, `hmac` e `secrets` | Geração e verificação segura de senhas. |
| `json` | Leitura e gravação de permissões dos cargos. |
| `datetime` e `time` | Datas, horários e prazos de garantia. |
| `getpass` | Entrada oculta de senha no modo terminal. |
| `os`, `math`, `random`, `re` e `sys` | Operações auxiliares do sistema. |

No Windows, instale o Python pelo instalador oficial e habilite o Tcl/Tk se essa opção for exibida. No Linux, talvez seja necessário instalar o suporte ao Tkinter pelo gerenciador de pacotes da distribuição (por exemplo, `sudo apt install python3-tk` no Ubuntu/Debian). O modo terminal não precisa do Tkinter.

Não é necessário executar `pip install` para iniciar o projeto.

## Como executar

Abra um terminal na pasta do projeto — a mesma pasta onde está `main.py` — e execute:

```bash
python main.py
```

Esse comando abre a interface gráfica. Para usar a interface de terminal:

```bash
python main.py --terminal
```

Em algumas instalações do Windows, o comando para iniciar Python é `py` em vez de `python`; nesse caso, use `py main.py` ou `py main.py --terminal`.

## Primeiro acesso

Na primeira execução, o sistema cria o banco de dados SQLite e os cargos e funcionários iniciais, caso ainda não existam:

| Matrícula | Perfil |
| --- | --- |
| `1001` | Administrador principal |
| `2001` | Fiscal / gerente |
| `3001` | Vendedor |

O administrador principal entra sem senha. Os demais funcionários definem uma senha no primeiro acesso; senhas consideradas fracas são recusadas. Depois disso, a senha será solicitada nos próximos logins.

> **Importante:** no primeiro acesso, a matrícula é suficiente para iniciar o cadastro da senha. Compartilhe as matrículas iniciais somente com os funcionários correspondentes e, após entrar como administrador principal, revise os acessos iniciais. Uma etapa de ativação com código entregue ao funcionário é recomendável antes de usar o sistema em um ambiente real.

## Banco de dados

Os dados são armazenados no arquivo `loja_baterias.db`, criado na pasta de trabalho ao iniciar o aplicativo. Para manter o banco esperado, execute os comandos a partir da pasta do projeto. Faça cópias de segurança regulares desse arquivo; não o substitua enquanto o sistema estiver em uso.

## Estrutura do projeto

| Caminho | Responsabilidade |
| --- | --- |
| `main.py` | Ponto de entrada e seleção entre interface gráfica e terminal. |
| `desktop_app.py` | Interface gráfica desktop e navegação por permissões. |
| `database/` | Conexão, criação e migração do banco SQLite. |
| `models/` | Modelos das entidades do sistema. |
| `repositories/` | Persistência e consultas ao banco de dados. |
| `views/` | Fluxos da interface de terminal. |
| `utils/` | Funções utilitárias, incluindo segurança de senha e criptografia de dados. |

## Observações

- A exclusão de um funcionário é lógica: o cadastro é inativado para preservar o histórico e pode ser reativado.
- Um cargo não pode ser excluído enquanto estiver associado a funcionários; primeiro altere os cargos desses funcionários.
- As opções disponíveis variam de acordo com as permissões do cargo do operador.
