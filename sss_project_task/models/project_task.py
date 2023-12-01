# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProjectTask(models.Model):
	_inherit = "project.task"

	hours = fields.Char(string="Estimated Hours")
	amount = fields.Float(string="Estimated Amount", compute="_compute_total_amount")
	total_amount = fields.Float(string="Total Amount")

	@api.depends('hours')
	def _compute_total_amount(self):
		for rec in self:
			rec.amount = 0
			if rec.hours:
				if ':' in rec.hours:
					hours, minutes = map(int, rec.hours.split(":"))
					total_hours = hours + minutes / 60.0
					rec.amount = float(total_hours) * 25

				else:
					rec.amount = float(rec.hours) * 25
