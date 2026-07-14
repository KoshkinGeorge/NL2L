from .terminals import BaseTransformer

class TrigToLatex(BaseTransformer):  # Наследуем от BaseTransformer
    def start(self, items):
        return items[0]
    
    def value(self, items):
        return items[0]

    def expr(self, items):
        """Обрабатывает составные выражения"""
        if len(items) == 1:
            return items[0]
        # items = [левый_операнд, оператор, правый_операнд]
        left = items[0]
        op = items[1]
        right = items[2]
        
        return f"{left}{op}{right}"
    
    def trig_expr(self, items):
        return items[0]
    
    def sine(self, items):
        return f'\\sin({items[0]})'
    
    def cosine(self, items):
        return f'\\cos({items[0]})'
    
    def tangent(self, items):
        return f'\\tan({items[0]})'
    
    def cotangent(self, items):
        return f'\\cot({items[0]})'