import signal
import sys

from jarvis.engine import Engine

def main():
    engine = Engine()
    def signal_handler(sig, frame):
        engine.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    engine.startup()
    
if __name__ == "__main__":
    main()
