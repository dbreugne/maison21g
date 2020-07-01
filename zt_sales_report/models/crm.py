from odoo import models,fields,api


class CRM(models.Model):

    _inherit = 'crm.lead'

    industry= fields.Selection([('bank','Bank'),('real_estate','Real Estate'),('mnc','MNCs'),('brand','Brand'),('market_place','Marketplace'),('hair_saloon','Hair Salon,')
                                ,('spa','Spa'),('gym','Gym'),('hotel','Hotel'),('cruise','Cruise'),('club','Club')],string='Industry')

    category = fields.Selection([('corp_scent_design','Corporate Scent Design'),('luxury_hotel','Luxury Hotel'),
                                 ('yatch','Yatch'),('villa','Villa'),('wedding','wedding'),('event','Event'),('mall','Mall')],string='Category')


