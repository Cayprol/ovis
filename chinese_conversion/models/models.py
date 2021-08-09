# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from opencc import OpenCC

class BaseModelExtend(models.AbstractModel):

	_inherit = 'base'
	_description = 'Extend BaseModel _search'

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		"""
		:return: a list of record ids or an integer (if count is True)
		"""
		available_modules = ['s2t.json', 't2s.json']
		multi_record_ids = []
		for m in available_modules:
			new_args = []
			for arg in args:
				if len(arg)>1 and type(arg[2]) is str:
					list_arg = list(arg)
					list_arg[2] = OpenCC(m).convert(arg[2])
					new_args.append(tuple(list_arg))		
				else:
					new_args.append(arg)

			record_ids = super(BaseModelExtend, self)._search(new_args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if type(record_ids) is list:
				multi_record_ids += record_ids
			else:
				return record_ids
		# Don't use list(set(multi_record_ids)), because we'd like to preserve ordering of the list for dependency.
		return list(dict.fromkeys(multi_record_ids))