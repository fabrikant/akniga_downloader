import base64
import hashlib

from Crypto.Cipher import AES  # from pycryptodomex v-3.10.4
from Crypto.Random import get_random_bytes

HASH_NAME = "SHA256"
IV_LENGTH = 16
SALT_LENGHT = 8
ITERATION_COUNT = 65536
KEY_LENGTH = 32


def pad(s):
    return s + (IV_LENGTH - len(s) % IV_LENGTH) * chr(IV_LENGTH - len(s) % IV_LENGTH)


def unpad(s):
    return s[0 : -ord(s[-1:])]


def get_secret_key(password, salt):
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt.encode(), ITERATION_COUNT, KEY_LENGTH
    )


def encrypt(password, salt, message):
    secret = get_secret_key(password, salt)
    message = pad(message)
    iv = get_random_bytes(IV_LENGTH)
    iv_string = iv.hex()
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    cipher_bytes = base64.b64encode(iv + cipher.encrypt(message.encode("utf8")))
    return bytes.decode(cipher_bytes), iv_string


def decrypt(password, salt, cipher_text):
    secret = get_secret_key(password, salt)
    decoded = base64.b64decode(cipher_text)
    iv = decoded[: AES.block_size]
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    original_bytes = unpad(cipher.decrypt(decoded[IV_LENGTH:]))
    return bytes.decode(original_bytes)


def get_akniga_encrypt_dict(password, message):
    salt = get_random_bytes(SALT_LENGHT).hex()
    ct, iv = encrypt(password, salt, message)

    result = {"ct": ct, "iv": iv, "s": salt}
    return result


if __name__ == "__main__":
    pass

    # hres = {
    #     "ct": "Ry18xl7z3QmCMcWRl8ySQ/CfETay0D92vOMzpeJR2q8MhP+BV5Pq2M9MrYSdTN0KiqsO35GrSoZQ4Zs9QQ1LmovheNMZwRZsKNMPUw3yYdLVrYM2INU9gZhMeF1B3KCO",
    #     "iv": "8441a7b2e15d055e43fe8a4a894719c8",
    #     "s": "9e4ad8ae010d7b96",
    # }

    # print(decrypt("ymXEKzvUkuo5G03.1C159BD535E9793", hres["s"], hres["ct"]))

# secret_text = "2e7b9e88a153fe407809c78d27a0e6d0"
# exmple_password = "ymXEKzvUkuo5G03.1C159BD535E9793"
# example_dict = {
#     "ct": "I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C",
#     "iv": "571529020e50abaff3cd66f5ed50bcbe",
#     "s": "959ba8e70ec66bc8",
# }

# print(get_akniga_encrypt_dict("ymXEKzvUkuo5G03.1C159BD535E9793", "2e7b9e88a153fe407809c78d27a0e6d0"))
# exit()

# f_salt = "959ba8e70ec66bc8"
# secret_key = "ymXEKzvUkuo5G03.1C159BD535E9793"
# plain_text = "2e7b9e88a153fe407809c78d27a0e6d0"

# cipherText, iv_string = encrypt(secret_key, f_salt, plain_text)
# print("CipherText: " + cipherText)

# decryptedMessage = decrypt(secret_key, f_salt, cipherText)
# print("DecryptedMessage: " + decryptedMessage)
