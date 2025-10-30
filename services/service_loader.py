"""
Service Loader - Dashboard Estoque TI
Carrega automaticamente o serviço correto (Excel ou PostgreSQL)
"""

import os
from loguru import logger


def get_estoque_service():
    """
    Retorna a classe EstoqueService apropriada baseada na configuração
    
    Ordem de prioridade:
    1. Variável de ambiente USE_POSTGRES=true
    2. Presença de DATABASE_URL
    3. Arquivo .env com DATABASE_URL
    4. Padrão: Excel
    
    Returns:
        Classe EstoqueService (PostgreSQL ou Excel)
    """
    
    # Verificar variável USE_POSTGRES explícita
    use_postgres_env = os.getenv("USE_POSTGRES", "").lower()
    if use_postgres_env in ("true", "1", "yes"):
        logger.info("🐘 Usando PostgreSQL (USE_POSTGRES=true)")
        from services.estoque_service_postgres import EstoqueService
        return EstoqueService
    
    if use_postgres_env in ("false", "0", "no"):
        logger.info("📊 Usando Excel (USE_POSTGRES=false)")
        from services.estoque_service import EstoqueService
        return EstoqueService
    
    # Verificar se DATABASE_URL existe
    database_url = os.getenv("DATABASE_URL")
    
    # Se não encontrar no env, tentar Streamlit secrets
    if not database_url:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                database_url = st.secrets['DATABASE_URL']
                logger.info("🔐 DATABASE_URL encontrada no Streamlit secrets")
        except:
            pass
    
    # Se tem DATABASE_URL, usar PostgreSQL
    if database_url:
        # Verificar se é PostgreSQL ou SQLite
        if "postgresql://" in database_url or "sqlite:///" in database_url:
            logger.info(f"🐘 Usando PostgreSQL/SQLite (DATABASE_URL configurada)")
            logger.info(f"   📍 Tipo: {'PostgreSQL' if 'postgresql' in database_url else 'SQLite'}")
            from services.estoque_service_postgres import EstoqueService
            return EstoqueService
    
    # Padrão: Excel
    logger.info("📊 Usando Excel (padrão - DATABASE_URL não encontrada)")
    from services.estoque_service import EstoqueService
    return EstoqueService


def get_service_info():
    """
    Retorna informações sobre qual serviço está sendo usado
    
    Returns:
        Dict com informações do serviço
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                database_url = st.secrets['DATABASE_URL']
        except:
            pass
    
    if database_url:
        if "postgresql://" in database_url:
            db_type = "PostgreSQL"
        elif "sqlite:///" in database_url:
            db_type = "SQLite"
        else:
            db_type = "Desconhecido"
        
        # Ofuscar senha na URL
        display_url = database_url
        if "@" in display_url:
            parts = display_url.split("@")
            user_pass = parts[0].split("://")
            if len(user_pass) > 1 and ":" in user_pass[1]:
                user = user_pass[1].split(":")[0]
                display_url = f"{user_pass[0]}://{user}:****@{parts[1]}"
        
        return {
            "tipo": db_type,
            "backend": "PostgreSQL/SQLite Service",
            "url": display_url,
            "persistente": True
        }
    else:
        return {
            "tipo": "Excel",
            "backend": "Excel Service",
            "arquivo": "estoque_ti.xlsx",
            "persistente": False,
            "aviso": "⚠️ Dados podem ser perdidos em restarts!"
        }


# Para uso como módulo
EstoqueService = None

def init_service():
    """Inicializa o serviço apropriado"""
    global EstoqueService
    if EstoqueService is None:
        EstoqueService = get_estoque_service()
    return EstoqueService

