from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_product_price_and_data(self, product):
        """
            This function will return a dict containing the price of the product variant with extra price.
        """
        self.ensure_one()
        product_infos=super(AccountMove,self)._get_product_price_and_data(product)
        product_infos['price']= product.lst_price if self.is_sale_document() else product.standard_price
        return product_infos
