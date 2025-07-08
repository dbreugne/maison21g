# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import pytz

class TangentSyncDateWizard(models.TransientModel):
    _name = 'tangent.sync.date.wizard'
    _description = 'Tangent Sync Date Selection Wizard'
    
    sync_date = fields.Date(
        string='Sync Date', 
        required=True,
        default=fields.Date.context_today,
        help='Select the date for which you want to synchronize POS orders'
    )
    api_config_id = fields.Many2one(
        'tangent.api.config',
        string='API Configuration',
        required=True
    )
    
    def action_sync(self):
        """Run synchronization with the selected date"""
        self.ensure_one()
        
        # Convert date to datetime with timezone
        user_tz = self.env.user.tz or 'UTC'
        sync_date = datetime.combine(self.sync_date, datetime.min.time())
        sync_date = pytz.timezone(user_tz).localize(sync_date)
        
        # Call the do_sync method with the selected date
        return self.api_config_id.with_context(sync_date=sync_date).do_sync(date=sync_date)
