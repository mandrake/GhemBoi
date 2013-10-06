from threading import Thread
import time

# The GB display has size 160x144
# but the buffer is 256x256

class Display(Thread):

    def __init__(self, mbc):
        Thread.__init__(self)
        self.memory = mbc
        self.enabled = False

    def run(self):
        while not self.enabled:
            x = self.memory[0xff40]
            if x & 0x80:
                self.enabled = True
            time.sleep(0.01)

        print "Display enabled"