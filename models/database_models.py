"""
Modelos de Banco de Dados - Dashboard Estoque TI
SQLAlchemy ORM Models para PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import os
from loguru import logger

Base = declarative_base()

class Equipamento(Base):
    """Modelo para tabela de equipamentos"""
    __tablename__ = 'equipamentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(50), nullable=False, index=True)
    marca = Column(String(100))
    modelo = Column(String(100))
    quantidade = Column(Integer, nullable=False, default=0)
    condicao = Column(String(20), nullable=False, default="Novo")  # Novo ou Usado
    valor_unitario = Column(Float, default=0.0)
    observacoes = Column(Text)
    data_cadastro = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ativo = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Equipamento(codigo='{self.codigo}', nome='{self.nome}', quantidade={self.quantidade})>"
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'Código': self.codigo,
            'Nome': self.nome,
            'Categoria': self.categoria,
            'Marca': self.marca or '',
            'Modelo': self.modelo or '',
            'Quantidade': self.quantidade,
            'Condição': self.condicao,
            'Valor Unitário': self.valor_unitario,
            'Observações': self.observacoes or '',
            'Data Cadastro': self.data_cadastro,
            'Data Atualização': self.data_atualizacao,
            'Ativo': self.ativo
        }


class Movimentacao(Base):
    """Modelo para tabela de movimentações"""
    __tablename__ = 'movimentacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(20), nullable=False, index=True)  # Entrada ou Saída
    codigo = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(50), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    quantidade = Column(Integer, nullable=False)
    condicao = Column(String(20), nullable=False)
    valor_unitario = Column(Float, default=0.0)
    observacoes = Column(Text)
    data_movimentacao = Column(DateTime, default=datetime.now, index=True)
    usuario = Column(String(100))  # Usuário que fez a movimentação
    
    def __repr__(self):
        return f"<Movimentacao(tipo='{self.tipo}', codigo='{self.codigo}', quantidade={self.quantidade})>"
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'Tipo': self.tipo,
            'Código': self.codigo,
            'Nome': self.nome,
            'Categoria': self.categoria,
            'Marca': self.marca or '',
            'Modelo': self.modelo or '',
            'Quantidade': self.quantidade,
            'Condição': self.condicao,
            'Valor Unitário': self.valor_unitario,
            'Observações': self.observacoes or '',
            'Data': self.data_movimentacao,
            'Usuário': self.usuario or 'Sistema'
        }


class DatabaseConnection:
    """Gerenciador de conexão com o banco de dados"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            # Obter URL do banco de dados
            database_url = self._get_database_url()
            
            # Criar engine
            self._engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Verifica conexão antes de usar
                pool_recycle=3600,   # Recicla conexões a cada 1 hora
                echo=False           # Não mostrar SQL no console
            )
            
            # Criar session factory
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Criar tabelas se não existirem
            Base.metadata.create_all(self._engine)
            
            logger.info("✅ Conexão com banco de dados estabelecida com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
            raise
    
    def _get_database_url(self) -> str:
        """
        Obtém URL do banco de dados das variáveis de ambiente
        Suporta tanto DATABASE_URL quanto Streamlit secrets
        """
        # Tentar obter do ambiente
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Tentar obter do Streamlit secrets
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                    database_url = st.secrets['DATABASE_URL']
            except:
                pass
        
        if not database_url:
            # Fallback para SQLite local (desenvolvimento)
            database_url = "sqlite:///estoque_ti.db"
            logger.warning("⚠️ DATABASE_URL não encontrada, usando SQLite local para desenvolvimento")
        
        # Ajustar URL do PostgreSQL se necessário (Heroku/Railway)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        return database_url
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        if self._session_factory is None:
            self._initialize_connection()
        return self._session_factory()
    
    def get_engine(self):
        """Retorna o engine do banco de dados"""
        if self._engine is None:
            self._initialize_connection()
        return self._engine
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self._engine:
            self._engine.dispose()
            logger.info("🔌 Conexão com banco de dados fechada")


# Instância global
db_connection = DatabaseConnection()


def get_db_session():
    """
    Função helper para obter uma sessão do banco
    Usar com context manager: with get_db_session() as session:
    """
    session = db_connection.get_session()
    try:
        yield session
    finally:
        session.close()

