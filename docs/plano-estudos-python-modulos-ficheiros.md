# Plano de estudos: módulos e manipulação de arquivos em Python

**Ponto de partida:** POO dominada (herança, encapsulamento, abstração, polimorfismo).
**Duração:** 4 semanas, cerca de 1h por dia. Pode ser comprimido se avançares mais rápido.
**Projeto-guia:** o `sistema/` com `models`, `services`, `repositories` e `utils`.

```
sistema/
├── main.py
├── models/         produto.py, cliente.py, pedido.py
├── services/       pagamento.py, notificacao.py
├── repositories/   produto_repository.py
└── utils/          formatacao.py
```

**Regra de dependência a respeitar (evita imports circulares):**
`utils` ← `models` ← `repositories` ← `services` ← `main.py`
Cada camada só importa das que estão à esquerda dela.

---

## Semana 1: Módulos e pacotes

**O que estudar**
- Diferença entre módulo (um `.py`) e pacote (pasta com `__init__.py`)
- `import x`, `from x import y`, `import x as z`
- Imports absolutos vs relativos (`from models.produto import Produto` vs `from .produto import Produto`)
- `if __name__ == "__main__":` e porque `main.py` é o ponto de entrada
- Como o Python encontra módulos: `sys.path`, e porque correr com `python -m` resolve muitos erros de import
- `__init__.py` para expor uma API limpa do pacote (`__all__`)
- Imports circulares: porque acontecem e como os evitar

**Prática**
1. Criar toda a estrutura de pastas e ficheiros vazios, com `__init__.py` em cada pasta.
2. Escrever `utils/formatacao.py` com `formatar_kwanza(valor)` e `formatar_data(data)`.
3. Escrever uma classe simples em `models/produto.py` e importá-la em `main.py`.
4. Provocar de propósito um import circular entre dois módulos, ler o erro e corrigir.

**Checkpoint:** consigo correr `python main.py` a partir da raiz, com imports de 3 pacotes diferentes, sem erros.

---

## Semana 2: Ficheiros de texto, caminhos e erros

**O que estudar**
- `pathlib.Path` (preferir sobre `os.path`): `exists()`, `mkdir(parents=True, exist_ok=True)`, `read_text()`, `write_text()`, `iterdir()`, `glob()`
- `open()` e modos: `r`, `w`, `a`, `x`, `rb`, `wb`
- Context manager `with open(...)` e porque é obrigatório
- `encoding="utf-8"` sempre explícito (importante para acentos em português)
- Ler linha a linha vs ler tudo de uma vez
- Exceções de ficheiros: `FileNotFoundError`, `PermissionError`, `IsADirectoryError`
- Caminho relativo à localização do script: `Path(__file__).resolve().parent`

**Prática**
1. Criar uma pasta `data/` na raiz do projeto, usando `pathlib`.
2. Escrever em `utils/` uma função `ler_linhas(caminho)` e outra `anexar_linha(caminho, texto)`.
3. Criar um log simples em ficheiro de texto (cada ação do sistema acrescenta uma linha com data e hora).
4. Tratar o caso de o ficheiro não existir (criar vazio vs avisar).

**Checkpoint:** o script funciona igual quando corrido de qualquer pasta (sem depender do diretório atual).

---

## Semana 3: JSON, CSV e persistência de objetos

**O que estudar**
- Módulo `json`: `dump`, `load`, `dumps`, `loads`, `indent`, `ensure_ascii=False`
- Módulo `csv`: `DictReader`, `DictWriter`, `newline=""`
- Serializar objetos: métodos `to_dict()` e `from_dict()` nos models
- `dataclasses` e `asdict()` como alternativa
- Tipos que o JSON não suporta (`datetime`, `Decimal`) e como converter
- Escrita segura: gravar num ficheiro temporário e depois renomear, para não corromper dados se o programa falhar a meio
- `JSONDecodeError`: ficheiro vazio ou corrompido

**Prática**
1. Adicionar `to_dict()` / `from_dict()` a `Produto`, `Cliente` e `Pedido`.
2. Implementar `repositories/produto_repository.py` com CRUD completo guardando em `data/produtos.json`:
   - `adicionar(produto)`, `listar()`, `buscar_por_id(id)`, `atualizar(produto)`, `remover(id)`
3. Adicionar `exportar_csv()` e `importar_csv()` ao repositório.
4. Tratar ficheiro inexistente, vazio ou com JSON inválido.

**Checkpoint:** fecho o programa, abro de novo, e os produtos continuam lá.

---

## Semana 4: Integração, testes e qualidade

**O que estudar**
- Ligar as camadas: `Pedido` usa `Cliente` e `Produto`; `services` recebem o repositório como argumento (injeção de dependência simples)
- `logging` com `FileHandler`, no lugar de um log manual
- Configuração em ficheiro (`config.json`) ou variáveis de ambiente
- `pytest` e a fixture `tmp_path` para testar ficheiros sem sujar o projeto
- Type hints (`list[Produto]`, `Path`, `Optional`)
- Ambiente virtual (`venv`) e `requirements.txt`
- Opcional: `sqlite3` como próximo passo natural depois de JSON

**Prática**
1. `services/pagamento.py`: processar um pedido e atualizar o stock via repositório.
2. `services/notificacao.py`: registar a notificação em ficheiro de log.
3. `main.py`: fluxo completo (criar cliente, escolher produtos, criar pedido, pagar, notificar).
4. Escrever testes para o `ProdutoRepository` usando `tmp_path`.

**Checkpoint (projeto final):** o fluxo completo corre, os dados persistem entre execuções, e os testes do repositório passam.

---

## Resumo semanal

| Semana | Tema | Entrega |
|---|---|---|
| 1 | Módulos e pacotes | Estrutura criada, imports a funcionar, `formatacao.py` |
| 2 | Ficheiros de texto e `pathlib` | Log em ficheiro, funções de leitura e escrita |
| 3 | JSON e CSV | `ProdutoRepository` com CRUD persistente |
| 4 | Integração e testes | Sistema completo e testes com `pytest` |

## Referências

- Tutorial oficial, secção Modules: https://docs.python.org/3/tutorial/modules.html
- Tutorial oficial, secção Input and Output: https://docs.python.org/3/tutorial/inputoutput.html
- Documentação do `pathlib`: https://docs.python.org/3/library/pathlib.html
- Documentação do `json`: https://docs.python.org/3/library/json.html
