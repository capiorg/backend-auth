from passlib.context import CryptContext


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(secret=plain_password, hash=hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(secret=password)
