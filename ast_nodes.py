from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Node:
    kind: str
    children: List[Any] = field(default_factory=list)
    value: Optional[Any] = None
    lineno: Optional[int] = None
    col: Optional[int] = None

    def to_dict(self):
        return {
            "kind": self.kind,
            "value": self.value,
            "lineno": self.lineno,
            "col": self.col,
            "children": [c.to_dict() if isinstance(c, Node) else c for c in self.children]
        }
