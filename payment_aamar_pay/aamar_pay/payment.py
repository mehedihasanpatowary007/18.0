
import hashlib,logging,requests,json
from typing import Dict
from decimal import Decimal
from odoo.addons.payment_aamar_pay.aamar_pay import _constants as const
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

class AamarPay:
    aamarpay_is_sandbox: bool
    aamarpay_store_id: str
    aamarpay_signature_key: str
    aamarpay_session_api: str
    aamarpay_mode_name: str

    integration_data: Dict[str, str] = {}

    def __init__(self, aamarpay_is_sandbox=True, aamarpay_store_id='', aamarpay_signature_key='') -> None:
        self.set_aamarpay_mode(aamarpay_is_sandbox)
        self.aamarpay_is_sandbox = aamarpay_is_sandbox
        self.aamarpay_store_id = aamarpay_store_id or const.storeID
        self.aamarpay_signature_key = aamarpay_signature_key or const.signature
        self.aamarpay_session_api = (
            const.sandBoxUrl if aamarpay_is_sandbox else const.productionUrl
        )

    @staticmethod
    def set_aamarpay_mode(aamarpay_is_sandbox: bool) -> str:
        if aamarpay_is_sandbox is True or aamarpay_is_sandbox == 1:
            return 'sandbox'
        else:
            return 'securepay'


