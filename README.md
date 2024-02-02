# guitar_pedal_control
guitar pedal based on raspberry pi
The original (v1) was based on a custom raspbian that autostarted both jack and guitarix, providing feedback from 4 footswitches. Commands were sent on guitarix control socket, that provided feedbacks on state changes as well.
the latter (v2) is based on patchobx and depmod and it uses the same footswitches to provide midi commands.
