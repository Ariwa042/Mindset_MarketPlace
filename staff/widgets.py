from django import forms
import json

class JSONEditorWidget(forms.Textarea):
    def format_value(self, value):
        if value is None:
            return ''
        return json.dumps(value, indent=2)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None
