from emulator import *

nes = Emulator('nes_files/mario.nes')
# nes = Debugger('nes_files/spritecans.nes')
while True:
    nes.run()