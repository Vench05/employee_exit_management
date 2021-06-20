# -*- coding: utf-8 -*-

from email.policy import default

from numpy import require
from odoo import models, fields, api
from odoo.exceptions import ValidationError 


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resignation_ids = fields.One2many('resignation.letter', 'employee_id')
    
class ResignationLetter(models.Model):
    _name = 'resignation.letter'

    description = fields.Text(string="Resignation Letter", required=True)

    
    employee_id = fields.Many2one(
        'hr.employee',
        string='employee',
        ondelete='cascade',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]),
        required=True
        )

    date = fields.Date(default=fields.Date.today())
    resignatory_template = fields.Binary(string="Resignatory Template",
                                        related="employee_id.job_id.signatory_files")
    resignatory_letter = fields.Binary(string="Upload Resignatory")                                 
    
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('sent', 'Sent'), 
        ('pending', 'Reviewing'),
        ('approve', 'Approve'),
        ('disapprove', 'Disapprove')
        ],
        default='draft')

    reason_disapprove = fields.Text(string="Reason/Rejected Message")


    def send_to_manager(self):
        self.state = 'sent'

    def approve(self):
        # self.state = 'approve'
        signatory_files = self.env['hr.job'].browse(1).signatory_files
        if not signatory_files:
            raise ValidationError('No uploaded template, Please contact your manager')
        return signatory_files

    def pending(self):
        self.state = 'pending'

    def disapprove(self):
        context = {
            'id': self.id,
        }
        return {
            'name': 'Reason why disapproving',
            'id': 'modal_reason_view_form',
            'res_model': 'modal.reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }


class DisapproveModal(models.TransientModel):
    _name = 'modal.reason'
    reason = fields.Text()


    def disapprove(self):
        resignation_letter = self.env['resignation.letter'].browse(int(self._context['id']))
        resignation_letter.state = 'disapprove'
        resignation_letter.reason_disapprove = self.reason

    def cancel(self):
        return { 'type': 'ir.actions.act_window_close' }


class HrJob(models.Model):
    _inherit = 'hr.job'

    signatory_files = fields.Binary(string='Signatory Template')

