import environ

env = environ.Env()
environ.Env.read_env()

BASE_URL = env("BASE_URL")
