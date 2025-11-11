"""
Email Template Renderer
Handles rendering HTML email templates with variable substitution
"""

from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import os


class EmailTemplateRenderer:
    """Renders HTML email templates with variable substitution"""

    def __init__(self):
        """Initialize template renderer"""
        self.templates_dir = Path(__file__).parent / "email_templates"
        if not self.templates_dir.exists():
            logger.warning(f"Email templates directory not found: {self.templates_dir}")

    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render an email template with variables

        Args:
            template_name: Name of template file (without .html extension)
            variables: Dictionary of variables to substitute

        Returns:
            Rendered HTML string

        Example:
            renderer.render_template("payment_confirmation", {
                "user_name": "John Doe",
                "amount_paid": "29.99",
                "plan_name": "Pro"
            })
        """
        template_path = self.templates_dir / f"{template_name}.html"

        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            raise FileNotFoundError(f"Email template '{template_name}' not found")

        try:
            # Read template
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Simple variable substitution using .format()
            # This is safer than eval/exec and works for simple placeholders
            rendered = template_content.format(**variables)

            return rendered

        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing required template variable: {e}")
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise

    def render_list_items(self, items: list, template: str = "<li>{item}</li>") -> str:
        """
        Render a list of items as HTML

        Args:
            items: List of items to render
            template: HTML template for each item (default: <li>)

        Returns:
            Rendered HTML list items
        """
        return "\n".join([template.format(item=item) for item in items])

    def render_card_list(self, cards: list, template: Optional[str] = None) -> str:
        """
        Render a list of cards (for jobs, courses, recommendations)

        Args:
            cards: List of dictionaries with card data
            template: Optional custom template

        Returns:
            Rendered HTML cards
        """
        if template is None:
            template = """
            <div class="card">
                <div class="card-title">{title}</div>
                <p>{description}</p>
                <div class="card-meta">{meta}</div>
                <a href="{link}" class="button" style="font-size:13px;padding:8px 16px">Learn More</a>
            </div>
            """

        return "\n".join([template.format(**card) for card in cards])


# Singleton instance
_renderer = None


def get_template_renderer() -> EmailTemplateRenderer:
    """Get or create template renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = EmailTemplateRenderer()
    return _renderer
