# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import requests
import json
from datetime import datetime


_logger = logging.getLogger(__name__)

class SteadfastAccount(models.Model):
    _name='betopia.steadfast.account'
    _description='Betopia Steadfast Account'

    name = fields.Char(string="Account Name", required=True)
    api_key = fields.Char(string="API Key", required=True)
    secret_key = fields.Char(string="Secret Key", required=True)
    base_url = fields.Char(string="Base URL", required=True, default="https://portal.packzy.com/api/v1")
    steadfast_ids = fields.One2many('betopia.steadfast', 'steadfast_account_id', string="Steadfast Orders")

    pricing_ids = fields.One2many(
        comodel_name="betopia.steadfast.pricing",  # your pricing model
        inverse_name="account_id",                 # field in pricing model pointing to account
        string="Bangladesh Pricing Rules"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SteadfastAccount, self).default_get(fields_list)

        # Pre-fill One2many pricing lines
        res['pricing_ids'] = [
            (0, 0, {
                'weight_min': 0,
                'weight_max': 1,
                'base_cost': 60,
                'zone_extra': 20,
                'speed_extra': 40,
                'cod_percent': 1
            }),
            (0, 0, {
                'weight_min': 1.1,
                'weight_max': 2,
                'base_cost': 90,
                'zone_extra': 30,
                'speed_extra': 50,
                'cod_percent': 1
            }),
            (0, 0, {
                'weight_min': 2.1,
                'weight_max': 5,
                'base_cost': 150,
                'zone_extra': 50,
                'speed_extra': 80,
                'cod_percent': 1.5
            }),
            (0, 0, {
                'weight_min': 5.1,
                'weight_max': 10,
                'base_cost': 250,
                'zone_extra': 80,
                'speed_extra': 100,
                'cod_percent': 2
            }),
            (0, 0, {
                'weight_min': 10.1,
                'weight_max': 9999,
                'base_cost': 400,
                'zone_extra': 100,
                'speed_extra': 150,
                'cod_percent': 2
            }),
        ]

        _logger.info("Default get result for SteadfastAccount: %s", res)

        return res


