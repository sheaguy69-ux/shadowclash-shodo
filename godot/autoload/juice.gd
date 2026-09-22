extends Node
## Freeze frame / hitstop manager — see docs/game-dev/game-juice-freeze-frame.md.
## Usage:  Juice.freeze_frames(3)         - light hit (frames at 60 fps)
##         Juice.freeze(0.12, 0.03)       - kill shot: 120 ms at 3% speed
## Overlap policy is extend-only: a jab landing during a finisher's freeze
## never cuts the finisher short.

signal freeze_started
signal freeze_ended

const RECOVERY_TIME := 0.10  # eased ramp back to full speed instead of a snap

var _freeze_end_at := 0.0    # real-clock seconds when the current freeze expires
var _active := false

func freeze_frames(frames: int, scale: float = 0.05) -> void:
	freeze(frames / 60.0, scale)

func freeze(duration: float, scale: float = 0.05) -> void:
	var now := Time.get_ticks_msec() / 1000.0
	_freeze_end_at = maxf(_freeze_end_at, now + duration)
	if _active:
		return
	_active = true
	freeze_started.emit()

	# Never a literal 0 — 2-10% keeps particles/shake crawling so the frozen
	# frame still feels alive.
	Engine.time_scale = clampf(scale, 0.01, 1.0)

	# ignore_time_scale=true (4th arg) or this timer never fires while frozen.
	while Time.get_ticks_msec() / 1000.0 < _freeze_end_at:
		var remaining := _freeze_end_at - Time.get_ticks_msec() / 1000.0
		await get_tree().create_timer(remaining, true, false, true).timeout

	# Ease back to full speed — a snap from 5% to 100% reads as a glitch.
	var tween := create_tween()
	tween.set_ignore_time_scale(true)
	tween.tween_property(Engine, "time_scale", 1.0, RECOVERY_TIME) \
		.set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	await tween.finished

	Engine.time_scale = 1.0
	_active = false
	freeze_ended.emit()
