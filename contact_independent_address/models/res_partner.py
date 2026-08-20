# -*- coding: utf-8 -*-

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        """Keep the company relation, but do not auto-copy the parent's address."""
        return {}

    def _fields_sync(self, values):
        """Preserve commercial-field sync while disabling address propagation."""
        if values.get('parent_id'):
            self.sudo()._commercial_sync_from_company()

        commercial_to_upstream = (
            bool(self.parent_id)
            and (self.commercial_partner_id != self)
            and (
                any(field in values for field in self._synced_commercial_fields())
                or 'parent_id' in values
            )
            and any(
                self[fname] != self.parent_id[fname]
                for fname in self._synced_commercial_fields()
            )
        )
        if commercial_to_upstream:
            new_synced_commercials = self._get_synced_commercial_values()
            self.parent_id.write(new_synced_commercials)

        self._children_sync(values)

    def _children_sync(self, values):
        """Only sync commercial data to children, not address fields."""
        if not self.child_ids:
            return
        if self.commercial_partner_id == self:
            fields_to_sync = values.keys() & self._commercial_fields()
            self.sudo()._commercial_sync_to_descendants(fields_to_sync)

    def _handle_first_contact_creation(self):
        """Do not assume the first child's address should become the parent address."""
        return

    def _load_records_create(self, vals_list):
        partners = super(
            ResPartner, self.with_context(_partners_skip_fields_sync=True)
        )._load_records_create(vals_list)

        groups = {}
        for partner, vals in zip(partners, vals_list):
            cp_id = None
            if vals.get('parent_id') and partner.commercial_partner_id != partner:
                cp_id = partner.commercial_partner_id.id
            groups.setdefault(cp_id, []).append(partner.id)

        for cp_id, children in groups.items():
            if not cp_id:
                continue
            to_write = self.browse(cp_id)._convert_fields_to_values(self._commercial_fields())
            if to_write:
                self.sudo().browse(children).write(to_write)

        for partner, vals in zip(partners, vals_list):
            partner._children_sync(vals)
            partner._handle_first_contact_creation()
        return partners
