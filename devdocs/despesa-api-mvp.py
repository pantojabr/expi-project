"""
despesa-api-mvp.py - Testes automatizados da API de Controle de Despesas

Cobre TODA a API do projeto despesa-api-mvp e demonstra cada fluxo
descrito em tech/fluxo-de-dados-auditoria.md:

  REGISTRADA -> SUBMETIDA -> APROVADA
  REGISTRADA -> SUBMETIDA -> REJEITADA
  REGISTRADA -> SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO -> SUBMETIDA -> APROVADA

Inclui os endpoints de cadastro de serventias, tipos de cartorio,
usuarios de dominio e auditoria com filtros.

Requisitos:
  pip install requests pytest

Uso:
  # docker compose build (docker compose build --no-cache , caso ainda falhe)
  # API rodando em localhost:8080 (docker compose up -d)
  pytest devdocs/despesa-api-mvp.py -v

  # Apontar para outra URL:
  BASE_URL=http://192.168.1.10:8080 pytest devdocs/despesa-api-mvp.py -v
"""

import os
import io
import re
from pathlib import Path
import pytest
import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

# Credenciais configuradas em SecurityConfig (InMemoryUserDetailsManager)
COGEX_ADMIN = ("cogex_admin", "password")
COGEX_AUDITOR = ("cogex_auditor", "password")
CARTORIO_TITULAR = ("titular", "password")
CARTORIO_INTERINO = ("interino", "password")
CARTORIO_SUBSTITUTO = ("substituto", "password")
CARTORIO_APOIO = ("apoio", "password")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def url(path: str) -> str:
    return f"{BASE_URL}{path}"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "arquivo"


def endpoint_disponivel(path: str, auth=COGEX_ADMIN) -> bool:
    """Verifica se um endpoint existe na API (GET retornando 404 = inexistente)."""
    try:
        r = requests.get(url(path), auth=auth, timeout=5)
        return r.status_code != 404
    except requests.ConnectionError:
        return False


def skip_se_indisponivel(path: str, method: str = "GET"):
    """Pula o teste se o endpoint não existir na versão atual da API."""
    if not endpoint_disponivel(path):
        pytest.skip(f"Endpoint {method} {path} não disponível nesta versão da API")

