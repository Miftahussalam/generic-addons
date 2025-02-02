import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class GenericResourceMixin(models.AbstractModel):
    _name = 'generic.resource.mixin'
    _description = 'Generic Resource MixIn'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.guard.fields',
    ]

    _generic_mixin_deny_write_fields = ['resource_id']

    resource_id = fields.Many2one(
        'generic.resource', index=True, auto_join=True,
        required=True, delegate=True, ondelete='restrict',
        string="Generic Resource")

    _sql_constraints = [
        ('unique_resource_id', 'UNIQUE(resource_id)',
         'Resource must be unique')
    ]

    @api.model
    def _get_generic_tracking_fields(self):
        """ Get tracking fields

            :return set(str): Set of names of fields to track changes
        """
        track_fields = super(
            GenericResourceMixin, self)._get_generic_tracking_fields()
        res_type = self._get_resource_type()
        return track_fields | res_type.get_resource_tracking_fields()

    def _preprocess_write_changes(self, changes):
        """ Called before write

            This method may be overridden by other addons to add
            some preprocessing of changes, before write

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :rtype: dict
            :return: values to update record with.
                     These values will be written just after write
        """
        vals = super(GenericResourceMixin, self)._preprocess_write_changes(
            changes)
        vals.update(self.resource_id._preprocess_resource_changes(changes))
        return vals

    def _postprocess_write_changes(self, changes):
        """ Called after write

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any  value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """
        res = super(GenericResourceMixin, self)._postprocess_write_changes(
            changes)
        self.resource_id._postprocess_resource_changes(changes)
        return res

    @api.model
    def default_get(self, fields_list):
        return super(
            GenericResourceMixin,
            self.with_context(generic_resource_type_model=self._name)
        ).default_get(fields_list)

    @api.model
    def create(self, vals):
        values = self.env['generic.resource']._get_resource_type_defaults(
            self._get_resource_type())
        values.update(vals)

        # Add fake resource id to values. This is required to create
        # 'generic.resource' record, because 'res_id' field is required
        # This field will be updated after record creation
        values['res_id'] = self.env[
            'generic.resource'
        ]._generic_mixin_guard__wrap_field('res_id', -1)

        # Create record
        # TODO: this create call somehow triggers write on self. Review.
        rec = super(GenericResourceMixin, self).create(values)

        # Update res_id with created id
        rec.sudo().resource_id.write({
            'res_id': self.env[
                'generic.resource'
            ]._generic_mixin_guard__wrap_field('res_id', rec.id),
        })

        # Call 'on_resource_created' hook
        rec.resource_id.on_resource_created()
        return rec

    def unlink(self):
        # Get resources
        resources = self.mapped('resource_id')

        # Delete records
        res = super(GenericResourceMixin, self).unlink()

        # Delete resources and return status
        # We are using sudo here to avoid access rights (ACL) conflicts.
        # resource's access rules (ir.rule) checked
        # when unlink called on this object.
        resources.sudo().unlink()
        return res

    def _get_resource_type(self):
        return self.env['generic.resource.type'].get_resource_type(self._name)

    def check_access_rule(self, operation):
        # Overriden to check access to generic resources also
        self.mapped('resource_id').check_access_rule(operation)
        return super(GenericResourceMixin, self).check_access_rule(operation)
