from energy_estimator import EnergyEstimator

def main():
    energy_estimator = EnergyEstimator()
    energy_estimator.get_fabric()
    energy_estimator.get_testbenches()
    energy_estimator.generate_estimates()
    return

if __name__ == "__main__":
    main()
