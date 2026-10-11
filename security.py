import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')  #convert to raw bytes; utf-8 -> char encoding into binary
    salt = bcrypt.gensalt()    #random seq of bytes appended to the password before hashing (for same passwords)
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)  #hashed, one-way (can't be reversed)
    return hashed_password.decode('utf-8')  #reconvert to text string

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(     #extracts the og salt and cost parameter embeddings in the hashed, hashes the submitted pw and compares
        plain_password.encode('utf-8'),    #user entered
        hashed_password.encode('utf-8')    #stored in db
    )