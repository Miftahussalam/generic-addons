from odoo.tests.common import TransactionCase


class TestConditionSimpleFieldSelection(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionSimpleFieldSelection, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')
        cls.TestModel = cls.env[cls.test_model.model]

        cls.test_field_selection = cls.test_model.field_id.filtered(
            lambda r: r.name == 'test_selection')

        cls.Condition = cls.env['generic.condition']
        cls.condition_data = {
            "name": 'Simple field condition',
            "model_id": cls.test_model.id,
            "type": 'simple_field',
        }

    def _create_condition(self, data):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_data.copy()
        condition_data.update(data)
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def _check_selection_condition(self, val1, val2, operator):
        """ Test selection values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_selection.id,
            'condition_simple_field_value_selection': val2,
            'condition_simple_field_selection_operator': operator,
        })
        return condition.check(self._create_record(test_selection=val1))

    def test_10_simple_field_selection(self):
        self.assertTrue(self._check_selection_condition('val1', 'val1', '='))
        self.assertFalse(self._check_selection_condition('val1', 'val2', '='))

        self.assertTrue(self._check_selection_condition('val1', 'val2', '!='))
        self.assertFalse(self._check_selection_condition('val2', 'val2', '!='))

        self.assertTrue(self._check_selection_condition('val1', False, 'set'))
        self.assertFalse(self._check_selection_condition(False, False, 'set'))

        self.assertTrue(
            self._check_selection_condition(False, False, 'not set'))
        self.assertFalse(
            self._check_selection_condition('val2', False, 'not set'))