class SteadfastModel(models.Model):

    _name = 'betopia.steadfast'
    _description = 'Betopia Steadfast Model'
    name = fields.Char(string="Order Reference", required=True)
    sale_order_id = fields.Many2one('sale.order')
    invoice = fields.Char(string="Invoice Number", required=True)
    tracking = fields.Char(string="Tracking Number", required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], string="Status", required=True, default="pending")
    steadfast_account_id = fields.Many2one('betopia.steadfast.account', string="Steadfast Account")
    date_ordered = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    date_shipped = fields.Datetime(string="Shipped Date")
    history_line_ids = fields.One2many('betopia.steadfast.history', 'steadfast_id', string="History")


    @api.depends('name')
    def set_sale_order_id(self):
        self.sale_order_id = self.env['sale.order'].sudo().search([('name','=',self.name)])

    def action_send_to_steadfast(self):

        for record in self:
            order = self.env['sale.order'].search([('steadfast_id', '=', record.id)], limit=1)
            if not order.partner_id:
                raise UserError(_("Customer information is missing."))

            api_key = record.steadfast_account_id.api_key
            secret_key = record.steadfast_account_id.secret_key
            base_url = record.steadfast_account_id.base_url
            if not api_key or not secret_key:
                raise UserError(_("Please configure Steadfast API keys in Settings."))
            url = f"{base_url}/create_order"

            payload = {
                "invoice": order.name,
                "recipient_name": order.partner_id.name,
                "recipient_phone": order.partner_id.phone or order.partner_id.mobile,
                "recipient_address": order.partner_id.contact_address or order.partner_id.street,
                "cod_amount": order.amount_total,
                "note": order.note or "",
            }

            headers = {
                "Api-Key": api_key,
                "Secret-Key": secret_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)

            if response.status_code != 200:
                raise UserError(_("Steadfast API Error: %s") % response.text)

            result = response.json()


            if result.get("status") == 200:
                consignment = result.get("consignment", {})
                order.write({
                    'steadfast_consignment_id': consignment.get("consignment_id"),
                    'steadfast_tracking_code': consignment.get("tracking_code"),
                    'steadfast_status': consignment.get("status"),
                    'steadfast_sent': True,
                })
                self.tracking = consignment.get("tracking_code")

                created_at = datetime.fromisoformat(result['consignment']['created_at'].replace("Z", ""))
                updated_at = datetime.fromisoformat(result['consignment']['updated_at'].replace("Z", ""))
                created_at = created_at.replace(tzinfo=None)
                updated_at = updated_at.replace(tzinfo=None)

                self.env['betopia.steadfast.history'].create({
                    'steadfast_id': self.id,
                    'consignment_id': consignment.get("consignment_id"),
                    'invoice': order.name,
                    'tracking_code': consignment.get("tracking_code"),
                    'status': consignment.get("status"),
                    'created_at': created_at,
                    'updated_at': updated_at,
                })

            else:
                raise UserError(_("Failed to create order in Steadfast: %s") % result.get("message"))


    #Acction tracking

    def action_show_tracking(self, api_response):

        Tracking = self.env['betopia.steadfast.tracking']
        Line = self.env['betopia.steadfast.tracking.line']

        tracking_data = api_response['result']
        tracking_lines = api_response['trackings']

        tracking = Tracking.create({
            'consignment_id': tracking_data['id'],
            'customer_name': tracking_data['cus_name'],
            'customer_address': tracking_data['cus_address'],
            'customer_phone': tracking_data['cus_phone'],
            'cod_amount': tracking_data['cod_amount'],
            'current_hub': tracking_data['currenthub']['name'] if tracking_data.get('currenthub') else '',
            'rider_name': tracking_data['rider']['name'] if tracking_data.get('rider') else '',
            'rider_phone': tracking_data['rider']['phone'] if tracking_data.get('rider') else '',
            'status': tracking_data['status'],
        })

        for line in tracking_lines:

            api_date = line['created_at']
            if api_date:
                dt_obj = datetime.strptime(api_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted_date = False
            Line.create({
                'tracking_id': tracking.id,
                'message': line['text'],
                'created_at': formatted_date,
                'deliveryman': line['deliveryman']['name'] if line.get('deliveryman') else '',
            })


    #Tracking acction start from here

    def action_fetch_and_show_tracking(self):

        if not self.tracking:
            raise UserError(_("Please set tracking code first"))
        url=f"https://steadfast.com.bd/track/consignment/{self.tracking}"
        api_key = self.steadfast_account_id.api_key
        secret_key = self.steadfast_account_id.secret_key
        base_url = self.steadfast_account_id.base_url
        if not api_key and not secret_key:
            raise UserError(_("Please configure Steadfast Api keys in Setting"))

        headers = {
            "Api-Key": api_key,
            "Secret-Key": secret_key,
            "Content-Type": "application/json"
           }

        try:
           response = requests.get(url, headers=headers, timeout=10)

        except requests.exceptions.RequestException as e :
            raise UserError(_("Failed to connect to Steadfast API: %s") % str(e))
        try:
            api_response = response.json()
        except json.JSONDecodeError:
            raise UserError(_("Invalid response from API."))

        self.action_show_tracking(api_response)

        tracking_model = self.env['betopia.steadfast.tracking']
        tracking = tracking_model.search([('consignment_id', '=', api_response['result']['id'])], limit=1)

        return {
            'name': _("Steadfast Tracking"),
            'type': 'ir.actions.act_window',
            'res_model': 'betopia.steadfast.tracking',
            'view_mode': 'form',
            'res_id': tracking.id,
            'target': 'current',
        }


class InheritedSaleOrder(models.Model):

    _inherit = 'sale.order'

    steadfast_id = fields.Many2one('betopia.steadfast', string="Steadfast Reference")
    steadfast_status = fields.Char(string="Steadfast Status")
    steadfast_tracking_code = fields.Char(string="Steadfast Tracking Code")
    steadfast_consignment_id = fields.Char(string="Steadfast Consignment ID")
    steadfast_sent = fields.Boolean(string="Sent to Steadfast", default=False)


    def action_check_delivery_status(self):
        for record in self:
            steadfast = record.steadfast_id
            if not steadfast:
                msg = f"No Steadfast record linked to this Sale Order: {record.name}"
                record.steadfast_status = msg
                record.message_post(body=msg)
                raise UserError(_(msg))

            if not record.partner_id:
                msg = f"Customer information is missing for Sale Order {record.name}."
                record.steadfast_status = msg
                record.message_post(body=msg)
                raise UserError(_(msg))

            api_key = steadfast.steadfast_account_id.api_key
            secret_key = steadfast.steadfast_account_id.secret_key
            base_url = steadfast.steadfast_account_id.base_url

            if not api_key or not secret_key:
                msg = "Please configure Steadfast API keys in Settings."
                record.steadfast_status = msg
                record.message_post(body=msg)
                raise UserError(_(msg))

            # Determine which identifier to use
            if record.steadfast_consignment_id:
                url = f"{base_url}/status_by_cid/{record.steadfast_consignment_id}"
                identifier = "Consignment ID"
            elif record.steadfast_tracking_code:
                url = f"{base_url}/status_by_trackingcode/{record.steadfast_tracking_code}"
                identifier = "Tracking Code"
            elif record.name:
                url = f"{base_url}/status_by_invoice/{record.name}"
                identifier = "Invoice ID"
            else:
                msg = "No valid field (Consignment ID, Tracking Code, or Invoice ID) found."
                record.steadfast_status = msg
                record.message_post(body=msg)
                raise UserError(_(msg))

            record.steadfast_status = f"Checking Delivery Status by {identifier}..."

            headers = {
                "Api-Key": api_key,
                "Secret-Key": secret_key,
                "Content-Type": "application/json"
            }

            try:
                response = requests.get(url, headers=headers, timeout=10)
                # Log raw response to chatter
                record.message_post(
                    body=f"Steadfast Raw Response for {record.name} ({identifier}):<br/>{response.text}"
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except Exception:
                        msg = f"Invalid JSON response: {response.text}"
                        record.steadfast_status = msg
                        record.message_post(body=msg)
                        continue

                    if result.get("status") == 200:
                        record.steadfast_status = result.get("delivery_status", "Status not available.")
                    elif result.get("status") == 404:
                        record.steadfast_status = "Order not found in Steadfast system."
                    else:
                        record.steadfast_status = f"API returned error: {result.get('message', result)}"
                else:
                    record.steadfast_status = f"HTTP error {response.status_code}: {response.text}"

            except requests.exceptions.RequestException as e:
                record.steadfast_status = f"API request failed: {str(e)}"

            # Post final status to chatter
            record.message_post(
                body=f"Steadfast Status for {record.name} ({identifier}): {record.steadfast_status}"
            )

        # Show temporary notification on the screen (toast)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Steadfast Status",
                "message": record.steadfast_status,
                "type": "info",       # info, success, warning, danger
                "sticky": False,      # False = disappears automatically
            },
        }



    def action_confirm_stead_fast(self):

        for order in self:
            if not order.steadfast_id:
                steadfast = self.env["betopia.steadfast"].sudo().create({
                    'name': order.name,
                    'invoice': order.name.replace("SO", "INV"),
                    'tracking': 'TRK' + order.name[-4:],
                    'status': 'pending',
                })
                order.steadfast_id = steadfast.id
            _logger.info("Steadfast record created for Sale Order %s", order.name)



