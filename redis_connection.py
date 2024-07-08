import redis
from environs import Env

env = Env()
env.read_env()

redis_host = env.str("REDIS_HOST", 'localhost')
redis_port = env.int("REDIS_PORT", '6379')
redis_db = env.int("REDIS_DB", '0')

pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
r = redis.Redis(connection_pool=pool)
