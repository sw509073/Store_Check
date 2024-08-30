from app import create_app, db
from app.routes import bp  # Make sure 'bp' is correctly imported

app = create_app()

# Register the blueprint
app.register_blueprint(bp, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)
