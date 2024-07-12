import redis


def get_redis_connection(redis_host, redis_port, redis_db):
    pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
    r = redis.Redis(connection_pool=pool)
    return r
