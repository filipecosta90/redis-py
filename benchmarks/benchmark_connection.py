#!/usr/bin/env python3
import os

import pyperf
from redis import Redis, BlockingConnectionPool

# ------------------------------------------------------
# benchmark definitions
# ------------------------------------------------------


def pool_get_connection(pool):
    conn = pool.get_connection("GET")
    pool.release(conn)

def pool_get_connection_get_set(pool, key):
    conn = pool.get_connection("GET")
    conn.send_command("GET", key)
    value = conn.read_response()
    conn.send_command("SET", key, value)
    conn.read_response()
    pool.release(conn)


def redis_get_set(redis_conn, key):
    value = redis_conn.get(key)
    redis_conn.set(key, value)


# ------------------------------------------------------
# benchmark runner
# ------------------------------------------------------

host = os.getenv('HOST','localhost')
port = os.getenv('PORT','6379')
password = os.getenv('PASS',None)
runner = pyperf.Runner()
pool = BlockingConnectionPool(host=host, port=port, password=password)
redis_conn = Redis(host=host, port=port, password=password, connection_pool=pool)
key = "key"
value = "value"
redis_conn.set(key, value)

runner.bench_func("BlockingConnectionPool_get_connection()", pool_get_connection, pool)

runner.bench_func(
    "BlockingConnectionPool_get_connection()_get()_set()",
    pool_get_connection_get_set,
    pool,
    key,
)
runner.bench_func("Redis_get()_set()", redis_get_set, redis_conn, key)
