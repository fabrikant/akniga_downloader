from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import hashlib

from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes


secret_text = "2e7b9e88a153fe407809c78d27a0e6d0"
exmple_password = b"ymXEKzvUkuo5G03.1C159BD535E9793"
example_dict = {
    "ct": "I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C",
    "iv": "571529020e50abaff3cd66f5ed50bcbe",
    "s": "959ba8e70ec66bc8",
}


def bytesToKey(salt, password):
    data = b""
    tmp = b""
    while len(data) < 48:
        md5 = MD5.new()
        md5.update(tmp + password + salt)
        tmp = md5.digest()
        data += tmp
    return data


def decrypt(password, decryptdict):
    ciphertext = base64.b64decode(decryptdict["ct"])
    salt = bytes.fromhex(decryptdict["s"])
    keyIv = bytesToKey(salt, password)
    key = keyIv[:32]
    iv = keyIv[32:]  # from key derivation
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decryptedstring = unpad(cipher.decrypt(ciphertext), 16)

    decrypt_string = decryptedstring.decode("utf8")
    print(decrypt_string)  # The quick brown fox jumps over the lazy dog
    if secret_text in decrypt_string:
        print("YES")
    else:
        print("NO")


HASH_NAME = "SHA256"
IV_LENGTH = 16
ITERATION_COUNT = 65536
KEY_LENGTH = 32


def pad(s):
    return s + (IV_LENGTH - len(s) % IV_LENGTH) * chr(IV_LENGTH - len(s) % IV_LENGTH)


# def unpad(s):
#     return s[0 : -ord(s[-1:])]


def get_secret_key(password, salt):
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt.encode(), ITERATION_COUNT, KEY_LENGTH
    )


def encrypt(password, salt, message):
    secret = get_secret_key(password, salt)
    message = pad(message)
    iv = get_random_bytes(IV_LENGTH)

    iv_string = base64.b64encode(iv).decode()
    print(f"iv {iv_string}")

    cipher = AES.new(secret, AES.MODE_CBC, iv)
    cipher_bytes = base64.b64encode(iv + cipher.encrypt(message.encode("utf8")))
    cipcher_message = bytes.decode(cipher_bytes)
    print(cipcher_message)
    return cipcher_message, iv_string


salt = "959ba8e70ec66bc8"
cipcher_message, iv_string = encrypt(exmple_password.decode(), salt, secret_text)

sample_dict = {
    "ct": cipcher_message,
    "iv": iv_string,
    "s": salt,
}
decrypt(exmple_password, sample_dict)


# # #"2e7b9e88a153fe407809c78d27a0e6d0"
# # # "{\"ct\":\"I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C\",\"iv\":\"571529020e50abaff3cd66f5ed50bcbe\",\"s\":\"959ba8e70ec66bc8\"}"
# def get_hash(security_ls_key):
#     assets = "ymXEKzvUkuo5G03.1C159BD535E9793"
#     cipher = AES.new(security_ls_key.encode("utf8"), AES.MODE_EAX)
#     ciphertext, tag = cipher.encrypt_and_digest(assets.encode())
#     nonce = cipher.nonce
#     # print(b64encode(ciphertext).decode())
#     # print(b64encode(nonce).decode())
#     # print(b64encode(tag).decode())

#     key = "959ba8e70ec66bc8".encode()
#     ciphertext = "I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C".encode()
#     nonce= "571529020e50abaff3cd66f5ed50bcbe".encode()

#     cipher = AES.new(key, AES.MODE_EAX)
#     plaintext = cipher.decrypt_and_verify(ciphertext)

#     print(b64encode(ciphertext).decode())
#     #CSwHy3ir3MZ7yvZ4CzHbgYOsKgzhMqjq6wEuutU7vJJTJ0c38ExWkAY1QkLO
#     print(plaintext.decode())

# if __name__ == "__main__":

#     get_hash("2e7b9e88a153fe407809c78d27a0e6d0")
