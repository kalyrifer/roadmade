import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='postgres', database='roadmate_db')
cursor = conn.cursor()
cursor.execute('DELETE FROM users WHERE email = %s', ('test@test.com',))
conn.commit()
cursor.close()
conn.close()
print('Cleaned up')