extends Node
## Registers the full 2-player input map in code — keeps project.godot readable
## and makes the bindings greppable/reviewable.
##
## P1: WASD move (W jump), J/K/L = light/medium/heavy, U = special, ; (semicolon) = defend
## P2: arrows move (Up jump), KP1/KP2/KP3 = light/medium/heavy, KP. = special, KP0 = defend
## Gamepads: device 0 -> P1, device 1 -> P2 (A jump, X/Y/B = L/M/H, RB defend, RT special)

const ACTIONS := ["left", "right", "up", "down", "jump", "light", "medium", "heavy", "special", "defend"]

const P1_KEYS := {
	"left": KEY_A, "right": KEY_D, "up": KEY_W, "down": KEY_S, "jump": KEY_W,
	"light": KEY_J, "medium": KEY_K, "heavy": KEY_L,
	"special": KEY_U, "defend": KEY_SEMICOLON,
}
const P2_KEYS := {
	"left": KEY_LEFT, "right": KEY_RIGHT, "up": KEY_UP, "down": KEY_DOWN, "jump": KEY_UP,
	"light": KEY_KP_1, "medium": KEY_KP_2, "heavy": KEY_KP_3,
	"special": KEY_KP_PERIOD, "defend": KEY_KP_0,
}

const PAD_BUTTONS := {
	"jump": JOY_BUTTON_A, "light": JOY_BUTTON_X, "medium": JOY_BUTTON_Y,
	"heavy": JOY_BUTTON_B, "defend": JOY_BUTTON_RIGHT_SHOULDER,
	"up": JOY_BUTTON_DPAD_UP, "down": JOY_BUTTON_DPAD_DOWN,
	"left": JOY_BUTTON_DPAD_LEFT, "right": JOY_BUTTON_DPAD_RIGHT,
}

func _ready() -> void:
	_register_player(1, P1_KEYS, 0)
	_register_player(2, P2_KEYS, 1)

func _register_player(player: int, keys: Dictionary, device: int) -> void:
	for action_suffix in ACTIONS:
		var action := "p%d_%s" % [player, action_suffix]
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		if keys.has(action_suffix):
			var key_event := InputEventKey.new()
			key_event.physical_keycode = keys[action_suffix]
			InputMap.action_add_event(action, key_event)
		if PAD_BUTTONS.has(action_suffix):
			var pad_event := InputEventJoypadButton.new()
			pad_event.device = device
			pad_event.button_index = PAD_BUTTONS[action_suffix]
			InputMap.action_add_event(action, pad_event)
	# Analog stick horizontal + special on right trigger.
	for axis_action in [["left", JOY_AXIS_LEFT_X, -1.0], ["right", JOY_AXIS_LEFT_X, 1.0],
			["up", JOY_AXIS_LEFT_Y, -1.0], ["down", JOY_AXIS_LEFT_Y, 1.0],
			["special", JOY_AXIS_TRIGGER_RIGHT, 1.0]]:
		var motion := InputEventJoypadMotion.new()
		motion.device = device
		motion.axis = axis_action[1]
		motion.axis_value = axis_action[2]
		InputMap.action_add_event("p%d_%s" % [player, axis_action[0]], motion)
