"""
Serviço para operações com Excel
"""

import pandas as pd
import os
from typing import Tuple, Optional
from loguru import logger
from config.settings import settings

class ExcelService:
    """Serviço para gerenciar dados no Excel"""
    
    def __init__(self):
        self.excel_file = settings.EXCEL_FILE
        self.sheet_estoque = settings.SHEET_ESTOQUE
        self.sheet_movimentacoes = settings.SHEET_MOVIMENTACOES
    
    def carregar_dados(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Carrega dados do Excel ou cria arquivo se não existir"""
        try:
            if os.path.exists(self.excel_file):
                logger.info(f"Carregando dados do arquivo {self.excel_file}")
                df_estoque = pd.read_excel(self.excel_file, sheet_name=self.sheet_estoque)
                df_movimentacoes = pd.read_excel(self.excel_file, sheet_name=self.sheet_movimentacoes)
                
                # Migrar dados se necessário
                if 'codigo_produto' not in df_estoque.columns:
                    logger.info("Migrando dados para incluir código do produto")
                    df_estoque = self._migrar_dados(df_estoque)
                    self.salvar_dados(df_estoque, df_movimentacoes)
                
                return df_estoque, df_movimentacoes
            else:
                logger.info("Criando arquivo Excel inicial com dados de exemplo")
                return self._criar_dados_iniciais()
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return self._criar_dados_iniciais()
    
    def _migrar_dados(self, df_estoque: pd.DataFrame) -> pd.DataFrame:
        """Migra dados existentes para incluir código do produto"""
        codigos = []
        for idx, row in df_estoque.iterrows():
            categoria = row['categoria']
            marca = row['marca']
            prefixo = settings.PREFIXOS_CODIGO.get(categoria, 'OUT')
            codigo = f"{prefixo}-{marca.upper()}-{idx+1:03d}"
            codigos.append(codigo)
        
        df_estoque['codigo_produto'] = codigos
        return df_estoque
    
    def _criar_dados_iniciais(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Cria estrutura inicial do Excel com dados de exemplo"""
        df_estoque = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'equipamento': ['Notebook Dell Latitude', 'Monitor LG 24"', 'Impressora HP LaserJet', 'Switch Cisco 24P', 'Servidor Dell PowerEdge'],
            'categoria': ['Notebook', 'Monitor', 'Impressora', 'Rede', 'Servidor'],
            'marca': ['Dell', 'LG', 'HP', 'Cisco', 'Dell'],
            'modelo': ['Latitude 5520', '24ML600', 'LaserJet Pro', 'Catalyst 2960', 'PowerEdge R740'],
            'codigo_produto': ['NB-DELL-001', 'MON-LG-002', 'IMP-HP-003', 'SW-CISCO-004', 'SRV-DELL-005'],
            'quantidade': [15, 25, 8, 12, 3],
            'valor_unitario': [3500.00, 800.00, 1200.00, 2500.00, 15000.00],
            'data_chegada': ['2024-01-15', '2024-02-10', '2024-01-20', '2024-03-05', '2024-02-28'],
            'fornecedor': ['Dell Brasil', 'LG Electronics', 'HP Brasil', 'Cisco Systems', 'Dell Brasil'],
            'status': ['Disponível', 'Disponível', 'Disponível', 'Disponível', 'Disponível']
        })
        
        df_movimentacoes = pd.DataFrame({
            'id': [1, 2, 3],
            'equipamento_id': [1, 2, 3],
            'tipo_movimentacao': ['Entrada', 'Saída', 'Entrada'],
            'quantidade': [15, 5, 8],
            'data_movimentacao': ['2024-01-15', '2024-02-15', '2024-01-20'],
            'destino_origem': ['Fornecedor: Dell Brasil', 'Loja: Shopping Center', 'Fornecedor: HP Brasil'],
            'observacoes': ['Compra inicial', 'Transferência para loja', 'Compra inicial']
        })
        
        self.salvar_dados(df_estoque, df_movimentacoes)
        return df_estoque, df_movimentacoes
    
    def salvar_dados(self, df_estoque: pd.DataFrame, df_movimentacoes: pd.DataFrame) -> bool:
        """Salva dados no Excel"""
        try:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                df_estoque.to_excel(writer, sheet_name=self.sheet_estoque, index=False)
                df_movimentacoes.to_excel(writer, sheet_name=self.sheet_movimentacoes, index=False)
            logger.info(f"Dados salvos com sucesso em {self.excel_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return False
    
    def backup_dados(self) -> Optional[str]:
        """Cria backup dos dados"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_estoque_{timestamp}.xlsx"
            
            if os.path.exists(self.excel_file):
                import shutil
                shutil.copy2(self.excel_file, backup_file)
                logger.info(f"Backup criado: {backup_file}")
                return backup_file
            return None
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None 