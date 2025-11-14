from flask import Flask, render_template
from config import Config
from extensions import db

def create_app(config_class=Config):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões com app
    db.init_app(app)
    
    # Registrar blueprints (rotas)
    from routes import main, escolas, alunos, disciplinas, historicos, gestores, amparos_legais
    
    app.register_blueprint(main.bp)
    app.register_blueprint(escolas.bp)
    app.register_blueprint(alunos.bp)
    app.register_blueprint(disciplinas.bp)
    app.register_blueprint(historicos.bp)
    app.register_blueprint(gestores.bp)
    app.register_blueprint(amparos_legais.bp)
    
    # Criar banco de dados se não existir
    with app.app_context():
        # Importar models para criar tabelas
        from models import Escola, Aluno, DisciplinaHistorica, Historico, Gestor
        db.create_all()
    
    # Rota de erro 404
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    # Rota de erro 500
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