class SteadfastHistory(models.Model):

    _name = "betopia.steadfast.history"
    _description = "Steadfast Order History"

    steadfast_id = fields.Many2one('betopia.steadfast', string="Steadfast Order")
    consignment_id = fields.Char(string="Consignment ID")
    invoice = fields.Char(string="Invoice")
    tracking_code = fields.Char(string="Tracking Code")
    status = fields.Char(string="Status")
    created_at = fields.Datetime(string="Created At")
    updated_at = fields.Datetime(string="Updated At")


#Tacking update model

class SteadfastTracking(models.Model):
    _name = "betopia.steadfast.tracking"
    _description = "Steadfast Tracking"

    consignment_id = fields.Char(string="Consignment ID")
    customer_name = fields.Char(string="Customer Name")
    customer_address = fields.Text(string="Address")
    customer_phone = fields.Char(string="Phone")
    current_hub = fields.Char(string="Current Hub")
    rider_name = fields.Char(string="Rider Name")
    rider_phone = fields.Char(string="Rider Phone")
    cod_amount = fields.Float(string="COD Amount")
    status = fields.Char(string="Status")

    tracking_lines = fields.One2many("betopia.steadfast.tracking.line", "tracking_id", string="Tracking History")


class SteadfastTrackingLine(models.Model):
    _name = "betopia.steadfast.tracking.line"
    _description = "Tracking History"

    tracking_id = fields.Many2one("betopia.steadfast.tracking", string="Tracking")
    message = fields.Text(string="Message")
    created_at = fields.Datetime(string="Date")
    deliveryman = fields.Char(string="Deliveryman")





class SteadfastPricing(models.Model):
    _name = "betopia.steadfast.pricing"
    _description = "Steadfast Courier Pricing Rules (Bangladesh)"


    account_id = fields.Many2one('betopia.steadfast.account', string="Account")
    weight_min = fields.Float(string="Min Weight (kg)", required=True)
    weight_max = fields.Float(string="Max Weight (kg)", required=True)
    base_cost = fields.Float(string="Base Cost (৳)", required=True)
    zone_extra = fields.Float(string="Zone Charge (Outside Dhaka)", required=True)
    speed_extra = fields.Float(string="Speed Charge (Express)", required=True)
    cod_percent = fields.Float(string="COD % of Item Value", required=True)

    @api.model
    def calculate_cost(self, weight, item_value, outside_dhaka=False, express=False, cod=False):
        """ Calculate total delivery cost for an order """
        rule = self.search([
            ('weight_min', '<=', weight),
            ('weight_max', '>=', weight)
        ], limit=1)

        if not rule:
            raise UserError("No Steadfast pricing rule found for this weight!")

        cost = rule.base_cost
        if outside_dhaka:
            cost += rule.zone_extra
        if express:
            cost += rule.speed_extra
        if cod:
            cost += (rule.cod_percent / 100.0) * item_value

        return cost
