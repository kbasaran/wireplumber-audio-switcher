"""
Switch audio devices in wireplumber
Kerem Basaran 2025
""""

import subprocess
import logging
import sounddevice as sd
import numpy as np
from scipy.signal.windows import general_cosine
logging.basicConfig(level=logging.WARNING)
import time


class Beeper():
    A = .7
    FS = 48000
    T = 0.1
    
    def old(self):
        t = np.arange(self.T * self.FS) / self.FS
        y = self.A * 0.75 * np.sin(t * 2 * np.pi * 440*2**(-7/12))
        y += self.A * 0.25 * np.sin(t * 2 * np.pi * 440*2**(-7/12) * 8)
        window = general_cosine(len(y), (0.3125, 0.46875, 0.1875, 0.03125))
        y = y * window
        
        zeros = np.zeros([int(self.FS * 0.02)])
        
        sd.play(np.concatenate((y, zeros)),
                samplerate=self.FS,
                blocking=True,
                )

    def new_good(self):
        t = np.arange(self.T * self.FS) / self.FS
        y = self.A * 0.75 * np.sin(t * 2 * np.pi * 440*2**(5/12))
        y += self.A * 0.25 * np.sin(t * 2 * np.pi * 440*2**(5/12) * 8)
        window = general_cosine(len(y), (0.3125, 0.46875, 0.1875, 0.03125))
        y = y * window
        
        zeros = np.zeros([int(self.FS * 0.02)])
        
        sd.play(np.concatenate((y, zeros)),
                samplerate=self.FS,
                blocking=True,
                )

    def new_bad(self):
        t = np.arange(self.T * self.FS) / self.FS
        y = self.A * 0.75 * np.sin(t * 2 * np.pi * 440*2**(-11/12))
        y += self.A * 0.25 * np.sin(t * 2 * np.pi * 440*2**(-11/12) * 8)
        window = general_cosine(len(y), (0.3125, 0.46875, 0.1875, 0.03125))
        y = y * window
        
        zeros = np.zeros([int(self.FS * 0.02)])
        
        sd.play(np.concatenate((y, zeros)),
                samplerate=self.FS,
                blocking=True,
                )

# function to parse output of command "wpctl status" and return dictionaries of sinks and sources with their id and name.
def parse_wpctl_status():
    # Execute the wpctl status command and store the output in a variable.
    # Code comes from https://github.com/Sebastiaan76/waybar_wireplumber_audio_changer
    output = str(subprocess.check_output("wpctl status", shell=True, encoding='utf-8'))

    # remove the ascii tree characters and return a list of lines
    lines = output.replace("├", "").replace("─", "").replace("│", "").replace("└", "").splitlines()

    #---- get the index of the Sinks line as a starting point
    sinks_index = None
    for index, line in enumerate(lines):
        if "Sinks:" in line:
            sinks_index = index
            break

    # start by getting the lines after "Sinks:" and before the next blank line and store them in a list
    sinks = []
    for line in lines[sinks_index +1:]:
        if not line.strip():
            break
        sinks.append(line.strip())
        
    # strip the * from the default sink
    for index, sink in enumerate(sinks):
        if sink.startswith("*"):
            sinks[index] = sink.strip().replace("*", "").strip()

    # remove the "[vol:" from the end of the sink name
    for index, sink in enumerate(sinks):
        sinks[index] = sink.split("[vol:")[0].strip()


    # make the dictionary in this format {'sink_id': <int>, 'sink_name': <str>}
    sinks_dict = [{"sink_id": int(sink.split(".")[0]), "sink_name": sink.split(".")[1].strip()} for sink in sinks]
    
    
    #---- get the index of the Sources line as a starting point
    sources_index = None
    for index, line in enumerate(lines):
        if "Sources:" in line:
            sources_index = index
            break

    # start by getting the lines after "Sources:" and before the next blank line and store them in a list
    sources = []
    for line in lines[sources_index +1:]:
        if not line.strip():
            break
        sources.append(line.strip())
        
    # strip the * from the default source
    for index, source in enumerate(sources):
        if source.startswith("*"):
            sources[index] = source.strip().replace("*", "").strip()

    # remove the "[vol:" from the end of the source name
    for index, source in enumerate(sources):
        sources[index] = source.split("[vol:")[0].strip()


    # make the dictionary in this format {'source_id': <int>, 'source_name': <str>}
    sources_dict = [{"source_id": int(source.split(".")[0]), "source_name": source.split(".")[1].strip()} for source in sources]

    return sinks_dict, sources_dict


scenarios = {
    "tv": (         ("Digital", "17h", "Stereo"),   ("HyperX", "Analog")),
    "headset": (    ("Analog", "H600"),             ("Mono", "H600")),
    "desk_call": (  ("UAC"),                        ("Mono", "Webcam")),
    "desk_music": ( ("Digital", "17h", "Stereo"),   ("Mono", "Webcam")),
    }


def change_scenario(scenario):
    global scenarios
    beeper = Beeper()
    sinks, sources = parse_wpctl_status()
    keywords_sink, keywords_source = scenarios[scenario]
    
    # sink
    selected_sink = [sink for sink in sinks if all([keyword in sink['sink_name'] for keyword in keywords_sink])]
    beeper.old()
    if not selected_sink:
        beeper.new_bad()
        logging.warning(f"No sink found with given keywords {keywords_sink}")
    elif len(selected_sink) > 1:
        beeper.new_bad()
        logging.error("Given keywords match multiple devices. Make them more specific.")
    else:

        subprocess.run(f"wpctl set-default {selected_sink[0]['sink_id']}",
                       shell=True,
                       )
        beeper.new_good()
        
    time.sleep(0.2)

    # source
    selected_source = [source for source in sources if all([keyword in source['source_name'] for keyword in keywords_source])]
    beeper.old()
    if not selected_source:
        beeper.new_bad()
        logging.warning(f"No source found with given keywords {keywords_source}")
    elif len(selected_source) > 1:
        beeper.new_bad()
        logging.error("Given keywords match multiple devices."
                      " Make them more specific.")
    else:
        subprocess.run(f"wpctl set-default {selected_source[0]['source_id']}",
                       shell=True,
                       )
        beeper.new_good()


def parse_args():
    import argparse
    global scenarios

    description = (
        "An app to change default auto devices in Wireplumber."
    )

    parser = argparse.ArgumentParser(prog="Audio switcher",
                                     description=description,
                                     )
    parser.add_argument('mode',
                        nargs='?',
                        type=str,
                        help="Choose the audio mode.",
                        choices=scenarios.keys(),
                        )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode is None:
        change_scenario("desk_call")  # for testing
    else:
        change_scenario(args.mode)
