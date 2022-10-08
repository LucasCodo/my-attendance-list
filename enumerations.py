from enum import Enum


class LicenseType(Enum):
    Free = "free"
    Monthly = "monthly"
    Yearly = "yearly"


class TransactionType(Enum):
    Bitcoin = "bitcoin"
    Lightning = "lightning"
    CreditCard = "credit"


class UserType(Enum):
    Teacher = "teacher"
    Student = "student"
    Organization = "organization"


if __name__ == "__main__":
    for a in map(lambda x: x.value, list(UserType)):
        print(a)
