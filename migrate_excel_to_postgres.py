"""
Script de Migração: Excel → PostgreSQL
Dashboard Estoque TI

Este script migra os dados do Excel para o PostgreSQL
"""

import pandas as pd
from datetime import datetime
from loguru import logger
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.excel_service import ExcelService
from services.database_service import DatabaseService
from config.settings import settings


class MigradorExcelParaPostgres:
    """Migrador de dados do Excel para PostgreSQL"""
    
    def __init__(self):
        self.excel_service = ExcelService()
        self.db_service = DatabaseService()
        logger.info("🔄 Migrador inicializado")
    
    def migrar(self, limpar_banco_antes: bool = False) -> bool:
        """
        Executa a migração completa
        
        Args:
            limpar_banco_antes: Se True, limpa o banco antes de migrar
        
        Returns:
            True se migração bem-sucedida
        """
        try:
            logger.info("=" * 60)
            logger.info("🚀 INICIANDO MIGRAÇÃO: Excel → PostgreSQL")
            logger.info("=" * 60)
            
            # Carregar dados do Excel
            logger.info("\n📂 1/4 - Carregando dados do Excel...")
            df_estoque, df_movimentacoes = self.excel_service.carregar_dados()
            
            if df_estoque.empty and df_movimentacoes.empty:
                logger.warning("⚠️ Nenhum dado encontrado no Excel!")
                return False
            
            logger.info(f"   ✅ {len(df_estoque)} equipamentos encontrados")
            logger.info(f"   ✅ {len(df_movimentacoes)} movimentações encontradas")
            
            # Limpar banco se solicitado
            if limpar_banco_antes:
                logger.info("\n🗑️ 2/4 - Limpando banco de dados...")
                self.db_service.limpar_banco()
                logger.info("   ✅ Banco limpo!")
            else:
                logger.info("\n⏭️ 2/4 - Mantendo dados existentes no banco")
            
            # Migrar equipamentos
            logger.info("\n📦 3/4 - Migrando equipamentos...")
            sucesso_equipamentos = self._migrar_equipamentos(df_estoque)
            
            # Migrar movimentações
            logger.info("\n📋 4/4 - Migrando movimentações...")
            sucesso_movimentacoes = self._migrar_movimentacoes(df_movimentacoes)
            
            # Resultado
            logger.info("\n" + "=" * 60)
            if sucesso_equipamentos and sucesso_movimentacoes:
                logger.info("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            else:
                logger.warning("⚠️ MIGRAÇÃO CONCLUÍDA COM AVISOS")
            logger.info("=" * 60)
            
            # Exibir estatísticas
            self._exibir_estatisticas()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA MIGRAÇÃO: {str(e)}")
            return False
    
    def _migrar_equipamentos(self, df: pd.DataFrame) -> bool:
        """Migra equipamentos do DataFrame para o banco"""
        if df.empty:
            logger.warning("   ⚠️ Nenhum equipamento para migrar")
            return True
        
        try:
            sucesso_total = 0
            erro_total = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extrair dados
                    codigo = str(row.get('codigo_produto', '')).strip().upper()
                    nome = str(row.get('equipamento', '')).strip()
                    categoria = str(row.get('categoria', 'Outro')).strip()
                    marca = str(row.get('marca', '')).strip()
                    modelo = str(row.get('modelo', '')).strip()
                    quantidade = int(row.get('quantidade', 0))
                    condicao = str(row.get('condicao', 'Novo')).strip()
                    valor_unitario = float(row.get('valor_unitario', 0))
                    observacoes = str(row.get('observacoes', '')).strip()
                    
                    # Validar dados essenciais
                    if not codigo or not nome:
                        logger.warning(f"   ⚠️ Linha {idx+1}: Código ou nome vazio, pulando...")
                        continue
                    
                    # Verificar se já existe
                    existe = self.db_service.buscar_equipamento(codigo, condicao)
                    
                    if existe:
                        # Atualizar
                        sucesso = self.db_service.atualizar_equipamento(
                            codigo=codigo,
                            condicao=condicao,
                            quantidade=quantidade
                        )
                    else:
                        # Adicionar novo
                        sucesso = self.db_service.adicionar_equipamento(
                            codigo=codigo,
                            nome=nome,
                            categoria=categoria,
                            marca=marca,
                            modelo=modelo,
                            quantidade=quantidade,
                            condicao=condicao,
                            valor_unitario=valor_unitario,
                            observacoes=observacoes
                        )
                    
                    if sucesso:
                        sucesso_total += 1
                    else:
                        erro_total += 1
                        
                except Exception as e:
                    logger.error(f"   ❌ Erro na linha {idx+1}: {str(e)}")
                    erro_total += 1
            
            logger.info(f"   ✅ {sucesso_total} equipamentos migrados")
            if erro_total > 0:
                logger.warning(f"   ⚠️ {erro_total} erros encontrados")
            
            return erro_total == 0
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao migrar equipamentos: {str(e)}")
            return False
    
    def _migrar_movimentacoes(self, df: pd.DataFrame) -> bool:
        """Migra movimentações do DataFrame para o banco"""
        if df.empty:
            logger.warning("   ⚠️ Nenhuma movimentação para migrar")
            return True
        
        try:
            sucesso_total = 0
            erro_total = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extrair dados
                    tipo = str(row.get('tipo', 'Entrada')).strip()
                    codigo = str(row.get('codigo_produto', '')).strip().upper()
                    nome = str(row.get('equipamento', '')).strip()
                    categoria = str(row.get('categoria', 'Outro')).strip()
                    marca = str(row.get('marca', '')).strip()
                    modelo = str(row.get('modelo', '')).strip()
                    quantidade = int(row.get('quantidade', 0))
                    condicao = str(row.get('condicao', 'Novo')).strip()
                    valor_unitario = float(row.get('valor_unitario', 0))
                    observacoes = str(row.get('observacoes', '')).strip()
                    usuario = str(row.get('usuario', 'Sistema')).strip()
                    
                    # Validar dados essenciais
                    if not codigo or not nome:
                        continue
                    
                    # Registrar movimentação
                    sucesso = self.db_service.registrar_movimentacao(
                        tipo=tipo,
                        codigo=codigo,
                        nome=nome,
                        categoria=categoria,
                        marca=marca,
                        modelo=modelo,
                        quantidade=quantidade,
                        condicao=condicao,
                        valor_unitario=valor_unitario,
                        observacoes=observacoes,
                        usuario=usuario
                    )
                    
                    if sucesso:
                        sucesso_total += 1
                    else:
                        erro_total += 1
                        
                except Exception as e:
                    logger.error(f"   ❌ Erro na linha {idx+1}: {str(e)}")
                    erro_total += 1
            
            logger.info(f"   ✅ {sucesso_total} movimentações migradas")
            if erro_total > 0:
                logger.warning(f"   ⚠️ {erro_total} erros encontrados")
            
            return erro_total == 0
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao migrar movimentações: {str(e)}")
            return False
    
    def _exibir_estatisticas(self):
        """Exibe estatísticas do banco após migração"""
        try:
            logger.info("\n📊 ESTATÍSTICAS DO BANCO:")
            stats = self.db_service.obter_estatisticas()
            
            logger.info(f"   📦 Total de equipamentos: {stats['total_equipamentos']}")
            logger.info(f"   💰 Valor total do estoque: R$ {stats['valor_total']:,.2f}")
            
            logger.info("\n   📂 Por Categoria:")
            for cat, total in stats['por_categoria'].items():
                logger.info(f"      • {cat}: {total}")
            
            logger.info("\n   🏷️ Por Condição:")
            for cond, total in stats['por_condicao'].items():
                logger.info(f"      • {cond}: {total}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao exibir estatísticas: {str(e)}")


def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("🔄 MIGRADOR: Excel → PostgreSQL")
    print("   Dashboard Estoque TI")
    print("=" * 60)
    
    # Perguntar se deve limpar banco
    print("\n⚠️  ATENÇÃO: Esta operação vai migrar dados do Excel para PostgreSQL")
    print("\nOpções:")
    print("  1 - Migrar SEM limpar banco (adiciona/atualiza dados)")
    print("  2 - Migrar E LIMPAR banco antes (APAGA tudo e recria)")
    print("  0 - Cancelar")
    
    escolha = input("\nEscolha uma opção [1]: ").strip() or "1"
    
    if escolha == "0":
        print("\n❌ Migração cancelada!")
        return
    
    limpar = escolha == "2"
    
    if limpar:
        confirma = input("\n⚠️  CONFIRMA limpar banco? (digite 'SIM'): ").strip()
        if confirma != "SIM":
            print("\n❌ Migração cancelada!")
            return
    
    # Executar migração
    print("\n")
    migrador = MigradorExcelParaPostgres()
    sucesso = migrador.migrar(limpar_banco_antes=limpar)
    
    if sucesso:
        print("\n✅ Migração concluída! Seus dados agora estão no PostgreSQL.")
        print("\n💡 Próximos passos:")
        print("   1. Configure a variável DATABASE_URL no .env")
        print("   2. Atualize o app.py para usar EstoqueService com PostgreSQL")
        print("   3. Faça backup do Excel e arquive-o")
    else:
        print("\n❌ Migração falhou! Verifique os logs acima.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Executar migração
    main()

