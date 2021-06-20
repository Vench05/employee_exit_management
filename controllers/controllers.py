# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeExitManagement(http.Controller):
#     @http.route('/employee_exit_management/employee_exit_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_exit_management/employee_exit_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_exit_management.listing', {
#             'root': '/employee_exit_management/employee_exit_management',
#             'objects': http.request.env['employee_exit_management.employee_exit_management'].search([]),
#         })

#     @http.route('/employee_exit_management/employee_exit_management/objects/<model("employee_exit_management.employee_exit_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_exit_management.object', {
#             'object': obj
#         })
