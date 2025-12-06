# app.py
# 后台服务器总入口
#
# @author n1ghts4kura
# @date 25-12-6
#

"""后台服务器总入口。"""

from flask import Flask

from src.backend.data_collector import bp as dc_bp


def create_app() -> Flask:
	app = Flask(__name__)
	app.register_blueprint(dc_bp)
	return app


app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)


