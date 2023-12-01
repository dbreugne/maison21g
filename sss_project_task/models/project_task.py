# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class ProjectTask(models.Model):
	_inherit = "project.task"

	hours = fields.Char(string="Estimated Hours")
	est_hours = fields.Float(string="Estimated Hours")
	amount = fields.Float(string="Estimated Amount", compute="_compute_total_amount")
	total_amount = fields.Float(string="Total Amount")

	@api.depends('est_hours')
	def _compute_total_amount(self):
		for rec in self:
			rec.amount = 0
			if rec.est_hours:
				rec.amount = float(rec.est_hours) * 25

