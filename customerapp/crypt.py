from binascii import unhexlify
from Crypto.Cipher import AES

BLOCK_SIZE = 16


def get_cipher_text_value(s):
    """
    this function using to split text to sub text
    @param s: the all text
    @return: return text
    """
    return (s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode("utf8")


def get_unpad_text_value(s):
    """
    this function using to split text to sub text
    @param s: the all text
    @return: return text
    """
    return s[:-ord(s[len(s) - 1:])]


def encrypt(plain_text, private_key, iv):
    """
    this function is used to encryption text using ase algorithm
    @param plain_text: the text for encryption
    @param private_key: this used to get private key value
    @param iv: the mode this used to get initialization vector value
    @return: encryption
    """
    raw = get_cipher_text_value(plain_text)
    cipher = AES.new(private_key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(raw).hex()


def decrypt(enc, private_key, iv):
    """
    this function is used to encryption text using ase algorithm
    @param enc: the text for encryption
    @param private_key: this used to get private key value
    @param iv: the mode this used to get initialization vector value
    @return: encryption
    """
    enc = unhexlify(enc)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return get_unpad_text_value(cipher.decrypt(enc)).decode('utf-8')
