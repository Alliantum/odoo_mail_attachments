from odoo import _, api, fields, models
import base64


class MailAttachmentLine(models.Model):
    _name = 'mail.attachment.line'
    _description = 'Mail Attachemnt Line'

    company_id = fields.Many2one('res.company', required=True, ondelete="cascade")
    model_id = fields.Many2one('ir.model', string='Apply on Model', required=True, ondelete="cascade")
    report_id = fields.Many2one('ir.actions.report', string="Report", required=True, ondelete="cascade")
    related_path = fields.Char('Path to Report Model')

    @api.model
    def recursive_get_report_record_id(self, records, attr, remaining_path):
        # records can be one or many records of the same model, so, this is simiar to an api.multi for loop
        report_record_ids = None
        for record in records:
            if hasattr(record, attr):
                if remaining_path and record._fields[attr].type in ['one2many', 'many2many', 'many2one']:
                    next_attr, next_remaining_path = remaining_path.split('.', 1)
                    return self.recursive_get_report_record_id(getattr(record, attr), next_attr, next_remaining_path)
                elif record._fields[attr].type in ['one2many', 'many2many', 'many2one']:
                    if not report_record_ids:
                        report_record_ids = getattr(record, attr)
                    else:
                        report_record_ids +=  getattr(record, attr)
        return report_record_ids

    @api.model
    def add_dynamic_reports(self, composer_id, value):
        attachment_ids = self.env['ir.attachment']
        for line in self.env.user.company_id.mail_attachment_line_ids.filtered(lambda line: line.model_id.model == composer_id.model):
            record_id = self.env[composer_id.model].browse(composer_id.res_id)
            if record_id:
                pdf, report_record_ids = None, None
                if line.related_path:
                    report_record_ids = line._get_id_from_related_path(record_id)
                else:
                    report_record_ids = record_id
                if report_record_ids:
                    pdf = line.report_id.render_qweb_pdf(report_record_ids.ids)
                    if pdf:
                        base64_pdf = base64.b64encode(pdf[0])
                        attachment_ids += composer_id.get_dynamic_attachments(record_id, base64_pdf, report_record_ids)
        if attachment_ids:
            value['value']['attachment_ids'] += [(4, attachment_id.id, False) for attachment_id in attachment_ids]
        return value

        # if self.model in ['sale.order', 'account.invoice']:
        #     record = self.env[self.model].browse(self.res_id)
        #     partner_lang = 'en_US'
        #     if record.partner_id:
        #         partner_lang = record.partner_id.lang
        #     if self.model == 'sale.order':
        #         report_id = self.env.ref('os_alveus_agb.action_alveus_agb').with_context(
        #             chosen_lang=partner_lang)
        #     else:
        #         report_id = self.env.ref('os_alveus_agb.action_alveus_agb_invoice').with_context(
        #             chosen_lang=partner_lang)
        #     if self.res_id:
        #         pdf = report_id.render_qweb_pdf([self.res_id])
        #         base64_pdf = base64.b64encode(pdf[0])
        #         ATTACHMENT_NAME = report_id.report_file
        #         file_name = self.env['ir.translation'].search(
        #             [('src', '=', 'Terms and Conditions'), ('lang', '=', partner_lang)], limit=1)
        #         file_name = file_name.value if file_name else 'Terms and Conditions'
        #         is_b2c = record.partner_id.customer_state == "private"
        #         # Reuse similar Terms and Conditions of same translated name to avoid too much files in the server.
        #         attachment_id = self.env['ir.attachment'].search(
        #             [('name', '=', file_name + '.pdf'), ('mimetype', '=', 'application/pdf'), ('description', '{}like'.format('' if is_b2c else 'not '), '%/b2c')], limit=1)
        #         if not bool(attachment_id):
        #             attachment_id = self.env['ir.attachment'].create({
        #                 'name': file_name + '.pdf',
        #                 'type': 'binary',
        #                 'datas': base64_pdf,
        #                 'datas_fname': file_name + '.pdf',
        #                 'store_fname': ATTACHMENT_NAME,
        #                 'res_model': self.model,
        #                 'res_id': self.res_id,
        #                 'mimetype': 'application/pdf',
        #                 'description': '/b2c' if is_b2c else '/b2b',
        #             })
        #         value['value']['attachment_ids'] += [(4, attachment_id.id, False)]
