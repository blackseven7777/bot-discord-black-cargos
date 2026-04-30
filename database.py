import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# 📦 TABELA DE CÓDIGOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS codigos (
    codigo TEXT PRIMARY KEY,
    cargo_id INTEGER,
    usos INTEGER,
    max_usos INTEGER,
    validade TEXT
)
""")

# 👤 TABELA DE USUÁRIOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios_codigos (
    user_id INTEGER,
    codigo TEXT,
    cargo_id INTEGER,
    expira_em TEXT
)
""")

conn.commit()

# ✅ CRIAR CÓDIGO (agora recebe data pronta)
def criar_codigo(codigo, cargo_id, max_usos, validade):
    cursor.execute(
        "INSERT INTO codigos VALUES (?, ?, ?, ?, ?)",
        (codigo, cargo_id, 0, max_usos, validade)
    )
    conn.commit()

# 🔍 PEGAR CÓDIGO
def pegar_codigo(codigo):
    cursor.execute("SELECT * FROM codigos WHERE codigo = ?", (codigo,))
    return cursor.fetchone()

# ➕ USAR CÓDIGO
def usar_codigo(codigo):
    cursor.execute("UPDATE codigos SET usos = usos + 1 WHERE codigo = ?", (codigo,))
    conn.commit()

# 🕒 REGISTRAR USO (agora recebe data exata)
def registrar_uso(user_id, codigo, cargo_id, expira_em):
    cursor.execute(
        "INSERT INTO usuarios_codigos VALUES (?, ?, ?, ?)",
        (user_id, codigo, cargo_id, expira_em)
    )
    conn.commit()

# 🔁 PEGAR EXPIRAÇÕES
def pegar_expiracoes():
    cursor.execute("SELECT * FROM usuarios_codigos")
    return cursor.fetchall()

# ❌ REMOVER REGISTRO
def remover_registro(user_id, codigo):
    cursor.execute(
        "DELETE FROM usuarios_codigos WHERE user_id = ? AND codigo = ?",
        (user_id, codigo)
    )
    conn.commit()
