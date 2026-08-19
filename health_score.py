class HealthScoreEngine:

    @staticmethod
    def calculate(patient, records):

        score = 100

        conditions = []

        for record in records:

            diagnosis = (
                record["diagnosis"] or ""
            ).lower()

            if "viral" in diagnosis:
                score -= 10
                conditions.append("Viral Infection")

            if "diabetes" in diagnosis:
                score -= 20
                conditions.append("Diabetes")

            if "hypertension" in diagnosis:
                score -= 15
                conditions.append("Hypertension")

        score = max(score, 0)

        if score >= 80:
            status = "Excellent"
        elif score >= 60:
            status = "Good"
        elif score >= 40:
            status = "Moderate"
        else:
            status = "Poor"

        return {
            "health_score": score,
            "health_status": status,
            "conditions": list(set(conditions))
        }