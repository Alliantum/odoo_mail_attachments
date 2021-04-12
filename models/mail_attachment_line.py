from odoo import _, api, fields, models


class MailAttachmentLine(models.Model):
    _name = 'mail.attachment.line'
    _description = 'Mail Attachemnt Line'

    company_id = fields.Many2one('res.company')
    model_id = fields.Many2one('ir.model', string='Apply on Model')
    report_id = fields.Many2one('ir.actions.report', string="Report")
    related_path = fields.Char('Path to Report Model')

    def _parse_related_path(self):
        ...
