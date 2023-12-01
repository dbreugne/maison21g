# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProjectTask(models.Model):
	_inherit = "project.task"

	hours = fields.Char(string="Estimated Hours")
	amount = fields.Float(string="Estimated Amount")
	total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount")

	@api.depends('hours', 'amount')
	def _compute_total_amount(self):
		for rec in self:
			rec.total_amount = 0
			if rec.hours:
				if ':' in rec.hours:
					hours, minutes = map(int, rec.hours.split(":"))
					total_hours = hours + minutes / 60.0
					rec.total_amount = float(total_hours) * rec.amount

				else:
					rec.total_amount = float(rec.hours) * rec.amount
