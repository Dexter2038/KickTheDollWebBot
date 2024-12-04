import json, numpy as np, pathlib, time


class RegistrationPredictor:

    def __init__(self, data_path="dates.json", order=3):
        self.data_path = pathlib.Path.cwd().joinpath(data_path)
        self.order = order
        self.x, self.y = self._load_data()
        print(
            f"RegistrationPredictor instance located at {pathlib.Path.cwd().resolve()}"
        )
        self._fit_model()

    def _load_data(self):
        try:
            with open(self.data_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            return [], []

        x_data = np.array(list(map(int, data.keys())))
        y_data = np.array(list(map(float, data.values())))
        return x_data, y_data

    def _fit_model(self):
        self.model = np.poly1d(np.polyfit(self.x, self.y, self.order))

    def predict_registration_date(self, tg_id):
        predicted_date = self.model(tg_id)
        current_time = time.time()

        if predicted_date > current_time:
            return current_time
        else:
            return predicted_date

    def is_ok_referal(self, tg_id):
        data = self.predict_registration_date(tg_id)
        diff = data - time.time()
        return diff < 12 * 30 * 24 * 60 * 60
        if diff > 12 * 30 * 24 * 60 * 60:
            return False
        else:
            return True


__all__ = ["RegistrationPredictor"]
