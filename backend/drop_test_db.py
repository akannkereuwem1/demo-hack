import psycopg2
conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'test_agronet_db' AND pid != pg_backend_pid()")
cur.execute("DROP DATABASE IF EXISTS test_agronet_db")
print("Dropped")
conn.close()
