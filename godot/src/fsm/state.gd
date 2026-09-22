class_name State
extends Node
## Base class for modular FSM states. States are children of a StateMachine
## node; the machine calls enter/exit and forwards per-frame callbacks.

var player: Player           # owning entity, injected by StateMachine
var machine: StateMachine    # back-reference for transitions

## msg carries transition context (e.g. attack tier, attacker for hitstun).
func enter(_msg: Dictionary = {}) -> void:
	pass

func exit() -> void:
	pass

func physics_update(_delta: float) -> void:
	pass

## Frames elapsed since this state was entered (60 fps physics ticks).
var frames := 0
