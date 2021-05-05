from odoo import models, api
from odoo.osv import expression


class GenericMixinNamesearchByFields(models.AbstractModel):
    """ Simple mixin, that allows to easily add ability to search record
        via name_search by some number of fields.

        So, if you want to add support for your model to use fields
        'name' and 'category' in name_search, then you can do following:

        class MyModel:
            _name = 'my.model'
            _inherit = 'generic.mixin.namesearch.by.fields'
            _generic_namesearch_fields = [
                'name',
                'category',
            ]
    """
    _name = 'generic.mixin.namesearch.by.fields'

    _generic_namesearch_fields = []

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not self._generic_namesearch_fields:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit)

        if not args:
            args = []

        args = expression.AND([
            args,
            expression.OR([
                [(fname, operator, name)]
                for fname in self._generic_namesearch_fields
            ]),
        ])
        return self.search(args, limit=limit).sudo().name_get()
