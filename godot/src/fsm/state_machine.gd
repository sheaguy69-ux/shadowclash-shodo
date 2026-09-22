class_name StateMachine
extends Node
## Modular FSM host. Child nodes extend State; the machine injects
## references, forwards physics ticks, and handles transitions.

@export var initial_state: NodePath

var current: State
var states: Dictionary = {}

func setup(player) -> void:
	for child in get_children():
		if child is State:
			states[child.name.to_lower()] = child
			child.player = player
			child.machine = self
	if initial_state:
		transition_to(get_node(initial_state).name)

func transition_to(state_name: String, msg: Dictionary = {}) -> void:
	var next: State = states.get(state_name.to_lower())
	if next == null or next == current:
		return
	if current:
		current.exit()
	current = next
	current.frames = 0
	current.enter(msg)

func physics_tick(delta: float) -> void:
	if current:
		current.frames += 1
		current.physics_update(delta)
