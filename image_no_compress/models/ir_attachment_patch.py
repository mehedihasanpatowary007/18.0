import logging
from odoo.addons.base.models.ir_attachment import IrAttachment

_logger = logging.getLogger(__name__)

_original = IrAttachment.create_unique


def create_unique_keep_original(self, values_list=None):
    """
    UNIVERSAL PATCH:
    Fixes ALL calling styles:
      - create_unique()
      - create_unique(None)
      - create_unique(dict)
      - create_unique([dict])
    And prevents any Odoo compression fields.
    """

    # CASE 1 → no argument or None
    if values_list is None:
        values_list = []

    # CASE 2 → dict passed
    if isinstance(values_list, dict):
        values_list = [values_list]

    # CASE 3 → list of dicts
    cleaned = []
    for vals in values_list:
        v = vals.copy()

        # remove resized fields
        for key in list(v.keys()):
            if key.startswith("image_") and key != "datas":
                v.pop(key, None)

        # remove processing fields
        v.pop("resized_images", None)
        v.pop("checksum", None)
        v.pop("index_content", None)

        cleaned.append(v)

    return _original(self, cleaned)


# APPLY PATCH
IrAttachment.create_unique = create_unique_keep_original
_logger.info("Universal image compression bypass active (Odoo 18)")
