import os
from url_shortener import create_app

app = create_app()

if __name__ == '__main__':
    app.run()