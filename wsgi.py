from app import app, init_db

if __name__ == "__main__":
    from waitress import serve
    init_db()
    serve(app, host='0.0.0.0', port=8080, threads=4)
