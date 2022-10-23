from typing import Any, Dict, List, Optional, Union

from .cose_key_interface import COSEKeyInterface
from .recipient import Recipient
from .recipient_interface import RecipientInterface


class Recipients:
    """
    A Set of COSE Recipients.
    """

    def __init__(self, recipients: List[RecipientInterface], verify_kid: bool = False):
        self._recipients = recipients
        self._verify_kid = verify_kid
        return

    @classmethod
    def from_list(cls, recipients: List[Any], verify_kid: bool = False):
        """
        Create Recipients from a CBOR-like list.
        """
        res: List[RecipientInterface] = []
        for r in recipients:
            res.append(Recipient.from_list(r))
        return cls(res, verify_kid)

    def extract(
        self,
        keys: List[COSEKeyInterface],
        context: Optional[Union[Dict[str, Any], List[Any]]] = None,
        alg: int = 0,
    ) -> COSEKeyInterface:
        """
        Decodes an appropriate key from recipients or keys provided as a parameter ``keys``.
        """
        if not self._recipients:
            raise ValueError("No recipients.")
        err: Exception = ValueError("key is not found.")
        for r in self._recipients:
            if not r.kid and self._verify_kid:
                raise ValueError("kid should be specified in recipient.")
            if r.kid:
                for k in keys:
                    if k.kid != r.kid:
                        continue
                    try:
                        return r.extract(k, alg=alg, context=context)
                    except Exception as e:
                        err = e
                continue
            for k in keys:
                try:
                    return r.extract(k, alg=alg, context=context)
                except Exception as e:
                    err = e
        raise err

    def decrypt(
        self,
        keys: List[COSEKeyInterface],
        aad: bytes = b"",
        alg: int = 0,
        context: Optional[Union[Dict[str, Any], List[Any]]] = None,
        payload: bytes = b"",
        nonce: bytes = b"",
    ) -> bytes:

        """
        Decrypts the supplied payload.
        """
        if not self._recipients:
            raise ValueError("No recipients.")
        err: Exception = ValueError("key is not found.")
        for r in self._recipients:
            if not r.kid and self._verify_kid:
                raise ValueError("kid should be specified in recipient.")
            if r.kid:
                for k in keys:
                    if k.kid != r.kid:
                        continue
                    try:
                        return (
                            r.open(k, aad)
                            if r.alg == -1
                            else r.extract(k, alg=alg, context=context).decrypt(payload, nonce, aad)
                        )
                    except Exception as e:
                        err = e
                continue
            for k in keys:
                try:
                    return (
                        r.open(k, aad) if r.alg == -1 else r.extract(k, alg=alg, context=context).decrypt(payload, nonce, aad)
                    )
                except Exception as e:
                    err = e
        raise err
