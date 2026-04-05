from precise_runner import PreciseEngine, PreciseRunner
import time
engine = PreciseEngine("/Users/melle/Projects/mycroft-precise/.venv/bin/precise-engine", "Precise-Modelfiles/jarvis.pb")

def detected():
    print("wake word detected")

def check_prob(prob):
    if prob > 0.01:
        print(f"Confidence: {prob:.2f}")

runner = PreciseRunner(engine, sensitivity=0.98, trigger_level=3, on_activation=detected, on_prediction=check_prob)

print("listening...")

runner.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("/nStopping...")
    runner.stop()