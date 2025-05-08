Python 3.13.3 (v3.13.3:6280bb54784, Apr  8 2025, 10:47:54) [Clang 15.0.0 (clang-1500.3.9.4)] on darwin
Enter "help" below or click "Help" above for more information.
>>> from flask import Flask
... from threading import Thread
... import os
... 
... app = Flask(__name__)
... 
... @app.route('/')
... def home():
...     return "Bot is alive!"
... 
... def run():
...     port = int(os.environ.get("PORT", 8080))  # Required by Render
...     app.run(host="0.0.0.0", port=port)
... 
... def keep_alive():
...     t = Thread(target=run)
