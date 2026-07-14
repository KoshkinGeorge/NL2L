from pylatexenc.latexwalker import LatexWalker, LatexSyntaxError
import logging

logger = logging.getLogger(__name__)

def validate_latex(latex_str: str) -> bool:
    """Проверяет, является ли строка синтаксически корректным LaTeX (без преамбулы)."""
    if not latex_str or not latex_str.strip():
        return False
    try:
        walker = LatexWalker(latex_str)
        walker.get_latex_nodes()
        return True
    except LatexSyntaxError as e:
        logger.debug(f"LaTeX validation failed: {e}")
        return False