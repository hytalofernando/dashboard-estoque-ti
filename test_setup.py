"""
Script de Teste - Dashboard Estoque TI
Verifica se o sistema está configurado corretamente
"""

import os
import sys
from loguru import logger

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO")

def test_imports():
    """Testa se todas as importações necessárias estão disponíveis"""
    logger.info("=" * 60)
    logger.info("🧪 TESTE 1: Verificando Importações")
    logger.info("=" * 60)
    
    try:
        import streamlit
        logger.info("✅ Streamlit OK")
    except ImportError as e:
        logger.error(f"❌ Streamlit não encontrado: {e}")
        return False
    
    try:
        import pandas
        logger.info("✅ Pandas OK")
    except ImportError as e:
        logger.error(f"❌ Pandas não encontrado: {e}")
        return False
    
    try:
        import sqlalchemy
        logger.info("✅ SQLAlchemy OK")
    except ImportError as e:
        logger.error(f"❌ SQLAlchemy não encontrado: {e}")
        return False
    
    try:
        import psycopg2
        logger.info("✅ psycopg2 OK")
    except ImportError as e:
        logger.warning(f"⚠️  psycopg2 não encontrado (OK se usar SQLite): {e}")
    
    return True


def test_models():
    """Testa se os modelos do banco de dados estão OK"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TESTE 2: Verificando Modelos do Banco")
    logger.info("=" * 60)
    
    try:
        from models.database_models import Equipamento, Movimentacao, Base, db_connection
        logger.info("✅ Modelos do banco importados com sucesso")
        
        # Verificar se as tabelas têm os campos esperados
        equipamento_columns = [c.name for c in Equipamento.__table__.columns]
        logger.info(f"   📋 Equipamento tem {len(equipamento_columns)} colunas")
        
        movimentacao_columns = [c.name for c in Movimentacao.__table__.columns]
        logger.info(f"   📋 Movimentacao tem {len(movimentacao_columns)} colunas")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao importar modelos: {e}")
        return False


def test_services():
    """Testa se os serviços estão OK"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TESTE 3: Verificando Serviços")
    logger.info("=" * 60)
    
    try:
        from services import EstoqueService, get_service_info
        logger.info("✅ EstoqueService importado com sucesso")
        
        # Obter informações do serviço
        service_info = get_service_info()
        logger.info(f"   📊 Tipo de banco: {service_info['tipo']}")
        logger.info(f"   🔧 Backend: {service_info['backend']}")
        logger.info(f"   💾 Persistente: {service_info.get('persistente', False)}")
        
        if service_info.get('aviso'):
            logger.warning(f"   {service_info['aviso']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao importar serviços: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Testa conexão com o banco de dados"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TESTE 4: Testando Conexão com Banco")
    logger.info("=" * 60)
    
    try:
        from services import get_service_info
        service_info = get_service_info()
        
        # Se for PostgreSQL/SQLite, tentar conectar
        if service_info['tipo'] in ['PostgreSQL', 'SQLite']:
            from services.database_service import DatabaseService
            
            db_service = DatabaseService()
            logger.info("✅ DatabaseService inicializado")
            
            # Tentar obter estatísticas
            stats = db_service.obter_estatisticas()
            logger.info(f"   📦 Total de equipamentos: {stats['total_equipamentos']}")
            logger.info(f"   💰 Valor total do estoque: R$ {stats['valor_total']:,.2f}")
            
            if stats['por_categoria']:
                logger.info("   📂 Categorias encontradas:")
                for cat, total in stats['por_categoria'].items():
                    logger.info(f"      • {cat}: {total}")
            
        else:
            logger.info("📊 Usando Excel - Conexão com banco não aplicável")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_estoque_service():
    """Testa o EstoqueService completo"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TESTE 5: Testando EstoqueService Completo")
    logger.info("=" * 60)
    
    try:
        from services import EstoqueService
        
        # Inicializar serviço
        estoque_service = EstoqueService()
        logger.info("✅ EstoqueService instanciado com sucesso")
        
        # Testar obter equipamentos
        df = estoque_service.obter_equipamentos()
        logger.info(f"   📊 DataFrame retornado: {len(df)} linhas")
        
        if not df.empty:
            logger.info(f"   📋 Colunas: {list(df.columns)}")
            logger.info(f"   ✅ Total de equipamentos: {df['quantidade'].sum()}")
        else:
            logger.warning("   ⚠️  Nenhum equipamento encontrado (banco vazio)")
        
        # Testar estatísticas
        stats = estoque_service.obter_estatisticas()
        logger.info(f"   📊 Estatísticas obtidas com sucesso")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar EstoqueService: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    logger.info("\n")
    logger.info("🚀" * 30)
    logger.info("DASHBOARD ESTOQUE TI - TESTE DE CONFIGURAÇÃO")
    logger.info("🚀" * 30)
    logger.info("\n")
    
    # Exibir configuração do ambiente
    logger.info("🔧 Configuração do Ambiente:")
    logger.info(f"   DATABASE_URL: {'✅ Configurada' if os.getenv('DATABASE_URL') else '❌ Não configurada'}")
    logger.info(f"   USE_POSTGRES: {os.getenv('USE_POSTGRES', 'Não definida')}")
    logger.info("\n")
    
    # Executar testes
    results = []
    
    results.append(("Importações", test_imports()))
    results.append(("Modelos do Banco", test_models()))
    results.append(("Serviços", test_services()))
    results.append(("Conexão com Banco", test_database_connection()))
    results.append(("EstoqueService", test_estoque_service()))
    
    # Resumo
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{status} - {test_name}")
    
    logger.info("\n")
    logger.info(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("\n")
        logger.info("🎉" * 30)
        logger.info("✅ TODOS OS TESTES PASSARAM!")
        logger.info("✅ O sistema está pronto para uso!")
        logger.info("🎉" * 30)
        logger.info("\n")
        logger.info("🚀 Para iniciar o dashboard:")
        logger.info("   streamlit run app.py")
        return True
    else:
        logger.error("\n")
        logger.error("❌" * 30)
        logger.error(f"❌ {total - passed} TESTE(S) FALHARAM!")
        logger.error("❌ Verifique os erros acima")
        logger.error("❌" * 30)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

