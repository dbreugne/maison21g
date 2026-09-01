import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Backfill purchase_order.custom_sale_id from the first PO line carrying a
    sale order, for orders that already existed before the field was added."""
    cr.execute(
        """
        UPDATE purchase_order po
           SET custom_sale_id = sub.custom_sale_id
          FROM (
                SELECT DISTINCT ON (order_id) order_id, custom_sale_id
                  FROM purchase_order_line
                 WHERE custom_sale_id IS NOT NULL
                 ORDER BY order_id, sequence, id
               ) sub
         WHERE po.id = sub.order_id
           AND po.custom_sale_id IS DISTINCT FROM sub.custom_sale_id
        """
    )
    _logger.info("custom_sale_id backfilled on %s purchase orders", cr.rowcount)
