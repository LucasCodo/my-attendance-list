import Lnpay
import pyqrcode
import os

Public = Lnpay.Public()
Public.importkey(os.environ['public_lnpay_api_key'])
Wallet = Lnpay.Wallet()
keys = {'wallet_read': str(os.environ['wallet_read']),
        'wallet_id': str(os.environ['wallet_id']),
        'wallet_invoice': str(os.environ['wallet_invoice']),
        'wallet_admin': str(os.environ['wallet_admin'])}

Wallet.importkeys(keys)


def get_invoice(num_satoshis: int = 2, passthru: dict = None, memo: str = '', expiry: int = 600):
    if passthru is None:
        passthru = {}
    return Wallet.newinvoice(num_satoshis, passthru, memo, expiry)


def invoice_qrcode(invoice: dict):
    myqr = pyqrcode.create(str(invoice["payment_request"]))
    return myqr.png_as_base64_str(scale=6)


def been_invoice_paid(invoice_id: str) -> bool:
    node = Lnpay.Lntx()
    status = node.status(invoice_id)
    return bool(status["settled"])


if __name__ == "__main__":
    invoice = get_invoice()
    node = Lnpay.Lntx()
    print(been_invoice_paid(invoice["id"]))
