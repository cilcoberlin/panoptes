
def _new_or_old_field_property(prop, new_field, old_field, old_priority):
		"""
		Get the given property on the old field or the new field, with priority given
		to a field of the user's choosing.

		Arguments:
		prop -- a string of the requested property name
		old_field -- the old field as a Field instance
		new_field -- the new field as a Field instance
		old_priority -- a boolean that, if True, gives priority to the old
		                field, and, if False, gives priority to the new field

		Returns: the requested property on the new field or old field

		"""
		new_prop = getattr(new_field, prop)
		old_prop = getattr(old_field, prop)
		if old_priority:
			return old_prop or new_prop
		else:
			return new_prop or old_prop

def replace_form_field(form, field_name, new_field, use_old_values=True):
		"""Replace a form field in place, optionally preserving the original values.

		Arguments:
		form -- an instance of a Form or ModelForm class
		field_name -- the string name of the field on the form
		new_field -- an instance of a Field class
		use_old_values -- a boolean that, if True, will use the field's old settings

		"""

		try:
			old_field = form.fields[field_name]
		except (AttributeError, KeyError):
			return

		field_props = ('help_text', 'initial', 'label', 'required', 'error_messages')
		field_vals = {}
		if use_old_values:
			for prop in field_props:
				field_vals[prop] = _new_or_old_field_property(prop, new_field, old_field, use_old_values)

		form.fields[field_name] = new_field

		#  Update the field's attributes
		if use_old_values:
			for prop, value in field_vals.iteritems():
				setattr(form.fields[field_name], prop, value)
