from emulator import *

nes = Emulator('nes_files/mario.nes')
# nes = Debugger('nes_files/01.basics.nes')
while True:
    nes.run()