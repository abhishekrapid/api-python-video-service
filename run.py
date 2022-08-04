from extensions import (
    app,
    os
)

from app.controller.service_controller import api

#import logging

#logging.basicConfig(level=logging.DEBUG)

#app.logger.setLevel(logging.INFO)


# register the api
app.register_blueprint(api)

if __name__ == '__main__':
    #  app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # app.config['SECRET_KEY'] = 'testing1234567890e3r3deget5g5g5gl5glktl5k5t5ere'
    app.config['SECRET_KEY'] = "gptmwojm13uxinoe3e3r3!"
    app.run('localhost', 8080, debug=True)