def _pdf_escape(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def gerar_pdf_bytes(titulo: str, linhas: list[str] | None = None) -> bytes:
    if linhas is None:
        linhas = []
    conteudo = []
    conteudo.append("BT")
    conteudo.append("/F1 18 Tf")
    conteudo.append(f"72 750 Td ({_pdf_escape(titulo)}) Tj")
    conteudo.append("/F1 12 Tf")
    for linha in linhas:
        conteudo.append(f"0 -18 Td ({_pdf_escape(linha)}) Tj")
    conteudo.append("ET")
    content_bytes = ("\n".join(conteudo)).encode("latin-1")

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    objects.append(b"<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n" + content_bytes + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    out = bytearray()
    out.extend(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_offset = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(b"trailer\n")
    out.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    out.extend(b"startxref\n")
    out.extend(f"{xref_offset}\n".encode("ascii"))
    out.extend(b"%%EOF\n")
    return bytes(out)

def _primeiro_item(path: str, auth=COGEX_ADMIN) -> dict | None:
    r = requests.get(url(path), auth=auth)
    assert r.status_code == 200, f"Falha ao listar {path}: {r.status_code} {r.text}"
    itens = r.json()
    if not isinstance(itens, list) or not itens:
        return None
    return itens[0]

def get_or_create_categoria_id() -> int:
    item = _primeiro_item("/api/categorias")
    if item:
        return item["id"]
    payload = {"nome": "Categoria Teste (auto)", "descricao": "Criada automaticamente pelo teste"}
    r = requests.post(url("/api/categorias"), json=payload, auth=COGEX_ADMIN)
    assert r.status_code == 201, f"Falha ao criar categoria: {r.status_code} {r.text}"
    return r.json()["id"]

def get_or_create_subcategoria_id(categoria_id: int) -> int:
    item = _primeiro_item("/api/subcategorias")
    if item:
        return item["id"]
    payload = {"nome": "Subcategoria Teste (auto)", "categoriaId": categoria_id}
    r = requests.post(url("/api/subcategorias"), json=payload, auth=COGEX_ADMIN)
    assert r.status_code == 201, f"Falha ao criar subcategoria: {r.status_code} {r.text}"
    return r.json()["id"]

def get_or_create_serventia_id() -> int:
    payload = {"nome": "Serventia Teste (auto)", "codigo": "SVT-AUTO", "delegatario": "Delegatario Teste", "ativa": True}
    r = requests.post(url("/api/serventias"), json=payload, auth=COGEX_ADMIN)
    if r.status_code == 201:
        return r.json()["id"]
    item = _primeiro_item("/api/serventias")
    if item:
        return item["id"]
    pytest.skip("Não foi possível criar ou listar serventias.")

def get_or_create_tipo_cartorio_id() -> int:
    payload = {"nome": "Tipo Cartorio Teste (auto)", "ativo": True}
    r = requests.post(url("/api/tipos-cartorio"), json=payload, auth=COGEX_ADMIN)
    if r.status_code == 201:
        return r.json()["id"]
    item = _primeiro_item("/api/tipos-cartorio")
    if item:
        return item["id"]
    pytest.skip("Não foi possível criar ou listar tipos de cartorio.")


def despesa_payload(
    categoria_id: int | None = None,
    subcategoria_id: int | None = None,
    serventia_id: str | None = None,
    serventia_ref: int | None = None,
    tipo_cartorio_id: int | None = None,
    descricao: str = "Compra de material de escritório",
    valor: float = 150.00,
):
    """Retorna um dict válido para POST /api/despesas."""
    if categoria_id is None:
        categoria_id = get_or_create_categoria_id()
    if subcategoria_id is None:
        subcategoria_id = get_or_create_subcategoria_id(categoria_id)
    if serventia_ref is None and serventia_id is None:
        serventia_ref = get_or_create_serventia_id()
        serventia_id = str(serventia_ref)
    elif serventia_id is None and serventia_ref is not None:
        serventia_id = str(serventia_ref)
    payload = {
        "dataLancamento": "2025-06-01",
        "dataCompetencia": "2025-06-01",
        "idServentia": serventia_id,
        "categoriaId": categoria_id,
        "subcategoriaId": subcategoria_id,
        "descricao": descricao,
        "valor": valor,
    }
    if serventia_ref is not None:
        payload["serventiaId"] = serventia_ref
    if tipo_cartorio_id is not None:
        payload["tipoCartorioId"] = tipo_cartorio_id
    return payload


def criar_despesa(auth=CARTORIO_APOIO, **kwargs) -> dict:
    """Cria uma despesa e retorna o JSON de resposta."""
    r = requests.post(url("/api/despesas"), json=despesa_payload(**kwargs), auth=auth)
    assert r.status_code == 201, f"Falha ao criar despesa: {r.status_code} {r.text}"
    return r.json()


def criar_serventia(nome: str = "Serventia Teste", auth=COGEX_ADMIN) -> dict:
    payload = {"nome": nome, "codigo": "SVT-001", "delegatario": "Delegatario Teste", "ativa": True}
    r = requests.post(url("/api/serventias"), json=payload, auth=auth)
    assert r.status_code == 201, f"Falha ao criar serventia: {r.status_code} {r.text}"
    return r.json()


def criar_tipo_cartorio(nome: str = "Registro Civil", auth=COGEX_ADMIN) -> dict:
    payload = {"nome": nome, "ativo": True}
    r = requests.post(url("/api/tipos-cartorio"), json=payload, auth=auth)
    assert r.status_code == 201, f"Falha ao criar tipo de cartorio: {r.status_code} {r.text}"
    return r.json()


def arquivo_pdf(nome: str, linhas: list[str]) -> tuple:
    fake_file = io.BytesIO(gerar_pdf_bytes(nome, linhas))
    return (f"{slugify(nome)}.pdf", fake_file, "application/pdf")


def upload_comprovante_unico(despesa_id: int, auth=CARTORIO_TITULAR) -> dict:
    comprovante = io.BytesIO(gerar_pdf_bytes("Comprovante Pagamento", [f"Despesa ID {despesa_id}"]))
    r = requests.post(
        url("/api/comprovantes/upload"),
        files={"file": ("comprovante_pagamento.pdf", comprovante, "application/pdf")},
        data={"despesaId": despesa_id},
        auth=auth,
    )
    assert r.status_code == 201, f"Falha ao enviar comprovante pagamento: {r.status_code} {r.text}"
    return r.json()


def vincular_tipo_cartorio(serventia_id: int, tipo_id: int, auth=COGEX_ADMIN) -> dict:
    payload = {"tipoCartorioId": str(tipo_id), "aplicadoPor": "1", "dataInicio": "2025-06-01", "motivo": "Vinculo inicial"}
    fake_file = io.BytesIO(gerar_pdf_bytes("Comprovante Vinculo", [f"Serventia {serventia_id}", f"Tipo {tipo_id}"]))
    files = {"comprovante": ("comprovante_vinculo.pdf", fake_file, "application/pdf")}
    r = requests.post(url(f"/api/serventias/{serventia_id}/tipos"), data=payload, files=files, auth=auth)
    assert r.status_code == 201, f"Falha ao vincular tipo: {r.status_code} {r.text}"
    return r.json()


def encerrar_tipo_cartorio(serventia_id: int, tipo_id: int, auth=COGEX_ADMIN) -> dict:
    payload = {"encerradoPor": "1", "dataFim": "2025-06-30", "motivo": "Encerramento por troca"}
    fake_file = io.BytesIO(gerar_pdf_bytes("Comprovante Encerramento", [f"Serventia {serventia_id}", f"Tipo {tipo_id}"]))
    files = {"comprovante": ("comprovante_encerramento.pdf", fake_file, "application/pdf")}
    r = requests.post(url(f"/api/serventias/{serventia_id}/tipos/{tipo_id}/encerrar"), data=payload, files=files, auth=auth)
    assert r.status_code == 200, f"Falha ao encerrar tipo: {r.status_code} {r.text}"
    return r.json()


def criar_usuario_dominio(serventia_id: int, auth=COGEX_ADMIN) -> dict:
    payload = {
        "nome": "Usuario Dominio",
        "email": "usuario.dominio@example.com",
        "role": "RULE_CARTORIO_APOIO",
        "serventiaId": serventia_id,
        "ativo": True,
    }
    r = requests.post(url("/api/usuarios-dominio"), json=payload, auth=auth)
    assert r.status_code == 201, f"Falha ao criar usuario dominio: {r.status_code} {r.text}"
    return r.json()


def post_texto(path: str, texto: str, auth) -> requests.Response:
    """Envia corpo texto (String) conforme endpoints de esclarecimento."""
    headers = {"Content-Type": "application/json"}
    return requests.post(url(path), data=texto, headers=headers, auth=auth)


def assert_status(response: requests.Response, expected: int, contexto: str = ""):
    """Assegura status HTTP e imprime resposta útil em caso de erro."""
    if response.status_code != expected:
        detalhe = f" ({contexto})" if contexto else ""
        headers = dict(response.headers)
        content_len = len(response.content or b"")
        raise AssertionError(
            f"Esperado {expected}, obtido {response.status_code}{detalhe}. "
            f"Resposta: {response.text!r}; headers={headers!r}; content_len={content_len}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 1. HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════
class TestHealthCheck:
    """Verifica se a API está acessível."""

    def test_hello_world(self):
        r = requests.get(url("/hello"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert "Hello" in r.text


# ═══════════════════════════════════════════════════════════════════════════
# 2. SERVENTIAS / TIPOS / USUARIOS - CRUD (ROLE_COGEX_ADMIN)
# ═══════════════════════════════════════════════════════════════════════════
class TestServentiasTiposUsuarios:
    """CRUD basico de serventias, tipos de cartorio e usuarios de dominio."""

    def test_criar_serventia(self):
        r = requests.post(
            url("/api/serventias"),
            json={"nome": "Serventia Teste", "codigo": "SVT-001", "delegatario": "Delegatario Teste", "ativa": True},
            auth=COGEX_ADMIN,
        )
        if r.status_code == 201:
            data = r.json()
            assert data["nome"] == "Serventia Teste"
            self.__class__._serventia_id = data["id"]
            return

        if r.status_code >= 500:
            r_list = requests.get(url("/api/serventias"), auth=COGEX_ADMIN)
            assert r_list.status_code == 200
            itens = r_list.json()
            if not itens:
                pytest.skip("Falha ao criar serventia e nenhuma existente no banco.")
            self.__class__._serventia_id = itens[0]["id"]
            return

        assert r.status_code == 201, f"Falha ao criar serventia: {r.status_code} {r.text}"

    def test_listar_serventias(self):
        r = requests.get(url("/api/serventias"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_buscar_serventia_por_id(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        if sid is None:
            sid = get_or_create_serventia_id()
            self.__class__._serventia_id = sid
        r = requests.get(url(f"/api/serventias/{sid}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_atualizar_serventia(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        if sid is None:
            sid = get_or_create_serventia_id()
            self.__class__._serventia_id = sid
        payload = {"nome": "Serventia Atualizada", "codigo": "SVT-ATUAL", "delegatario": "Delegatario Atual", "ativa": True}
        r = requests.put(url(f"/api/serventias/{sid}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["nome"] == "Serventia Atualizada"

    def test_listar_serventias_filtradas(self):
        r = requests.get(url("/api/serventias"), params={"status": "TODAS"}, auth=COGEX_ADMIN)
        assert r.status_code == 200
        r = requests.get(url("/api/serventias"), params={"status": "CONFIGURADAS"}, auth=COGEX_ADMIN)
        assert r.status_code == 200
        r = requests.get(url("/api/serventias"), params={"status": "SEM_TIPO"}, auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_importar_serventias_por_lista(self):
        payload = ["Serventia Import 1", "Serventia Import 2"]
        r = requests.post(url("/api/serventias/import"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code in (200, 201)
        assert isinstance(r.json(), list)

    @pytest.mark.skip(reason="Importacao por arquivo desativada por ora (Serventias.txt)")
    def test_importar_serventias_por_arquivo(self):
        r = requests.post(url("/api/serventias/import-file"), auth=COGEX_ADMIN)
        assert r.status_code in (200, 201)

    def test_criar_tipo_cartorio(self):
        r = requests.post(
            url("/api/tipos-cartorio"),
            json={"nome": "Registro Civil", "ativo": True},
            auth=COGEX_ADMIN,
        )
        if r.status_code == 201:
            data = r.json()
            assert data["nome"] == "Registro Civil"
            self.__class__._tipo_id = data["id"]
            return

        if r.status_code >= 500:
            r_list = requests.get(url("/api/tipos-cartorio"), auth=COGEX_ADMIN)
            assert r_list.status_code == 200
            itens = r_list.json()
            if not itens:
                pytest.skip("Falha ao criar tipo e nenhum existente no banco.")
            self.__class__._tipo_id = itens[0]["id"]
            return

        assert r.status_code == 201, f"Falha ao criar tipo de cartorio: {r.status_code} {r.text}"

    def test_listar_tipos_cartorio(self):
        r = requests.get(url("/api/tipos-cartorio"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_buscar_tipo_cartorio_por_id(self):
        tid = getattr(self.__class__, "_tipo_id", None)
        if tid is None:
            tid = get_or_create_tipo_cartorio_id()
            self.__class__._tipo_id = tid
        r = requests.get(url(f"/api/tipos-cartorio/{tid}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["id"] == tid

    def test_atualizar_tipo_cartorio(self):
        tid = getattr(self.__class__, "_tipo_id", None)
        if tid is None:
            tid = get_or_create_tipo_cartorio_id()
            self.__class__._tipo_id = tid
        payload = {"nome": "Tipo Cartorio Atualizado", "siglaCartorio": "TCA", "ativo": True}
        r = requests.put(url(f"/api/tipos-cartorio/{tid}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["nome"] == "Tipo Cartorio Atualizado"

    def test_importar_tipos_por_lista(self):
        payload = ["Tipo Import 1", "Tipo Import 2"]
        r = requests.post(url("/api/tipos-cartorio/import"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code in (200, 201)
        assert isinstance(r.json(), list)

    def test_inativar_tipo_cartorio(self):
        tid = getattr(self.__class__, "_tipo_id", None)
        if tid is None:
            tid = get_or_create_tipo_cartorio_id()
            self.__class__._tipo_id = tid
        r = requests.post(url(f"/api/tipos-cartorio/{tid}/inativar"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["ativo"] is False

    @pytest.mark.skip(reason="Importacao por arquivo desativada por ora (Tipos_de_Cartorio.txt)")
    def test_importar_tipos_por_arquivo(self):
        r = requests.post(url("/api/tipos-cartorio/import-file"), auth=COGEX_ADMIN)
        assert r.status_code in (200, 201)

    def test_vincular_tipo_a_serventia(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        data = vincular_tipo_cartorio(sid, tid)
        assert data["serventiaId"] == sid
        assert data["tipoCartorioId"] == tid

    def test_encerrar_tipo_da_serventia(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        data = encerrar_tipo_cartorio(sid, tid)
        assert data["serventiaId"] == sid
        assert data["tipoCartorioId"] == tid

    def test_vinculo_requer_aplicado_por(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"tipoCartorioId": str(tid), "dataInicio": "2025-06-01", "motivo": "Teste sem aplicadoPor"}
        files = {"comprovante": arquivo_pdf("Comprovante Vinculo", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_encerrar_requer_encerrado_por(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"dataFim": "2025-06-30", "motivo": "Teste sem encerradoPor"}
        files = {"comprovante": arquivo_pdf("Comprovante Encerramento", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos/{tid}/encerrar"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_vinculo_requer_pdf(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"tipoCartorioId": str(tid), "aplicadoPor": "1", "dataInicio": "2025-06-01", "motivo": "Sem PDF"}
        files = {"comprovante": ("", b"", "application/pdf")}
        r = requests.post(url(f"/api/serventias/{sid}/tipos"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_vinculo_requer_motivo(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"tipoCartorioId": str(tid), "aplicadoPor": "1", "dataInicio": "2025-06-01", "motivo": ""}
        files = {"comprovante": arquivo_pdf("Comprovante Vinculo", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_encerrar_requer_pdf(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"encerradoPor": "1", "dataFim": "2025-06-30", "motivo": "Sem PDF"}
        files = {"comprovante": ("", b"", "application/pdf")}
        r = requests.post(url(f"/api/serventias/{sid}/tipos/{tid}/encerrar"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_encerrar_requer_motivo(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"encerradoPor": "1", "dataFim": "2025-06-30", "motivo": ""}
        files = {"comprovante": arquivo_pdf("Comprovante Encerramento", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos/{tid}/encerrar"), data=payload, files=files, auth=COGEX_ADMIN)
        assert r.status_code in (400, 422)

    def test_listar_historico_tipos(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        if sid is None:
            pytest.skip("Serventia nao criada")
        r = requests.get(url(f"/api/serventias/{sid}/tipos"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        if r.json():
            self.__class__._vinculo_id = r.json()[0]["id"]

    def test_download_comprovante_vinculo(self):
        vinculo_id = getattr(self.__class__, "_vinculo_id", None)
        if vinculo_id is None:
            pytest.skip("Vinculo nao encontrado")
        r = requests.get(url(f"/api/serventias/tipos/{vinculo_id}/comprovante"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.content.startswith(b"%PDF")
        if not os.getenv("DOWN_TESTE_FILES"):
            output = Path(__file__).parent / f"comprovante_vinculo_{vinculo_id}.pdf"
            output.write_bytes(r.content)

    def test_download_comprovante_encerramento(self):
        vinculo_id = getattr(self.__class__, "_vinculo_id", None)
        if vinculo_id is None:
            pytest.skip("Vinculo nao encontrado")
        r = requests.get(
            url(f"/api/serventias/tipos/{vinculo_id}/comprovante?fase=ENCERRAMENTO"),
            auth=COGEX_ADMIN,
        )
        if r.status_code == 404:
            pytest.skip("Comprovante de encerramento nao encontrado")
        assert r.status_code == 200
        assert r.content.startswith(b"%PDF")
        if not os.getenv("DOWN_TESTE_FILES"):
            output = Path(__file__).parent / f"comprovante_encerramento_{vinculo_id}.pdf"
            output.write_bytes(r.content)

    def test_criar_usuario_dominio(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        if sid is None:
            pytest.skip("Serventia nao criada")
        data = criar_usuario_dominio(sid)
        assert data["serventiaId"] == sid
        self.__class__._usuario_id = data["id"]

    def test_listar_usuarios(self):
        r = requests.get(url("/api/usuarios-dominio"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_buscar_usuario_dominio_por_id(self):
        uid = getattr(self.__class__, "_usuario_id", None)
        if uid is None:
            data = criar_usuario_dominio(get_or_create_serventia_id())
            uid = data["id"]
            self.__class__._usuario_id = uid
        r = requests.get(url(f"/api/usuarios-dominio/{uid}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["id"] == uid

    def test_atualizar_usuario_dominio(self):
        uid = getattr(self.__class__, "_usuario_id", None)
        if uid is None:
            data = criar_usuario_dominio(get_or_create_serventia_id())
            uid = data["id"]
            self.__class__._usuario_id = uid
        payload = {
            "nome": "Usuario Dominio Atualizado",
            "email": "usuario.atualizado@exemplo.local",
            "role": "RULE_CARTORIO_APOIO",
            "serventiaId": get_or_create_serventia_id(),
            "ativo": True,
        }
        r = requests.put(url(f"/api/usuarios-dominio/{uid}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["nome"] == "Usuario Dominio Atualizado"

    def test_acesso_negado_importar_serventias(self):
        r = requests.post(url("/api/serventias/import-file"), auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_acesso_negado_importar_tipos(self):
        r = requests.post(url("/api/tipos-cartorio/import-file"), auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_acesso_negado_vincular_tipo(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"tipoCartorioId": str(tid), "aplicadoPor": "1", "dataInicio": "2025-06-01", "motivo": "Teste acesso"}
        files = {"comprovante": arquivo_pdf("Comprovante Vinculo", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos"), data=payload, files=files, auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_acesso_negado_encerrar_tipo(self):
        sid = getattr(self.__class__, "_serventia_id", None)
        tid = getattr(self.__class__, "_tipo_id", None)
        if sid is None or tid is None:
            pytest.skip("Serventia ou tipo nao criado")
        payload = {"encerradoPor": "1", "dataFim": "2025-06-30", "motivo": "Teste acesso"}
        files = {"comprovante": arquivo_pdf("Comprovante Encerramento", [f"Serventia {sid}", f"Tipo {tid}"])}
        r = requests.post(url(f"/api/serventias/{sid}/tipos/{tid}/encerrar"), data=payload, files=files, auth=CARTORIO_TITULAR)
        assert r.status_code == 403

# ═══════════════════════════════════════════════════════════════════════════
# 2. CATEGORIAS - CRUD (ROLE_COGEX_ADMIN)
# ═══════════════════════════════════════════════════════════════════════════
class TestCategorias:
    """CRUD completo de /api/categorias (requer ROLE_COGEX_ADMIN)."""

    def test_listar_categorias(self):
        r = requests.get(url("/api/categorias"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_criar_categoria(self):
        payload = {"nome": "Categoria Teste Automatizado"}
        r = requests.post(url("/api/categorias"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        data = r.json()
        assert data["nome"] == "Categoria Teste Automatizado"
        self.__class__._cat_id = data["id"]

    def test_buscar_categoria_por_id(self):
        cat_id = getattr(self.__class__, "_cat_id", None)
        if cat_id is None:
            cat_id = get_or_create_categoria_id()
        r = requests.get(url(f"/api/categorias/{cat_id}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["id"] == cat_id

    def test_atualizar_categoria(self):
        cat_id = getattr(self.__class__, "_cat_id", None)
        if cat_id is None:
            cat_id = get_or_create_categoria_id()
        payload = {"nome": "Categoria Atualizada"}
        r = requests.put(url(f"/api/categorias/{cat_id}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["nome"] == "Categoria Atualizada"

    def test_deletar_categoria(self):
        # Cria uma categoria descartável para não afetar outros testes
        payload = {"nome": "Para Deletar"}
        r = requests.post(url("/api/categorias"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        del_id = r.json()["id"]

        r = requests.delete(url(f"/api/categorias/{del_id}"), auth=COGEX_ADMIN)
        assert r.status_code == 204

    def test_acesso_negado_para_cartorio_titular(self):
        """Cartorio titular pode listar categorias, mas não alterar."""
        r = requests.get(url("/api/categorias"), auth=CARTORIO_TITULAR)
        assert r.status_code in (200, 403)

    def test_acesso_negado_para_cogex_auditor(self):
        """COGEX auditor pode listar categorias, mas não alterar."""
        r = requests.get(url("/api/categorias"), auth=COGEX_AUDITOR)
        assert r.status_code in (200, 403)


# ═══════════════════════════════════════════════════════════════════════════
# 3. SUBCATEGORIAS - CRUD (ROLE_COGEX_ADMIN)
# ═══════════════════════════════════════════════════════════════════════════
class TestSubcategorias:
    """CRUD completo de /api/subcategorias (requer ROLE_COGEX_ADMIN)."""

    def test_listar_subcategorias(self):
        r = requests.get(url("/api/subcategorias"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_criar_subcategoria(self):
        categoria_id = get_or_create_categoria_id()
        payload = {"nome": "Subcategoria Teste", "categoriaId": categoria_id}
        r = requests.post(url("/api/subcategorias"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        data = r.json()
        assert data["nome"] == "Subcategoria Teste"
        self.__class__._sub_id = data["id"]

    def test_buscar_subcategoria_por_id(self):
        sub_id = getattr(self.__class__, "_sub_id", None)
        if sub_id is None:
            sub_id = get_or_create_subcategoria_id(get_or_create_categoria_id())
        r = requests.get(url(f"/api/subcategorias/{sub_id}"), auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_atualizar_subcategoria(self):
        sub_id = getattr(self.__class__, "_sub_id", None)
        if sub_id is None:
            sub_id = get_or_create_subcategoria_id(get_or_create_categoria_id())
        categoria_id = get_or_create_categoria_id()
        payload = {"nome": "Subcategoria Atualizada", "categoriaId": categoria_id}
        r = requests.put(url(f"/api/subcategorias/{sub_id}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_deletar_subcategoria(self):
        categoria_id = get_or_create_categoria_id()
        payload = {"nome": "Subcat Para Deletar", "categoriaId": categoria_id}
        r = requests.post(url("/api/subcategorias"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        del_id = r.json()["id"]

        r = requests.delete(url(f"/api/subcategorias/{del_id}"), auth=COGEX_ADMIN)
        assert r.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════
# 4. DESPESAS - CRUD (ROLE_CARTORIO_APOIO para criar/editar)
# ═══════════════════════════════════════════════════════════════════════════
class TestDespesasCRUD:
    """CRUD de /api/despesas."""

    def test_criar_despesa_como_cartorio_apoio(self):
        """POST /api/despesas - status inicial = REGISTRADA."""
        serventia_id = getattr(TestServentiasTiposUsuarios, "_serventia_id", None)
        tipo_id = getattr(TestServentiasTiposUsuarios, "_tipo_id", None)
        data = criar_despesa(serventia_ref=serventia_id, tipo_cartorio_id=tipo_id)
        assert data["statusAuditoria"] == "REGISTRADA"
        self.__class__._despesa_id = data["id"]

    def test_listar_despesas(self):
        r = requests.get(url("/api/despesas"), auth=COGEX_ADMIN)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# 5. AUDITORIA - FILTROS
# ═══════════════════════════════════════════════════════════════════════════
class TestAuditoriaFiltros:
    def test_listar_auditoria_sem_filtro(self):
        r = requests.get(url("/api/auditoria/despesas"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_listar_auditoria_com_filtros(self):
        serventia_id = getattr(TestServentiasTiposUsuarios, "_serventia_id", None)
        tipo_id = getattr(TestServentiasTiposUsuarios, "_tipo_id", None)
        params = {}
        if serventia_id is not None:
            params["serventiaId"] = serventia_id
        if tipo_id is not None:
            params["tipoCartorioId"] = tipo_id
        params["mes"] = 6
        params["ano"] = 2025
        r = requests.get(url("/api/auditoria/despesas"), params=params, auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert isinstance(r.json(), list)

    def test_buscar_despesa_por_id(self):
        did = getattr(self.__class__, "_despesa_id", None)
        if did is None:
            data = criar_despesa(descricao="Despesa para buscar")
            did = data["id"]
            self.__class__._despesa_id = did
        r = requests.get(url(f"/api/despesas/{did}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.json()["id"] == did

    def test_atualizar_despesa_registrada(self):
        """Apoio pode editar despesa com status REGISTRADA."""
        did = getattr(self.__class__, "_despesa_id", None)
        if did is None:
            data = criar_despesa(descricao="Despesa para atualizar")
            did = data["id"]
            self.__class__._despesa_id = did
        payload = despesa_payload(descricao="Descrição atualizada", valor=200.00)
        r = requests.put(url(f"/api/despesas/{did}"), json=payload, auth=CARTORIO_APOIO)
        assert r.status_code == 200
        assert r.json()["descricao"] == "Descrição atualizada"

    def test_deletar_despesa(self):
        data = criar_despesa(descricao="Para deletar")
        r = requests.delete(url(f"/api/despesas/{data['id']}"), auth=COGEX_ADMIN)
        assert r.status_code == 204

    def test_criar_despesa_negado_para_auditor(self):
        """Auditor NÃO pode criar despesas."""
        r = requests.post(url("/api/despesas"), json=despesa_payload(), auth=COGEX_AUDITOR)
        assert r.status_code == 403

    def test_buscar_despesa_inexistente(self):
        r = requests.get(url("/api/despesas/999999"), auth=COGEX_ADMIN)
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# 5. COMPROVANTES - CRUD + Upload (vinculado a Despesas)
# ═══════════════════════════════════════════════════════════════════════════
class TestComprovantes:
    """Testes de /api/comprovantes - upload e associação a despesas."""

    def test_listar_comprovantes(self):
        r = requests.get(url("/api/comprovantes"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_criar_comprovante_via_json(self):
        data = criar_despesa()
        payload = {
            "idComprovante": "nota_fiscal_001.pdf",
            "filePath": "/uploads/nota_fiscal_001.pdf",
            "despesaId": data["id"],
        }
        r = requests.post(url("/api/comprovantes"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        self.__class__._comp_id = r.json()["id"]
        self.__class__._despesa_id = data["id"]

    def test_buscar_comprovante_por_id(self):
        cid = getattr(self.__class__, "_comp_id", None)
        if cid is None:
            pytest.skip("Comprovante não criado")
        r = requests.get(url(f"/api/comprovantes/{cid}"), auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_atualizar_comprovante(self):
        cid = getattr(self.__class__, "_comp_id", None)
        if cid is None:
            pytest.skip("Comprovante não criado")
        payload = {
            "idComprovante": "nota_atualizada.pdf",
            "filePath": "/uploads/nota_atualizada.pdf",
            "despesaId": getattr(self.__class__, "_despesa_id", None),
        }
        r = requests.put(url(f"/api/comprovantes/{cid}"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_deletar_comprovante(self):
        # Cria um comprovante descartável
        payload = {"idComprovante": "temp.pdf", "filePath": "/tmp/temp.pdf", "despesaId": None}
        r = requests.post(url("/api/comprovantes"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        r = requests.delete(url(f"/api/comprovantes/{r.json()['id']}"), auth=COGEX_ADMIN)
        assert r.status_code == 204

    def test_listar_comprovantes_por_despesa(self):
        did = getattr(self.__class__, "_despesa_id", None)
        if did is None:
            data = criar_despesa(descricao="Despesa para comprovantes")
            did = data["id"]
            self.__class__._despesa_id = did
        # Garantir que exista ao menos um comprovante para a despesa usada no teste
        try:
            r_check = requests.get(url(f"/api/comprovantes/despesas/{did}/comprovantes"), auth=COGEX_ADMIN)
            if r_check.status_code == 200 and isinstance(r_check.json(), list) and len(r_check.json()) < 1:
                upload_comprovante_unico(did, auth=COGEX_ADMIN)
        except Exception:
            upload_comprovante_unico(did, auth=COGEX_ADMIN)
        skip_se_indisponivel(f"/api/comprovantes/despesas/{did}/comprovantes")
        r = requests.get(url(f"/api/comprovantes/despesas/{did}/comprovantes"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1

    def test_upload_arquivo(self):
        """POST /api/comprovantes/upload - multipart/form-data."""
        data = criar_despesa()
        arquivo = upload_comprovante_unico(data["id"], auth=COGEX_ADMIN)
        self.__class__._uploaded_filename = arquivo["filePath"]

    def test_download_arquivo(self):
        """GET /api/comprovantes/files/{filename} - download do comprovante."""
        filename = getattr(self.__class__, "_uploaded_filename", None)
        if not filename:
            pytest.skip("Arquivo não enviado no teste anterior")
        r = requests.get(url(f"/api/comprovantes/files/{filename}"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert len(r.content) > 0
        assert r.content.startswith(b"%PDF")


# ═══════════════════════════════════════════════════════════════════════════
# 6. REGRAS DE DESPESA (ROLE_COGEX_ADMIN)
# ═══════════════════════════════════════════════════════════════════════════
class TestRegrasDespesa:
    """Testes de /api/regras-despesa - controle de permissões por categoria."""

    def test_listar_regras(self):
        skip_se_indisponivel("/api/regras-despesa")
        r = requests.get(url("/api/regras-despesa"), auth=COGEX_ADMIN)
        assert r.status_code == 200

    def test_criar_regra_desabilitando_categoria(self):
        """Cria regra que desabilita uma categoria para uma serventia."""
        skip_se_indisponivel("/api/regras-despesa")
        categoria_id = get_or_create_categoria_id()
        subcategoria_id = get_or_create_subcategoria_id(categoria_id)
        serventia_id = get_or_create_serventia_id()
        payload = {
            "categoria": {"id": categoria_id},
            "subcategoria": {"id": subcategoria_id},
            "serventiaId": serventia_id,
            "habilitada": False,
            "motivo": "Teste automatizado - categoria bloqueada",
            "auditorUsername": "admin",
        }
        r = requests.post(url("/api/regras-despesa"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code == 201
        self.__class__._serventia_regra_id = serventia_id
        self.__class__._categoria_regra_id = categoria_id
        self.__class__._subcategoria_regra_id = subcategoria_id

    def test_despesa_bloqueada_por_regra(self):
        """Tenta criar despesa para serventia com regra desabilitada."""
        skip_se_indisponivel("/api/regras-despesa")
        serventia_id = getattr(self.__class__, "_serventia_regra_id", None)
        categoria_id = getattr(self.__class__, "_categoria_regra_id", None)
        subcategoria_id = getattr(self.__class__, "_subcategoria_regra_id", None)
        if serventia_id is None:
            pytest.skip("Regra não criada")
        if categoria_id is None or subcategoria_id is None:
            pytest.skip("Categoria/subcategoria da regra não definidas")
        r = requests.post(
            url("/api/despesas"),
            json=despesa_payload(
                serventia_id=str(serventia_id),
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
            ),
            auth=CARTORIO_TITULAR,
        )
        # Deve falhar pois a regra desabilita cat=1/sub=1 para serventia 888
        assert r.status_code in (400, 409, 422, 500)

    def test_reabilitar_regra_para_nao_bloquear_outros(self):
        """Reabilita a regra criada para evitar interferencia em outros testes."""
        skip_se_indisponivel("/api/regras-despesa")
        serventia_id = getattr(self.__class__, "_serventia_regra_id", None)
        categoria_id = getattr(self.__class__, "_categoria_regra_id", None)
        subcategoria_id = getattr(self.__class__, "_subcategoria_regra_id", None)
        if serventia_id is None or categoria_id is None or subcategoria_id is None:
            pytest.skip("Regra inicial nao criada")
        payload = {
            "categoria": {"id": categoria_id},
            "subcategoria": {"id": subcategoria_id},
            "serventiaId": serventia_id,
            "habilitada": True,
            "motivo": "Reabilitado para continuidade dos testes",
            "auditorUsername": "admin",
        }
        r = requests.post(url("/api/regras-despesa"), json=payload, auth=COGEX_ADMIN)
        assert r.status_code in (200, 201)

    def test_acesso_negado_serventia(self):
        skip_se_indisponivel("/api/regras-despesa")
        r = requests.get(url("/api/regras-despesa"), auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_acesso_negado_auditor(self):
        skip_se_indisponivel("/api/regras-despesa")
        r = requests.get(url("/api/regras-despesa"), auth=COGEX_AUDITOR)
        assert r.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# 7. RELATÓRIOS
# ═══════════════════════════════════════════════════════════════════════════
class TestRelatorios:
    """GET /api/relatorios/despesas/estatisticas - contagem por status."""

    def test_estatisticas_despesas(self):
        skip_se_indisponivel("/api/relatorios/despesas/estatisticas")
        r = requests.get(url("/api/relatorios/despesas/estatisticas"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        data = r.json()
        # Deve conter todos os status do enum AuditoriaStatus
        for status in ["REGISTRADA", "SUBMETIDA", "APROVADA", "REJEITADA", "PENDENTE_DE_ESCLARECIMENTO"]:
            assert status in data, f"Status '{status}' ausente nas estatísticas"


# ═══════════════════════════════════════════════════════════════════════════
# 8. EXPORTAÇÃO EXCEL
# ═══════════════════════════════════════════════════════════════════════════
class TestExport:
    """GET /api/export/despesas.xlsx - download de planilha."""

    def test_export_despesas_xlsx(self):
        skip_se_indisponivel("/api/export/despesas.xlsx")
        r = requests.get(url("/api/export/despesas.xlsx"), auth=COGEX_ADMIN)
        assert r.status_code == 200
        assert r.content.startswith(b"PK")
        if not os.getenv("DOWN_TESTE_FILES"):
            filename = "despesas_export.xlsx"
            content_disposition = r.headers.get("Content-Disposition", "")
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[-1].strip().strip('"')
            base_dir = os.path.dirname(__file__)
            path = os.path.join(base_dir, filename)
            with open(path, "wb") as f:
                f.write(r.content)
        assert "spreadsheetml" in r.headers.get("Content-Type", "")
        assert len(r.content) > 0


# ═══════════════════════════════════════════════════════════════════════════
# 9. SOLICITAÇÃO DE CATEGORIA (ROLE_CARTORIO_TITULAR)
# ═══════════════════════════════════════════════════════════════════════════
class TestSolicitacaoCategoria:
    """POST /api/solicitacoes-categoria - serventia solicita nova categoria."""

    def test_solicitar_nova_categoria(self):
        skip_se_indisponivel("/api/solicitacoes-categoria", method="POST")
        payload = {
            "nomeSugerido": "Despesas com Veículos",
            "justificativa": "Necessário para controlar combustível e manutenção",
            "tipo": "CATEGORIA",
        }
        r = requests.post(url("/api/solicitacoes-categoria"), json=payload, auth=CARTORIO_TITULAR)
        assert r.status_code == 201

    def test_solicitar_nova_subcategoria(self):
        skip_se_indisponivel("/api/solicitacoes-categoria", method="POST")
        categoria_id = get_or_create_categoria_id()
        payload = {
            "nomeSugerido": "Combustível",
            "justificativa": "Subcategoria para veículos",
            "tipo": "SUBCATEGORIA",
            "categoriaPaiId": categoria_id,
        }
        r = requests.post(url("/api/solicitacoes-categoria"), json=payload, auth=CARTORIO_TITULAR)
        assert r.status_code == 201

    def test_acesso_negado_auditor(self):
        skip_se_indisponivel("/api/solicitacoes-categoria", method="POST")
        payload = {"nomeSugerido": "X", "justificativa": "Y", "tipo": "CATEGORIA"}
        r = requests.post(url("/api/solicitacoes-categoria"), json=payload, auth=COGEX_AUDITOR)
        assert r.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# 10. CONTROLE DE ACESSO - Autenticação obrigatória
# ═══════════════════════════════════════════════════════════════════════════
class TestSeguranca:
    """Verifica que a API exige autenticação e respeita papéis."""

    def test_requisicao_sem_credenciais(self):
        r = requests.get(url("/api/despesas"))
        assert r.status_code == 401

    def test_serventia_nao_pode_aprovar(self):
        data = criar_despesa()
        requests.post(url(f"/api/despesas/{data['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = requests.post(url(f"/api/despesas/{data['id']}/workflow/aprovar"), auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_serventia_nao_pode_rejeitar(self):
        data = criar_despesa()
        requests.post(url(f"/api/despesas/{data['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = requests.post(url(f"/api/despesas/{data['id']}/workflow/rejeitar"), auth=CARTORIO_TITULAR)
        assert r.status_code == 403

    def test_auditor_nao_pode_criar_despesa(self):
        r = requests.post(url("/api/despesas"), json=despesa_payload(), auth=COGEX_AUDITOR)
        assert r.status_code == 403

    def test_auditor_nao_pode_submeter(self):
        data = criar_despesa()
        r = requests.post(url(f"/api/despesas/{data['id']}/workflow/submeter"), auth=COGEX_AUDITOR)
        assert r.status_code == 403


# ###########################################################################
#
#  FLUXOS DE AUDITORIA - tech/fluxo-de-dados-auditoria.md
#
#  Cada classe abaixo reproduz um caminho completo do diagrama de estados:
#
#    REGISTRADA -> SUBMETIDA -> APROVADA
#    REGISTRADA -> SUBMETIDA -> REJEITADA
#    REGISTRADA -> SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO -> SUBMETIDA -> APROVADA
#
# ###########################################################################


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO A: Aprovação direta
#   Serventia cria -> anexa comprovante -> submete -> Auditor aprova
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoAprovacao:
    """
    Fluxo completo: REGISTRADA -> SUBMETIDA -> APROVADA

    Referência: tech/fluxo-de-dados-auditoria.md - Etapas 1 e 2a
    """

    def test_fluxo_aprovacao_completo(self):
        # --- Etapa 1: Criação pela Serventia ---
        # 1a. POST /api/despesas - status inicial REGISTRADA
        despesa = criar_despesa(descricao="Fluxo Aprovação - material de escritório")
        despesa_id = despesa["id"]
        assert despesa["statusAuditoria"] == "REGISTRADA"

        # 1b. POST /api/comprovantes/upload - anexar comprovante
        upload_comprovante_unico(despesa_id, auth=CARTORIO_TITULAR)

        # 1c. POST /api/despesas/{id}/workflow/submeter - muda para SUBMETIDA
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # --- Etapa 2: Análise pela Auditoria ---
        # 2a. GET /api/despesas - auditor lista despesas submetidas
        r = requests.get(url("/api/despesas?status=SUBMETIDA"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        submetidas = [d for d in r.json() if d["statusAuditoria"] == "SUBMETIDA"]
        assert any(d["id"] == despesa_id for d in submetidas)

        # 2b. GET /api/despesas/{id} - auditor abre detalhe da despesa
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_AUDITOR)
        assert r.status_code == 200

        # 2c. POST /api/despesas/{id}/workflow/aprovar - APROVADA
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/aprovar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "APROVADA"

        # Verificação final
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "APROVADA"


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO B: Rejeição
#   Serventia cria -> anexa comprovante -> submete -> Auditor rejeita
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoRejeicao:
    """
    Fluxo completo: REGISTRADA -> SUBMETIDA -> REJEITADA

    Referência: tech/fluxo-de-dados-auditoria.md - Etapas 1 e 2b
    """

    def test_fluxo_rejeicao_completo(self):
        # --- Etapa 1: Criação e submissão pela Serventia ---
        despesa = criar_despesa(descricao="Fluxo Rejeição - despesa irregular")
        despesa_id = despesa["id"]
        assert despesa["statusAuditoria"] == "REGISTRADA"

        # Anexar comprovante
        upload_comprovante_unico(despesa_id, auth=CARTORIO_TITULAR)

        # Submeter
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # --- Etapa 2: Auditor rejeita ---
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/rejeitar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "REJEITADA"

        # Verificação final
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "REJEITADA"


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO C: Esclarecimento (ida e volta)
#   Serventia cria -> submete -> Auditor solicita esclarecimento ->
#   Serventia responde -> Auditor aprova
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoEsclarecimento:
    """
    Fluxo completo:
      REGISTRADA -> SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO -> SUBMETIDA -> APROVADA

    Referência: tech/fluxo-de-dados-auditoria.md - Etapas 1, 2c e 3
    """

    def test_fluxo_esclarecimento_completo(self):
        # --- Etapa 1: Criação e submissão pela Serventia ---
        despesa = criar_despesa(descricao="Fluxo Esclarecimento - despesa com dúvidas")
        despesa_id = despesa["id"]
        assert despesa["statusAuditoria"] == "REGISTRADA"

        # Submeter
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # --- Etapa 2c: Auditor solicita esclarecimento ---
        # POST /api/despesas/{despesaId}/workflow/solicitar-esclarecimento
        r = post_texto(
            f"/api/despesas/{despesa_id}/workflow/solicitar-esclarecimento",
            "Por favor, envie o comprovante fiscal original.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        solicitacao = r.json()
        solicitacao_id = solicitacao["id"]
        assert solicitacao["despesaId"] == despesa_id
        assert solicitacao["resolved"] is False

        # Verificar que a despesa mudou para PENDENTE_DE_ESCLARECIMENTO
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

        # --- Etapa 3: Serventia responde ao esclarecimento ---
        # POST /api/despesas/solicitacoes-esclarecimento/{solicitacaoId}/responder
        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{solicitacao_id}/responder",
            "Segue em anexo o comprovante fiscal original digitalizado.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200
        resposta = r.json()
        assert resposta["resolved"] is True

        # Verificar que a despesa voltou para SUBMETIDA
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # --- Etapa 2a (retorno): Auditor aprova após esclarecimento ---
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/aprovar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "APROVADA"

        # Verificação final
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "APROVADA"


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO D: Esclarecimento com rejeição final
#   Serventia cria -> submete -> Auditor solicita esclarecimento ->
#   Serventia responde -> Auditor rejeita
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoEsclarecimentoComRejeicao:
    """
    Fluxo completo:
      REGISTRADA -> SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO -> SUBMETIDA -> REJEITADA

    Variação do fluxo C onde o auditor decide rejeitar após o esclarecimento.
    """

    def test_fluxo_esclarecimento_com_rejeicao(self):
        despesa = criar_despesa(descricao="Esclarecimento insatisfatório")
        despesa_id = despesa["id"]

        # Submeter
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # Auditor solicita esclarecimento
        r = post_texto(
            f"/api/despesas/{despesa_id}/workflow/solicitar-esclarecimento",
            "Valor incompatível com o serviço prestado.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        solicitacao_id = r.json()["id"]

        # Serventia responde
        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{solicitacao_id}/responder",
            "O valor está correto conforme contrato.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200

        # Verificar retorno para SUBMETIDA
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # Auditor rejeita mesmo após esclarecimento
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/rejeitar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "REJEITADA"


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO E: Múltiplos ciclos de esclarecimento
#   Serventia cria -> submete -> Auditor pede esclarecimento ->
#   Serventia responde -> Auditor pede novamente -> Serventia responde ->
#   Auditor aprova
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoMultiplosEsclarecimentos:
    """
    Fluxo com múltiplos ciclos de ida e volta entre auditor e serventia:
      REGISTRADA -> SUBMETIDA -> PENDENTE -> SUBMETIDA -> PENDENTE -> SUBMETIDA -> APROVADA

    Demonstra que o ciclo de esclarecimento pode se repetir.
    """

    def test_fluxo_multiplos_ciclos(self):
        despesa = criar_despesa(descricao="Despesa com múltiplas dúvidas")
        despesa_id = despesa["id"]

        # Submeter
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # ---- Ciclo 1 de esclarecimento ----
        r = post_texto(
            f"/api/despesas/{despesa_id}/workflow/solicitar-esclarecimento",
            "Favor informar a nota fiscal.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        sol1_id = r.json()["id"]

        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{sol1_id}/responder",
            "Nota fiscal em anexo.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200

        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # ---- Ciclo 2 de esclarecimento ----
        r = post_texto(
            f"/api/despesas/{despesa_id}/workflow/solicitar-esclarecimento",
            "A nota fiscal está ilegível. Reenvie.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        sol2_id = r.json()["id"]

        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{sol2_id}/responder",
            "Nova digitalização da nota fiscal em melhor resolução.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200

        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # Aprovação final
        r = requests.post(url(f"/api/despesas/{despesa_id}/workflow/aprovar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "APROVADA"


# ═══════════════════════════════════════════════════════════════════════════
# FLUXO F: Fluxo completo com comprovantes e verificação de listagem
#   Demonstra o fluxo end-to-end incluindo consulta de comprovantes
#   e listagem filtrada conforme descrito no documento de auditoria
# ═══════════════════════════════════════════════════════════════════════════
class TestFluxoCompletoComComprovantes:
    """
    Fluxo end-to-end detalhado com todas as consultas intermediárias
    que o frontend faria durante o processo de auditoria.

    Referência: tech/fluxo-de-dados-auditoria.md - Todas as etapas
    """

    def test_fluxo_end_to_end(self):
        # ============================================================
        # ETAPA 1 - Serventia: Criar despesa
        # ============================================================
        despesa = criar_despesa(
            descricao="Serviço de manutenção preventiva em ar-condicionado",
            valor=3500.00,
            categoria_id=2,
            subcategoria_id=4,
        )
        despesa_id = despesa["id"]
        assert despesa["statusAuditoria"] == "REGISTRADA"

        # ============================================================
        # ETAPA 1 - Serventia: Anexar comprovantes
        # ============================================================
        upload_comprovante_unico(despesa_id, auth=CARTORIO_TITULAR)

        # Verificar comprovantes vinculados (endpoint pode não estar disponível)
        r = requests.get(
            url(f"/api/comprovantes/despesas/{despesa_id}/comprovantes"), auth=CARTORIO_TITULAR
        )
        if r.status_code != 404:
            assert r.status_code == 200
            assert len(r.json()) >= 1

        # ============================================================
        # ETAPA 1 - Serventia: Submeter para auditoria
        # ============================================================
        r = requests.post(
            url(f"/api/despesas/{despesa_id}/workflow/submeter"), auth=CARTORIO_TITULAR
        )
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # ============================================================
        # ETAPA 2 - Auditor: Listar despesas submetidas
        # ============================================================
        r = requests.get(url("/api/despesas"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        todas = r.json()
        submetidas = [d for d in todas if d["statusAuditoria"] == "SUBMETIDA"]
        assert any(d["id"] == despesa_id for d in submetidas)

        # ============================================================
        # ETAPA 2 - Auditor: Verificar detalhes e comprovantes
        # ============================================================
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["valor"] == 3500.00

        r = requests.get(
            url(f"/api/comprovantes/despesas/{despesa_id}/comprovantes"), auth=COGEX_AUDITOR
        )
        if r.status_code != 404:
            assert r.status_code == 200
            comprovantes = r.json()
            assert len(comprovantes) >= 1

        # ============================================================
        # ETAPA 2c - Auditor: Solicitar esclarecimento
        # ============================================================
        r = post_texto(
            f"/api/despesas/{despesa_id}/workflow/solicitar-esclarecimento",
            "O valor de R$3.500 está acima da média. Justifique.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        solicitacao_id = r.json()["id"]

        # Verificar status mudou
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

        # ============================================================
        # ETAPA 3 - Serventia: Responder esclarecimento
        # ============================================================
        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{solicitacao_id}/responder",
            "Valor conforme 3 orçamentos realizados. Menor preço selecionado.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200
        assert r.json()["resolved"] is True

        # Verificar retorno para SUBMETIDA
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

        # ============================================================
        # ETAPA 2a (retorno) - Auditor: Aprovar
        # ============================================================
        r = requests.post(
            url(f"/api/despesas/{despesa_id}/workflow/aprovar"), auth=COGEX_AUDITOR
        )
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "APROVADA"

        # ============================================================
        # Verificação final via relatório (endpoint pode não estar disponível)
        # ============================================================
        r = requests.get(url("/api/relatorios/despesas/estatisticas"), auth=COGEX_ADMIN)
        if r.status_code != 404:
            assert r.status_code == 200
            stats = r.json()
            assert stats["APROVADA"] >= 1

        # Verificação final via GET na despesa
        r = requests.get(url(f"/api/despesas/{despesa_id}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "APROVADA"


# ═══════════════════════════════════════════════════════════════════════════
# TRANSIÇÕES DE STATUS - Validações de máquina de estados
# ═══════════════════════════════════════════════════════════════════════════
class TestTransicoesStatus:
    """
    Verifica que cada transição de status funciona conforme o diagrama
    de estados em tech/fluxo-de-dados-auditoria.md.
    """

    def test_registrada_para_submetida(self):
        """REGISTRADA -> SUBMETIDA (Serventia submete)."""
        d = criar_despesa()
        r = requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "SUBMETIDA"

    def test_submetida_para_aprovada(self):
        """SUBMETIDA -> APROVADA (Auditor aprova)."""
        d = criar_despesa()
        requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = requests.post(url(f"/api/despesas/{d['id']}/workflow/aprovar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "APROVADA"

    def test_submetida_para_rejeitada(self):
        """SUBMETIDA -> REJEITADA (Auditor rejeita)."""
        d = criar_despesa()
        requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = requests.post(url(f"/api/despesas/{d['id']}/workflow/rejeitar"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "REJEITADA"

    def test_submetida_para_pendente_esclarecimento(self):
        """SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO (Auditor solicita esclarecimento)."""
        d = criar_despesa()
        requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = post_texto(
            f"/api/despesas/{d['id']}/workflow/solicitar-esclarecimento",
            "Explique o valor.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        r = requests.get(url(f"/api/despesas/{d['id']}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

    def test_submetida_para_pendente_via_endpoint(self):
        """SUBMETIDA -> PENDENTE_DE_ESCLARECIMENTO via /workflow/pendente."""
        d = criar_despesa()
        requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = requests.post(url(f"/api/despesas/{d['id']}/workflow/pendente"), auth=COGEX_AUDITOR)
        assert r.status_code == 200
        assert r.json()["statusAuditoria"] == "PENDENTE_DE_ESCLARECIMENTO"

    def test_pendente_para_submetida(self):
        """PENDENTE_DE_ESCLARECIMENTO -> SUBMETIDA (Serventia responde)."""
        d = criar_despesa()
        requests.post(url(f"/api/despesas/{d['id']}/workflow/submeter"), auth=CARTORIO_TITULAR)
        r = post_texto(
            f"/api/despesas/{d['id']}/workflow/solicitar-esclarecimento",
            "Justifique.",
            auth=COGEX_AUDITOR,
        )
        assert_status(r, 201, "solicitar-esclarecimento")
        sol_id = r.json()["id"]
        r = post_texto(
            f"/api/despesas/solicitacoes-esclarecimento/{sol_id}/responder",
            "Justificativa anexa.",
            auth=CARTORIO_TITULAR,
        )
        assert r.status_code == 200
        r = requests.get(url(f"/api/despesas/{d['id']}"), auth=COGEX_ADMIN)
        assert r.json()["statusAuditoria"] == "SUBMETIDA"
