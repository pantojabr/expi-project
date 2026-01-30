# Orientações que sempre devem ser seguidas
Para nos projetos nas pastas `despesa-api-mvp` e `despesas-front-mvp`

## Language

*   Aways response in PT-BR

## resplog

## testes resilientes (banco compartilhado)
- Nao assumir banco vazio nem IDs fixos.
- Preferir criar recursos e usar o ID retornado; se falhar, listar e usar o primeiro existente.
- Evitar IDs magicos (ex.: 1, 888) em payloads; usar helpers para obter IDs reais.
- Se nao for possivel criar/listar, o teste deve pular de forma explicita.

## Directory Overview

This directory serves as a knowledge base and research repository for a project focused on the extrajudicial (notarial and registry) services of the State of Amapá's Court of Justice (TJAP). The primary goal is to analyze the legal framework, revenue streams, and operational procedures governing these services.

The content consists of Brazilian legal texts, analyses, technical notes, and planning documents. The key objective appears to be understanding the flow of funds (emoluments, fees), the role of specific funds like FERC and FMRJ, and the use of authentication stamps (`Selo`) for tracking and oversight.

## Key Files & Directories

*   `README.md`: The main entry point, providing an overview of the project, a study plan for the relevant laws, and key discoveries.
*   `Report.md`: A technical report detailing inconsistencies found in data extraction for the TLP (Tabela de Lotação de Pessoal), indicating a data analysis component to the project.
*   `TODO.md`: Contains a list of tasks, primarily related to analyzing data inconsistencies in tables.
*   **Law Directories** (e.g., `1436-custas-e-emolumentos-2009`, `1847-selo-FERC-2014`): Each of these directories is dedicated to a specific state or federal law, containing the original text, cleaned-up markdown versions, and analysis.
*   `research/`: Contains thematic analyses. For example, `01-receitas.md` breaks down how different revenue sources are collected and allocated.
*   `tech/`: Contains technical documentation. `DEV.md` outlines a study plan and potential modules for a future software system (API, Stamp Issuance, Fraud Tracking). The `sql/` subdirectory contains queries related to the project's data.

## Usage

This directory is intended for research, analysis, and planning. It is used to:
1.  Consolidate all relevant legal and technical documentation.
2.  Analyze the complex rules governing notarial fees, taxes, and fund contributions.
3.  Define the requirements and architecture for a potential future software system to manage and audit these processes.

The workflow involves studying the laws in the specified order (`README.md`), analyzing the data (`Report.md`, `tech/sql/`), and designing a system (`tech/DEV.md`).



