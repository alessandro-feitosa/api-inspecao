import bcrypt

senha_text = 'nivia'.encode('utf-8')
print(f'Passo 1: {senha_text}')

salt = bcrypt.gensalt()
senha_hash_bytes = bcrypt.hashpw(senha_text, salt)
print(f'Passo 2: {senha_hash_bytes}')

senha_hash_str = senha_hash_bytes.decode('utf-8')
print(f'Passo 3: {senha_hash_str}')
    