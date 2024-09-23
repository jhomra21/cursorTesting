from gevent import monkey
monkey.patch_all()

from app import app, celery

if __name__ == '__main__':
    with app.app_context():
        celery.start()