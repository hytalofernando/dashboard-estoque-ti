"""
Configuração do Banco de Dados - Dashboard Estoque TI
Permite alternar entre Excel e PostgreSQL
"""

import os
from loguru import logger


class DatabaseConfig:
    """Configuração centralizada do tipo de banco de dados"""
    
    # ========================================
    # CONFIGURAÇÃO: Altere aqui para mudar o banco
    # ========================================
    
    # Opções: "EXCEL" ou "POSTGRES"
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "POSTGRES")
    
    # URL do banco (apenas para PostgreSQL)
    DATABASE_URL = os.getenv("DATABASE_URL", None)
    
    @classmethod
    def usar_postgres(cls) -> bool:
        """
        Retorna True se deve usar PostgreSQL
        
        Critérios:
        1. DATABASE_TYPE está configurado como "POSTGRES"
        2. DATABASE_URL está configurada
        3. Ou DATABASE_URL existe (mesmo sem DATABASE_TYPE definido)
        """
        # Se DATABASE_TYPE for explicitamente EXCEL, usar Excel
        if cls.DATABASE_TYPE.upper() == "EXCEL":
            logger.info("📊 Usando EXCEL (configurado explicitamente)")
            return False
        
        # Se DATABASE_TYPE for POSTGRES e tiver URL, usar PostgreSQL
        if cls.DATABASE_TYPE.upper() == "POSTGRES" and cls.DATABASE_URL:
            logger.info("🐘 Usando POSTGRESQL (configurado explicitamente)")
            return True
        
        # Se DATABASE_URL existir, usar PostgreSQL por padrão
        if cls.DATABASE_URL and "postgresql://" in cls.DATABASE_URL:
            logger.info("🐘 Usando POSTGRESQL (DATABASE_URL encontrada)")
            return True
        
        # Se DATABASE_URL for SQLite, usar SQLite (tratado pelo PostgreSQL service)
        if cls.DATABASE_URL and "sqlite:///" in cls.DATABASE_URL:
            logger.info("🗄️ Usando SQLite (DATABASE_URL sqlite)")
            return True
        
        # Padrão: usar Excel
        logger.info("📊 Usando EXCEL (padrão)")
        return False
    
    @classmethod
    def info(cls):
        """Retorna informações sobre a configuração atual"""
        if cls.usar_postgres():
            db_type = "PostgreSQL/SQLite"
            location = cls.DATABASE_URL if cls.DATABASE_URL else "Não configurado"
        else:
            db_type = "Excel"
            location = "estoque_ti.xlsx"
        
        return {
            "tipo": db_type,
            "localizacao": location,
            "usar_postgres": cls.usar_postgres()
        }


# Instância global
db_config = DatabaseConfig()

