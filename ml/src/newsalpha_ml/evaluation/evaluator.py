from newsalpha_ml.pipelines.train_baselines import train_all_baselines


def evaluate_models() -> dict:
    return train_all_baselines()

