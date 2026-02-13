"""
populate_data.py - Popula o banco de dados com despesas de teste seguindo o fluxo de auditoria.

Cria despesas para as primeiras 22 serventias, variando os status e garantindo
que os documentos obrigatórios (Nota Fiscal e Comprovante) sejam anexados antes da submissão.

Uso:
  python3 devdocs/populate_data.py
"""

import os
import io
import random
import time
import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8180")

# Credenciais
COGEX_ADMIN = ("cogex_admin", "password")
COGEX_AUDITOR = ("cogex_auditor", "password")
# Senha padrão para usuários criados
DEFAULT_PASS = "password"

# ---------------------------------------------------------------------------
# Helpers (adaptados de despesa-api-mvp.py)
# ---------------------------------------------------------------------------
def url(path: str) -> str:
    return f"{BASE_URL}{path}"

def gerar_pdf_bytes(linhas: list[str]) -> bytes:
    """Gera um PDF simples em formato A4 com o conteudo textual linha a linha."""
    
    content_ops = []
    y_pos = 800 # Start near top
    
    for linha in linhas:
        texto_safe = str(linha).replace("(", "\\(").replace(")", "\\)")
        # BT = Begin Text, /F1 12 Tf = Font, x y Td = Position, Tj = Show text, ET = End Text
        content_ops.append(f"BT /F1 12 Tf 50 {y_pos} Td ({texto_safe}) Tj ET")
        y_pos -= 20 # Move down for next line
    
    stream_content = ("\n".join(content_ops)).encode("latin-1")
    
    length = len(stream_content)

    # Objetos do PDF
    objects = [
        # 1. Catalog
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj",
        # 2. Pages
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj",
        # 3. Page (A4 size: 595 x 842 points)
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj",
        # 4. Font (Helvetica)
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj",
        # 5. Content Stream
        f"5 0 obj\n<< /Length {length} >>\nstream\n".encode("ascii") + stream_content + b"\nendstream\nendobj"
    ]

    # Construção do corpo
    body = b"%PDF-1.4\n"
    xref_offsets = [0] # 0 65535 f
    running_offset = len(body)

    # Adiciona objetos e calcula offsets
    for obj in objects:
        xref_offsets.append(running_offset)
        body += obj + b"\n"
        running_offset = len(body)

    # XREF table
    xref = b"xref\n0 " + str(len(objects) + 1).encode("ascii") + b"\n0000000000 65535 f \n"
    for offset in xref_offsets[1:]:
        xref += f"{offset:010d} 00000 n \n".encode("ascii")

    # Trailer
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{running_offset}\n%%EOF\n".encode("ascii")

    return body + xref + trailer

def criar_usuario_se_nao_existir(serventia_id: int):
    email = f"titular.{serventia_id}@serventia.local"
    payload = {
        "nome": f"Titular Serventia {serventia_id}",
        "email": email,
        "role": "RULE_CARTORIO_TITULAR",
        "serventiaId": serventia_id,
        "ativo": True
    }
    
    r = requests.post(url("/api/usuarios-dominio"), json=payload, auth=COGEX_ADMIN)
    if r.status_code == 201:
        print(f"Usuario criado: {email}")
        return (email, DEFAULT_PASS)
        
    return (email, "password")

def get_primeiro_id(endpoint):
    r = requests.get(url(endpoint), auth=COGEX_ADMIN)
    if r.status_code == 200 and len(r.json()) > 0:
        return r.json()[0]['id']
    return None