class AmarPaySession(AamarPay):

    def __init__(self, aamarpay_is_sandbox=True, aamarpay_store_id='', aamarpay_signature_key='') -> None:
        super().__init__(aamarpay_is_sandbox, aamarpay_store_id, aamarpay_signature_key)


    def set_urls(self, success_url: str, fail_url: str, cancel_url: str,ipn_url: str = '') -> None:
        self.integration_data['success_url'] = success_url
        self.integration_data['fail_url'] = fail_url
        self.integration_data['cancel_url'] = cancel_url
        self.integration_data['ipn_url'] = ipn_url

    def set_product_integration(self, tran_id: str,desc:str, amount: Decimal, currency: str, product_category: str, product_name: str, num_of_item: int, shipping_method: str, product_profile: str = 'None') -> None:
        self.integration_data['store_id'] = self.aamarpay_store_id
        self.integration_data['signature_key'] = self.aamarpay_signature_key
        self.integration_data['tran_id'] = tran_id
        self.integration_data['amount'] = amount
        self.integration_data['currency'] = currency
        self.integration_data['product_category'] = product_category
        self.integration_data['desc'] = desc
        self.integration_data['product_name'] = product_name
        self.integration_data['num_of_item'] = num_of_item
        self.integration_data['shipping_method'] = shipping_method
        self.integration_data['product_profile'] = product_profile

    def set_customer_info(self, name: str, email: str, mobile: str, address1: str = '', address2: str = '',
                        city: str = '', state: str = '', postcode: str = '', country: str = 'Bangladesh') -> None:
        self.integration_data['cus_name'] = name
        self.integration_data['cus_email'] = email
        self.integration_data['cus_phone'] = mobile
        self.integration_data['cus_add1'] = address1
        self.integration_data['cus_add2'] = address2
        self.integration_data['cus_city'] = city
        self.integration_data['cus_state'] = state
        self.integration_data['cus_postcode'] = postcode
        self.integration_data['cus_country'] = country

    def set_shipping_info(self, shipping_to: str, address: str, city: str, postcode: str, country: str) -> None:
        self.integration_data['ship_name'] = shipping_to
        self.integration_data['ship_add1'] = address
        self.integration_data['ship_city'] = city
        self.integration_data['ship_postcode'] = postcode
        self.integration_data['ship_country'] = country

    def set_additional_values(self, value_a: str = '', value_b: str = '', value_c: str = '', value_d: str = '') -> None:
        self.integration_data['opt_a'] = value_a
        self.integration_data['opt_b'] = value_b
        self.integration_data['opt_c'] = value_c
        self.integration_data['opt_d'] = value_d

    def init_payment(self) -> Dict[str, str]:
        """Initialize payment with AamarPay API"""

        _logger.info("Initialize payment with AamarPay API")
        try:
            if isinstance(self.integration_data.get('amount'), Decimal):
                self.integration_data['amount'] = str(self.integration_data['amount'])

            # Always request JSON if supported
            self.integration_data['type'] = 'json'
            _logger.info("All Integration Data ::::: %s",self.integration_data)
            response = requests.post(
                self.aamarpay_session_api,
                json=self.integration_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30,
            )
            _logger.info(response)
            _logger.error("AAMARPAY API URL => %s", self.aamarpay_session_api)
            _logger.error(
                "AAMARPAY ENV => provider_state=%s | store_id=%s",
                self.env["payment.provider"].browse(self.provider_id.id).state if hasattr(self, "provider_id") else "unknown",
                self.integration_data.get("store_id"),
            )

          

            # response = requests.post(self.aamarpay_session_api, data=self.integration_data)

            if response.status_code == 200:
                # Try JSON first
                try:
                    response_json = response.json()
                    if isinstance(response_json, dict) and "payment_url" in response_json:
                        _logger.info("PAYMENT URL ::::: %s",response_json["payment_url"])
                        return {"status": "SUCCESS", "payment_url": response_json["payment_url"]}
                except ValueError:
                    pass

                # Fallback: parse HTML response

                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form", {"name": "redirectpost"})
                if form and form.get("action"):
                    return {"status": "SUCCESS", "payment_url": form["action"]}

                return {"status": "FAILED", "error": f"Invalid response: {response.text}"}
            else:
                return {"status": "FAILED", "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}




class AamarPayValidation(AamarPay):
    """Optional Validation Class if AamarPay supports validation API"""
    def __init__(self, aamarpay_is_sandbox=True, aamarpay_store_id='', aamarpay_signature_key='') -> None:
        super().__init__(aamarpay_is_sandbox, aamarpay_store_id, aamarpay_signature_key)


    def validate_transaction(self, transaction_id: str) -> Dict[str, str]:
        """Check transaction status from AamarPay API"""
        # AamarPay does not provide detailed validation endpoint in docs,
        # But if provided, implement like below:
        query_params = {
            "store_id": self.aamarpay_store_id,
            "tran_id": transaction_id,
            "signature_key": self.aamarpay_signature_key,
            "type": "json"
        }
        _logger.info("Query Params :::: ",query_params)
        try:
            validation_response = requests.get(self.aamarpay_session_api, params=query_params)
            if validation_response.status_code == 200:
                return {"status": "SUCCESS", "data": validation_response.json()}
            else:
                return {"status": "FAILED", "error": validation_response.text}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def validate_ipn_hash(self, ipn_data):
        if self.key_check(ipn_data, 'verify_key') and self.key_check(ipn_data, 'verify_sign'):
            check_params: Dict[str, str] = {}
            verify_key = ipn_data['verify_key'].split(',')

            for key in verify_key:
                check_params[key] = ipn_data[key]

            store_pass = self.sslc_store_pass.encode()
            store_pass_hash = hashlib.md5(store_pass).hexdigest()
            check_params['aamarpay_signature_key'] = store_pass_hash
            check_params = self.sort_keys(check_params)

            sign_string = ''
            for key in check_params:
                sign_string += key[0] + '=' + str(key[1]) + '&'

            sign_string = sign_string.strip('&')
            sign_string_hash = hashlib.md5(sign_string.encode()).hexdigest()

            if sign_string_hash == ipn_data['verify_sign']:
                return True
            return False

    @staticmethod
    def key_check(data_dict, check_key):
        if check_key in data_dict.keys():
            return True
        return False

    @staticmethod
    def sort_keys(data_dict):
        return [(key, data_dict[key]) for key in sorted(data_dict.keys())]
