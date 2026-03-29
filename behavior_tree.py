#!/usr/bin/env python3
"""behavior_tree - Behavior tree for game AI (sequence, selector, decorator)."""
import sys

class Status:
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class Node:
    def tick(self, blackboard):
        raise NotImplementedError

class Action(Node):
    def __init__(self, fn):
        self.fn = fn
    def tick(self, bb):
        return self.fn(bb)

class Condition(Node):
    def __init__(self, fn):
        self.fn = fn
    def tick(self, bb):
        return Status.SUCCESS if self.fn(bb) else Status.FAILURE

class Sequence(Node):
    def __init__(self, children):
        self.children = children
    def tick(self, bb):
        for child in self.children:
            result = child.tick(bb)
            if result != Status.SUCCESS:
                return result
        return Status.SUCCESS

class Selector(Node):
    def __init__(self, children):
        self.children = children
    def tick(self, bb):
        for child in self.children:
            result = child.tick(bb)
            if result != Status.FAILURE:
                return result
        return Status.FAILURE

class Inverter(Node):
    def __init__(self, child):
        self.child = child
    def tick(self, bb):
        r = self.child.tick(bb)
        if r == Status.SUCCESS: return Status.FAILURE
        if r == Status.FAILURE: return Status.SUCCESS
        return r

class Repeater(Node):
    def __init__(self, child, times):
        self.child = child
        self.times = times
    def tick(self, bb):
        for _ in range(self.times):
            r = self.child.tick(bb)
            if r == Status.FAILURE:
                return Status.FAILURE
        return Status.SUCCESS

def test():
    log = []
    def attack(bb):
        log.append("attack")
        return Status.SUCCESS
    def heal(bb):
        log.append("heal")
        return Status.SUCCESS
    tree = Sequence([
        Condition(lambda bb: bb.get("health", 100) > 20),
        Action(attack),
    ])
    bb = {"health": 50}
    assert tree.tick(bb) == Status.SUCCESS
    assert "attack" in log
    log.clear()
    bb["health"] = 10
    assert tree.tick(bb) == Status.FAILURE
    assert "attack" not in log
    sel = Selector([
        Sequence([Condition(lambda bb: bb.get("health", 0) < 30), Action(heal)]),
        Action(attack),
    ])
    log.clear()
    bb["health"] = 10
    assert sel.tick(bb) == Status.SUCCESS
    assert log == ["heal"]
    log.clear()
    bb["health"] = 100
    assert sel.tick(bb) == Status.SUCCESS
    assert log == ["attack"]
    inv = Inverter(Condition(lambda bb: False))
    assert inv.tick({}) == Status.SUCCESS
    count = [0]
    rep = Repeater(Action(lambda bb: (count.__setitem__(0, count[0]+1), Status.SUCCESS)[1]), 3)
    assert rep.tick({}) == Status.SUCCESS
    assert count[0] == 3
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("behavior_tree: Behavior tree AI. Use --test")