def upload_docs(despesa, auth):
    despesa_id = despesa['id']
    
    # Dados comuns
    info_base = [
        f"ID Despesa: {despesa['id']}",
        f"Serventia: {despesa.get('serventiaId', '?')}",
        f"Competencia: {despesa.get('dataCompetencia', '?')}",
        f"Categoria: {despesa.get('categoriaId', '?')}",
        f"Subcategoria: {despesa.get('subcategoriaId', '?')}",
        f"Descricao: {despesa.get('descricao', '?')}",
        f"Valor: R$ {despesa.get('valor', '?')}"
    ]

    # Nota Fiscal
    nf_lines = ["--- NOTA FISCAL ---"] + info_base + ["", "Documento fiscal gerado automaticamente para fins de teste."]
    requests.post(
        url("/api/documentos/upload"),
        files={"file": ("nota_fiscal.pdf", io.BytesIO(gerar_pdf_bytes(nf_lines)), "application/pdf")},
        data={"despesaId": despesa_id, "tipoDocumento": "NOTA_FISCAL"},
        auth=auth
    )
    
    # Comprovante
    comp_lines = ["--- COMPROVANTE DE PAGAMENTO ---"] + info_base + ["", "Pagamento realizado via transferencia bancaria."]
    requests.post(
        url("/api/documentos/upload"),
        files={"file": ("comprovante.pdf", io.BytesIO(gerar_pdf_bytes(comp_lines)), "application/pdf")},
        data={"despesaId": despesa_id, "tipoDocumento": "COMPROVANTE_PAGAMENTO"},
        auth=auth
    )

def main():
    print("Iniciando populacao de dados...")
    
    # IDs base
    cat_id = get_primeiro_id("/api/categorias") or 1
    sub_id = get_primeiro_id("/api/subcategorias") or 1
    tipo_id = get_primeiro_id("/api/tipos-cartorio") or 1

    # Para as primeiras 22 serventias
    for s_id in range(1, 23):
        print(f"Processando Serventia {s_id}...")
        
        # Credenciais do titular (criadas pelo data.sql ou assumidas)
        auth_titular = (f"titular.{s_id}@serventia.local", "password")
        
        # Criar 5 despesas variadas
        for i in range(5):
            # 1. Criar Despesa
            payload = {
                "dataLancamento": "2025-02-01",
                "dataCompetencia": "2025-01-01",
                "idServentia": str(s_id),
                "serventiaId": s_id,
                "categoriaId": cat_id,
                "subcategoriaId": sub_id,
                "tipoCartorioId": tipo_id,
                "descricao": f"Despesa Automatica {i+1} - Serventia {s_id}",
                "valor": round(random.uniform(100.0, 5000.0), 2)
            }
            
            r = requests.post(url("/api/despesas"), json=payload, auth=auth_titular)
            if r.status_code != 201:
                print(f"  [Erro] Falha ao criar despesa: {r.status_code} - {r.text}")
                continue
                
            despesa = r.json()
            d_id = despesa['id']
            print(f"  Despesa {d_id} criada.")
            
            # 2. Upload Arquivos (Obrigatorio para submeter)
            upload_docs(despesa, auth_titular)
            
            # 3. Variar Status
            target_status = random.choice(['REGISTRADA', 'SUBMETIDA', 'APROVADA', 'REJEITADA', 'PENDENTE'])
            
            if target_status == 'REGISTRADA':
                continue # Já está no status inicial
                
            # Submeter
            r = requests.post(url(f"/api/despesas/{d_id}/workflow/submeter"), auth=auth_titular)
            if r.status_code != 200:
                print(f"  [Erro] Falha ao submeter {d_id}: {r.status_code}")
                continue
                
            if target_status == 'SUBMETIDA':
                continue
                
            # Ações de Auditor
            if target_status == 'APROVADA':
                requests.post(url(f"/api/despesas/{d_id}/workflow/aprovar"), auth=COGEX_AUDITOR)
            elif target_status == 'REJEITADA':
                requests.post(url(f"/api/despesas/{d_id}/workflow/rejeitar"), auth=COGEX_AUDITOR, data="Rejeitado pelo script")
            elif target_status == 'PENDENTE':
                requests.post(url(f"/api/despesas/{d_id}/workflow/solicitar-esclarecimento"), auth=COGEX_AUDITOR, data="Esclareça este valor")

    print("Populacao concluida.")

if __name__ == "__main__":
    main()