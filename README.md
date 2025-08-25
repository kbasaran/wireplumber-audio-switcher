# Wireplumber Audio Switcher
CLI tool to quickly switch microphone and speaker (source and sink) to predefined devices.

## How to use
Run `wpctl status` to see the names of your devices and edit the `scenarios` dictionary in `audio_switcher.py`. This dictionary will define the devices to switch to.
- Each key in `scenarios` is the name of a scenario, such as `tv`, `headset` or `computer_desk`.
- Each value is a tuple of two tuples.
  - First tuple in the tuple is sink keywords, such as `("Philips", "HDMI", "Digital")`.
  - Second tuple in the tuple is source keywords, such as `("Presonus", "Microphone", "Digital")`.

Run the tool from command line with the desired dictionary key:
`/home/myhome/python_venv/bin/python /home/myhome/documents/audio_switcher.py tv`
The script will look for devices that contain all the defined keywords and switch to those devices immediately. 

## Audio hints
The tool plays audio hints to clarify if the switch was successful. First two notes for the sink (play device), then two notes for the source (record device).
### Sink notes
The script will play an E4 note on the old device first. As for second note,
- If new device is found, it will play an E5 on the new device.
- If device not found, it will play a C5 on the old device.
### Source notes
The script will play an E4 note. As for second note,
- If new device is found, it will play an E5.
- If device not found, it will play a C5.
All notes for source will play on default sink.
