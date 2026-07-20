"""
Phase 3: Symbol Table
Tracks variable name, data type, scope, and initial value.
Supports nested scopes (block scoping) via a stack of dictionaries.
"""


class SymbolTable:
    def __init__(self):
        # each scope is a dict: name -> {type, initial_value}
        self.scopes = [{}]
        self.scope_names = ["global"]
        self._next_scope_id = 1

    def enter_scope(self, label=None):
        self.scopes.append({})
        self.scope_names.append(label or f"block{self._next_scope_id}")
        self._next_scope_id += 1

    def exit_scope(self):
        self.scopes.pop()
        self.scope_names.pop()

    def declare(self, name, var_type, initial_value=None):
        """Returns False if the name is already declared in current scope."""
        current = self.scopes[-1]
        if name in current:
            return False
        current[name] = {
            "type": var_type,
            "scope": self.scope_names[-1],
            "initial_value": initial_value,
        }
        return True

    def lookup(self, name):
        """Search from innermost to outermost scope. Returns entry dict or None."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def is_declared_in_current_scope(self, name):
        return name in self.scopes[-1]

    def all_entries(self):
        """Flatten all scopes into a list of (name, entry) for printing."""
        result = []
        for scope in self.scopes:
            for name, entry in scope.items():
                result.append((name, entry))
        return result

    def print_table(self):
        print(f"{'Name':<10}{'Type':<10}{'Scope':<10}{'InitValue'}")
        print("-" * 45)
        for name, entry in self.all_entries():
            print(f"{name:<10}{entry['type']:<10}{entry['scope']:<10}{entry['initial_value']}")
