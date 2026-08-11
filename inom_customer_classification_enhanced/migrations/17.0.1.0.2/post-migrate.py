import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Backfill purchase_order.customer_id from the sale order already resolved
    on the purchase order (see 17.0.1.0.1, which fills custom_sale_id first)."""
    cr.execute(
        """
        UPDATE purchase_order po
           SET customer_id = so.partner_id
          FROM sale_order so
         WHERE so.id = po.custom_sale_id
           AND po.customer_id IS DISTINCT FROM so.partner_id
        """
    )
    _logger.info("customer_id backfilled on %s purchase orders", cr.rowcount)
