import os

from management import client

if __name__ == '__main__':
    client.run(os.environ['TRIGOBOT_ACCESS_TOKEN'])
