import datetime
import time
import base64
import dateutil
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class MailAttachmentLine(models.Model):
    _name = 'mail.attachment.line'
    _description = 'Mail Attachemnt Line'

    company_id = fields.Many2one('res.company', required=True, ondelete="cascade")
    model_id = fields.Many2one('ir.model', string='Apply on Model', required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model")
    filter_model_id = fields.Char(string="Model Filter")
    report_id = fields.Many2one('ir.actions.report', string="Report", required=True, ondelete="cascade")
    report_model_name = fields.Char(related="report_id.model_id.model")
    filter_report_id = fields.Char(string="Report Model Filter")
    related_path = fields.Char('Path to Report Model')

    def _get_eval_context(self):
        """ Prepare the context used when evaluating python code
            :returns: dict -- evaluation context given to safe_eval
        """
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user,
        }

    def _pass_filter(self, filter_field, records):
        """ Filter the records that satisfy the precondition of action ``self``. """
        if getattr(self, filter_field, False) and records:
            domain = [('id', 'in', records.ids)] + safe_eval(getattr(self, filter_field), self._get_eval_context())
            return records.search(domain)
        else:
            return records

    def _report_record_pass_filter(self, records):
        """ Filter the records that satisfy the precondition of action ``self``. """
        if self.filter_pre_domain and records:
            domain = [('id', 'in', records.ids)] + safe_eval(self.filter_pre_domain, self._get_eval_context())
            return records.search(domain)
        else:
            return records

    @api.model
    def recursive_get_report_record_id(self, records, attr, remaining_path):
        # records can be one or many records of the same model, so, this is simiar to an api.multi for loop
        report_record_ids = None
        for record in records:
            if hasattr(record, attr):
                if remaining_path and record._fields[attr].type in ['one2many', 'many2many', 'many2one']:
                    if remaining_path.count('.') > 0:
                        next_attr, next_remaining_path = remaining_path.split('.', 1)
                    else:
                        next_attr, next_remaining_path = remaining_path, None
                    return self.recursive_get_report_record_id(getattr(record, attr), next_attr, next_remaining_path)
                elif record._fields[attr].type in ['one2many', 'many2many', 'many2one']:
                    if not report_record_ids:
                        report_record_ids = getattr(record, attr)
                    else:
                        report_record_ids += getattr(record, attr)
        return report_record_ids

    def _get_id_from_related_path(self, record_id):
        if self.related_path.count('.') > 0:
            report_record_ids = self.recursive_get_report_record_id(record_id, *self.related_path.split('.', 1))
        else:
            report_record_ids = getattr(record_id, self.related_path, None)
        if report_record_ids and isinstance(report_record_ids[0], self.env[self.report_id.model_id.model].__class__):
            return report_record_ids

    @api.model
    def add_dynamic_reports(self, composer_id, value):
        attachment_ids = self.env['ir.attachment']
        for line in self.env.user.company_id.mail_attachment_line_ids.filtered(lambda line: line.model_id.model == composer_id.model):
            record_id = line._pass_filter('filter_model_id', self.env[composer_id.model].browse(composer_id.res_id))
            if record_id:
                pdf, report_record_ids = None, None
                if line.related_path:
                    report_record_ids = line._pass_filter('filter_report_id', line._get_id_from_related_path(record_id))
                else:
                    report_record_ids = line._pass_filter('filter_report_id', record_id)
                if report_record_ids:
                    pdf = line.report_id.render_qweb_pdf(report_record_ids.ids)
                    if pdf:
                        base64_pdf = base64.b64encode(pdf[0])
                        attachment_ids += composer_id.get_dynamic_attachments(line.report_id, base64_pdf, report_record_ids)
        if attachment_ids:
            value['value']['attachment_ids'] += [(4, attachment_id.id, False) for attachment_id in attachment_ids]
        return value
