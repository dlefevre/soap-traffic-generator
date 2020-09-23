#!/usr/bin/python3 

from zeep import Client
import yaml
import io
import getopt
import sys
import time
from threading import Thread


class GeneratorThread (Thread):
    def __init__(self, thinktime, wsdl):
        Thread.__init__(self)
        self.active = True
        self.thinktime = thinktime
        self.client = Client(wsdl=wsdl)

    def stop(self):
        self.active = False

    def run(self):
        print("Starting thread " + self.name + ".")
        while self.active:
            try:
                self.client.service.getUniversalLaw()
            except:
                pass
            time.sleep(self.thinktime)
        print("Thread " + self.name + " stopped.")


def usage():
    print("usage: generator.py [-h][-t <threads>]")
    print("options:")
    print("  -h, --help         Show this message.")
    print("  -t, --threads=...  Update the number of active threads.")


def loadConfig():
    with open("config.yaml", "r") as fh_config:
        return yaml.safe_load(fh_config)


def updateConfig(config):
    with io.open("config.yaml", "w") as fh_config:
        yaml.dump(config, fh_config, default_flow_style=False, allow_unicode=True)


def masterLoop():
    nthreads = 0
    procs = []

    while True:
        config = loadConfig()
        threads = config["threads"]

        if threads < nthreads:
            tmp = []
            for index in range(nthreads):
                if index < threads:
                    tmp.append(procs[index])
                else:
                    procs[index].stop()

            procs = tmp
            nthreads = threads
        elif threads > nthreads:
            while nthreads < threads:
                thread = GeneratorThread(config["thinktime"], config["wsdl"])
                thread.start()

                procs.append(thread)
                nthreads = nthreads + 1

        if nthreads <= 0:
            return

        time.sleep(1)


def main():
    try:
        opts, values = getopt.getopt(sys.argv[1:], "ht:", ["help", "threads="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)

    config = loadConfig()
    print("config: " + str(config))

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-t", "--threads"):
            config['threads'] = int(arg)
            updateConfig(config)
            sys.exit()
    
    masterLoop()

if __name__ == "__main__":
    main();

