"""
Simple template engine for generating HTML from templates.
"""
import re
from typing import Dict, Any, List


class TemplateEngine:
    def __init__(self):
        self.template_cache = {}
    
    def load_template(self, template_path: str) -> str:
        """Load template from file and cache it."""
        if template_path not in self.template_cache:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template_cache[template_path] = f.read()
        return self.template_cache[template_path]
    
    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        """Render template with context variables."""
        template = self.load_template(template_path)
        
        # Handle {% for %} loops
        template = self._process_for_loops(template, context)
        
        # Handle {{ variable }} substitutions
        template = self._process_variables(template, context)
        
        return template
    
    def _process_for_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Process {% for %} loops in template."""
        # Find all for loops
        for_pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_for_loop(match):
            var_name = match.group(1)
            list_name = match.group(2)
            loop_content = match.group(3)
            
            if list_name not in context:
                return ""
            
            items = context[list_name]
            if not isinstance(items, list):
                return ""
            
            result = ""
            for item in items:
                if isinstance(item, dict):
                    # Create a new context with the loop variable
                    loop_context = context.copy()
                    loop_context[var_name] = item
                    # Process variables in the loop content
                    processed_content = self._process_variables(loop_content, loop_context)
                    result += processed_content
                else:
                    # Simple variable substitution
                    loop_context = context.copy()
                    loop_context[var_name] = item
                    processed_content = self._process_variables(loop_content, loop_context)
                    result += processed_content
            
            return result
        
        return re.sub(for_pattern, replace_for_loop, template, flags=re.DOTALL)
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Process {{ variable }} substitutions in template."""
        def replace_variable(match):
            var_path = match.group(1).strip()
            
            # Handle nested attributes (e.g., article.title)
            if '.' in var_path:
                parts = var_path.split('.')
                value = context
                try:
                    for part in parts:
                        if isinstance(value, dict):
                            value = value[part]
                        else:
                            value = getattr(value, part)
                except (KeyError, AttributeError):
                    return ""
            else:
                value = context.get(var_path, "")
            
            # Convert to string and handle None
            if value is None:
                return ""
            return str(value)
        
        return re.sub(r'{{\s*([^}]+)\s*}}', replace_variable, template)


# Global template engine instance
template_engine = TemplateEngine()