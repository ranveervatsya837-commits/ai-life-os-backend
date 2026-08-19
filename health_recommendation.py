class HealthRecommendationEngine:

    @staticmethod
    def generate(patient, records, health_score):

        recommendations = []

        if health_score >= 80:
            recommendations.append(
                "Maintain your current healthy lifestyle."
            )

        if health_score < 80:
            recommendations.append(
                "Schedule regular health checkups."
            )

        for record in records:

            diagnosis = (
                record["diagnosis"] or ""
            ).lower()

            if "viral" in diagnosis:
                recommendations.append(
                    "Stay hydrated and complete your medication course."
                )

            if "diabetes" in diagnosis:
                recommendations.append(
                    "Monitor blood sugar regularly and avoid sugary foods."
                )

            if "hypertension" in diagnosis:
                recommendations.append(
                    "Reduce salt intake and monitor blood pressure."
                )

        return list(set(recommendations))