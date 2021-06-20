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
        self.state = 'approve'
        clearance = self.env['clearance.signatory'].create({
            'employee_id': self.employee_id.id,
        })
        action = self.env.ref('employee_exit_management.clearance_signatory_action')
        return {
            'res_id': clearance.id,
            'name': action.name,
            'type': action.type,
            'res_model': action.res_model,
            'view_mode': 'form',
        }


    def pending(self):
        self.state = 'pending'

    def disapprove(self):
        context = {
            'id': self.id,
            'model': 'resignation.letter'
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

    def send_signatory(self):
        clearance = self.env['clearance.signatory'].search([
            ('employee_id', '=', self.employee_id.id)
        ], limit=1, order='id desc')
        action = self.env.ref('employee_exit_management.clearance_signatory_action')
        return {
            'res_id': clearance.id,
            'name': action.name,
            'type': action.type,
            'res_model': action.res_model,
            'view_mode': 'form',
        }
        


class DisapproveModal(models.TransientModel):
    _name = 'modal.reason'
    reason = fields.Text()


    def disapprove(self):
        model = self._context['model']
        resignation_letter = self.env[model].browse(int(self._context['id']))
        resignation_letter.state = 'disapprove'
        resignation_letter.reason_disapprove = self.reason

    def cancel(self):
        return { 'type': 'ir.actions.act_window_close' }


class HrJob(models.Model):
    _inherit = 'hr.job'

    signatory_files = fields.Binary(string='Signatory Template')

class ClearanceSignatory(models.Model):
    _name = 'clearance.signatory'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        )

    signatory_template = fields.Binary(string="Resignatory Template",
                                        related="employee_id.job_id.signatory_files")
    signatory_letter = fields.Binary(string="Upload Resignatory")  

    reason_disapprove = fields.Text(string="Reason/Rejected Message")


    state = fields.Selection([
        ('draft', 'Draft'), 
        ('sent', 'Sent'), 
        ('pending', 'Reviewing'),
        ('approve', 'Approve'),
        ('disapprove', 'Disapprove')
        ],
        default='draft')


    def submit(self):
        if not self.signatory_letter:
            raise ValidationError('Please upload your signatory letter')
        self.state = 'sent'

    def approve(self):
        self.state = 'approve'


    def pending(self):
        self.state = 'pending'

    def disapprove(self):
        context = {
            'id': self.id,
            'model': 'clearance.signatory'
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