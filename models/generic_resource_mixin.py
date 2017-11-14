# -*- coding: utf-8 -*-

from openerp import fields, models, api


import logging
_logger = logging.getLogger(__name__)


class GenericResourceMixin(models.AbstractModel):
    _name = 'generic.resource.mixin'

    resource_id = fields.Many2one(
        'generic.resource', index=True, auto_join=True, ondelete='restrict',
        required=True, delegate=True)

    _sql_constraints = [
        ('unique_resource_id', 'UNIQUE(resource_id)',
         'Resource must be unique')
    ]

    @api.multi
    def write(self, vals):
        # Deny write resource_id field
        if vals.get('resource_id', None):
            _logger.warning("Trying write something in the resource_id field")
            del vals['resource_id']

        return super(GenericResourceMixin, self).write(vals)

    @api.model
    def create(self, vals):
        # Add vals for resource with fake id
        vals['res_type_id'] = self._get_resource_type().id
        vals['res_id'] = -1

        res = super(GenericResourceMixin, self).create(vals)

        # Update res_id with created id
        res.resource_id.update({'res_id': res.id})
        return res

    def unlink(self):
        # Get resources
        resources = self.mapped('resource_id')

        # Delete records
        res = super(GenericResourceMixin, self).unlink()
        # Delete resources and return status
        resources.unlink()
        return res

    def _get_resource_type(self):
        r_type_env = self.env['generic.resource.type']
        return r_type_env.search([('model_id.model', '=', self._name)])


class GenericResourceMixinInvNumber(models.AbstractModel):
    ''' generic_resource_mixin_inv_number model is meant to be inherited by
     any model that needs to have automaticali generated field inv_number for
     inventory number.
     For use it you must create sequence in "ir.sequence" model in data
     directory.
     For example:
        <record id="id_for_your_sequence" model="ir.sequence">
            <field name="name">name_for_your_sequence</field>
            <field name="code">code_for_your_sequence</field>
            <field name="prefix">prefix_for_your_inv_number</field>
            <field name="padding">count_of_integer_in your_inv_number</field>
        </record>
     '''
    _name = 'generic.resource.mixin.inv.number'
    _description = 'Generic Resource Mixin Inv Number'
    _inv_number_seq_code = None

    inv_number = fields.Char(index=True, required=True,
                             readonly=True, default='')

    @api.model
    def create(self, vals):
        if self._inv_number_seq_code is not None and (
                not vals.get('inv_number')):
            vals['inv_number'] = self.env['ir.sequence'].next_by_code(
                self._inv_number_seq_code)
        result = super(GenericResourceMixinInvNumber, self).create(vals)
        return result
