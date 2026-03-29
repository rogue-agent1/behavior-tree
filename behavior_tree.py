#!/usr/bin/env python3
"""behavior_tree - Behavior tree for AI decision making (sequence, selector, etc)."""
import sys

SUCCESS, FAILURE, RUNNING = "success", "failure", "running"

class Node:
    def tick(self, ctx): raise NotImplementedError

class Action(Node):
    def __init__(self, fn): self.fn = fn
    def tick(self, ctx): return self.fn(ctx)

class Condition(Node):
    def __init__(self, pred): self.pred = pred
    def tick(self, ctx): return SUCCESS if self.pred(ctx) else FAILURE

class Sequence(Node):
    def __init__(self, children): self.children = children
    def tick(self, ctx):
        for child in self.children:
            r = child.tick(ctx)
            if r != SUCCESS: return r
        return SUCCESS

class Selector(Node):
    def __init__(self, children): self.children = children
    def tick(self, ctx):
        for child in self.children:
            r = child.tick(ctx)
            if r != FAILURE: return r
        return FAILURE

class Inverter(Node):
    def __init__(self, child): self.child = child
    def tick(self, ctx):
        r = self.child.tick(ctx)
        if r == SUCCESS: return FAILURE
        if r == FAILURE: return SUCCESS
        return r

class RepeatN(Node):
    def __init__(self, child, n): self.child, self.n = child, n
    def tick(self, ctx):
        for _ in range(self.n):
            r = self.child.tick(ctx)
            if r != SUCCESS: return r
        return SUCCESS

def test():
    log = []
    tree = Sequence([
        Condition(lambda ctx: ctx["health"] > 0),
        Selector([
            Sequence([
                Condition(lambda ctx: ctx.get("enemy_near")),
                Action(lambda ctx: (log.append("attack"), SUCCESS)[1]),
            ]),
            Action(lambda ctx: (log.append("patrol"), SUCCESS)[1]),
        ]),
    ])
    ctx = {"health": 100, "enemy_near": True}
    assert tree.tick(ctx) == SUCCESS
    assert log == ["attack"]
    log.clear()
    ctx["enemy_near"] = False
    assert tree.tick(ctx) == SUCCESS
    assert log == ["patrol"]
    ctx["health"] = 0
    assert tree.tick(ctx) == FAILURE
    inv = Inverter(Condition(lambda c: False))
    assert inv.tick({}) == SUCCESS
    print("behavior_tree: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: behavior_tree.py --test")
